import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import requests

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET', 'change_this_now')

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, 'data.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        created_at TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS sites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        site_url TEXT,
        added_at TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS keywords (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        site_id INTEGER,
        keyword TEXT,
        last_checked TEXT,
        last_result TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS ad_views (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        viewed_at TEXT
    )''')
    conn.commit()
    conn.close()

def get_db_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.before_first_request
def setup():
    init_db()

# --- Simple local auth (email-as-username) ---
@app.route('/', methods=['GET'])
def home():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form.get('username')
    password = request.form.get('password')
    if not username or not password:
        flash('Provide username and password', 'error')
        return redirect(url_for('home'))
    conn = get_db_conn()
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username,password,created_at) VALUES (?,?,?)',
                  (username, password, datetime.utcnow().isoformat()))
        conn.commit()
        flash('Account created. Please login.', 'success')
    except Exception as e:
        flash('Username exists or error creating account.', 'error')
    conn.close()
    return redirect(url_for('home'))

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    conn = get_db_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
    user = c.fetchone()
    conn.close()
    if user:
        session['user'] = username
        session['user_id'] = user['id']
        return redirect(url_for('dashboard'))
    flash('Invalid credentials', 'error')
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# --- Dashboard & basic CRUD ---
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('home'))
    user_id = session.get('user_id')
    conn = get_db_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM sites WHERE user_id=?', (user_id,))
    sites = c.fetchall()
    totals = {'sites': len(sites), 'keywords': 0}
    keywords = []
    for s in sites:
        c.execute('SELECT * FROM keywords WHERE site_id=?', (s['id'],))
        kws = c.fetchall()
        totals['keywords'] += len(kws)
        for k in kws:
            keywords.append({'site': s['site_url'], 'keyword': k['keyword'], 'last_checked': k['last_checked'], 'last_result': k['last_result']})
    conn.close()
    metrics = {'ai_mentions': 0, 'visibility_score': '0%', 'coverage': '0%'}
    return render_template('dashboard.html', user=session.get('user'), sites=sites, totals=totals, keywords=keywords, metrics=metrics)

@app.route('/sites/add', methods=['GET','POST'])
def add_site():
    if 'user' not in session:
        return redirect(url_for('home'))
    if request.method == 'POST':
        site_url = request.form.get('site_url')
        user_id = session.get('user_id')
        conn = get_db_conn()
        c = conn.cursor()
        c.execute('INSERT INTO sites (user_id,site_url,added_at) VALUES (?,?,?)',
                  (user_id, site_url, datetime.utcnow().isoformat()))
        conn.commit()
        conn.close()
        flash('Site added.', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_site.html')

@app.route('/keywords/add', methods=['POST'])
def add_keyword():
    if 'user' not in session:
        return redirect(url_for('home'))
    site_id = request.form.get('site_id')
    keyword = request.form.get('keyword')
    conn = get_db_conn()
    c = conn.cursor()
    c.execute('INSERT INTO keywords (site_id,keyword,last_checked,last_result) VALUES (?,?,?,?)',
              (site_id, keyword, None, None))
    conn.commit()
    conn.close()
    flash('Keyword added.', 'success')
    return redirect(url_for('dashboard'))

# --- Demo keyword check (uses PERPLEXITY_API_KEY if provided) ---
@app.route('/api/check_keyword', methods=['POST'])
def check_keyword():
    data = request.json or {}
    keyword = data.get('keyword')
    site = data.get('site')
    per_key = os.environ.get('PERPLEXITY_API_KEY')
    result = {'keyword': keyword, 'mentioned': False, 'cited': False, 'engine': 'demo'}
    if per_key:
        try:
            headers = {'Authorization': f'Bearer {per_key}'}
            payload = {'query': keyword}
            resp = requests.post('https://api.perplexity.ai/search', json=payload, headers=headers, timeout=15)
            if resp.status_code == 200:
                j = resp.json()
                text = str(j)
                if site and site.lower() in text.lower():
                    result['cited'] = True
                if session.get('user') and session.get('user').lower() in text.lower():
                    result['mentioned'] = True
                result['engine'] = 'perplexity'
        except Exception as e:
            result['engine'] = 'perplexity_error'
    else:
        # simple demo heuristics
        if keyword and 'best' in keyword.lower():
            result['mentioned'] = True
        if keyword and 'compare' in keyword.lower():
            result['cited'] = True
    return jsonify(result)

# --- Ad watched endpoint (client informs server) ---
@app.route('/api/ad_watched', methods=['POST'])
def ad_watched():
    if 'user' not in session:
        return jsonify({'ok': False, 'error': 'not_logged_in'}), 401
    conn = get_db_conn()
    c = conn.cursor()
    c.execute('INSERT INTO ad_views (user_id, viewed_at) VALUES (?,?)', (session.get('user_id'), datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

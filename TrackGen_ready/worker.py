import os
import sqlite3
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

DB_PATH = 'data.db'

def get_db_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def send_weekly_report(user_id):
    conn = get_db_conn()
    c = conn.cursor()
    c.execute('SELECT username FROM users WHERE id=?', (user_id,))
    u = c.fetchone()
    if not u:
        return False
    user_email = u['username']
    body = f'Weekly report for {user_email}\n'
    c.execute('SELECT * FROM sites WHERE user_id=?', (user_id,))
    for s in c.fetchall():
        body += f"Site: {s['site_url']}\n"
    sg_key = os.environ.get('SENDGRID_API_KEY')
    if sg_key:
        try:
            message = Mail(from_email='noreply@trackgen.example', to_emails=user_email, subject='Weekly AI Visibility', plain_text_content=body)
            sg = SendGridAPIClient(sg_key)
            sg.send(message)
            return True
        except Exception as e:
            print('SendGrid error', e)
            return False
    else:
        with open(f'/tmp/report_{user_id}.txt', 'w') as f:
            f.write(body)
        return True

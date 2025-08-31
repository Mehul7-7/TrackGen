from playwright.sync_api import sync_playwright
import time

def fetch_sge_answer(query):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('https://www.google.com', timeout=60000)
        page.fill('input[name=q]', query)
        page.keyboard.press('Enter')
        page.wait_for_timeout(2000)
        selectors = ['div[role="article"]', 'div[jsname]']
        for sel in selectors:
            try:
                el = page.query_selector(sel)
                if el:
                    text = el.inner_text()
                    browser.close()
                    return {'query': query, 'text': text}
            except Exception:
                continue
        browser.close()
        return {'query': query, 'text': None}

if __name__ == '__main__':
    print(fetch_sge_answer('best luggage brand India'))

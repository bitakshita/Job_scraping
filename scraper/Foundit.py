"""
Foundit.in (formerly Monster India) scraper — 2025 HTML structure.
"""
import requests
from bs4 import BeautifulSoup
import time, random, re

HDR = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-IN,en-US;q=0.9,en;q=0.8",
    "Referer": "https://www.foundit.in/",
    "Connection": "keep-alive",
}

def _t(tag):
    if not tag: return None
    v = tag.get_text(separator=" ", strip=True)
    return re.sub(r'\s+', ' ', v).strip() or None

def scrape_foundit(keyword="developer"):
    kw = keyword.replace(" ", "%20")
    url = f"https://www.foundit.in/srp/results?query={kw}&locationId=1&sort=1&limit=25"
    print(f"\n[Foundit] {url}")
    jobs = []
    try:
        s = requests.Session()
        s.get("https://www.foundit.in", headers=HDR, timeout=10)
        time.sleep(random.uniform(1.5, 2.5))
        r = s.get(url, headers=HDR, timeout=15)
        print(f"[Foundit] HTTP {r.status_code} ({len(r.text)} bytes)")
        if r.status_code != 200:
            print("[Foundit] Blocked — skip"); return []
        soup = BeautifulSoup(r.text, "lxml")

        # Foundit uses div.card-apply-content or div.jobcard
        cards = (soup.find_all("div", class_=lambda c: c and "jobcard" in (c or "").lower()) or
                 soup.find_all("div", class_=lambda c: c and "card-apply" in (c or "").lower()) or
                 soup.find_all("article", class_=lambda c: c and "job" in (c or "").lower()))
        print(f"[Foundit] {len(cards)} cards")

        for card in cards:
            try:
                title = (_t(card.find("a", class_=lambda c: c and "title" in (c or "").lower())) or
                         _t(card.find("h3")) or _t(card.find("h2")) or "N/A")
                company = (_t(card.find("span", class_=lambda c: c and "comp" in (c or "").lower())) or
                           _t(card.find("div", class_=lambda c: c and "company" in (c or "").lower())) or "N/A")
                location_val = (_t(card.find("span", class_=lambda c: c and "loc" in (c or "").lower())) or "India")
                sal_tag = card.find("span", class_=lambda c: c and "salary" in (c or "").lower())
                salary = _t(sal_tag) or ""
                a = card.find("a", href=True)
                href = a["href"] if a else ""
                link = ("https://www.foundit.in" + href) if href.startswith("/") else href or url
                if title and title != "N/A":
                    jobs.append({"title": title, "company": company,
                                 "location": location_val, "salary": salary,
                                 "source": "Foundit", "url": link})
            except Exception as e:
                print(f"[Foundit] card err: {e}")
            time.sleep(random.uniform(0.3, 0.7))
    except Exception as e:
        print(f"[Foundit] fatal: {e}")
    print(f"[Foundit] done — {len(jobs)} jobs")
    return jobs
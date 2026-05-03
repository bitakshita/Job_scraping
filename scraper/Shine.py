import requests
from bs4 import BeautifulSoup
import time, random, re

HDR = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-IN,en-US;q=0.9,en;q=0.8",
    "Referer": "https://www.shine.com/",
    "Connection": "keep-alive",
}

def _t(tag):
    if not tag: return None
    v = tag.get_text(separator=" ", strip=True)
    return re.sub(r'\s+', ' ', v).strip() or None

def scrape_shine(keyword="python developer"):
    kw = keyword.lower().replace(" ", "-")
    url = f"https://www.shine.com/job-search/{kw}-jobs/"
    print(f"\n[Shine] {url}")
    jobs = []
    try:
        s = requests.Session()
        s.get("https://www.shine.com", headers=HDR, timeout=10)
        time.sleep(random.uniform(1.5, 2.5))
        r = s.get(url, headers=HDR, timeout=15)
        print(f"[Shine] HTTP {r.status_code} ({len(r.text)} bytes)")
        if r.status_code != 200:
            print("[Shine] Blocked — skip"); return []
        soup = BeautifulSoup(r.text, "lxml")

        # Shine 2024-25 uses div.job-ads-details or article.job-listing
        cards = (soup.find_all("div", class_=lambda c: c and "job-ads" in (c or "")) or
                 soup.find_all("article", class_=lambda c: c and "job" in (c or "").lower()) or
                 soup.find_all("div", class_=lambda c: c and "jobCard" in (c or "")))
        print(f"[Shine] {len(cards)} cards")

        for card in cards:
            try:
                # TITLE
                title = (_t(card.find("h2")) or
                         _t(card.find("h3")) or
                         _t(card.find("a", class_=lambda c: c and "title" in (c or "").lower())) or "N/A")
                # COMPANY
                company = (_t(card.find("span", class_=lambda c: c and "company" in (c or "").lower())) or
                           _t(card.find("div", class_=lambda c: c and "company" in (c or "").lower())) or "N/A")
                # LOCATION
                location_val = (_t(card.find("span", class_=lambda c: c and "location" in (c or "").lower())) or
                                _t(card.find("div", class_=lambda c: c and "location" in (c or "").lower())) or "India")
                # SALARY
                sal_tag = card.find("span", class_=lambda c: c and "salary" in (c or "").lower())
                salary = _t(sal_tag) or ""
                # URL
                a = card.find("a", href=True)
                href = a["href"] if a else ""
                link = ("https://www.shine.com" + href) if href.startswith("/") else href or url
                if title and title != "N/A":
                    jobs.append({"title": title, "company": company,
                                 "location": location_val, "salary": salary,
                                 "source": "Shine", "url": link})
            except Exception as e:
                print(f"[Shine] card err: {e}")
            time.sleep(random.uniform(0.3, 0.7))
    except Exception as e:
        print(f"[Shine] fatal: {e}")
    print(f"[Shine] done — {len(jobs)} jobs")
    return jobs
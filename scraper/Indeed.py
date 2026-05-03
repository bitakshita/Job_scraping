"""
Indeed India scraper — 2025 HTML structure.
Indeed is JS-heavy but the SSR HTML still contains job cards in <div class="job_seen_beacon">.
KEY FIX: Title in h2.jobTitle > a > span[title] or span text.
Salary in div.salary-snippet-container or metadata tokens.
"""
import requests
from bs4 import BeautifulSoup
import time, random, re

HDR = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-IN,en-US;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://in.indeed.com/",
    "DNT": "1", "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document", "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
}

def _t(tag):
    if not tag: return None
    v = tag.get_text(separator=" ", strip=True)
    return re.sub(r'\s+', ' ', v).strip() or None

def scrape_indeed(keyword="python developer", location="India"):
    kw  = keyword.replace(" ", "+")
    loc = location.replace(" ", "+")
    url = f"https://in.indeed.com/jobs?q={kw}&l={loc}&sort=date"
    print(f"\n[Indeed] {url}")
    jobs = []
    try:
        s = requests.Session()
        s.get("https://in.indeed.com", headers=HDR, timeout=10)
        time.sleep(random.uniform(2, 3))
        r = s.get(url, headers=HDR, timeout=15)
        print(f"[Indeed] HTTP {r.status_code} ({len(r.text)} bytes)")
        if r.status_code != 200:
            print("[Indeed] Blocked — skip"); return []
        soup = BeautifulSoup(r.text, "lxml")

        # Primary card selector (2024-25 layout)
        cards = (soup.find_all("div", class_="job_seen_beacon") or
                 soup.find_all("div", class_=lambda c: c and "cardOutline" in (c or "")) or
                 soup.find_all("li", class_=lambda c: c and "result" in (c or "").lower()))
        print(f"[Indeed] {len(cards)} cards")

        for card in cards:
            try:
                # TITLE: h2.jobTitle > a > span[title] attribute preferred
                title = None
                h2 = card.find("h2", class_=lambda c: c and "jobTitle" in (c or ""))
                if h2:
                    a = h2.find("a")
                    if a:
                        span = a.find("span", attrs={"title": True})
                        title = span["title"] if span and span.get("title") else _t(a)
                if not title:
                    title = _t(card.find("h2")) or "N/A"

                # COMPANY: span.companyName
                company = (_t(card.find("span", class_="companyName")) or
                           _t(card.find("span", class_=lambda c: c and "company" in (c or "").lower())) or
                           "N/A")

                # LOCATION: div.companyLocation
                location_val = (_t(card.find("div", class_="companyLocation")) or
                                _t(card.find("span", class_=lambda c: c and "location" in (c or "").lower())) or
                                "India")

                # SALARY: div.salary-snippet-container or metadata
                sal_tag = (card.find("div", class_="salary-snippet-container") or
                           card.find("div", class_=lambda c: c and "salary" in (c or "").lower()) or
                           card.find("span", class_=lambda c: c and "salary" in (c or "").lower()))
                salary = _t(sal_tag) or ""

                # URL: base + href from h2 > a
                link = "https://in.indeed.com"
                if h2:
                    a = h2.find("a")
                    if a and a.get("href"):
                        href = a["href"]
                        link = ("https://in.indeed.com" + href) if href.startswith("/") else href

                if title and title != "N/A":
                    jobs.append({"title": title, "company": company,
                                 "location": location_val, "salary": salary,
                                 "source": "Indeed", "url": link})
            except Exception as e:
                print(f"[Indeed] card err: {e}")
            time.sleep(random.uniform(0.4, 1.0))
    except Exception as e:
        print(f"[Indeed] fatal: {e}")
    print(f"[Indeed] done — {len(jobs)} jobs")
    return jobs
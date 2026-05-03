"""
Naukri.com scraper — 2025 HTML structure.
Naukri renders jobs server-side (SSR), so plain requests works.
KEY FIX: Title in article > a.title, Salary in span.salary.
"""
import requests
from bs4 import BeautifulSoup
import time, random, re

HDR = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-IN,en-US;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1", "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Referer": "https://www.naukri.com/",
    "Sec-Fetch-Dest": "document", "Sec-Fetch-Mode": "navigate",
}

def _t(tag):
    if not tag: return None
    v = tag.get_text(separator=" ", strip=True)
    return re.sub(r'\s+', ' ', v).strip() or None

def scrape_naukri(keyword="developer", location="India"):
    kw  = keyword.lower().replace(" ", "-")
    loc = location.lower().replace(" ", "-")
    url = f"https://www.naukri.com/{kw}-jobs-in-{loc}" if loc != "india" else f"https://www.naukri.com/{kw}-jobs"
    print(f"\n[Naukri] {url}")
    jobs = []
    try:
        s = requests.Session()
        s.get("https://www.naukri.com", headers=HDR, timeout=10)
        time.sleep(random.uniform(2, 3))
        r = s.get(url, headers=HDR, timeout=15)
        print(f"[Naukri] HTTP {r.status_code} ({len(r.text)} bytes)")
        if r.status_code != 200:
            print("[Naukri] Blocked — skip"); return []
        soup = BeautifulSoup(r.text, "lxml")

        # Naukri 2024-25: article.jobTuple or div.srp-jobtuple-wrapper
        cards = (soup.find_all("article", class_=lambda c: c and "jobTuple" in (c or "")) or
                 soup.find_all("div", class_="srp-jobtuple-wrapper") or
                 soup.find_all("div", class_=lambda c: c and "jobTuple" in (c or "")))
        print(f"[Naukri] {len(cards)} cards")

        for card in cards:
            try:
                # TITLE: a.title (the main job link)
                a_title = card.find("a", class_="title")
                title = _t(a_title) or _t(card.find("a", class_=lambda c: c and "title" in (c or ""))) or "N/A"

                # COMPANY: a.comp-name or span.comp-name
                company = (_t(card.find("a", class_="comp-name")) or
                           _t(card.find("span", class_="comp-name")) or
                           _t(card.find("a", class_=lambda c: c and "comp" in (c or "").lower())) or "N/A")

                # LOCATION: span.locWdth or li with location info
                location_val = (_t(card.find("span", class_="locWdth")) or
                                _t(card.find("span", class_=lambda c: c and "loc" in (c or "").lower())) or
                                _t(card.find("li", class_=lambda c: c and "location" in (c or "").lower())) or
                                "India")

                # EXPERIENCE
                exp = (_t(card.find("span", class_="expwdth")) or
                       _t(card.find("span", class_=lambda c: c and "exp" in (c or "").lower())) or "")

                # SALARY: span.salary or div containing lpa/lakhs
                sal_tag = (card.find("span", class_="salary") or
                           card.find("span", class_=lambda c: c and "salary" in (c or "").lower()) or
                           card.find("div", class_=lambda c: c and "salary" in (c or "").lower()))
                salary = _t(sal_tag) or ""
                if not salary:
                    # scan all spans for salary pattern
                    for sp in card.find_all("span"):
                        t = _t(sp) or ""
                        if re.search(r'(\d+[\.,]?\d*\s*(lpa|lakhs?|lakh|₹|rs\.))', t, re.I):
                            salary = t[:60]; break

                # URL
                link = ""
                if a_title and a_title.get("href"):
                    link = a_title["href"]
                    if not link.startswith("http"):
                        link = "https://www.naukri.com" + link
                if not link:
                    link = url

                if title and title != "N/A":
                    jobs.append({"title": title, "company": company,
                                 "location": location_val, "salary": salary,
                                 "source": "Naukri", "url": link})
            except Exception as e:
                print(f"[Naukri] card err: {e}")
            time.sleep(random.uniform(0.4, 0.9))
    except Exception as e:
        print(f"[Naukri] fatal: {e}")
    print(f"[Naukri] done — {len(jobs)} jobs")
    return jobs
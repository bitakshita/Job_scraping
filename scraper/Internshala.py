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
    "Sec-Fetch-Dest": "document", "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none", "Cache-Control": "max-age=0",
}

def _t(tag):
    if not tag: return None
    v = tag.get_text(separator=" ", strip=True)
    return re.sub(r'\s+', ' ', v).strip() or None

def scrape_internshala(keyword="python developer"):
    kw = keyword.strip().lower().replace(" ", "-")
    url = f"https://internshala.com/jobs/{kw}-jobs"
    print(f"\n[Internshala] {url}")
    jobs = []
    try:
        s = requests.Session()
        s.get("https://internshala.com", headers=HDR, timeout=10)
        time.sleep(random.uniform(1.5, 2.5))
        r = s.get(url, headers=HDR, timeout=15)
        print(f"[Internshala] HTTP {r.status_code} ({len(r.text)} bytes)")
        if r.status_code != 200:
            print("[Internshala] Blocked — skip"); return []
        soup = BeautifulSoup(r.text, "lxml")
        cards = soup.find_all("div", class_="individual_internship") or \
                soup.find_all("div", attrs={"data-internship_id": True})
        print(f"[Internshala] {len(cards)} cards")
        for card in cards:
            try:
                title = (_t(card.find("a", class_="job-title-href")) or
                         _t(card.find("h3", class_="job-internship-name")) or
                         _t(card.find("h3", class_="profile")) or
                         _t(card.find("h3")) or "N/A")
                company = (_t(card.find("p", class_="company-name")) or
                           _t(card.find("h4", class_="company-name")) or "N/A")
                location = (_t(card.find("p", class_="locations")) or
                            _t(card.find("div", class_="location_link")) or
                            _t(card.find("span", class_="location")) or "N/A")
                salary = (_t(card.find("span", class_="stipend")) or
                          _t(card.find("div", class_="stipend_container")) or
                          _t(card.find("span", class_="salary")) or "")
                a = (card.find("a", class_="job-title-href") or
                     card.find("a", class_="view_detail_button") or
                     (card.find("h3").find("a") if card.find("h3") else None))
                href = a["href"] if a and a.get("href") else ""
                link = ("https://internshala.com" + href) if href.startswith("/") else href or url
                if title and title != "N/A":
                    jobs.append({"title": title, "company": company,
                                 "location": location, "salary": salary,
                                 "source": "Internshala", "url": link})
            except Exception as e:
                print(f"[Internshala] card err: {e}")
            time.sleep(random.uniform(0.3, 0.8))
    except Exception as e:
        print(f"[Internshala] fatal: {e}")
    print(f"[Internshala] done — {len(jobs)} jobs")
    return jobs
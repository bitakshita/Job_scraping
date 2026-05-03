"""
TimesJobs scraper — 2025 HTML structure.
KEY FIX: Title is in h2 > a (not h2 directly).
Salary is in span.salary inside .jd-stats.
"""
import requests
from bs4 import BeautifulSoup
import time, random, re

HDR = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-IN,en-US;q=0.9,en;q=0.8",
    "Referer": "https://www.timesjobs.com/",
    "Connection": "keep-alive",
}

def _t(tag):
    if not tag: return None
    v = tag.get_text(separator=" ", strip=True)
    return re.sub(r'\s+', ' ', v).strip() or None

def scrape_timesjobs(keyword="python developer"):
    kw = keyword.strip().replace(" ", "%20")
    url = f"https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&txtKeywords={kw}&txtLocation="
    print(f"\n[TimesJobs] {url}")
    jobs = []
    try:
        s = requests.Session()
        s.get("https://www.timesjobs.com", headers=HDR, timeout=10)
        time.sleep(random.uniform(1.5, 2.5))
        r = s.get(url, headers=HDR, timeout=15)
        print(f"[TimesJobs] HTTP {r.status_code} ({len(r.text)} bytes)")
        if r.status_code != 200:
            print("[TimesJobs] Blocked — skip"); return []
        soup = BeautifulSoup(r.text, "lxml")
        cards = (soup.find_all("li", class_="clearfix job-bx wht-shd-bx") or
                 soup.find_all("li", class_=lambda c: c and "job-bx" in c))
        print(f"[TimesJobs] {len(cards)} cards")
        for card in cards:
            try:
                # TITLE: h2 > a  (the anchor text is the job title)
                h2 = card.find("h2")
                if h2:
                    a_title = h2.find("a")
                    title = _t(a_title) if a_title else _t(h2)
                else:
                    title = None
                if not title or title == "":
                    title = "N/A"

                # COMPANY: h3.joblist-comp-name — strip "More jobs by this company"
                co_tag = card.find("h3", class_="joblist-comp-name")
                company = _t(co_tag) or "N/A"
                company = company.replace("More jobs by this company", "").strip()

                # LOCATION: look for span/li containing city names or "loc_" class
                location = "India"
                loc_tag = (card.find("span", class_=lambda c: c and "loc" in (c or "").lower()) or
                           card.find("li", class_="srp-zindex location-tru"))
                if loc_tag:
                    location = _t(loc_tag) or "India"
                else:
                    # scan li items inside ul.top-jd-dtl
                    for li in card.select("ul.top-jd-dtl li"):
                        txt = _t(li) or ""
                        if any(city in txt for city in [
                            "Delhi","Mumbai","Bangalore","Bengaluru","Hyderabad",
                            "Chennai","Pune","Kolkata","Noida","Gurgaon","Gurugram",
                            "Jaipur","Ahmedabad","Remote","India","Rajasthan"
                        ]):
                            location = txt[:80]; break

                # SALARY: span with class containing 'salary', or inside .jd-stats
                sal_tag = (card.find("span", class_=lambda c: c and "salary" in (c or "").lower()) or
                           card.find("li", class_=lambda c: c and "salary" in (c or "").lower()))
                salary = _t(sal_tag) or ""
                # Some cards show salary as "Rs. X - Y Lacs" in plain text blocks
                if not salary:
                    for li in card.select("ul.jd-desc li"):
                        t = _t(li) or ""
                        if "lakh" in t.lower() or "lpa" in t.lower() or "rs." in t.lower() or "₹" in t:
                            salary = t[:60]; break

                # URL
                link = url
                if h2:
                    a = h2.find("a")
                    if a and a.get("href"):
                        link = a["href"]

                if title and title != "N/A":
                    jobs.append({"title": title, "company": company,
                                 "location": location, "salary": salary,
                                 "source": "TimesJobs", "url": link})
            except Exception as e:
                print(f"[TimesJobs] card err: {e}")
            time.sleep(random.uniform(0.3, 0.8))
    except Exception as e:
        print(f"[TimesJobs] fatal: {e}")
    print(f"[TimesJobs] done — {len(jobs)} jobs")
    return jobs
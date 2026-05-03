"""
NCS (National Career Service) Govt Portal scraper.
NCS uses an AJAX/API endpoint to return job JSON — no JS rendering needed.
Endpoint: https://www.ncs.gov.in/api/jobs/search  (POST with JSON body)
Fallback: scrape the public job listing page directly.
"""
import requests
from bs4 import BeautifulSoup
import time, random, re, json

HDR_JSON = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-IN,en-US;q=0.9",
    "Content-Type": "application/json",
    "Referer": "https://www.ncs.gov.in/",
    "Origin": "https://www.ncs.gov.in",
    "Connection": "keep-alive",
}
HDR_HTML = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-IN,en-US;q=0.9",
    "Referer": "https://www.ncs.gov.in/",
    "Connection": "keep-alive",
}

def _t(tag):
    if not tag: return None
    v = tag.get_text(separator=" ", strip=True)
    return re.sub(r'\s+', ' ', v).strip() or None

def scrape_ncs(keyword="python developer", location=""):
    print(f"\n[NCS] Keyword: '{keyword}'")
    jobs = []

    # ── Method 1: Try the JSON API endpoint ──────────────────────
    try:
        api_url = "https://www.ncs.gov.in/api/jobs/search"
        payload = {
            "keyword": keyword,
            "location": location,
            "pageNo": 1,
            "pageSize": 20,
            "sortBy": "postingDate",
        }
        s = requests.Session()
        s.get("https://www.ncs.gov.in", headers=HDR_HTML, timeout=10)
        time.sleep(random.uniform(1, 2))
        r = s.post(api_url, json=payload, headers=HDR_JSON, timeout=15)
        print(f"[NCS API] HTTP {r.status_code} ({len(r.text)} bytes)")

        if r.status_code == 200:
            try:
                data = r.json()
                # NCS API returns {"data": {"jobList": [...]}}  or {"jobs": [...]}
                job_list = (
                    data.get("data", {}).get("jobList", []) or
                    data.get("jobs", []) or
                    data.get("jobDetails", []) or
                    (data if isinstance(data, list) else [])
                )
                print(f"[NCS API] {len(job_list)} jobs in response")
                for j in job_list:
                    title    = j.get("jobTitle") or j.get("title") or j.get("post_name") or "N/A"
                    company  = j.get("empName") or j.get("employer") or j.get("company") or j.get("organizationName") or "N/A"
                    location_val = j.get("jobLocation") or j.get("location") or j.get("city") or "India"
                    salary   = j.get("salary") or j.get("ctc") or j.get("payScale") or ""
                    job_id   = j.get("jobId") or j.get("id") or ""
                    link     = f"https://www.ncs.gov.in/jobseeker/pages/jobsearch/jobdetail.aspx?jobid={job_id}" if job_id else "https://www.ncs.gov.in"

                    if title and title != "N/A":
                        jobs.append({"title": str(title), "company": str(company),
                                     "location": str(location_val), "salary": str(salary),
                                     "source": "Govt/NCS", "url": link})
                if jobs:
                    print(f"[NCS] done via API — {len(jobs)} jobs")
                    return jobs
            except json.JSONDecodeError:
                print("[NCS API] Response not JSON — trying HTML fallback")
    except Exception as e:
        print(f"[NCS API] Error: {e}")

    # ── Method 2: HTML scrape fallback ───────────────────────────
    try:
        kw_enc = keyword.replace(" ", "+")
        html_url = f"https://www.ncs.gov.in/jobseeker/pages/jobsearch/jobsearch.aspx?keyword={kw_enc}"
        print(f"[NCS HTML] {html_url}")
        r = requests.get(html_url, headers=HDR_HTML, timeout=15)
        print(f"[NCS HTML] HTTP {r.status_code} ({len(r.text)} bytes)")
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "lxml")
            # NCS HTML uses table rows or div.job-list-item
            rows = (soup.find_all("div", class_=lambda c: c and "job" in (c or "").lower()) or
                    soup.find_all("tr", class_=lambda c: c and "job" in (c or "").lower()))
            print(f"[NCS HTML] {len(rows)} rows found")
            for row in rows:
                try:
                    cells = row.find_all(["td", "div"])
                    if len(cells) >= 2:
                        title    = _t(cells[0]) or _t(cells[1]) or "N/A"
                        company  = _t(cells[1]) if len(cells) > 1 else "Govt"
                        location_val = _t(cells[2]) if len(cells) > 2 else "India"
                        salary   = _t(cells[3]) if len(cells) > 3 else ""
                        a        = row.find("a", href=True)
                        href     = a["href"] if a else ""
                        link     = ("https://www.ncs.gov.in" + href) if href.startswith("/") else href or html_url
                        if title and title != "N/A":
                            jobs.append({"title": title, "company": company,
                                         "location": location_val, "salary": salary,
                                         "source": "Govt/NCS", "url": link})
                except Exception as e:
                    print(f"[NCS HTML] row err: {e}")
    except Exception as e:
        print(f"[NCS HTML] Error: {e}")

    print(f"[NCS] done — {len(jobs)} jobs")
    return jobs
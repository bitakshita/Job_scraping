"""
Main scraper runner — runs all active scrapers for all keywords.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_handler import init_db, save_job
from config import KEYWORDS, ACTIVE_SCRAPERS

def run_scraper():
    init_db()
    total_new  = 0
    all_new    = []

    # Import only active scrapers
    scrapers = {}
    if "internshala" in ACTIVE_SCRAPERS:
        from scraper.Internshala import scrape_internshala
        scrapers["internshala"] = scrape_internshala
    if "timesjobs" in ACTIVE_SCRAPERS:
        from scraper.timesjob import scrape_timesjobs
        scrapers["timesjobs"] = scrape_timesjobs
    if "indeed" in ACTIVE_SCRAPERS:
        from scraper.Indeed import scrape_indeed
        scrapers["indeed"] = scrape_indeed
    if "naukri" in ACTIVE_SCRAPERS:
        from scraper.Naukri import scrape_naukri
        scrapers["naukri"] = scrape_naukri
    if "shine" in ACTIVE_SCRAPERS:
        from scraper.Shine import scrape_shine
        scrapers["shine"] = scrape_shine
    if "foundit" in ACTIVE_SCRAPERS:
        from scraper.Foundit import scrape_foundit
        scrapers["foundit"] = scrape_foundit
    if "ncs" in ACTIVE_SCRAPERS:
        from scraper.Ncs import scrape_ncs
        scrapers["ncs"] = scrape_ncs

    for keyword in KEYWORDS:
        print(f"\n{'='*50}")
        print(f"  Keyword: {keyword}")
        print(f"{'='*50}")

        for name, fn in scrapers.items():
            try:
                jobs = fn(keyword)
                for job in jobs:
                    is_new = save_job(
                        title=job.get("title", "N/A"),
                        company=job.get("company", "N/A"),
                        location=job.get("location", "N/A"),
                        salary=job.get("salary", ""),
                        source=job.get("source", name),
                        url=job.get("url", ""),
                        posted_date=job.get("posted_date", ""),
                    )
                    if is_new:
                        total_new += 1
                        all_new.append(job)
                        print(f"  ✓ NEW: [{job['source']}] {job['title']} @ {job['company']}")
            except Exception as e:
                print(f"  ✗ {name} scraper crashed: {e}")

    print(f"\n{'='*50}")
    print(f"  DONE — {total_new} new jobs saved to database")
    print(f"{'='*50}\n")
    return total_new, all_new


if __name__ == "__main__":
    run_scraper()
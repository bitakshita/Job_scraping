import sqlite3
from datetime import datetime

DB_PATH = "database/jobs.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT,
            company     TEXT,
            location    TEXT,
            salary      TEXT,
            source      TEXT,
            url         TEXT UNIQUE,
            posted_date TEXT,
            scraped_at  TEXT,
            notified    INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def save_job(title, company, location, salary, source, url, posted_date=""):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO jobs (title, company, location, salary, source, url, posted_date, scraped_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (title, company, location, salary, source, url,
              posted_date, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_all_jobs(search="", source="", filter_type=""):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = "SELECT * FROM jobs WHERE 1=1"
    params = []

    if search:
        query += " AND (title LIKE ? OR company LIKE ? OR location LIKE ?)"
        like = f"%{search}%"
        params += [like, like, like]

    if source and source != "all":
        query += " AND source = ?"
        params.append(source)

    if filter_type == "new":
        query += " AND DATE(scraped_at) = DATE('now')"
    elif filter_type == "remote":
        query += " AND location LIKE '%Remote%'"
    elif filter_type == "python":
        query += " AND title LIKE '%Python%'"
    elif filter_type == "ml":
        query += " AND (title LIKE '%ML%' OR title LIKE '%AI%' OR title LIKE '%Data%' OR title LIKE '%Machine Learning%')"

    query += " ORDER BY scraped_at DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM jobs")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM jobs WHERE DATE(scraped_at) = DATE('now')")
    new_today = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT source) FROM jobs")
    sources = cursor.fetchone()[0]

    cursor.execute("""
        SELECT source, COUNT(*) as cnt FROM jobs
        GROUP BY source ORDER BY cnt DESC
    """)
    by_source = [{"source": r[0], "count": r[1]} for r in cursor.fetchall()]

    # top skill
    skills = ["Python", "Data", "ML", "Java", "React", "Django", "AI", "Cloud"]
    skill_counts = {}
    for skill in skills:
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE title LIKE ?", (f"%{skill}%",))
        cnt = cursor.fetchone()[0]
        if cnt > 0:
            skill_counts[skill] = cnt
    top_skill = max(skill_counts, key=skill_counts.get) if skill_counts else "N/A"
    top_skill_count = skill_counts.get(top_skill, 0)

    cursor.execute("SELECT scraped_at FROM jobs ORDER BY scraped_at DESC LIMIT 1")
    last = cursor.fetchone()
    last_scan = last[0] if last else "Never"

    conn.close()
    return {
        "total": total,
        "new_today": new_today,
        "sources": sources,
        "by_source": by_source,
        "top_skill": top_skill,
        "top_skill_count": top_skill_count,
        "last_scan": last_scan
    }

def delete_job(job_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
    conn.commit()
    conn.close()

def clear_all_jobs():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM jobs")
    conn.commit()
    conn.close()

def get_sources():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT source FROM jobs ORDER BY source")
    sources = [r[0] for r in cursor.fetchall()]
    conn.close()
    return sources
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, jsonify, request
from database.db_handler import init_db, get_all_jobs, get_stats, get_sources, delete_job, clear_all_jobs
import threading

app = Flask(__name__)

# ── Pages ────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

# ── API ──────────────────────────────────────────────────────────

@app.route("/api/jobs")
def api_jobs():
    search      = request.args.get("search", "")
    source      = request.args.get("source", "all")
    filter_type = request.args.get("filter", "all")
    jobs = get_all_jobs(search=search, source=source, filter_type=filter_type)
    return jsonify(jobs)

@app.route("/api/stats")
def api_stats():
    return jsonify(get_stats())

@app.route("/api/sources")
def api_sources():
    return jsonify(get_sources())

@app.route("/api/scrape", methods=["POST"])
def api_scrape():
    """Runs the scraper in a background thread so the UI doesn't hang."""
    def _run():
        from scraper_run import run_scraper
        run_scraper()
    t = threading.Thread(target=_run, daemon=True)
    t.start()
    return jsonify({"status": "started", "message": "Scraper running in background"})

@app.route("/api/jobs/<int:job_id>", methods=["DELETE"])
def api_delete_job(job_id):
    delete_job(job_id)
    return jsonify({"status": "deleted"})

@app.route("/api/jobs/clear", methods=["POST"])
def api_clear():
    clear_all_jobs()
    return jsonify({"status": "cleared"})

# ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    print("\n🚀  JobRadar running at  http://localhost:5000\n")
    app.run(debug=True, port=5000)
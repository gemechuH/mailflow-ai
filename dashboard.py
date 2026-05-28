from flask import Flask, render_template, jsonify
from summary import DailySummary
from email_log import get_history
from config import COMPANY_NAME, DEPARTMENTS

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html", company=COMPANY_NAME)


@app.route("/api/stats")
def stats():
    daily = DailySummary()
    return jsonify({
        "date": str(daily.date),
        "total": daily.total_processed,
        "skipped": daily.skipped,
        "errors": daily.errors,
        "departments": {
            dept: {
                "count": daily.counts.get(dept, 0),
                "email": DEPARTMENTS[dept]["email"],
            }
            for dept in DEPARTMENTS
        },
    })


@app.route("/api/emails")
def emails():
    return jsonify(get_history(100))


if __name__ == "__main__":
    print(f"\nDashboard running at: http://localhost:5000")
    app.run(debug=False, port=5000)

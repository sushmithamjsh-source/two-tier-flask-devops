import os
import time
import pymysql
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

DB_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "localhost"),
    "user": os.environ.get("MYSQL_USER", "root"),
    "password": os.environ.get("MYSQL_PASSWORD", ""),
    "database": os.environ.get("MYSQL_DB", "devops"),
    "cursorclass": pymysql.cursors.DictCursor,
}


def get_connection(retries=10, delay=3):
    """MySQL takes time to start, so retry instead of crashing."""
    for attempt in range(retries):
        try:
            return pymysql.connect(**DB_CONFIG)
        except pymysql.err.OperationalError:
            print(f"DB not ready, retry {attempt + 1}/{retries}", flush=True)
            time.sleep(delay)
    raise RuntimeError("Could not connect to the database")


@app.route("/health")
def health():
    return {"status": "ok"}, 200


@app.route("/", methods=["GET", "POST"])
def index():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            if request.method == "POST":
                text = request.form.get("message", "").strip()
                if text:
                    cur.execute("INSERT INTO messages (message) VALUES (%s)", (text,))
                    conn.commit()
                return redirect("/")
            cur.execute("SELECT message FROM messages ORDER BY id DESC")
            messages = [row["message"] for row in cur.fetchall()]
    finally:
        conn.close()
    return render_template("index.html", messages=messages)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

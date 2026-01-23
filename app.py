from flask import Flask, render_template, request, redirect, session, abort, jsonify, url_for
import sqlite3
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import re

# ✅ Cloudinary
import cloudinary
import cloudinary.uploader

app = Flask(__name__)
app.secret_key = "huliyar-secret-key-change-this"

# ✅ Editor login (Phone + Password)
EDITOR_PHONE = "9036860070"
EDITOR_PASSWORD = "12345"

# ✅ Allowed types
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif", "mp4", "webm", "ogg", "mov", "3gp", "mkv"}

# ✅ Cloudinary config (from Render Environment Variables)
cloudinary.config(
    cloud_name=os.environ.get("dvi3nqttx"),
    api_key=os.environ.get("613868972687331"),
    api_secret=os.environ.get("N5IB2"),
    secure=True
)


def db():
    # ✅ Always correct db path (Render fix)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "news.db")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            content TEXT NOT NULL,
            thumb TEXT,
            views INTEGER DEFAULT 0,
            breaking INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def editor_required():
    return session.get("is_editor") is True


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------------- PUBLIC ----------------

@app.route("/")
def public_home():
    lang = request.args.get("lang", "kn")

    conn = db()
    news_list = conn.execute("SELECT * FROM news ORDER BY id DESC").fetchall()
    trending = conn.execute("SELECT * FROM news ORDER BY views DESC LIMIT 10").fetchall()
    breaking_list = conn.execute("SELECT * FROM news WHERE breaking=1 ORDER BY id DESC LIMIT 10").fetchall()
    conn.close()

    return render_template(
        "public_home.html",
        news_list=news_list,
        trending=trending,
        breaking_list=breaking_list,
        lang=lang
    )


@app.route("/news/<int:news_id>")
def news_detail(news_id):
    lang = request.args.get("lang", "kn")

    conn = db()
    conn.execute("UPDATE news SET views = views + 1 WHERE id=?", (news_id,))
    conn.commit()

    item = conn.execute("SELECT * FROM news WHERE id=?", (news_id,)).fetchone()
    conn.close()

    if not item:
        abort(404)

    return render_template("news_detail.html", item=item, lang=lang)


@app.route("/category/<catname>")
def category_page(catname):
    lang = request.args.get("lang", "kn")

    conn = db()
    news_list = conn.execute(
        "SELECT * FROM news WHERE lower(category)=lower(?) ORDER BY id DESC",
        (catname,)
    ).fetchall()

    trending = conn.execute("SELECT * FROM news ORDER BY views DESC LIMIT 10").fetchall()
    breaking_list = conn.execute("SELECT * FROM news WHERE breaking=1 ORDER BY id DESC LIMIT 10").fetchall()
    conn.close()

    return render_template(
        "category.html",
        catname=catname,
        news_list=news_list,
        trending=trending,
        breaking_list=breaking_list,
        lang=lang
    )


# ---------------- EDITOR ----------------

@app.route("/editor/login", methods=["GET", "POST"])
def editor_login():
    if request.method == "POST":
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "").strip()

        if phone == EDITOR_PHONE and password == EDITOR_PASSWORD:
            session["is_editor"] = True
            return redirect("/editor/dashboard")

        return render_template("editor_login.html", error="❌ Phone number / Password ತಪ್ಪಾಗಿದೆ!")

    return render_template("editor_login.html", error=None)


@app.route("/editor/logout")
def editor_logout():
    session.clear()
    return redirect("/")


@app.route("/editor/dashboard")
def editor_dashboard():
    if not editor_required():
        return redirect("/editor/login")

    conn = db()
    news_list = conn.execute("SELECT * FROM news ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("editor_dashboard.html", news_list=news_list)


@app.route("/editor/new", methods=["GET", "POST"])
def editor_new():
    if not editor_required():
        return redirect("/editor/login")

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        category = request.form.get("category", "").strip()
        content = request.form.get("content", "").strip()
        breaking = 1 if request.form.get("breaking") == "1" else 0

        if not title or not content:
            return "❌ Error: Title or Content empty"

        created_at = datetime.now().strftime("%d-%m-%Y %I:%M %p")

        # ✅ auto thumbnail from first image in content
        thumb = None
        m = re.search(r'<img[^>]+src="([^"]+)"', content)
        if m:
            thumb = m.group(1)  # Cloudinary URL will be stored here automatically

        conn = db()
        conn.execute(
            "INSERT INTO news (title, category, content, thumb, breaking, created_at) VALUES (?,?,?,?,?,?)",
            (title, category, content, thumb, breaking, created_at)
        )
        conn.commit()
        conn.close()

        return redirect("/editor/dashboard")

    return render_template("editor_new.html")


@app.route("/editor/edit/<int:news_id>", methods=["GET", "POST"])
def editor_edit(news_id):
    if not editor_required():
        return redirect("/editor/login")

    conn = db()
    item = conn.execute("SELECT * FROM news WHERE id=?", (news_id,)).fetchone()

    if not item:
        conn.close()
        abort(404)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        category = request.form.get("category", "").strip()
        content = request.form.get("content", "").strip()
        breaking = 1 if request.form.get("breaking") == "1" else 0

        # ✅ auto thumbnail from first image in content
        thumb = None
        m = re.search(r'<img[^>]+src="([^"]+)"', content)
        if m:
            thumb = m.group(1)  # Cloudinary URL

        conn.execute("""
            UPDATE news SET title=?, category=?, content=?, thumb=?, breaking=?
            WHERE id=?
        """, (title, category, content, thumb, breaking, news_id))

        conn.commit()
        conn.close()

        return redirect("/editor/dashboard")

    conn.close()
    return render_template("editor_edit.html", item=item)


@app.route("/editor/delete/<int:news_id>")
def editor_delete(news_id):
    if not editor_required():
        return redirect("/editor/login")

    conn = db()
    conn.execute("DELETE FROM news WHERE id=?", (news_id,))
    conn.commit()
    conn.close()
    return redirect("/editor/dashboard")


# ✅ CKEditor upload handler (Cloudinary images + videos)
@app.route("/upload-media", methods=["POST"])
def upload_media():
    if not editor_required():
        return jsonify({"uploaded": 0, "error": {"message": "Session expired. Please login again."}}), 401

    file = request.files.get("upload")
    if not file:
        return jsonify({"uploaded": 0, "error": {"message": "No file received"}}), 400

    if file.filename == "":
        return jsonify({"uploaded": 0, "error": {"message": "Empty filename"}}), 400

    if not allowed_file(file.filename):
        return jsonify({"uploaded": 0, "error": {"message": "Invalid file type"}}), 400

    try:
        filename = secure_filename(file.filename)
        ext = filename.rsplit(".", 1)[-1].lower()

        is_video = ext in {"mp4", "webm", "ogg", "mov", "3gp", "mkv"}

        # ✅ Upload to Cloudinary
        result = cloudinary.uploader.upload(
            file,
            resource_type="video" if is_video else "image",
            folder="huliyar_news"
        )

        url = result.get("secure_url")
        if not url:
            return jsonify({"uploaded": 0, "error": {"message": "Cloudinary upload failed"}}), 500

        return jsonify({"uploaded": 1, "fileName": filename, "url": url})

    except Exception as e:
        return jsonify({"uploaded": 0, "error": {"message": str(e)}}), 500


if __name__ == "__main__":
    init_db()
    app.run(debug=True)


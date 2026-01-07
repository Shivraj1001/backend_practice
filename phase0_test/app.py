from flask import Flask, request
from scraper import scrape_title
from db import get_connection

app = Flask(__name__)

@app.route("/delete", methods=["POST"])
def delete_page():
    url = request.json.get("url")
    
    if not url:
        return {"status": "error", "message": "url required"}, 400
    
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM pages WHERE url = ?",
        (url,)
    )

    conn.commit()
    conn.close()

    return {"status": "success"}

@app.route("/update", methods=["POST"])
def update_page():
    url = request.json.get("url")
    new_title = request.json.get("title")

    if not url or not new_title:
        return {"status": "error", "message": "url and title required"}, 400
    
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE pages SET title = ? WHERE url = ?",
        (new_title, url)
    )

    conn.commit()
    conn.close()

    return {"status": "success"}

@app.route("/scrape")
def scrape():
    url = request.args.get("url")

    if not url:
        return {
            "status":"error",
            "message": "url parameter is required"
        }, 400
    
    title = scrape_title(url)

    if not title:
        return {
            "status": "error",
            "message": "could not scrape the page"
        }, 500
    
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO pages (url, title) VALUES (?, ?)",
        (url, title)
    )

    conn.commit()
    conn.close()

    return {
        "status": "success",
        "data": {"url": url, "title": title}
    }

@app.route("/pages")
def get_pages():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT url, title FROM pages")
    rows = cursor.fetchall()

    conn.close()
    data = []
    for row in rows:
        data.append({
            "url": row[0],
            "title": row[1]
        })
    return{
        "status": "success",
        "count": len(data),
        "data": data
    }

if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect("bookstore.db")
    conn.row_factory = sqlite3.Row
    return conn

def get_categories():
    conn = get_db_connection()
    categories = conn.execute("SELECT * FROM categories").fetchall()
    conn.close()
    return categories

@app.route('/')
def home():
    return render_template("index.html", categories=get_categories())

@app.route('/category')
def category():
    category_id = request.args.get("categoryId", type=int)

    conn = get_db_connection()
    books = conn.execute(
        "SELECT * FROM books WHERE categoryId = ?", 
        (category_id,)
    ).fetchall()
    conn.close()

    return render_template(
        "category.html",
        categories=get_categories(),
        books=books,
        selectedCategory=category_id
    )

@app.route('/search', methods=['POST'])
def search():
    term = request.form.get("search", "").strip()

    conn = get_db_connection()
    books = conn.execute(
        "SELECT * FROM books WHERE LOWER(title) LIKE LOWER(?)",
        (f"%{term}%",)
    ).fetchall()
    conn.close()

    return render_template(
        "search.html",
        categories=get_categories(),
        books=books,
        term=term
    )

@app.route('/book/<int:book_id>')
def book_detail(book_id):
    conn = get_db_connection()
    book = conn.execute("""
        SELECT books.*, categories.name AS categoryName
        FROM books
        JOIN categories ON categories.id = books.categoryId
        WHERE books.id = ?
    """, (book_id,)).fetchone()
    conn.close()

    return render_template(
        "book_detail.html",
        book=book,
        categories=get_categories(),
        selectedCategory=book["categoryId"]
    )

@app.errorhandler(Exception)
def handle_error(e):
    return render_template('error.html', error=e)

if __name__ == "__main__":
    app.run(debug=True)

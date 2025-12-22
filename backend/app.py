from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import cloudinary
import cloudinary.uploader

# -------------------------------
# APP SETUP
# -------------------------------
app = Flask(__name__)
CORS(app)

# -------------------------------
# CLOUDINARY CONFIG
# -------------------------------
cloudinary.config(
    cloud_name="deozvs4nz",
    api_key="779479864166864",
    api_secret="4G4-xGyuEn7-9G6gAy9xS38CK_c"
)

# -------------------------------
# DATABASE (ABSOLUTE PATH)
# -------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

def get_db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

# -------------------------------
# CREATE TABLES
# -------------------------------
with get_db() as con:
    con.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price TEXT,
            image TEXT,
            ingredients TEXT
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS wishlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            product TEXT
        )
    """)

# -------------------------------
# SAFE DATA READER (FINAL)
# -------------------------------
def get_data():
    data = request.get_json(silent=True)
    if data is not None:
        return data
    return request.form

# -------------------------------
# REGISTER
# -------------------------------
@app.route("/register", methods=["POST"])
def register():
    data = get_data()

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify(success=False, message="All fields required")

    with get_db() as con:
        cur = con.execute(
            "SELECT id FROM users WHERE email = ?",
            (email.strip(),)
        )
        if cur.fetchone():
            return jsonify(success=False, message="Email already exists")

        con.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name.strip(), email.strip(), password.strip())
        )

    return jsonify(success=True)

# -------------------------------
# LOGIN
# -------------------------------
@app.route("/login", methods=["POST"])
def login():
    data = get_data()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify(success=False)

    # ADMIN LOGIN
    if email == "admin@gmail.com" and password == "abc212":
        return jsonify(success=True, admin=True)

    with get_db() as con:
        user = con.execute(
            "SELECT * FROM users WHERE email = ? AND password = ?",
            (email.strip(), password.strip())
        ).fetchone()

    if user:
        return jsonify(success=True, admin=False)

    return jsonify(success=False)

# -------------------------------
# ADD PRODUCT
# -------------------------------
@app.route("/add-product", methods=["POST"])
def add_product():
    name = request.form.get("name")
    price = request.form.get("price")
    ingredients = request.form.get("ingredients")
    image = request.files.get("image")

    if not image:
        return jsonify(success=False, message="No image provided")

    upload = cloudinary.uploader.upload(image)
    image_url = upload["secure_url"]

    with get_db() as con:
        con.execute(
            "INSERT INTO products (name, price, image, ingredients) VALUES (?, ?, ?, ?)",
            (name, price, image_url, ingredients)
        )

    return jsonify(success=True)

# -------------------------------
# PRODUCTS
# -------------------------------
@app.route("/products")
def products():
    with get_db() as con:
        rows = con.execute("SELECT * FROM products").fetchall()
    return jsonify([dict(r) for r in rows])

# -------------------------------
# DELETE PRODUCT
# -------------------------------
@app.route("/delete-product/<int:id>", methods=["DELETE"])
def delete_product(id):
    with get_db() as con:
        con.execute("DELETE FROM products WHERE id = ?", (id,))
    return jsonify(success=True)

# -------------------------------
# WISHLIST
# -------------------------------
@app.route("/wishlist", methods=["POST"])
def wishlist():
    data = get_data()
    with get_db() as con:
        con.execute(
            "INSERT INTO wishlist (email, product) VALUES (?, ?)",
            (data.get("email"), data.get("product"))
        )
    return jsonify(success=True)

# -------------------------------
# ADMIN DATA
# -------------------------------
@app.route("/users")
def users():
    with get_db() as con:
        rows = con.execute("SELECT id, name, email FROM users").fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/wishlist-data")
def wishlist_data():
    with get_db() as con:
        rows = con.execute("SELECT email, product FROM wishlist").fetchall()
    return jsonify([dict(r) for r in rows])

# -------------------------------
# START SERVER
# -------------------------------
if __name__ == "__main__":
    print("Using database:", DB_PATH)
    print("Backend running at http://127.0.0.1:5000")
    app.run(debug=True)

from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import cloudinary
import cloudinary.uploader
import os

app = Flask(__name__)
CORS(app)

# -------------------------------
# CLOUDINARY
# -------------------------------
cloudinary.config(
    cloud_name="deozvs4nz",
    api_key="779479864166864",
    api_secret="4G4-xGyuEn7-9G6gAy9xS38CK_c"
)

# -------------------------------
# MONGODB (PERMANENT STORAGE)
# -------------------------------
MONGO_URL = "mongodb+srv://herbaladmin:abc212@herbalskincare.qp8v4s6.mongodb.net/?appName=HERBALSKINCARE"

client = MongoClient(MONGO_URL)
db = client["herbal"]
users_col = db["users"]
products_col = db["products"]
wishlist_col = db["wishlist"]

# -------------------------------
# REGISTER
# -------------------------------
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if users_col.find_one({"email": data["email"]}):
        return jsonify(success=False, message="Email exists")

    users_col.insert_one({
        "name": data["name"],
        "email": data["email"],
        "password": data["password"]
    })
    return jsonify(success=True)

# -------------------------------
# LOGIN
# -------------------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if data["email"] == "admin@gmail.com" and data["password"] == "abc212":
        return jsonify(success=True, admin=True)

    user = users_col.find_one({
        "email": data["email"],
        "password": data["password"]
    })
    return jsonify(success=bool(user), admin=False)

# -------------------------------
# ADD PRODUCT
# -------------------------------
@app.route("/add-product", methods=["POST"])
def add_product():
    image = request.files["image"]
    upload = cloudinary.uploader.upload(image)

    products_col.insert_one({
        "name": request.form.get("name"),
        "price": request.form.get("price"),
        "ingredients": request.form.get("ingredients"),
        "image": upload["secure_url"]
    })

    return jsonify(success=True)

# -------------------------------
# GET PRODUCTS
# -------------------------------
@app.route("/products")
def products():
    data = list(products_col.find({}, {"_id": 0}))
    return jsonify(data)

# -------------------------------
# DELETE PRODUCT
# -------------------------------
@app.route("/delete-product/<name>", methods=["DELETE"])
def delete_product(name):
    products_col.delete_one({"name": name})
    return jsonify(success=True)

# -------------------------------
# WISHLIST
# -------------------------------
@app.route("/wishlist", methods=["POST"])
def wishlist():
    data = request.get_json()
    wishlist_col.insert_one(data)
    return jsonify(success=True)

# -------------------------------
# ADMIN DATA
# -------------------------------
@app.route("/users")
def users():
    data = list(users_col.find({}, {"_id": 0, "password": 0}))
    return jsonify(data)

@app.route("/wishlist-data")
def wishlist_data():
    data = list(wishlist_col.find({}, {"_id": 0}))
    return jsonify(data)

# -------------------------------
# START
# -------------------------------
if __name__ == "__main__":
    app.run()

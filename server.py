from flask import Flask, request, jsonify
from bson import ObjectId
import pymongo

app = Flask(__name__)

try:
    client = pymongo.MongoClient(
        host="localhost", port=27017, serverSelectionTimeoutMS=1000)
    db = client.company
    collection = db["users"]
    client.server_info()
except pymongo.errors.ServerSelectionTimeoutError:
    print("Error: Cannot connect to MongoDB")


def validate_user_data(data):
    required_fields = ["name", "email"]
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    return True, None


def is_email_unique(email):
    existing_user = collection.find_one({"email": email})
    return existing_user is None


@app.route('/user', methods=['POST'])
def create_user():
    try:
        if not request.json:
            return jsonify({"error": "Invalid JSON request"}), 400

        is_valid, error_message = validate_user_data(request.json)
        if not is_valid:
            return jsonify({"error": error_message}), 400

        name = request.json["name"]
        email = request.json["email"]
        age = request.json.get("age")
        department = request.json.get("department")

        if not is_email_unique(email):
            return jsonify({"error": "Email already exists"}), 409

        collection.insert_one({"name": name, "email": email,
                               "age": age, "department": department})
        return jsonify({"message": "User created successfully"}), 201
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500


@app.route('/users', methods=['GET'])
def get_users():
    try:
        cursor = collection.find({})
        users_list = []
        for document in cursor:
            document['_id'] = str(document['_id'])
            users_list.append(document)

        return jsonify({"users": users_list}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500


if __name__ == "__main__":
    app.run(port=3000, debug=True)

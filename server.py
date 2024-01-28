from flask import Flask, request, jsonify
import pymongo

app = Flask(__name__)

try:
    client = pymongo.MongoClient(
        host="localhost", port=27017, serverSelectionTimeoutMS=1000)
    db = client.company
    client.server_info()
except:
    print("Error: Cannot connect to MongoDB")


def validate_user_data(data):
    required_fields = ["name", "email"]
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    return True, None


def is_email_unique(email):
    existing_user = db.users.find_one({"email": email})
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
        age = request.json.get("age")  # Using get() to handle optional field
        department = request.json.get("department")

        if not is_email_unique(email):
            return jsonify({"error": "Email already exists"}), 409

        db.users.insert_one({"name": name, "email": email,
                            "age": age, "department": department})
        return jsonify({"message": "User created successfully"}), 201
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500


if __name__ == "__main__":
    app.run(port=3000, debug=True)

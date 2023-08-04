from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import uuid

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(80), unique = True, nullable = True)
    email = db.Column(db.String(120), unique = True, nullable = True)
    password = db.Column(db.String(100), nullable = True)
    full_name = db.Column(db.String(100), nullable = True)
    age = db.Column(db.Integer)
    gender = db.Column(db.String)



class KeyValueData(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    key = db.Column(db.String(100), nullable = False)
    value = db.Column(db.String(1000), nullable = False)


@app.route('/')
def Home():
    return "Hello Saurabh, This one is your Assignment"

    
@app.route('/api/register', methods=['POST'])
def register_user():
    user_data = request.get_json()

    # Checking the required fields are provided
    required_fields = ["username", "email", "password", "full_name"]
    for field in required_fields:
        if field not in user_data:
            return jsonify({
                "status": "error",
                "code": "INVALID_REQUEST",
                "message": "Invalid request. Please provide all required fields: username, email, password, full_name."
            }), 400

    # Check if the username or email is already taken
    existing_user = User.query.filter_by(username=user_data["username"]).first()
    if existing_user:
        return jsonify({
            "status": "error",
            "code": "USERNAME_EXISTS",
            "message": "The provided username is already taken. Please choose a different username."
        }), 409

    existing_email = User.query.filter_by(email=user_data["email"]).first()
    if existing_email:
        return jsonify({
            "status": "error",
            "code": "EMAIL_EXISTS",
            "message": "The provided email is already registered. Please use a different email address."
        }), 409

    # Check if the password meets the requirements
    password = user_data["password"]
    if len(password) < 8 or not any(c.isupper() for c in password) or not any(c.islower() for c in password) or not any(c.isdigit() for c in password) or not any(c in '!@#$%^&*()_-+={}[]|:;<>,.?/~`' for c in password):
        return jsonify({
            "status": "error",
            "code": "INVALID_PASSWORD",
            "message": "The provided password does not meet the requirements. Password must be at least 8 characters long and contain a mix of uppercase and lowercase letters, numbers, and special characters."
        }), 400

    # Check if age is a positive integer
    age = user_data.get("age")
    if age is not None and (not isinstance(age, int) or age <= 0):
        return jsonify({
            "status": "error",
            "code": "INVALID_AGE",
            "message": "Invalid age value. Age must be a positive integer."
        }), 400

    # Check if gender is provided
    gender = user_data.get("gender")
    if not gender:
        return jsonify({
            "status": "error",
            "code": "GENDER_REQUIRED",
            "message": "Gender field is required. Please specify the gender (e.g., male, female, non-binary)."
        }), 400

    # Your user registration logic and database insertion code will go here
    new_user = User(
        username = user_data["username"],
        email = user_data["email"],
        password = user_data["password"],
        full_name = user_data["full_name"],
        age = user_data.get("age"),
        gender = user_data.get("gender")
    )

    try:
        db.session.add(new_user)
        db.session.commit()

        response_data = {
        "user_id" : new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "full_name": new_user.full_name,
        "age": new_user.age,
        "gender": new_user.gender
        }
    
        return jsonify({
            "status": "success",
            "message": "User Successfully registered",
            "data": response_data
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({  
            "message": "error",
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An internal server error occured while registering the use. Please try again later"
        }), 500
    

@app.route('/api/token', methods=['POST'])
def generate_token():
    user_data = request.get_json()

    required_fields = ["username", "password"]
    for field in required_fields:
        if field not in user_data:
            return jsonify({
                "status": "error",
                "code": "MISSING_FIELDS",
                "message": "Missing fields. Please provide both username and password."
            }), 400
    
    username = user_data["username"]
    password = user_data["password"]

    user = User.query.filter_by(username=username).first()
    if user is None or user.password != password:
        return jsonify({
            "status": "error",
            "code": "INVALID_CREDENTIALS",
            "message": "Invalid credentials. The provided username or password is incorrect."
        }), 401

    access_token = str(uuid.uuid4())
    expires_in = 3600

    try:
        # Code to generate and return the access token
        return jsonify({
            "status": "success",
            "message": "Access token generated successfully.",
            "data": {
                "access_token": access_token,
                "expires_in": expires_in
            }
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "code": "INTERNAL_ERROR",
            "message": "Internal server error occurred. Please try again later."
        }), 500



def authorize(f):
    @wraps(f)
    def decorated_function(*args, **Kwargs):
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer'):
            access_token = auth_header.split(' ')[1]
            # logic of checking access token from database or temporary work depends on the requirement
            def is_valid_access_token(access_token):
                pass
                # Return True if correct and False if not

            if is_valid_access_token(access_token):
                return f(*args, **Kwargs)
            
        return jsonify({
            "status": "error",
            "code": "INVALID_TOKEN",
            "message": "Invalid access token provided"
        }), 401
    
    return decorated_function

@app.route('/api/data', methods = ['POST'])
# @authorize      --- This is code suppose to be here, as we have no logic for validation of code we keep is commented
def store_data():

    data = request.get_json()

    if 'key' not in data:
        return jsonify({
            "status": "error",
            "code": "INVALID_KEY",
            "message": "Invalid request. Please Provide the key"
        }), 400
    
    if 'value' not in data:
        return jsonify({
            "status": "error",
            "code": "INVALID_VALUE",
            "message": "Invalid request. Please Provide the value"
        }), 400
    
    if KeyValueData.query.filter_by(key = data['key']).first():
        return jsonify({
            "status": "error",
            "code": "KEY_EXISTS",
            "message": "The provided data already exists in the database"
        }), 400
    
    new_data = KeyValueData(key = data['key'], value = data['value'])
    db.session.add(new_data)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Data stored successfully"
    }), 200

@app.route('/api/data/<string:key>', methods = ['GET'])
# @authorize
def retrieve_data(key):
    data = KeyValueData.query.filter_by(key=key).first()
    if data is None:
        return jsonify({
            "status": "error",
            "code": "KEY_NOT_FOUND",
            "message": "The provided key does not exist in the database"
        }), 404

    return jsonify({
        "status": "success",
        "data":{
            "key": data.key,
            "value": data.value
        } 
    }), 200

@app.route('/api/data/<string:key>', methods=['PUT'])
# @authorize
def update_data(key):
    data = KeyValueData.query.filter_by().first()
    if data is None:
        return jsonify({
            "status": "error",
            "code": "KEY_NOT_FOUND",
            "message": "The provided key does not exist in the database"
        }), 404
    
    update_json = request.get_json()
    new_value = update_json.get("value")

    if new_value is None:
        return jsonify({
            "status": "error",
            "code": "INVALID_VALUE",
            "message": "The provided VALUE properly"
        }), 400
    
    data.value = new_value
    db.session.commit()

    return jsonify({
        "status" : "success",
        "message" : "Data updated successfully"
    }), 200

@app.route('/api/data/<string:key>', methods=['DELETE'])
# @authorize
def delete_data(key):
    data = KeyValueData.query.filter_by(key=key).first()

    if data is None:
        return jsonify({
            "status": "error",
            "code": "KEY_NOT_FOUND",
            "message": "The provided key does not exist in the database."
        }), 404

    db.session.delete(data)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Data deleted successfully."
    }), 200



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

import validators
from flasgger import swag_from
from src.database import User, db
from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash 
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity
from src.constants.http_status_code import (
    HTTP_200_OK, 
    HTTP_201_CREATED, 
    HTTP_400_BAD_REQUEST, 
    HTTP_401_UNAUTHORIZED, 
    HTTP_409_CONFLICT, 
    HTTP_404_NOT_FOUND
)

auth = Blueprint("auth", __name__, url_prefix="/api/v1/auth")

@auth.route("/register",methods=['POST'])  
@swag_from("/home/hardikve/Desktop/LINK_SAVER_WEB_APP/src/docs/auth/register.yaml")
def register():
    user_name = request.json['user_name']
    email = request.json['email']
    password = request.json['password']

    if len(password)<6:
        return jsonify({"Error":"Password is too short."}), HTTP_400_BAD_REQUEST

    if len(user_name)<3:
        return jsonify({"Error":"Username is too short."}), HTTP_400_BAD_REQUEST
    
    if not user_name.isalnum() or " " in user_name:
        return jsonify({"Error":"Username should be alphanumeric, and no spaces."}), HTTP_400_BAD_REQUEST
    
    if not validators.email(email):
        return jsonify({"error": "Email is not valid"}), HTTP_400_BAD_REQUEST

    if User.query.filter_by(email=email).first() is not None:
        return jsonify({"error": "Email already exists"}), HTTP_409_CONFLICT

    if User.query.filter_by(user_name=user_name).first() is not None:
        return jsonify({"error": "UserName already exists"}), HTTP_409_CONFLICT

    # hashing password
    pwd_hash = generate_password_hash(password)
    
    user = User(user_name=user_name, password=pwd_hash, email=email)

    db.session.add(user)
    db.session.commit()

    return jsonify({"message":"user created", "user": {"user_name":user_name, "email":email}}), HTTP_201_CREATED

@auth.route("/login", methods=['POST'])
@swag_from("/home/hardikve/Desktop/LINK_SAVER_WEB_APP/src/docs/auth/login.yaml")
def login():
    email = request.json.get('email', '')
    password = request.json.get('password', '')

    user = User.query.filter_by(email=email).first()

    if user:
        # Convert password to hash and compare it if its valid
        is_pass_correct = check_password_hash(user.password, password)

        if is_pass_correct:
            # The create_refresh_token function is a method in the Flask-JWT-Extended package that 
            # generates a new refresh token for a user after they have successfully authenticated.
            refresh = create_refresh_token(identity=user.id)
            access = create_access_token(identity=user.id)

            return jsonify({
                "user": {
                    "refresh":refresh,
                    "access":access,
                    "user_name":user.user_name,
                    "email":user.email
                }
            }), HTTP_200_OK

    return jsonify({"error":"Wrong credentials"}), HTTP_401_UNAUTHORIZED


@auth.route("/me",methods=['GET'])
@jwt_required() # authentication required token
def me():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    return jsonify({"user_name": user.user_name, "email": user.email}), HTTP_200_OK

@auth.route("/token/refresh", methods=['GET'])
@jwt_required(refresh=True) # are expecting it to give a refresh token
def refresh_user_token():
    identity = get_jwt_identity()
    access = create_access_token(identity=identity)

    return jsonify({'access':access}), HTTP_200_OK
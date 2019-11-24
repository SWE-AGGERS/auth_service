from flask import Blueprint, request, jsonify
from auth_service.database import db, User
import jwt
import datetime as dt

auth = Blueprint('auth', __name__)

PASS_KEY = 'JWT-SECRET-PASS'

@auth.route('/login', methods=['POST'])
def login():
    json = request.get_json()
    email = json['email']
    password = json['password']
    response = False
    user_id = -1
    if email and password:
        query = db.session.query(User).filter(User.email == email)
        user = query.first()

        if user is not None and user.authenticate(password):
            response = True
            user_id = user.get_id()
        else:
            response = False

    return jsonify({"response": response,
                    "user_id": user_id,
                    "auth_token": encode_auth_token(user_id).decode()
                    })


@auth.route("/signup", methods=['POST'])
def signup():
    json = request.get_json()
    email = json['email']
    check_query = db.session.query(User).filter(User.email == email)
    result = check_query.first()

    error_message = ""
    user_id = -1
    error = False
    auth_token = ""
    if result is None:
        user = User()
        user.firstname = json['firstname']
        user.lastname = json['lastname']
        user.email = json['email']
        user.dateofbirth = dt.datetime(json['dateofbirth']["year"],json['dateofbirth']["month"],json['dateofbirth']["day"])
        print(json['password'])
        user.set_password(password=json['password'])
        db.session.add(user)
        db.session.commit()

        user_query = db.session.query(User).filter(User.email == email)
        existing_user = user_query.first()
        user_id = existing_user.get_id()
        auth_token = encode_auth_token(user_id).decode()
    else:
        error = True
        error_message = "User is already exist"

    return jsonify({'user_id': user_id, 'error': error, 'error_message': error_message, "auth_token":auth_token })


@auth.route("/delete/<user_id>", methods=['DELETE'])
def delete(user_id):
    query = db.session.query(User).filter(User.id == user_id)
    user = query.first()
    response = False
    if user:
        db.session.query(User).filter(User.id == user_id).delete()
        db.session.commit()
        response = True
    else:
        response = False

    return jsonify({"response": response})


@auth.route("/users", methods=["GET"])
def users():
        data = []
        users = db.session.query(User).all()
        for user in users:
            usern = {
                 "user_id" : user.id,
                 "firstname": user.firstname,
                 "lastname": user.lastname,
                 "email": user.email,
                 "dateofbirth": user.dateofbirth}

            data.append(usern)

        return jsonify(data)


@auth.route("/user/<user_id>", methods=["GET"])
def user(user_id):
    query = db.session.query(User).filter(User.id == user_id)
    user = query.first()
    return jsonify({"firstname": user.firstname, "lastname": user.lastname, "email":user.email, "dateofbirth": user.dateofbirth})


def encode_auth_token(user_id):
    """
    Generates the Auth Token
    :return: string
    """
    try:
        payload = {
            'exp': dt.datetime.utcnow() + dt.timedelta(hours=1),
            'iat': dt.datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(
            payload,
            PASS_KEY,
            algorithm='HS256'
        )
    except Exception as e:
        return e
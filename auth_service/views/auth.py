from flask import Blueprint, request, jsonify
from sqlalchemy import func

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

    return jsonify({
             "response": response,
             "user_id": user_id,
             "firstname": user.firstname,
             "lastname": user.lastname,
             "email": user.email,
             "dateofbirth": user.dateofbirth,
             "auth_token": encode_auth_token(user_id).decode(),
             "is_admin": user.is_admin,
             "is_active": user.is_active,
             "is_authenticated": user.authenticated
             })


@auth.route("/user_exist/<user_id>",methods=['GET'])
def check_user(user_id):
    query = db.session.query(User).filter(User.id == user_id)
    user = query.first()
    response = False
    if user :
        response = True

    return jsonify({"registered": response})


@auth.route("/signup", methods=['POST'])
def signup():
    json = request.get_json()
    email = json['email']
    check_query = db.session.query(User).filter(User.email == email)
    result = check_query.first()

    if result is None:
        user = User()
        user.firstname = json['firstname']
        user.lastname = json['lastname']
        user.email = json['email']
        user.dateofbirth = dt.datetime(int(json['dateofbirth']["day"]), int(json['dateofbirth']["month"]), int(json['dateofbirth']["year"]))
        user.set_password(password=json['password'])
        db.session.add(user)
        db.session.commit()

        user_query = db.session.query(User).filter(User.email == email)
        existing_user = user_query.first()
        user_id = existing_user.get_id()
        auth_token = encode_auth_token(user_id).decode()
        return jsonify({
            "error": False,
            "firstname": user.firstname,
            "lastname": user.lastname,
            "email": user.email,
            "dateofbirth": user.dateofbirth,
            "auth_token":auth_token,
            "is_admin": user.is_admin,
            "is_active": user.is_active,
            "is_authenticated": user.authenticated,
            "user_id": user.id
        })
    else:
        error = True
        error_message = "User is already exist"
        return jsonify({'error': error,
                        'error_message': error_message})


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

    return jsonify({"response":True,
                    "firstname": user.firstname,
                    "lastname": user.lastname,
                    "email":user.email,
                    "dateofbirth": user.dateofbirth,
                    "auth_token": encode_auth_token(user_id).decode(),
                    "is_admin": user.is_admin,
                    "is_active": user.is_active,
                    "is_authenticated": user.authenticated,
                    "user_id": user.id
                    })


@auth.route("/search/<keywords>", methods=["GET"])
def search(keywords):
    parameters = keywords.split()
    users = []

    if len(parameters) == 2:
        r1 = User.query.filter(func.lower(User.firstname) == func.lower(parameters[0]))
        for user in r1:
            user_json = result_json(user_id=user.id, firstname=user.firstname, lastname=user.lastname)
            users.append(user_json)
        r2 = User.query.filter(func.lower(User.lastname) == func.lower(parameters[1]))
        for user in r2:
            user_json = result_json(user_id=user.id, firstname=user.firstname, lastname=user.lastname)
            users.append(user_json)

    elif len(parameters) == 1:
        r1 = User.query.filter(func.lower(User.firstname) == func.lower(parameters[0]))
        for user in r1:
            user_json = result_json(user_id=user.id, firstname=user.firstname, lastname=user.lastname)
            users.append(user_json)
        r2 = User.query.filter(func.lower(User.lastname) == func.lower(parameters[0]))
        for user in r2:
            user_json = result_json(user_id=user.id, firstname=user.firstname, lastname=user.lastname)
            users.append(user_json)

    return jsonify(users) if len(users) > 0 else None


def result_json(user_id, firstname, lastname):
    return {"user_id": user_id, "firstname": firstname, "lastname": lastname}



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
from flask import Blueprint, render_template, redirect, request, jsonify
from flask_login import (current_user, login_user, logout_user, login_required)

from auth_service.database import db, User
from auth_service.forms import LoginForm
from auth_service.forms import UserForm
import datetime

auth = Blueprint('auth', __name__)


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
    return jsonify({"response": response, "user_id": user_id})


@auth.route("/logout")
def logout():
    logout_user()
    return redirect('/')


@auth.route("/signup", methods=['POST'])
def signup():
    json = request.get_json()
    print(json)
    email = json['email']
    check_query = db.session.query(User).filter(User.email == email)
    user = check_query.first()

    error_message = ""
    user_id = -1
    error = False

    if user is None:
        user = User()
        user.firstname = json['firstname']
        user.lastname = json['lastname']
        user.email = json['email']
        user.dateofbirth = datetime.datetime(json['dateofbirth']["year"],json['dateofbirth']["month"],json['dateofbirth']["day"])
        print(json['password'])
        user.set_password(password=json['password'])
        db.session.add(user)
        db.session.commit()

        user_query = db.session.query(User).filter(User.email == email)
        existing_user = user_query.first()
        user_id = existing_user.get_id()

    else:
        error = True
        error_message = "User is already exist"

    return jsonify({'user_id': user_id, 'error': error, 'error_message': error_message })

@auth.route("/delete", methods=['DELETE'])
def delete():
    json = request.get_json()
    user_id = json['user_id']
    db.session.query(User).filter(User.id == user_id).delete()
    db.session.commit()
    return jsonify({"response": True})

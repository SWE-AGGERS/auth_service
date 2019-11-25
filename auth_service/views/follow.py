from flask import Blueprint, request, jsonify
from auth_service.database import db, Followers, User
from sqlalchemy import and_

follow = Blueprint('follow', __name__)

# Follow a writer
@follow.route('/follow/<int:follower_id>/<int:followed_id>', methods=['POST'])
def follow_user(follower_id,followed_id):
    # get the user who want following userid
    subject = follower_id

    # if try to follow himeself
    if int(followed_id) == int(subject):
        return jsonify({"followed": -2, "message": "You can't self-follow"})

    # if already followed
    if is_follower(subject, followed_id):
        return jsonify({"followed": -1, "message": "You already follow this user"})

    # if the followed user do not exist
    if User.query.filter_by(id=followed_id).first() == None:
        return jsonify({"followed": -3, "message": "The user does not exist"})

    # add to follower_table the tuple (follower_id, followed_id)
    result = add_follow(subject, followed_id)
    if result == -1:
        # db.session.add error
        return jsonify({"followed": -4, "message": "DB error during add_follow"})

    # return OK + number of users followed
    return jsonify({"followed": get_followed_number(subject), "message": "OK"})


# Unfollow a writer
@follow.route('/follow/<int:follower_id>/<int:followed_id>', methods=['DELETE'])
def unfollow_user(follower_id,followed_id):
    # get the user who want to unfollow userid
    subject = follower_id

    if followed_id == subject:
        return {"followed": -2, "message": "You can't self-unfollow"}

    # if the followed user do not exist
    if User.query.filter_by(id=followed_id).first() == None:
        return {"followed": -3, "message": "The user does not exist"}

    # if user not followed
    if not is_follower(subject, followed_id):
        return {"followed": -1, "message": "You do not already follow this user"}

    # remove from follower_table the tuple (follower_id, followed_id)
    if delete_follow(subject, followed_id) == -1:
        # db delete error
        return {"followed": -4, "message": "DB error during add_follow"}

    # return OK
    return {"followed": get_followed_number(subject), "message": "OK"}


@follow.route('/unfollow//<int:follower_id>/<int:followed_id>', methods=['POST'])
def unfollow_user_post(follower_id,followed_id):
    # Unfollow user API as POST to be compatible with forms
    return unfollow_user(follower_id,followed_id)


@follow.route('/is_follower/<user_a>/<user_b>', methods=['GET'])
def get_is_follower(user_a, user_b):
    """check if user_a follow user_b"""
    return jsonify({'follow': is_follower(user_a, user_b)})


@follow.route('/followed/list/<int:subject>', methods=['GET'])
def followed_list(subject):
    followed = db.session.query(Followers, User).filter(
        Followers.followed_id == User.id).filter_by(follower_id=subject).all()
    result = []
    for f in followed:
        result.append(f[0].follower_id)
    return jsonify({"followed": result})



# =============================================================================
# UTILITY FUNC
# =============================================================================
# Get the list of followers of the user_id
#check if user_a follow user_b
def is_follower(user_a, user_b):
    item = Followers.query.filter_by(
        follower_id=user_a, followed_id=user_b).first()
    if item is None:
        return False
    else:
        return True

def create_follow(user_a, user_b):
    item = Followers()
    item.follower_id = int(user_a)
    item.followed_id = int(user_b)
    return item


# TODO: use celerity
def add_follow(user_a, user_b):
    try:
        db.session.add(create_follow(user_a, user_b))
        db.session.commit()
        return 1
    except:
        db.session.rollback()
        return -1


# TODO: use celerity
def delete_follow(user_a, user_b):
    try:
        item = Followers.query.filter_by(
            follower_id=user_a, followed_id=user_b).first()
        db.session.delete(item)
        db.session.commit()
        return 1
    except:
        db.session.rollback()
        return -1

# Get the number of followed
def get_followed_number(user_id):
    return len(get_followers_of(user_id))


def get_followers_of(user_id):
    L = Followers.query.filter_by(follower_id=user_id).all()
    return L

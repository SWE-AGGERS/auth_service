import unittest
import json
from flask import request, jsonify
from auth_service.app import create_app
from auth_service.database import db, User, Followers
from auth_service.views.follow import create_follow, is_follower
from auth_service.tests.restart_db import restart_db_tables


_app = None
 
class TestFollow(unittest.TestCase):

    def test_follow_user(self):
        global _app
        if _app is None:
            tested_app = create_app(debug=True)
            _app = tested_app
        else:
            tested_app = _app
        restart_db_tables(db, tested_app)

        with tested_app.test_client() as client:
            with client.session_transaction() as session:
                user_a_id, user_b_id, user_c_id, aemail = create_test_users(session)
            
            # login as user_1
            login(client, aemail, 'test')

            # call /follow/a/b
            # return {"followed": 1, "message": "OK"}
            reply = client.post('/follow/'+str(user_a_id)+'/'+str(user_b_id))
            data = b'{\"followed": 1, "message": "OK"}'
            self.assertIn(data, str(reply.data))

            # call /follow/a/b another time
            # return {"followed": -1, "message": "You already follow this user"}
            reply = client.post('/follow/'+str(user_a_id)+'/'+str(user_b_id))
            data = b'{"followed": -1, "message": "You already follow this user"}'
            self.assertIn(data, str(reply.data))


            # call /follow/a/c
            # return {"followed": 1, "message": "OK"}
            reply = client.post('/follow/'+str(user_a_id)+'/'+str(user_c_id))
            data = b'{\"followed": 2, "message": "OK"}'
            self.assertIn(data, str(reply.data))

            # call /follow/a/b another time
            # return {"followed": -1, "message": "You already follow this user"}
            reply = client.post('/follow/'+str(user_a_id)+'/'+str(user_b_id))
            data = b'{"followed": -1, "message": "You already follow this user"}'
            self.assertIn(data, str(reply.data))

            # call /follow/a/a (himslef)
            # return {"followed": -2, "message": "You can't self-follow"}
            reply = client.post('/follow/'+str(user_a_id)+'/'+str(user_a_id))
            data = b'{"followed": -2, "message": "You can\'t self-follow"}'
            self.assertIn(data, str(reply.data))
            
            # call /follow/a/not_exist_id
            # return {"followed": -3, "message": "The user does not exist"}
            user_not_exist_id = 99999999999
            reply = client.post('/follow/'+str(user_a_id)+'/'+str(user_not_exist_id))
            data = b'{"followed": -3, "message": "The user does not exist"}'
            self.assertIn(data, str(reply.data))

            logout(client)        

    def test_followers_list(self):
        global _app
        if _app is None:
            tested_app = create_app(debug=True)
            _app = tested_app
        else:
            tested_app = _app
            restart_db_tables(db, tested_app)

            with tested_app.test_client() as client:
                with client.session_transaction() as session:
                   user_a_id, user_b_id, user_c_id, aemail = create_test_users(session)

                
                # login as user_1
                login(client, aemail, 'test')

                # call /followed/list/a
                # return {"followed": []}
                reply = client.get('/followed/list/'+str(user_a_id))
                data = 0
                res = len(json.dump(reply.data).followed)
                self.assertEqual(data, res)

                # Create followers
                with client.session_transaction() as session:
                    create_test_follow(session, user_a_id, user_b_id, user_c_id)

                # call /followed/list/a
                # return {"followed": [<b>, <c>]}
                reply = client.get('/followed/list/'+str(user_a_id))
                data = 2
                res = len(json.dump(reply.data).followed)
                self.assertEqual(data, res)                    

                client.delete('/follow/'+str(user_a_id)+'/'+str(user_b_id))

                # call /followed/list/a
                # return {"followed": [<c>]}
                reply = client.get('/followed/list/'+str(user_a_id))
                data = 1
                res = len(json.dump(reply.data).followed)
                self.assertEqual(data, res)   
                    

    def test_unfollow_user(self):

        global _app
        if _app is None:
            tested_app = create_app(debug=True)
            _app = tested_app
        else:
            tested_app = _app
        restart_db_tables(db, tested_app)

        with tested_app.test_client() as client:
            with client.session_transaction() as session:
                user_a_id, user_b_id, user_c_id, aemail = create_test_users(session)
            with client.session_transaction() as session:
                create_test_follow(session, user_a_id, user_b_id, user_c_id)
            
            # login as user_1
            login(client, aemail, 'test')

            # call /follow/a/a
            # return {"followed": -2, "message": "You can't self-unfollow"}
            reply = client.delete('/follow/'+str(user_a_id)+'/'+str(user_a_id))
            data = b'{"followed": -2, "message": "You can\'t self-unfollow"}'
            self.assertIn(data, str(reply.data))

            # call /follow/a/b
            # return {"followed": 1, "message": "OK"}
            reply = client.delete('/follow/'+str(user_a_id)+'/'+str(user_b_id))
            data = b'{"followed": 1, "message": "OK"}'
            self.assertIn(data, str(reply.data))

            # call /follow/a/b another time
            # return {"followed": -1, "message": "You do not already follow this user"}
            reply = client.delete('/follow/'+str(user_a_id)+'/'+str(user_b_id))
            data = b'{"followed": -1, "message": "You do not already follow this user"}'
            self.assertIn(data, str(reply.data))

            # call /follow/a/not_exist_id
            # return {"followed": -3, "message": "The user does not exist"}
            user_not_exist_id = 999999999999
            reply = client.delete('/follow/'+str(user_a_id)+'/'+str(user_not_exist_id))
            data = b'{"followed": -3, "message": "The user does not exist"}'
            self.assertIn(data, str(reply.data))

def login(client, username, password):
    return client.post('/login',
                       json=
                         {
                             "email": username,
                             "password": password
                         }
                       ,
                       follow_redirects=True)


def logout(client):
    return client.get('/logout', follow_redirects=True)


def create_test_users(session):
    user_a = User()
    user_a.firstname = "Pippo"
    user_a.lastname = "Pippo"
    user_a.email = 'testa@test.com'
    user_a.set_password('test')

    user_b = User()
    user_b.firstname = "Pluto"
    user_b.lastname = "Mouse"
    user_b.email = 'testb@test.com'
    user_b.set_password('test')

    user_c = User()
    user_c.firstname = "Paperino"
    user_c.lastname = "Duck"
    user_c.email = 'testc@test.com'
    user_c.set_password('test')

    db.session.add(user_a)
    db.session.add(user_b)
    db.session.add(user_c)
    db.session.commit()


    # Get users ID
    user_a_id = User.query.filter_by(email=user_a.email).first().get_id()
    user_b_id = User.query.filter_by(email=user_b.email).first().get_id()
    user_c_id = User.query.filter_by(email=user_c.email).first().get_id()

    return user_a_id, user_b_id, user_c_id, user_a.email


def create_test_follow(session, user_a_id, user_b_id, user_c_id):
    follow_ab = create_follow(user_a_id, user_b_id)
    follow_ac = create_follow(user_a_id, user_c_id)
    follow_bc = create_follow(user_b_id, user_c_id)

    db.session.add(follow_ab)
    db.session.add(follow_ac)
    db.session.add(follow_bc)
    db.session.commit()

if __name__ == '__main__':
    unittest.main()
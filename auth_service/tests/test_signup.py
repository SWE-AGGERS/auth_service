import unittest
from auth_service import app


class SignupTestCase(unittest.TestCase):

    def testSuccessfulSignup(self):
        tester = self.getTester()
        user = {
            "firstname": "selman",
            "lastname": "alpdündar",
            "email": "selman.alp@hotmail.com.tr",
            "dateofbirth": {
                "year": 1994,
                "month": 9,
                "day": 10
            },
            "password": "admin"
        }
        response = signup(client=tester, data=user)
        assert b'"error":false,"error_message":"","user_id":2' in response.data

    def testUnsuccessfulSignup(self):
        tester = self.getTester()
        user = {
            "firstname": "Admin",
            "lastname": "Admin",
            "email": "example@example.com",
            "dateofbirth": {
                "year": 2020,
                "month": 10,
                "day": 5
            },
            "password": "admin"
        }
        response = signup(client=tester, data=user)
        assert b'"error":true,"error_message":"User is already exist","user_id":-1' in response.data

    def getTester(self):
        application = app.create_app()
        tester = application.test_client(self)
        return tester


def signup(client, data):
    return client.post('/signup',
                       json=data,
                       follow_redirects=True)

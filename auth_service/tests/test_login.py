import unittest
from auth_service import app


class LoginTestCase(unittest.TestCase):

    def testUnsuccessfulLogin(self):
        tester = self.getTester
        reply = login(tester, "selman@hotmail", "12345")

        assert b'"response":false,"user_id":-1' in reply.data

    def testSuccessfulLogin(self):
        tester = self.getTester
        reply = login(tester, "example@example.com", "admin")
        assert b'"response":true,"user_id":1' in reply.data


    @property
    def getTester(self):
        application = app.create_app()
        tester = application.test_client(self)
        return tester


def login(client, username, password):
    return client.post('/login',
                       json=
                         {
                             "email": username,
                             "password": password
                         }
                       ,
                       follow_redirects=True)


import unittest
from auth_service import app
from flask import jsonify


class GetUserByIdTestCase(unittest.TestCase):

    def testGetUser(self):
        tester = self.getTester

        reply = get(tester, user_id=1)

        assert b'{"dateofbirth":"Mon, 05 Oct 2020 00:00:00 GMT","email":"example@example.com","firstname":"Admin","lastname":"Admin"}' in reply.data

    @property
    def getTester(self):
        application = app.create_app()
        tester = application.test_client(self)
        return tester


def get(client, user_id):
    return client.get('/user/{}'.format(user_id),
                      follow_redirects=True)

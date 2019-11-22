import unittest
from auth_service import app
from flask import jsonify


class GetUsersTestCase(unittest.TestCase):

    def testGetUser(self):
        tester = self.getTester

        reply = get(tester)

        assert  b'{"dateofbirth":"Mon, 05 Oct 2020 00:00:00 GMT","email":"example@example.com","firstname":"Admin","lastname":"Admin","user_id":1}' in reply.data

    @property
    def getTester(self):
        application = app.create_app()
        tester = application.test_client(self)
        return tester


def get(client  ):
    return client.get('/users',
                      follow_redirects=True)

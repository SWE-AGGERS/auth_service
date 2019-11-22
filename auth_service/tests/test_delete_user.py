import unittest
from auth_service import app
from flask import jsonify


class DeleteUserTestCase(unittest.TestCase):

    def testSuccessfullyDelete(self):
        tester = self.getTester

        reply = delete(tester, user_id = 1)

        assert b'{"response":true}' in reply.data

    def testUnsuccessfullyDelete(self):
        tester = self.getTester
        reply = delete(tester, user_id=1)
        assert b'{"response":false}' in reply.data

    @property
    def getTester(self):
        application = app.create_app()
        tester = application.test_client(self)
        return tester


def delete(client, user_id):
    return client.delete('/delete/{}'.format(user_id),
                         follow_redirects=True)

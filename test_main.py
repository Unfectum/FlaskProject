from unittest import TestCase

from main import db
from main import app


class MyTest(TestCase):

    SQLALCHEMY_DATABASE_URI = "sqlite://"
    TESTING = True

    def create_app(self):

        # pass in test configuration
        return app

    def setUp(self):

        db.create_all()

    def tearDown(self):

        db.session.remove()
        db.drop_all()


class TestRequestApi(TestCase):
    def test_get(self):


    def test_put(self):


from unittest import TestCase

from flask_sqlalchemy import SQLAlchemy
from flask_testing import TestCase
import unittest
from sqlalchemy import create_engine
from models.model import db, hash_password, Course
from main import app
from models.model import User
import psycopg2
from sqlalchemy.util import b64encode


class MyTest(TestCase):
    TESTING = True
    WTF_CSRF_ENABLED = True
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:1234@localhost:5432/Test_db"

    def create_app(self):
        return app

    def setUp(self):
        db.create_all()
        db.session.commit()
        student = User(id=11, username="student", password=hash_password("password"), firstname="firstname",
                       lastname="lastname",
                       role="student")

        db.session.add(student)
        teacher = User(id=12, username="teacher", password=hash_password("password"), firstname="firstname",
                       lastname="lastname",
                       role="teacher")
        course = Course(id=11, title="title", filling="filling", creator_id=teacher.id)
        course2 = Course(id=12, title="title1", filling="filling1", creator_id=teacher.id)
        db.session.add(teacher)
        db.session.add(course)
        db.session.add(course2)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class TestApi(MyTest):
    def test_user_post(self):
        test = self.client.post("/user", data={"username": "username555", "password": "password", "firstname": "lastname","lastname": "firstname", "role": "student"})
        print(test.data)
        self.assertEqual(201, test.status_code)

    def test_user_put(self):
        user = User(id=4, username="username", password=hash_password("password"), firstname="firstname", lastname="lastname", role="student")
        db.session.add(user)
        db.session.commit()
        credentials = b64encode(b"username:password")
        test = self.client.put("/user", headers={"Authorization": f"Basic {credentials}"}, data={"firstname": "testf", "lastname": "testl", "username": "testu", "password": "testp"})
        print(test.data)
        self.assertEqual(200, test.status_code)

    def test_user_delete(self):
        user = User(id=3, username="delete", password=hash_password("password"), firstname="firstname", lastname="lastname", role="student")
        db.session.add(user)
        db.session.commit()
        credentials = b64encode(b"delete:password")
        test = self.client.delete("/user", headers={"Authorization": f"Basic {credentials}"})
        self.assertEqual(204, test.status_code)

    def test_user_get(self):
        credentials = b64encode(b"student:password")
        test = self.client.get("/user", headers={"Authorization": f"Basic {credentials}"})
        self.assertEqual(200, test.status_code)

    def test_teacher_course_get_fail(self):
        user = User(id=4, username="fail", password=hash_password("password"), firstname="firstname", lastname="lastname", role="teacher")
        db.session.add(user)
        db.session.commit()
        credentials = b64encode(b"fail:password")
        test = self.client.get("/course", headers={"Authorization": f"Basic {credentials}"})
        self.assertEqual(404, test.status_code)

    def test_teacher_course_get(self):
        credentials = b64encode(b"teacher:password")
        test = self.client.get("/course", headers={"Authorization": f"Basic {credentials}"})
        print(test.data)
        self.assertEqual(200, test.status_code)

    def test_student_course_get_fail(self):
        credentials = b64encode(b"student:password")
        test = self.client.get("/course", headers={"Authorization": f"Basic {credentials}"})
        self.assertEqual(404, test.status_code)

    def test_post(self):

        credentials = b64encode(b"teacher:password")
        test = self.client.post("/course", headers={"Authorization": f"Basic {credentials}"}, data={"title": "title", "filling": "filling"})
        print(test.data)
        self.assertEqual(201, test.status_code)

    def test_delete(self):
        course = Course(id=5, title="title", filling="filling", creator_id=12)

        db.session.add(course)
        db.session.commit()
        credentials = b64encode(b"teacher:password")
        test = self.client.delete("/course", headers={"Authorization": f"Basic {credentials}"}, data={"id": 5})
        self.assertEqual(204, test.status_code)

    def test_put(self):
        course = Course(id=5, title="title", filling="filling", creator_id=12)

        db.session.add(course)
        db.session.commit()
        credentials = b64encode(b"teacher:password")
        test = self.client.put("/course", headers={"Authorization": f"Basic {credentials}"},
                                  data={"id":5,"title": "testtitle",
                                      "filling": "testfilling"})
        self.assertEqual(201, test.status_code)

    def test_post_request(self):
        credentials = b64encode(b"student:password")
        test = self.client.post("/request", headers={"Authorization": f"Basic {credentials}"},
                                data={"course_id":11})
        print(test.data)
        self.assertEqual(201, test.status_code)

    def test_get_request_student(self):
        credentials = b64encode(b"student:password")
        test = self.client.get("/request", headers={"Authorization": f"Basic {credentials}"})
        print(test.data)
        self.assertEqual(404, test.status_code)

    def test_get_request_teacher(self):
        credentials = b64encode(b"teacher:password")
        test = self.client.get("/request", headers={"Authorization": f"Basic {credentials}"})
        print(test.data)
        self.assertEqual(404, test.status_code)

    def test_gelete_request_student(self):
        credentials = b64encode(b"student:password")
        test=self.client.post("/request", headers={"Authorization": f"Basic {credentials}"},
                         data={"course_id": 11})
        print(test.data)
        test = self.client.delete("/request", headers={"Authorization": f"Basic {credentials}"},
                                data={"id":1})
        print(test.data)
        self.assertEqual(204, test.status_code)

    def test_gelete_request_teacher(self):
        credentials = b64encode(b"student:password")
        test=self.client.post("/request", headers={"Authorization": f"Basic {credentials}"},
                         data={"course_id": 11})
        print(test.data)
        credentials = b64encode(b"teacher:password")
        test = self.client.delete("/request", headers={"Authorization": f"Basic {credentials}"},
                                data={"id":1})
        print(test.data)
        self.assertEqual(204, test.status_code)

    def test_put_request_teacher(self):
        credentials = b64encode(b"student:password")
        test=self.client.post("/request", headers={"Authorization": f"Basic {credentials}"},
                         data={"course_id": 11})
        print(test.data)
        credentials = b64encode(b"teacher:password")
        test = self.client.put("/request", headers={"Authorization": f"Basic {credentials}"},
                                data={"id":1,
    "is_confirmed": 1})
        print(test.data)
        self.assertEqual(201, test.status_code)

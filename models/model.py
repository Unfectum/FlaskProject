from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, orm
from flask_login import UserMixin
from sqlalchemy.ext.declarative import declarative_base
from flask_bcrypt import Bcrypt


app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost:5432/Test_db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
Base = declarative_base()


def hash_password(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True)
    password = Column(String)
    firstname = Column(String)
    lastname = Column(String)
    courses = orm.relationship("Course", secondary="requests")
    role = Column(String)


class Course(db.Model):
    __tablename__ = 'courses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    filling = Column(String)
    creator_id = Column(Integer, ForeignKey(User.id))
    creator = orm.relationship(User, backref="User", lazy="joined")
    students = orm.relationship("User", secondary="requests")


class Request(db.Model):
    __tablename__ = 'requests'

    id = Column(Integer, primary_key=True, autoincrement=True)
    is_confirmed = Column(Boolean, default=False)
    course_id = Column(Integer, ForeignKey(Course.id))
    student_id = Column(Integer, ForeignKey(User.id))
    student = orm.relationship(User, backref=orm.backref("course_students", cascade="all, delete-orphan"))
    course = orm.relationship(Course, backref=orm.backref("course_students", cascade="all, delete-orphan"))

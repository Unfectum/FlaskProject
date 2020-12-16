from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, ForeignKey, orm, create_engine

from sqlalchemy.ext.declarative import declarative_base
from flask_bcrypt import Bcrypt
# engine= create_engine(BD_URI)
app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost:5432/laba5db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
Base = declarative_base()


# server_default=text("CURRENT_TIMESTAMP"))


class Student(db.Model):
    __tablename__ = 'Student'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String)
    password = Column(String)
    firstname = Column(String)
    lastname = Column(String)
    courses = orm.relationship("Course", secondary="orders")


    def hash_password(password):
        return bcrypt.generate_password_hash(password)


class Teacher(db.Model):
    __tablename__ = 'Teacher'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String)
    password = Column(String)
    firstname = Column(String)
    lastname = Column(String)

    def __repr__(self):
        return f"Video(name = {self.username}, views = {self.firstname}, likes = {self.lastname})"



class Course(db.Model):
    __tablename__ = 'Course'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    filling = Column(String)
    creator_id = Column(Integer, ForeignKey(Teacher.id))
    creator = orm.relationship(Teacher, backref="Teacher", lazy="joined")
    students = orm.relationship("Student", secondary="orders")

class Request(db.Model):
    __tablename__ = 'Request'

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey(Course.id))
    student_id = Column(Integer, ForeignKey(Student.id))
    teacher_id = Column(Integer, ForeignKey(Teacher.id))
    course = orm.relationship(Course, foreign_keys=[course_id], backref="course", lazy="joined")
    student = orm.relationship(Student, foreign_keys=[student_id], backref="student", lazy="joined")
    teacher = orm.relationship(Teacher, foreign_keys=[teacher_id], backref="teacher", lazy="joined")

class Order(db.Model):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey(Student.id))
    course_id = Column(Integer, ForeignKey(Course.id))
    student = orm.relationship(Student, backref=orm.backref("orders", cascade="all, delete-orphan"))
    product = orm.relationship(Course, backref=orm.backref("orders", cascade="all, delete-orphan"))
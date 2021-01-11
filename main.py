import copy

from flask import Flask

from flask_restful import Api, Resource, reqparse, abort, marshal_with, fields
from flask_sqlalchemy import SQLAlchemy

from models.model import User, Request, Course, bcrypt, hash_password
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)

api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost:5432/Test_db'
db = SQLAlchemy(app)
auth = HTTPBasicAuth()


@auth.verify_password
def verify_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password, password):
        return user


@auth.get_user_roles
def get_user_roles(user):
    return user.role


user_post_args = reqparse.RequestParser()
user_post_args.add_argument("username", type=str, required=True)
user_post_args.add_argument("password", type=str, required=True)
user_post_args.add_argument("firstname", type=str)
user_post_args.add_argument("lastname", type=str)
user_post_args.add_argument("role", type=str, required=True)

user_put_args = reqparse.RequestParser()
user_put_args.add_argument("username", type=str)
user_put_args.add_argument("password", type=str)
user_put_args.add_argument("firstname", type=str)
user_put_args.add_argument("lastname", type=str)

user_resource_fields = {
    'id': fields.Integer,
    'username': fields.String,
    'password': fields.String,
    'firstname': fields.String,
    'lastname': fields.String,
    'role': fields.String,
}


class UserApi(Resource):
    @marshal_with(user_resource_fields)
    def post(self):
        args = user_post_args.parse_args()
        password = hash_password(args['password'])
        user = User(
            username=args['username'],
            password=password,
            firstname=args['firstname'],
            lastname=args['lastname'],
            role=args['role']
        )
        user = db.session.merge(user)
        user_copy = copy.deepcopy(user)
        db.session.add(user)
        db.session.commit()
        db.session.close()
        return user_copy, 201

    @auth.login_required
    @marshal_with(user_resource_fields)
    def put(self):
        args = user_put_args.parse_args()
        result = User.query.get(ident=auth.current_user().id)
        if not result:
            abort(404, message="User doesn't exist, cannot update")
        if args['username']:
            result.username = args['username']
        if args['password']:
            result.password = hash_password(args['password'])
        if args['firstname']:
            result.firstname = args['firstname']
        if args['lastname']:
            result.lastname = args['lastname']
        result = db.session.merge(result)
        user_copy = copy.deepcopy(result)
        db.session.add(result)
        db.session.commit()
        db.session.close()
        return user_copy, 200

    @auth.login_required
    @marshal_with(user_resource_fields)
    def delete(self):
        result = User.query.get(ident=auth.current_user().id)
        if not result:
            abort(404, message="User doesn't exist, cannot delete")
        result = db.session.merge(result)
        db.session.delete(result)
        db.session.commit()
        return 'User deleted', 204

    @auth.login_required
    @marshal_with(user_resource_fields)
    def get(self):
        result = User.query.get(ident=auth.current_user().id)
        if not result:
            abort(404, message="No one user in database")
        return result, 200


course_post_args = reqparse.RequestParser()
course_post_args.add_argument("title", type=str, required=True)
course_post_args.add_argument("filling", type=str, required=True)

course_put_args = reqparse.RequestParser()
course_put_args.add_argument("id", type=int, required=True)
course_put_args.add_argument("title", type=str)
course_put_args.add_argument("filling", type=str)

course_resource_fields = {
    'id': fields.Integer,
    'title': fields.String,
    'filling': fields.String,
    'creator_id': fields.Integer,
}


class CourseApi(Resource):
    @auth.login_required
    @marshal_with(course_resource_fields)
    def get(self):
        if auth.current_user().role == 'teacher':
            result = Course.query.filter_by(creator_id=auth.current_user().id).all()
            if not result:
                abort(404, message="No one course in database")
            return result, 200
        if auth.current_user().role == 'student':
            result = []
            temp = Request.query.filter_by(student_id=auth.current_user().id).all()
            for _ in temp:
                if _.is_confirmed:
                    result.append(Course.query.get(ident=_.course_id))
            if not result:
                abort(404, message="No one course in database")
            return result, 200

    @auth.login_required(role='teacher')
    @marshal_with(course_resource_fields)
    def post(self):
        args = course_post_args.parse_args()
        course = Course(
            title=args['title'],
            filling=args['filling'],
            creator_id=auth.current_user().id
        )
        course_copy = copy.deepcopy(course)
        db.session.add(course)
        db.session.commit()
        db.session.close()
        return course_copy, 201

    @auth.login_required(role='teacher')
    @marshal_with(course_resource_fields)
    def delete(self):
        args = course_put_args.parse_args()
        course = Course.query.filter_by(id=args['id'], creator_id=auth.current_user().id).first()
        if course:
            course = db.session.merge(course)
            db.session.delete(course)
            db.session.commit()
            return "Successfully deleted", 204
        return abort(404, message="Course not found")

    @auth.login_required(role='teacher')
    @marshal_with(course_resource_fields)
    def put(self):
        args = course_put_args.parse_args()
        course = Course.query.get(ident=args['id'])
        if not course:
            abort(404, message="Course doesn't exist, cannot update")
        if course.creator_id != auth.current_user().id:
            return abort(405, message="You can not update this course")
        if args['title']:
            course.title = args['title']
        if args['filling']:
            course.filling = args['filling']
        course = db.session.merge(course)
        course_copy = copy.deepcopy(course)
        db.session.add(course)
        db.session.commit()
        db.session.close()
        return course_copy, 201


request_post_args = reqparse.RequestParser()
request_post_args.add_argument("course_id", type=int, required=True)

request_put_args = reqparse.RequestParser()
request_put_args.add_argument("is_confirmed", type=bool)
request_put_args.add_argument("id", type=int, required=True)

request_resource_fields = {
    'id': fields.Integer,
    'course_id': fields.Integer,
    'student_id': fields.Integer,
    'is_confirmed': fields.Integer,
}


class RequestApi(Resource):
    @auth.login_required
    @marshal_with(request_resource_fields)
    def get(self):
        if auth.current_user().role == 'teacher':
            courses = Course.query.filter_by(creator_id=auth.current_user().id).all()
            result = []
            for course in courses:
                temp = Request.query.filter_by(course_id=course.id).all()
                for request in temp:
                    result.append(request)
            if not result:
                abort(404, message="No one request in database")
            return result, 200
        if auth.current_user().role == 'student':
            result = Request.query.filter_by(student_id=auth.current_user().id).all()
            if not result:
                abort(404, message="No one request in database")
            return result, 200

    @auth.login_required(role='student')
    @marshal_with(request_resource_fields)
    def post(self):
        args = request_post_args.parse_args()
        course = Course.query.get(ident=args['course_id'])
        course.students.append(User.query.get(ident=auth.current_user().id))
        course = db.session.merge(course)
        db.session.add(course)
        db.session.commit()
        return Request.query.filter_by(course_id=args['course_id'], student_id=auth.current_user().id).first(), 201

    @auth.login_required(role='teacher')
    @marshal_with(request_resource_fields)
    def put(self):
        args = request_put_args.parse_args()
        request = Request.query.get(ident=args['id'])
        if args['is_confirmed']:
            temp = Request.query.filter_by(course_id=request.course_id, is_confirmed=True).all()
            print(temp, len(temp))
            if len(temp) >= 2:
                return abort(405, message="No more than 5 students can be added")
        request.is_confirmed = args['is_confirmed']
        request = db.session.merge(request)
        request_copy = copy.deepcopy(request)
        db.session.add(request)
        db.session.commit()
        db.session.close()
        return request_copy, 201

    @auth.login_required
    @marshal_with(request_resource_fields)
    def delete(self):
        args = request_put_args.parse_args()
        if auth.current_user().role == 'teacher':
            courses = Course.query.filter_by(creator_id=auth.current_user().id).all()
            result = []
            for course in courses:
                result.append(Request.query.filter_by(course_id=course.id).all())
                for _ in result:
                    for c in _:
                        if c.id == args['id']:
                            c = db.session.merge(c)
                            db.session.delete(c)
                            db.session.commit()
                            return "Successfully deleted", 204

            return abort(404, message="Request not found")

        if auth.current_user().role == 'student':
            requests = Request.query.filter_by(student_id=auth.current_user().id).all()
            for request in requests:
                if request.id == args['id']:
                    request = db.session.merge(request)
                    db.session.delete(request)
                    db.session.commit()
                    return "Successfully deleted", 204

            return abort(404, message="Request not found")


api.add_resource(UserApi, "/user")
api.add_resource(CourseApi, "/course")
api.add_resource(RequestApi, "/request")

if __name__ == "__main__":
    app.run(debug=True)
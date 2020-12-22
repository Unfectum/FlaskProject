from flask import Flask

from flask_restful import Api, Resource, reqparse, abort, marshal_with, fields
from flask_sqlalchemy import SQLAlchemy

from models.model import User, Request, Course, bcrypt, hash_password
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)

api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost:5432/Flask_db'
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
        db.session.add(user)
        db.session.commit()
        return user, 201

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
            result.password = args['password']
        if args['firstname']:
            result.firstname = args['firstname']
        if args['lastname']:
            result.lastname = args['lastname']
        result = db.session.merge(result)
        db.session.add(result)
        db.session.commit()
        return result

    @auth.login_required
    @marshal_with(user_resource_fields)
    def delete(self):
        result = User.query.get(ident=auth.current_user().id)
        if not result:
            abort(500, message="User doesn't exist, cannot delete")
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
        return result


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
            return result
        if auth.current_user().role == 'student':
            result = []
            temp = Request.query.filter_by(student_id=auth.current_user().id).all()
            for _ in temp:
                if _.is_confirmed:
                    result.append(Course.query.get(ident=_.course_id))
            if not result:
                abort(404, message="No one course in database")
            return result

    @auth.login_required(role='teacher')
    @marshal_with(course_resource_fields)
    def post(self):
        args = course_post_args.parse_args()
        course = Course(
            title=args['title'],
            filling=args['filling'],
            creator_id=auth.current_user().id
        )
        db.session.add(course)
        db.session.commit()
        return course, 201

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
        db.session.add(course)
        db.session.commit()
        return course, 201


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
            return result
        if auth.current_user().role == 'student':
            result = Request.query.filter_by(student_id=auth.current_user().id).all()
            if not result:
                abort(404, message="No one request in database")
            return result

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
            temp = Request.query.filter_by(id=args['id'], is_confirmed=True)
            if len(temp) == 5:
                return abort(405, message="No more than 5 students can be added")
        request.is_confirmed = args['is_confirmed']
        request = db.session.merge(request)
        db.session.add(request)
        db.session.commit()
        return request, 201

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

# class TeacherApi(Resource):
#     @auth.login_required
#     @marshal_with(teacher_resource_fields)
#     def get(self):
#         result = Teacher.query.all()
#         if not result:
#             abort(404, message="No one teacher in database")
#         return result
#
#     @marshal_with(teacher_resource_fields)
#     def post(self):
#         args = teacher_post_args.parse_args()
#         if not (Student.query.filter_by(username=args['username']).first() or Teacher.query.filter_by(
#                 username=args['username']).first()):
#             passw = hash_password(args['password'])
#             video = Teacher(username=args['username'], password=passw,
#                             firstname=args['firstname'],
#                             lastname=args['lastname'])
#             db.session.add(video)
#             db.session.commit()
#             return video, 201
#         else:
#             return "Username already exist", 405
#
#
# class TeacheridApi(Resource):
#
#     @marshal_with(teacher_resource_fields)
#     def get(self, teacher_id):
#         result = Teacher.query.get(ident=teacher_id)
#         if not result:
#             abort(404, message="Could not find teacher with that id")
#         return result
#
#     @marshal_with(teacher_resource_fields)
#     def put(self, teacher_id):
#         args = teacher_update_args.parse_args()
#         result = Teacher.query.filter_by(id=teacher_id).first()
#         if not result:
#             abort(404, message="Teacher doesn't exist, cannot update")
#         if args['username']:
#             result.username = args['username']
#         if args['password']:
#             result.password = args['password']
#         if args['firstname']:
#             result.firstname = args['firstname']
#         if args['lastname']:
#             result.lastname = args['lastname']
#         result = db.session.merge(result)
#         db.session.add(result)
#         db.session.commit()
#
#         return result
#
#     def delete(self, teacher_id):
#         result = Teacher.query.filter_by(id=teacher_id).first()
#         if not result:
#             abort(500, message="Teacher doesn't exist, cannot delete")
#         result = db.session.merge(result)
#         db.session.delete(result)
#         db.session.commit()
#         return 'Teacher deleted', 204
#
#
# student_post_args = reqparse.RequestParser()
# student_post_args.add_argument("username", type=str, required=True)
# student_post_args.add_argument("password", type=str, required=True)
# student_post_args.add_argument("firstname", type=str, required=True)
# student_post_args.add_argument("lastname", type=str, required=True)
# # student_post_args.add_argument("course", type=list)
#
# student_update_args = reqparse.RequestParser()
# student_update_args.add_argument("username", type=str)
# student_update_args.add_argument("password", type=str)
# student_update_args.add_argument("firstname", type=str)
# student_update_args.add_argument("lastname", type=str)
# # student_update_args.add_argument("course", type=list)
#
# course_resource_fields = {
#     'id': fields.Integer,
#     'title': fields.String,
#     'filling': fields.String,
#     'creator_id': fields.Integer,
# }
#
# student_resource_fields = {
#     'id': fields.Integer,
#     'username': fields.String,
#     'password': fields.String,
#     'firstname': fields.String,
#     'lastname': fields.String,
#     'courses': fields.List(fields.Nested(course_resource_fields))
# }
#
#
# class StudentApi(Resource):
#     @auth.login_required
#     @marshal_with(student_resource_fields)
#     def get(self):
#         result = Student.query.all()
#
#         if not result:
#             abort(404, message="No one student in database")
#
#         return result
#
#     @marshal_with(student_resource_fields)
#     def post(self):
#         args = student_post_args.parse_args()
#         # courselist=[]
#         # if(args['course']):
#         #     for c in args['course']:
#         #         courselist.append(Course.query.get(ident=c))
#
#         # for co in range(len(courselist)):
#         #     courselist[co] = db.session.merge(courselist[co])
#         if not (Student.query.filter_by(username=args['username']).first() or Teacher.query.filter_by(
#                 username=args['username']).first()):
#
#             passw = hash_password(args['password'])
#
#             video = Student(username=args['username'], password=passw, firstname=args['firstname'],
#                             lastname=args['lastname'])
#             db.session.add(video)
#             db.session.commit()
#             return video, 201
#         else:
#             return None, 405
#
#
# class StudentidApi(Resource):
#
#     @marshal_with(student_resource_fields)
#     def get(self, student_id):
#
#         result = Student.query.get(ident=student_id)
#
#         if not result:
#             abort(404, message="Could not find student with that id")
#         return result, 200
#
#     @marshal_with(student_resource_fields)
#     def put(self, student_id):
#         args = student_update_args.parse_args()
#         result = Student.query.filter_by(id=student_id).first()
#         if not result:
#             abort(404, message="Student doesn't exist, cannot update")
#
#         if args['username']:
#             result.username = args['username']
#         if args['password']:
#             result.password = args['password']
#         if args['firstname']:
#             result.firstname = args['firstname']
#         if args['lastname']:
#             result.lastname = args['lastname']
#
#         result = db.session.merge(result)
#
#         db.session.add(result)
#         db.session.commit()
#
#         return result
#
#     def delete(self, student_id):
#         result = Student.query.filter_by(id=student_id).first()
#         if not result:
#             abort(500, message="Student doesn't exist, cannot delete")
#         result = db.session.merge(result)
#
#         db.session.delete(result)
#         db.session.commit()
#         return "Student deleted", 205
#
#
# order_post_args = reqparse.RequestParser()
#
# order_post_args.add_argument("course_id", type=int, required=True)
#
# order_update_args = reqparse.RequestParser()
# order_update_args.add_argument("student_id", type=int, required=True)
# order_update_args.add_argument("course_id", type=int, required=True)
#
# order_resource_fields = {
#     'id': fields.Integer,
#     'student_id': fields.Integer,
#     'course_id': fields.Integer,
#
# }
#
#
# class OrderApi(Resource):
#     @auth.login_required
#     def post(self):
#         args = order_post_args.parse_args()
#         video = Connection(student_id=Student.query.filter_by(username=auth.current_user().username()).id,
#                            course_id=args['course_id'])
#         db.session.add(video)
#         db.session.commit()
#         return video, 201
#
#
# class OrderidApi(Resource):
#     @marshal_with(order_resource_fields)
#     def delete(self, student_id, course_id):
#         result = Student.query.filter_by(id=student_id).first()
#         if not result:
#             abort(500, message="Student doesn't exist, cannot delete")
#         result = db.session.merge(result)
#         # result.courses.remove(Course.query.get(ident=course_id))
#         result.courses.pop(course_id)
#         # db.session.delete(result)
#         db.session.commit()
#         return course_id, 204
#
#     @marshal_with(order_resource_fields)
#     def post(self, student_id, course_id):
#         result = Student.query.filter_by(id=student_id).first()
#
#         if len(result.courses) < 5:
#
#             result.courses.append(Course.query.get(ident=course_id))
#             result = db.session.merge(result)
#             db.session.add(result)
#             db.session.commit()
#         else:
#             abort(500, message="Maximum 5 courses")
#         return course_id, 204
#
#
# request_post_args = reqparse.RequestParser()
# request_post_args.add_argument("course_id", type=int, required=True)
# request_post_args.add_argument("student_id", type=int, required=True)
# request_post_args.add_argument("teacher_id", type=int, required=True)
#
# request_update_args = reqparse.RequestParser()
# request_update_args.add_argument("course_id", type=int, required=True)
# request_update_args.add_argument("student_id", type=int, required=True)
# request_update_args.add_argument("teacher_id", type=int, required=True)
#
# request_resource_fields = {
#     'id': fields.Integer,
#     'course_id': fields.Integer,
#     'student_id': fields.Integer,
#     'teacher_id': fields.Integer,
# }
#
#
# class RequestApi(Resource):
#     @marshal_with(request_resource_fields)
#     def get(self):
#         result = Request.query.all()
#         if not result:
#             abort(404, message="No one request in database")
#         return result
#
#     @marshal_with(request_resource_fields)
#     def post(self):
#         args = request_post_args.parse_args()
#         result = Request(course_id=args['course_id'], student_id=args['student_id'],
#                          teacher_id=args['teacher_id'])
#         db.session.add(result)
#         db.session.commit()
#         return result, 201
#
#
# class RequestidApi(Resource):
#
#     @marshal_with(request_resource_fields)
#     def get(self, request_id):
#         result = Request.query.get(ident=request_id)
#
#         if not result:
#             abort(404, message="Could not find request with that id")
#         return result
#
#     @marshal_with(student_resource_fields)
#     def put(self, request_id):
#         args = request_post_args.parse_args()
#         result = Request.query.filter_by(id=request_id).first()
#         if not result:
#             abort(404, message="Request doesn't exist, cannot update")
#
#         if args['course_id']:
#             result.course_id = args['course_id']
#         if args['student_id']:
#             result.student_id = args['student_id']
#         if args['teacher_id']:
#             result.teacher_id = args['teacher_id']
#
#         result = db.session.merge(result)
#         db.session.add(result)
#         db.session.commit()
#
#         return result
#
#     def delete(self, request_id):
#         result = Request.query.filter_by(id=request_id).first()
#         if not result:
#             abort(500, message="Student doesn't exist, cannot delete")
#         result = db.session.merge(result)
#         db.session.delete(result)
#         db.session.commit()
#         return 'Request deleted', 204
#
#
# course_post_args = reqparse.RequestParser()
# course_post_args.add_argument("title", type=str, required=True)
# course_post_args.add_argument("filling", type=str, required=True)
# course_post_args.add_argument("creator_id", type=int, required=True)
#
# course_update_args = reqparse.RequestParser()
# course_update_args.add_argument("title", type=str, required=True)
# course_update_args.add_argument("filling", type=str, required=True)
# course_update_args.add_argument("creator_id", type=int, required=True)
#
#
# class CourseApi(Resource):
#     @marshal_with(course_resource_fields)
#     def get(self):
#         result = Course.query.all()
#         if not result:
#             abort(404, message="No one course in database")
#         return result
#
#     @marshal_with(course_resource_fields)
#     def post(self):
#         args = course_post_args.parse_args()
#         result = Course(title=args['title'], filling=args['filling'],
#                         creator_id=args['creator_id'])
#         db.session.add(result)
#         db.session.commit()
#         return result, 201
#
#
# class CourseidApi(Resource):
#
#     @marshal_with(course_resource_fields)
#     def get(self, course_id):
#         result = Course.query.get(ident=course_id)
#
#         if not result:
#             abort(404, message="Could not find course with that id")
#         return result
#
#     @marshal_with(course_resource_fields)
#     def put(self, course_id):
#         args = course_post_args.parse_args()
#         result = Course.query.filter_by(id=course_id).first()
#         if not result:
#             abort(404, message="Course doesn't exist, cannot update")
#
#         if args['title']:
#             result.title = args['title']
#         if args['filling']:
#             result.filling = args['filling']
#         if args['creator_id']:
#             result.creator_id = args['creator_id']
#
#         result = db.session.merge(result)
#         db.session.add(result)
#         db.session.commit()
#
#         return result
#
#     def delete(self, course_id):
#         result = Course.query.filter_by(id=course_id).first()
#         if not result:
#             abort(500, message="Course doesn't exist, cannot delete")
#         result = db.session.merge(result)
#         db.session.delete(result)
#         db.session.commit()
#         return 'Request deleted', 204
#
#
# api.add_resource(OrderidApi, "/order/<int:course_id>")
# api.add_resource(OrderApi, "/order")
#
# api.add_resource(CourseidApi, "/course/<int:course_id>")
# api.add_resource(CourseApi, "/course")
#
# api.add_resource(RequestidApi, "/request/<int:request_id>")
# api.add_resource(RequestApi, "/request")
#
# api.add_resource(StudentidApi, "/student/<int:student_id>")
# api.add_resource(StudentApi, "/student")
#
# api.add_resource(TeacheridApi, "/teacher/<int:teacher_id>")
# api.add_resource(TeacherApi, "/teacher")
#
# if __name__ == "__main__":
#     app.run(debug=True)

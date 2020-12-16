
from flask import Flask

from flask_restful import Api, Resource, reqparse, abort, marshal_with, fields
from flask_sqlalchemy import SQLAlchemy


from models.model import Teacher, Student, Request, Course, Order

app = Flask(__name__)

api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost:5432/laba5db'
db = SQLAlchemy(app)

teacher_put_args = reqparse.RequestParser()
teacher_put_args.add_argument("username", type=str, required=True)
teacher_put_args.add_argument("password", type=str, required=True)
teacher_put_args.add_argument("firstname", type=str, required=True)
teacher_put_args.add_argument("lastname", type=str, required=True)

teacher_update_args = reqparse.RequestParser()
teacher_update_args.add_argument("username", type=str)
teacher_update_args.add_argument("password", type=str)
teacher_update_args.add_argument("firstname", type=str)
teacher_update_args.add_argument("lastname", type=str)

teacher_resource_fields = {
    'id': fields.Integer,
    'username': fields.String,
    'password': fields.String,
    'firstname': fields.String,
    'lastname': fields.String,
}


class TeacherApi(Resource):
    @marshal_with(teacher_resource_fields)
    def get(self):
        result = Teacher.query.all()
        if not result:
            abort(404, message="No one teacher in database")
        return result

    @marshal_with(teacher_resource_fields)
    def put(self):
        args = teacher_put_args.parse_args()
        video = Teacher(username=args['username'], password=Student.hash_password(args['password']), firstname=args['firstname'],
                        lastname=args['lastname'])
        db.session.add(video)
        db.session.commit()
        return video, 201


class TeacheridApi(Resource):

    @marshal_with(teacher_resource_fields)
    def get(self, teacher_id):
        result = Teacher.query.get(ident=teacher_id)
        if not result:
            abort(404, message="Could not find teacher with that id")
        return result

    @marshal_with(teacher_resource_fields)
    def patch(self, teacher_id):
        args = teacher_update_args.parse_args()
        result = Teacher.query.filter_by(id=teacher_id).first()
        if not result:
            abort(404, message="Teacher doesn't exist, cannot update")
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

    def delete(self, teacher_id):
        result = Teacher.query.filter_by(id=teacher_id).first()
        if not result:
            abort(500, message="Teacher doesn't exist, cannot delete")
        result = db.session.merge(result)
        db.session.delete(result)
        db.session.commit()
        return 'Teacher deleted', 204


student_put_args = reqparse.RequestParser()
student_put_args.add_argument("username", type=str, required=True)
student_put_args.add_argument("password", type=str, required=True)
student_put_args.add_argument("firstname", type=str, required=True)
student_put_args.add_argument("lastname", type=str, required=True)
#student_put_args.add_argument("course", type=list)

student_update_args = reqparse.RequestParser()
student_update_args.add_argument("username", type=str)
student_update_args.add_argument("password", type=str)
student_update_args.add_argument("firstname", type=str)
student_update_args.add_argument("lastname", type=str)
#student_update_args.add_argument("course", type=list)

course_resource_fields = {
    'id': fields.Integer,
    'title': fields.String,
    'filling': fields.String,
    'creator_id': fields.Integer,
}


student_resource_fields = {
    'id': fields.Integer,
    'username': fields.String,
    'password': fields.String,
    'firstname': fields.String,
    'lastname': fields.String,
    'courses': fields.List(fields.Nested(course_resource_fields))
}


class StudentApi(Resource):
    @marshal_with(student_resource_fields)
    def get(self):
        result = Student.query.all()

        if not result:
            abort(404, message="No one student in database")

        return result

    @marshal_with(student_resource_fields)
    def put(self):
        args = student_put_args.parse_args()
        # courselist=[]
        # if(args['course']):
        #     for c in args['course']:
        #         courselist.append(Course.query.get(ident=c))

        # for co in range(len(courselist)):
        #     courselist[co] = db.session.merge(courselist[co])
        video = Student(username=args['username'], password=args['password'], firstname=args['firstname'],
                        lastname=args['lastname'])
        db.session.add(video)
        db.session.commit()
        return video, 201


class StudentidApi(Resource):

    @marshal_with(student_resource_fields)
    def get(self, student_id):

        result=Student.query.get(ident=student_id)

        if not result:
            abort(404, message="Could not find student with that id")
        return result, 200

    @marshal_with(student_resource_fields)
    def patch(self, student_id):
        args = student_update_args.parse_args()
        result = Student.query.filter_by(id=student_id).first()
        if not result:
            abort(404, message="Student doesn't exist, cannot update")

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

    def delete(self, student_id):
        result = Student.query.filter_by(id=student_id).first()
        if not result:
            abort(500, message="Student doesn't exist, cannot delete")
        result = db.session.merge(result)

        db.session.delete(result)
        db.session.commit()
        return  "Student deleted",205


order_put_args = reqparse.RequestParser()
order_put_args.add_argument("student_id", type=int, required=True)
order_put_args.add_argument("course_id", type=int, required=True)


order_update_args = reqparse.RequestParser()
order_update_args.add_argument("student_id", type=int, required=True)
order_update_args.add_argument("course_id", type=int, required=True)

order_resource_fields = {
    'id': fields.Integer,
    'student_id': fields.Integer,
    'course_id': fields.Integer,


}

class OrderApi(Resource):
    def put(self):
        args = order_put_args.parse_args()
        video = Order(student_id=args['student_id'], course_id=args['course_id'])
        db.session.add(video)
        db.session.commit()
        return video, 201

class OrderidApi(Resource):
    @marshal_with(order_resource_fields)
    def delete(self, student_id, course_id):
        result = Student.query.filter_by(id=student_id).first()
        if not result:
            abort(500, message="Student doesn't exist, cannot delete")
        result = db.session.merge(result)
        #result.courses.remove(Course.query.get(ident=course_id))
        result.courses.pop(course_id)
        # db.session.delete(result)
        db.session.commit()
        return course_id, 204

    @marshal_with(order_resource_fields)
    def put(self, student_id, course_id):
        result = Student.query.filter_by(id=student_id).first()

        if(len(result.courses)<5):

            result.courses.append(Course.query.get(ident=course_id))
            result = db.session.merge(result)
            db.session.add(result)
            db.session.commit()
        else:
            abort(500, message="Maximum 5 courses")
        return course_id, 204

request_put_args = reqparse.RequestParser()
request_put_args.add_argument("course_id", type=int, required=True)
request_put_args.add_argument("student_id", type=int, required=True)
request_put_args.add_argument("teacher_id", type=int, required=True)

request_update_args = reqparse.RequestParser()
request_update_args.add_argument("course_id", type=int, required=True)
request_update_args.add_argument("student_id", type=int, required=True)
request_update_args.add_argument("teacher_id", type=int, required=True)

request_resource_fields = {
    'id': fields.Integer,
    'course_id': fields.Integer,
    'student_id': fields.Integer,
    'teacher_id': fields.Integer,
}


class RequestApi(Resource):
    @marshal_with(request_resource_fields)
    def get(self):
        result = Request.query.all()
        if not result:
            abort(404, message="No one request in database")
        return result

    @marshal_with(request_resource_fields)
    def put(self):
        args = request_put_args.parse_args()
        result = Request(course_id=args['course_id'], student_id=args['student_id'],
                         teacher_id=args['teacher_id'])
        db.session.add(result)
        db.session.commit()
        return result, 201


class RequestidApi(Resource):

    @marshal_with(request_resource_fields)
    def get(self, request_id):
        result = Request.query.get(ident=request_id)

        if not result:
            abort(404, message="Could not find request with that id")
        return result

    @marshal_with(student_resource_fields)
    def patch(self, request_id):
        args = request_put_args.parse_args()
        result = Request.query.filter_by(id=request_id).first()
        if not result:
            abort(404, message="Request doesn't exist, cannot update")

        if args['course_id']:
            result.course_id = args['course_id']
        if args['student_id']:
            result.student_id = args['student_id']
        if args['teacher_id']:
            result.teacher_id = args['teacher_id']

        result = db.session.merge(result)
        db.session.add(result)
        db.session.commit()

        return result

    def delete(self, request_id):
        result = Request.query.filter_by(id=request_id).first()
        if not result:
            abort(500, message="Student doesn't exist, cannot delete")
        result = db.session.merge(result)
        db.session.delete(result)
        db.session.commit()
        return 'Request deleted', 204


course_put_args = reqparse.RequestParser()
course_put_args.add_argument("title", type=str, required=True)
course_put_args.add_argument("filling", type=str, required=True)
course_put_args.add_argument("creator_id", type=int, required=True)

course_update_args = reqparse.RequestParser()
course_update_args.add_argument("title", type=str, required=True)
course_update_args.add_argument("filling", type=str, required=True)
course_update_args.add_argument("creator_id", type=int, required=True)




class CourseApi(Resource):
    @marshal_with(course_resource_fields)
    def get(self):
        result = Course.query.all()
        if not result:
            abort(404, message="No one course in database")
        return result

    @marshal_with(course_resource_fields)
    def put(self):
        args = course_put_args.parse_args()
        result = Course(title=args['title'], filling=args['filling'],
                        creator_id=args['creator_id'])
        db.session.add(result)
        db.session.commit()
        return result, 201


class CourseidApi(Resource):

    @marshal_with(course_resource_fields)
    def get(self, course_id):
        result = Course.query.get(ident=course_id)

        if not result:
            abort(404, message="Could not find course with that id")
        return result

    @marshal_with(course_resource_fields)
    def patch(self, course_id):
        args = course_put_args.parse_args()
        result = Course.query.filter_by(id=course_id).first()
        if not result:
            abort(404, message="Course doesn't exist, cannot update")

        if args['title']:
            result.title = args['title']
        if args['filling']:
            result.filling = args['filling']
        if args['creator_id']:
            result.creator_id = args['creator_id']

        result = db.session.merge(result)
        db.session.add(result)
        db.session.commit()

        return result

    def delete(self, course_id):
        result = Course.query.filter_by(id=course_id).first()
        if not result:
            abort(500, message="Course doesn't exist, cannot delete")
        result = db.session.merge(result)
        db.session.delete(result)
        db.session.commit()
        return 'Request deleted', 204


api.add_resource(OrderidApi, "/order/<int:student_id>/<int:course_id>")
api.add_resource(OrderApi, "/order")

api.add_resource(CourseidApi, "/course/<int:course_id>")
api.add_resource(CourseApi, "/course")

api.add_resource(RequestidApi, "/request/<int:request_id>")
api.add_resource(RequestApi, "/request")

api.add_resource(StudentidApi, "/student/<int:student_id>")
api.add_resource(StudentApi, "/student")

api.add_resource(TeacheridApi, "/teacher/<int:teacher_id>")
api.add_resource(TeacherApi, "/teacher")

if __name__ == "__main__":
    app.run(debug=True)

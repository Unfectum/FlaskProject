from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.model import Student, Teacher, Request, Course

engine = create_engine('postgresql://postgres:1234@localhost:5432/laba5db')
Session = sessionmaker(bind=engine)
session = Session()

teacher = Teacher(firstname="oleg", id=1, password="qwerty", username="Illia")

student2 = Student(firstname="vova", id=2, password="12345", username="NeIllia")
course1 = Course(id=1, title="title1", filling="filling1", creator_id=teacher.id)
course2 = Course(id=2, title="title2", filling="filling2", creator_id=teacher.id)
student1 = Student(firstname="vova", id=1, password="12345", username="NeIllia", courses=[course1, course2])
request = Request(id=1, course_id=course1.id, student_id=student1.id, teacher_id=teacher.id)
course3 = Course(id=3, title="title3", filling="filling3", creator_id=teacher.id, students=[student1,student2])
course4 = Course(id=4, title="title4", filling="filling4", creator_id=teacher.id)
request2 = Request(id=2, course_id=course3.id, student_id=student1.id, teacher_id=teacher.id)

session.add(teacher)
session.add(student1)
session.add(course1)
session.add(student2)
session.add(course2)
session.add(request)
session.add(request2)
session.add(course3)
session.add(course4)

session.commit()

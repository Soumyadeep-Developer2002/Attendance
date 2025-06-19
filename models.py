from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class InstituteDetails(db.Model, UserMixin):
    __tablename__ = 'Institute_Details'
    Institute_ID = db.Column(db.String(100), primary_key=True)  
    Institute_Name = db.Column(db.String(100), nullable=False)
    Name = db.Column(db.String(100), nullable=False)
    Email_id = db.Column(db.String(100), nullable=False)
    Phone_Number = db.Column(db.String(20), nullable=False)
    Registration_Date = db.Column(db.DateTime, default=datetime.utcnow)
    Password = db.Column(db.String(100), nullable=False)
    Photo = db.Column(db.String(225))
    Video = db.Column(db.String(225))
    
    def get_id(self):
        return str(self.Institute_ID)


class StudentDetails(db.Model, UserMixin):
    __tablename__ = 'Student_Details'
    Student_ID = db.Column(db.String(100), primary_key=True)  
    Institute_Name = db.Column(db.String(100), nullable=False)
    Institute_ID = db.Column(db.String(100), db.ForeignKey('Institute_Details.Institute_ID'), nullable=False) 
    Name = db.Column(db.String(100), nullable=False)
    Email_id = db.Column(db.String(100), nullable=False)
    Phone_Number = db.Column(db.String(20), nullable=False)
    Registration_Date = db.Column(db.DateTime, default=datetime.utcnow)
    Password = db.Column(db.String(100), nullable=False)
    Photo = db.Column(db.String(225))
    Video = db.Column(db.String(225))

    Institute = db.relationship('InstituteDetails', backref='students')

    def get_id(self):
        return str(self.Student_ID)


class TeacherDetails(db.Model, UserMixin):
    __tablename__ = 'Teacher_Details'
    Teacher_ID = db.Column(db.String(100), primary_key=True)
    Institute_Name = db.Column(db.String(100), nullable=False)
    Institute_ID = db.Column(db.String(100), db.ForeignKey('Institute_Details.Institute_ID'), nullable=False) 
    Name = db.Column(db.String(100), nullable=False)
    Email_id = db.Column(db.String(100), nullable=False)
    Phone_Number = db.Column(db.String(20), nullable=False)
    Registration_Date = db.Column(db.DateTime, default=datetime.utcnow)
    Password = db.Column(db.String(100), nullable=False)
    Photo = db.Column(db.String(225))
    Video = db.Column(db.String(225))

    Institute = db.relationship('InstituteDetails', backref='teachers')
    subjects = db.relationship('TeacherSubject', backref='teacher', cascade='all, delete-orphan')

    def get_id(self):
        return str(self.Teacher_ID)


class StudentTeacherMap(db.Model):
    __tablename__ = 'Student_Teacher_Ids'
    Student_ID = db.Column(db.String(100), db.ForeignKey('Student_Details.Student_ID'), primary_key=True)
    Teacher_ID = db.Column(db.String(100), db.ForeignKey('Teacher_Details.Teacher_ID'), primary_key=True)

    Student = db.relationship('StudentDetails', backref='IDMap')
    Teacher = db.relationship('TeacherDetails', backref='IDMap')



class ClassPhoto(db.Model):
    __tablename__ = 'Class_Photos'
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.String(100), db.ForeignKey('Teacher_Details.Teacher_ID'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    photo_url = db.Column(db.String(225), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ClassAttendance(db.Model):
    __tablename__ = 'Class_Attendance'
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.String(100), db.ForeignKey('Teacher_Details.Teacher_ID'), nullable=False)
    student_id = db.Column(db.String(100), db.ForeignKey('Student_Details.Student_ID'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    is_present = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    teacher = db.relationship('TeacherDetails', backref='attendances')
    student = db.relationship('StudentDetails', backref='attendances')

class TeacherSubject(db.Model):
    __tablename__ = 'Teacher_Subjects'
    id = db.Column(db.Integer, primary_key=True)
    Teacher_ID = db.Column(db.String(100), db.ForeignKey('Teacher_Details.Teacher_ID'), nullable=False)
    Year = db.Column(db.String(10), nullable=False)
    Subject = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<TeacherSubject {self.Teacher_ID} - {self.Year} - {self.Subject}>'

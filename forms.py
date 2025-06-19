from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from flask_wtf.file import FileAllowed, FileField

class RegistrationForm(FlaskForm):
    role = SelectField('Register As', choices=[('Student', 'Student'), ('Institute', 'Institute')], validators=[DataRequired()])

    Institute_Name = StringField('Institute Name', validators=[DataRequired()])
    Name = StringField('Name', validators=[DataRequired()])
    Email = StringField('Email', validators=[DataRequired(), Email()])
    Phone_Number = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    Registration_Date = DateField('Registration Date', format='%Y-%m-%d', validators=[DataRequired()])
    Password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    Confirm_Password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('Password')])
    Photo = FileField('Upload Your Photo', validators=[DataRequired()])
    Video = FileField('UPload Your Video', validators=[DataRequired()])
    
    Student_ID = StringField('Student ID')
    Institute_ID = StringField('Institute ID', validators=[DataRequired()])

    Submit = SubmitField('Register')


class LoginForm(FlaskForm):
    role = SelectField('Login As', choices=[('Student', 'Student'), ('Teacher', 'Teacher'), ('Institute', 'Institute')])
    Identifier = StringField('ID', validators=[DataRequired()])
    Password = PasswordField('Password', validators=[DataRequired()])
    
    Submit = SubmitField('Login')


class ClassPhotoForm(FlaskForm):
    class_photo = FileField('Upload Class Photo', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    subject = SelectField('Subject', validators=[DataRequired()])
    submit = SubmitField('Upload Photo')


class ComplaintForm(FlaskForm):
    subject = StringField('Subject', validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Submit Complaint')


class TeacherEnrollmentForm(FlaskForm):
    Name = StringField('Teacher Name', validators=[DataRequired()])
    Teacher_ID = StringField('Teacher ID', validators=[DataRequired()])
    Email_id = StringField('Email', validators=[DataRequired(), Email()])
    Password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    
    Year1 = SelectField('Year 1', choices=[
        ('1st', '1st Year'),
        ('2nd', '2nd Year'),
        ('3rd', '3rd Year'),
        ('4th', '4th Year')
    ], validators=[DataRequired()])
    Subject1 = StringField('Subject 1', validators=[DataRequired()])
    
    Year2 = SelectField('Year 2', choices=[
        ('1st', '1st Year'),
        ('2nd', '2nd Year'),
        ('3rd', '3rd Year'),
        ('4th', '4th Year')
    ], validators=[DataRequired()])
    Subject2 = StringField('Subject 2', validators=[DataRequired()])
    
    Year3 = SelectField('Year 3', choices=[
        ('1st', '1st Year'),
        ('2nd', '2nd Year'),
        ('3rd', '3rd Year'),
        ('4th', '4th Year')
    ], validators=[DataRequired()])
    Subject3 = StringField('Subject 3', validators=[DataRequired()])
    
    Year4 = SelectField('Year 4', choices=[
        ('1st', '1st Year'),
        ('2nd', '2nd Year'),
        ('3rd', '3rd Year'),
        ('4th', '4th Year')
    ], validators=[DataRequired()])
    Subject4 = StringField('Subject 4', validators=[DataRequired()])
    
    Submit = SubmitField('Enroll Teacher')


class TeacherProfileForm(FlaskForm):
    Name = StringField('Name', validators=[DataRequired()])
    Email_id = StringField('Email', validators=[DataRequired(), Email()])
    Phone_Number = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    Photo = FileField('Upload New Photo', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    Current_Password = PasswordField('Current Password', validators=[DataRequired()])
    New_Password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    Confirm_Password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('New_Password')])
    Submit = SubmitField('Update Profile')

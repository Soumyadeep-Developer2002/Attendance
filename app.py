import os
from flask import Flask, render_template, flash, url_for, redirect, send_file
from forms import RegistrationForm, LoginForm, ClassPhotoForm, ComplaintForm, TeacherEnrollmentForm, TeacherProfileForm
from models import StudentDetails, TeacherDetails, InstituteDetails, ClassPhoto, ClassAttendance, db, TeacherSubject, StudentTeacherMap
from flask_login import login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import cloudinary
import cloudinary.uploader
from io import StringIO, BytesIO
import csv
from datetime import datetime
from flask_mail import Mail, Message


app = Flask(__name__)

# Configure Cloudinary
cloudinary.config(
    cloud_name = 'duxusnkun',
    api_key = '541916917721478',
    api_secret = 'IkcE4UrQCwESmIyRBp3rLopNCgw'
)

# Configure Email
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'soumyadeep.ghosh220402@gmail.com'
app.config['MAIL_PASSWORD'] = '@Cle_Project'
mail = Mail(app)

# Configure DATABASE
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///data.db'
app.config['SECRET_KEY'] = '@Cle_Project'
db.init_app(app)

# Configure Files
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'mp4'}
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024


# LOGIN MANAGER
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    user = StudentDetails.query.filter_by(Student_ID=user_id).first()
    if user:
        return user
    user = TeacherDetails.query.filter_by(Teacher_ID=user_id).first()
    if user:
        return user
    user = InstituteDetails.query.filter_by(Institute_ID=user_id).first()
    return user 

@app.route('/', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = None
        if form.role.data == 'Student':
            user = StudentDetails.query.filter_by(Student_ID=form.Identifier.data).first()
        elif form.role.data == 'Teacher':
            user = TeacherDetails.query.filter_by(Teacher_ID=form.Identifier.data).first()
        elif form.role.data == 'Institute':
            user = InstituteDetails.query.filter_by(Institute_ID=form.Identifier.data).first()

        if user and user.Password == form.Password.data:
            login_user(user)
            flash("Login Successful")
            if form.role.data == 'Student':
                return redirect(url_for('student_dashboard'))
            elif form.role.data == 'Teacher':
                return redirect(url_for('teacher_dashboard'))
            else:
                return redirect(url_for('Institute_dashboard'))
        else:
            flash("Login Failed")

    return render_template('login.html', form=form)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    
    Photo_cloudinary_url = None
    Video_cloudinary_url = None

    if form.validate_on_submit():
        if form.Photo.data and allowed_file(form.Photo.data.filename):
            Photo_file : FileStorage = form.Photo.data
            Photo_filename = secure_filename(Photo_file.filename)
            try:
                response_image = cloudinary.uploader.upload(Photo_file.stream)
                Photo_cloudinary_url = response_image.get('secure_url', None)
            except Exception as e:
                print("Something Error")

        if form.Video.data and allowed_file(form.Video.data.filename):
            Video_file : FileStorage = form.Video.data
            Video_filename = secure_filename(Video_file.filename)
            try:
                response_video = cloudinary.uploader.upload_large(Video_file.stream, resource_type= 'video')
                Video_cloudinary_url = response_video.get('secure_url')
            except Exception as e:
                print("Something Error")
        

        newUser = None
        
        if form.role.data == 'Student':
            newUser = StudentDetails(
                Institute_Name=form.Institute_Name.data,
                Institute_ID=form.Institute_ID.data,
                Name=form.Name.data,
                Student_ID=form.Student_ID.data,
                Email_id=form.Email.data,
                Phone_Number=form.Phone_Number.data,
                Registration_Date=form.Registration_Date.data,
                Password=form.Password.data,
                Photo=Photo_cloudinary_url,
                Video=Video_cloudinary_url
            )
        elif form.role.data == 'Institute':
            newUser = InstituteDetails(
                Institute_Name=form.Institute_Name.data,
                Name=form.Name.data,
                Institute_ID=form.Institute_ID.data,
                Email_id=form.Email.data,
                Phone_Number=form.Phone_Number.data,
                Registration_Date=form.Registration_Date.data,
                Password=form.Password.data,
                Photo=Photo_cloudinary_url,
                Video=Video_cloudinary_url
            )

        db.session.add(newUser)
        db.session.commit()
        flash("Registration Successful! Please Login")
        return redirect(url_for('login'))

    return render_template('home.html', form=form)


@app.route('/about')
def aboutPage():
    return render_template('about.html')

@app.route('/contact')
def contactPage():
    return render_template('contact.html')

@app.route('/student-dashboard')
@login_required
def student_dashboard():
    if not isinstance(current_user, StudentDetails):
        flash('Access denied. Students only.', 'error')
        return redirect(url_for('login'))
    
    today = datetime.now().date()
    today_attendance = ClassAttendance.query.filter_by(
        student_id=current_user.Student_ID,
        date=today
    ).first()
    
    # Get last 7 days of attendance history
    attendance_history = ClassAttendance.query.filter_by(
        student_id=current_user.Student_ID
    ).order_by(ClassAttendance.date.desc()).limit(7).all()
    
    complaint_form = ComplaintForm()
    
    return render_template('student_dashboard.html',
                         today_date=today,
                         today_attendance=today_attendance,
                         attendance_history=attendance_history,
                         complaint_form=complaint_form)

@app.route('/submit-complaint', methods=['POST'])
@login_required
def submit_complaint():
    if not isinstance(current_user, StudentDetails):
        flash('Access denied. Students only.', 'error')
        return redirect(url_for('login'))
    
    form = ComplaintForm()
    if form.validate_on_submit():
        try:
            # Create email message
            msg = Message(
                subject=f"Complaint from {current_user.Name} ({current_user.Student_ID})",
                sender=current_user.Email_id,
                recipients=['soumyadeep.ghosh220402@gmail.com']
            )
            msg.body = f"""
            From: {current_user.Name}
            Student ID: {current_user.Student_ID}
            Email: {current_user.Email_id}
            
            Subject: {form.subject.data}
            
            Message:
            {form.message.data}
            """
            
            # Send email
            mail.send(msg)
            flash('Your complaint has been submitted successfully!', 'success')
        except Exception as e:
            flash('Error submitting complaint. Please try again later.', 'error')
            print(f"Error sending email: {str(e)}")
    
    return redirect(url_for('student_dashboard'))

@app.route('/teacher-dashboard', methods=['GET', 'POST'])
@login_required
def teacher_dashboard():
    if not isinstance(current_user, TeacherDetails):
        flash('Access denied. Teachers only.', 'error')
        return redirect(url_for('login'))
    
    form = ClassPhotoForm()
    profile_form = TeacherProfileForm()
    today = datetime.now().date()
    
    # Get teacher's subjects and populate the form choices
    teacher_subjects = TeacherSubject.query.filter_by(Teacher_ID=current_user.Teacher_ID).all()
    form.subject.choices = [(f"{subject.Year}-{subject.Subject}", f"{subject.Year} Year: {subject.Subject}") for subject in teacher_subjects]
    
    # Get today's attendance for the current teacher
    today_attendance = ClassAttendance.query.filter_by(
        teacher_id=current_user.Teacher_ID,
        date=today
    ).all()

    return render_template('teacher_dashboard.html', 
                         form=form,
                         profile_form=profile_form,
                         today_date=today,
                         today_attendance=today_attendance)

@app.route('/update-teacher-profile', methods=['POST'])
@login_required
def update_teacher_profile():
    if not isinstance(current_user, TeacherDetails):
        flash('Access denied. Teachers only.', 'error')
        return redirect(url_for('login'))
    
    form = TeacherProfileForm()
    if form.validate_on_submit():
        try:
            # Verify current password
            if form.Current_Password.data != current_user.Password:
                flash('Current password is incorrect!', 'error')
                return redirect(url_for('teacher_dashboard'))

            # Update basic information
            current_user.Name = form.Name.data
            current_user.Email_id = form.Email_id.data
            current_user.Phone_Number = form.Phone_Number.data

            # Update password if new one is provided
            if form.New_Password.data:
                current_user.Password = form.New_Password.data

            # Handle photo upload
            if form.Photo.data:
                try:
                    response_image = cloudinary.uploader.upload(form.Photo.data)
                    current_user.Photo = response_image.get('secure_url', None)
                except Exception as e:
                    print(f"Error uploading photo: {str(e)}")

            db.session.commit()
            flash('Profile updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error updating profile. Please try again.', 'error')
            print(f"Error: {str(e)}")
    
    return redirect(url_for('teacher_dashboard'))

@app.route('/get-attendance-csv')
@login_required
def get_attendance_csv():
    today = datetime.now().date()

    # Get today's attendance
    attendance_records = ClassAttendance.query.filter_by(
        teacher_id=current_user.Teacher_ID,
        date=today
    ).all()

    # Create CSV data
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Student ID', 'Name', 'Status', 'Date'])

    for record in attendance_records:
        writer.writerow([
            record.student.Student_ID,
            record.student.Name,
            'Present' if record.is_present else 'Absent',
            record.date
        ])

    # Convert CSV to BytesIO for sending as file
    csv_data = BytesIO(output.getvalue().encode('utf-8'))
    csv_data.seek(0)

    # Create the response
    return send_file(
        csv_data,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'attendance_{today}.csv'
    )
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/Institute-dashboard')
@login_required
def Institute_dashboard():
    if not isinstance(current_user, InstituteDetails):
        flash('Access denied. Institute only.', 'error')
        return redirect(url_for('login'))
    
    teacher_form = TeacherEnrollmentForm()
    
    # Get all teachers in this institute
    teachers = TeacherDetails.query.filter_by(Institute_Name=current_user.Institute_Name).all()
    
    # Get all students in this institute
    students = StudentDetails.query.filter_by(Institute_Name=current_user.Institute_Name).all()
    
    # Calculate total teachers and students
    total_teachers = len(teachers)
    total_students = len(students)
    
    # Calculate average attendance (placeholder for now)
    average_attendance = 85
    
    # Debug print to check data
    print(f"Number of students found: {len(students)}")
    for student in students:
        print(f"Student: {student.Name}, ID: {student.Student_ID}")
    
    return render_template('Institute_dashboard.html', 
                         teacher_form=teacher_form,
                         teachers=teachers,
                         students=students,  # Make sure students is passed
                         total_teachers=total_teachers,
                         total_students=total_students,
                         average_attendance=average_attendance)

@app.route('/enroll-teacher', methods=['POST'])
@login_required
def enroll_teacher():
    if not isinstance(current_user, InstituteDetails):
        flash('Access denied. Institute only.', 'error')
        return redirect(url_for('login'))
    
    form = TeacherEnrollmentForm()
    if form.validate_on_submit():
        try:
            # Check if teacher ID already exists
            existing_teacher = TeacherDetails.query.filter_by(Teacher_ID=form.Teacher_ID.data).first()
            if existing_teacher:
                flash('Teacher ID already exists!', 'error')
                return redirect(url_for('Institute_dashboard'))
            
            # Create new teacher
            new_teacher = TeacherDetails(
                Teacher_ID=form.Teacher_ID.data,
                Name=form.Name.data,
                Email_id=form.Email_id.data,
                Password=form.Password.data,
                Institute_Name=current_user.Institute_Name,
                Institute_ID=current_user.Institute_ID,
                Phone_Number="Not Provided",
                Registration_Date=datetime.utcnow()
            )
            
            db.session.add(new_teacher)
            db.session.flush()  # Flush to get the teacher ID

            # Create subject records for each year-subject combination
            subjects = [
                (form.Year1.data, form.Subject1.data),
                (form.Year2.data, form.Subject2.data),
                (form.Year3.data, form.Subject3.data),
                (form.Year4.data, form.Subject4.data)
            ]

            for year, subject in subjects:
                teacher_subject = TeacherSubject(
                    Teacher_ID=new_teacher.Teacher_ID,
                    Year=year,
                    Subject=subject
                )
                db.session.add(teacher_subject)

            db.session.commit()

            # Send email to teacher with credentials
            try:
                msg = Message(
                    subject='Your Teacher Account Credentials',
                    sender=app.config['MAIL_USERNAME'],
                    recipients=[form.Email_id.data]
                )
                msg.body = f"""
                Dear {form.Name.data},

                Your account has been created successfully. Please update your details after logging in.

                Here are your login credentials:

                Teacher ID: {form.Teacher_ID.data}
                Password: {form.Password.data}

                Please login at: http://localhost:5000
                
                Thank You!

                Best regards,
                {current_user.Institute_Name} Administration
                """
                
                mail.send(msg)
                flash('Teacher enrolled successfully and credentials sent to their email!', 'success')
            except Exception as e:
                print(f"Error sending email: {str(e)}")
                flash('Teacher enrolled but failed to send email. Please contact the teacher with their credentials.', 'warning')
            
        except Exception as e:
            db.session.rollback()
            flash('Error enrolling teacher. Please try again.', 'error')
            print(f"Error: {str(e)}")
    else:
        # Form validation failed
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'error')
    
    return redirect(url_for('Institute_dashboard'))

@app.route('/upload-class-photo', methods=['POST'])
@login_required
def upload_class_photo():
    form = ClassPhotoForm()
    
    # Get teacher's subjects and populate the form choices
    teacher_subjects = TeacherSubject.query.filter_by(Teacher_ID=current_user.Teacher_ID).all()
    form.subject.choices = [(f"{subject.Year}-{subject.Subject}", f"{subject.Year} Year: {subject.Subject}") for subject in teacher_subjects]
    
    if form.validate_on_submit():
        if form.class_photo.data:
            try:
                # Upload photo to Cloudinary
                response = cloudinary.uploader.upload(form.class_photo.data)
                photo_url = response.get('secure_url')

                # Save class photo record
                class_photo = ClassPhoto(
                    teacher_id=current_user.Teacher_ID,
                    date=form.date.data,
                    photo_url=photo_url,
                    subject=form.subject.data
                )
                db.session.add(class_photo)
                
                # Get all students from the same institute
                students = StudentDetails.query.filter_by(Institute_Name=current_user.Institute_Name).all()
                
                # Create StudentTeacherMap entries for each student
                for student in students:
                    # Check if mapping already exists
                    existing_map = StudentTeacherMap.query.filter_by(
                        Student_ID=student.Student_ID,
                        Teacher_ID=current_user.Teacher_ID
                    ).first()
                    
                    if not existing_map:
                        # Create new mapping
                        student_teacher_map = StudentTeacherMap(
                            Student_ID=student.Student_ID,
                            Teacher_ID=current_user.Teacher_ID
                        )
                        db.session.add(student_teacher_map)
                
                db.session.commit()
                flash('Class photo uploaded successfully and student-teacher mappings created!', 'success')
            except Exception as e:
                db.session.rollback()
                flash('Error uploading photo. Please try again.', 'error')
                print(f"Error: {str(e)}")
    
    return redirect(url_for('teacher_dashboard'))

if __name__ == "__main__":
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
    app.run(debug=True)

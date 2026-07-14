from flask import Blueprint, render_template, request, session, flash, redirect
from datetime import date, timedelta, datetime
from datetime import date
from models.db import marks_collection
from models.diary_model import add_diary
from models.attendance_model import mark_attendance
from models.marks_model import add_marks
from models.quiz_model import create_quiz
from models.db import attendance_collection
from models.db import diary_collection
from datetime import datetime
from models.db import quiz_collection
from models.db import notice_collection

from models.db import students_collection, faculty_collection, users_collection, db

from utils.constants import get_subjects_by_class
from utils.auth import hash_password

faculty = Blueprint('faculty', __name__, template_folder='../templates')
def faculty_required():
    if session.get('role') != 'faculty':
        return False
    return True

# =========================
# ADD / UPDATE DAILY DIARY
# =========================
# =========================
# ADD / UPDATE DAILY DIARY
# =========================
@faculty.route('/faculty/add-diary', methods=['GET', 'POST'])
def add_diary():

    from datetime import date, timedelta, datetime
    from models.db import diary_collection, faculty_collection

    # =========================
    # FACULTY
    # =========================

    faculty_id = session.get('user_id')

    faculty_data = faculty_collection.find_one({
        "faculty_id": faculty_id
    })

    if not faculty_data:
        return "Faculty not found ❌"

    # FACULTY SUBJECT
    faculty_subject = faculty_data['subject'].strip().lower()

    # =========================
    # CLASS
    # =========================

    class_name = request.form.get('class_name')

    if not class_name:
        class_name = request.args.get('class_name', '10')

    # =========================
    # DATE
    # =========================

    today = request.form.get('diary_date')

    if not today:
        today = request.args.get('diary_date')

    if not today:
        today = str(date.today())

    # =========================
    # AUTO DELETE OLD DIARIES
    # =========================

    seven_days_ago = date.today() - timedelta(days=7)

    old_diaries = diary_collection.find()

    for d in old_diaries:

        try:

            diary_date = datetime.strptime(
                d['date'],
                "%Y-%m-%d"
            ).date()

            if diary_date < seven_days_ago:

                diary_collection.delete_one({
                    "_id": d['_id']
                })

        except:
            pass

    # =========================
    # SUBJECTS BY CLASS
    # =========================

    class_num = int(class_name)

    if class_num <= 4:

        subjects = [
            "Telugu",
            "Hindi",
            "English",
            "Maths",
            "EVS",
            "GK",
            "Computer"
        ]

    elif 5 <= class_num <= 7:

        subjects = [
            "Telugu",
            "Hindi",
            "English",
            "Maths",
            "Science",
            "Social"
        ]

    else:

        subjects = [
            "Telugu",
            "Hindi",
            "English",
            "Maths",
            "Natural Science",
            "Physical Science",
            "Social"
        ]

    # =========================
    # FIND DIARY
    # =========================

    diary = diary_collection.find_one({
        "class": class_name,
        "date": today
    })

    # =========================
    # CREATE EMPTY DIARY
    # =========================

    if not diary:

        homework_data = {}

        for sub in subjects:
            homework_data[sub] = ""

        new_diary = {
            "class": class_name,
            "date": today,
            "homework": homework_data
        }

        diary_collection.insert_one(new_diary)

        diary = diary_collection.find_one({
            "class": class_name,
            "date": today
        })

    # =========================
    # SAVE HOMEWORK
    # =========================

    if request.method == 'POST':

        content = request.form.get('content')

        if content is not None:

            diary_collection.update_one(
                {
                    "class": class_name,
                    "date": today
                },
                {
                    "$set": {
                        f"homework.{faculty_data['subject']}": content
                    }
                }
            )

        return redirect(
            f'/faculty/add-diary?class_name={class_name}&diary_date={today}'
        )

    # =========================
    # RENDER PAGE
    # =========================

    return render_template(
        'faculty/add_diary.html',
        diary=diary,
        faculty_subject=faculty_subject,
        class_name=class_name,
        today=today
    )

# =========================
# ATTENDANCE
# =========================
@faculty.route('/faculty/attendance', methods=['GET', 'POST'])
def attendance():

    from datetime import date

    faculty_id = session.get('user_id')

    faculty_data = faculty_collection.find_one({
        "faculty_id": faculty_id
    })

    if not faculty_data:
        return "Faculty not found ❌"

    # =========================
    # CLASS
    # =========================

    class_name = faculty_data['class']

    # =========================
    # STUDENTS
    # =========================

    students = list(

        students_collection.find({
            "class": class_name
        })

    )

    # =========================
    # TODAY DATE
    # =========================

    today = str(date.today())

    # =========================
    # SAVE ATTENDANCE
    # =========================

    if request.method == 'POST':

        attendance_date = request.form.get(
            'attendance_date'
        )

        for student in students:

            status = request.form.get(
                student['student_id']
            )

            # =========================
            # SAVE DATA
            # =========================

            attendance_collection.update_one(

                {
                    "student_id": student['student_id'],
                    "date": attendance_date
                },

                {
                    "$set": {

                        "student_name": student['name'],
                        "class": class_name,
                        "date": attendance_date,
                        "status": status
                    }

                },

                upsert=True
            )

        flash("Attendance Saved Successfully ✅")

        return redirect('/faculty/attendance')

    # =========================
    # RENDER PAGE
    # =========================

    return render_template(

        'faculty/attendance.html',

        students=students,
        class_name=class_name,
        today=today
    )
# =========================
# ADD MARKS
# =========================
@faculty.route('/faculty/add-marks', methods=['GET', 'POST'])
def add_marks_route():

    faculty_id = session.get('user_id')

    faculty_data = faculty_collection.find_one({
        "faculty_id": faculty_id
    })

    if not faculty_data:
        return "Faculty not found ❌"

    # =========================
    # FACULTY DETAILS
    # =========================

    faculty_subject = faculty_data['subject']
    faculty_role = faculty_data.get(
        'role',
        'subject_teacher'
    )

    # =========================
    # CLASS
    # =========================

    class_name = request.args.get(
        'class_name',
        '10'
    )

    students = list(
        students_collection.find({
            "class": class_name
        })
    )

    class_num = int(class_name)

    # =========================
    # SUBJECTS BY CLASS
    # =========================

    if class_num <= 4:

        all_subjects = [
            "Telugu",
            "Hindi",
            "English",
            "Maths",
            "EVS",
            "GK",
            "Computer"
        ]

    elif 5 <= class_num <= 7:

        all_subjects = [
            "Telugu",
            "Hindi",
            "English",
            "Maths",
            "Science",
            "Social"
        ]

    else:

        all_subjects = [
            "Telugu",
            "Hindi",
            "English",
            "Maths",
            "Natural Science",
            "Physical Science",
            "Social"
        ]

    # =========================
    # ROLE PERMISSIONS
    # =========================

    if faculty_role == "class_teacher":

        subjects = all_subjects

    else:

        subjects = [faculty_subject]

    # =========================
    # MARK LIMITS
    # =========================

    if class_num <= 5:

        fa_max = 25
        sa_max = 50

    else:

        fa_max = 35
        sa_max = 100

    # =========================
    # SAVE MARKS
    # =========================

    if request.method == 'POST':

        exam = request.form.get('exam')

        for student in students:

            student_id = student['student_id']

            for subject in subjects:

                mark = request.form.get(
                    f"{student_id}_{subject}"
                )

                if mark == "":
                    continue

                mark = int(mark)

                # =========================
                # VALIDATION
                # =========================

                # FA EXAMS
                if exam in ['FA1', 'FA2', 'FA3', 'FA4']:

                    if mark > fa_max:

                        return f"""
                        {subject} marks cannot exceed
                        {fa_max} for {exam} ❌
                        """

                # SA EXAMS
                if exam in ['SA1', 'SA2']:

                    if mark > sa_max:

                        return f"""
                        {subject} marks cannot exceed
                        {sa_max} for {exam} ❌
                        """

                # =========================
                # SAVE TO DATABASE
                # =========================

                marks_collection.update_one(

                    {
                        "student_id": student_id,
                        "subject": subject
                    },

                    {
                        "$set": {
                            "student_name": student['name'],
                            "class": class_name,
                            f"marks.{exam}": mark
                        }
                    },

                    upsert=True
                )

        return "Marks Saved Successfully ✅"

    # =========================
    # RENDER PAGE
    # =========================

    return render_template(

        'faculty/add_marks.html',

        students=students,
        subjects=subjects,
        class_name=class_name,
        faculty_role=faculty_role,
        faculty_subject=faculty_subject,
        fa_max=fa_max,
        sa_max=sa_max
    )

@faculty.route('/faculty/create-quiz', methods=['GET', 'POST'])
def create_quiz():

    if request.method == 'POST':

        quiz_title = request.form.get('quiz_title')
        quiz_date = request.form.get('quiz_date')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')

        questions = []

        total_questions = int(request.form.get('total_questions'))

        for i in range(total_questions):

            q = {
                "question": request.form.get(f'question_{i}'),
                "options": [
                    request.form.get(f'option1_{i}'),
                    request.form.get(f'option2_{i}'),
                    request.form.get(f'option3_{i}'),
                    request.form.get(f'option4_{i}')
                ],
                "answer": request.form.get(f'answer_{i}')
            }

            questions.append(q)

        faculty_id = session.get('user_id')

        faculty_data = faculty_collection.find_one({
            "faculty_id": faculty_id
        })

        quiz_data = {

            "quiz_title": request.form['quiz_title'],
            "quiz_date": request.form['quiz_date'],
            "start_time": request.form['start_time'],
            "end_time": request.form['end_time'],

            "class": faculty_data['class'],

            "questions": questions

        }

        quiz_collection.insert_one(quiz_data)

        flash("Quiz Created Successfully ✅")

        return redirect('/faculty/create-quiz')

    return render_template('faculty/create_quiz.html')



@faculty.route('/faculty')
def faculty_dashboard():

    # 🔒 Protect route
    if session.get('role') != 'faculty':
        return redirect('/login')

    return render_template('faculty/faculty_dashboard.html')

@faculty.route('/faculty/add-student', methods=['GET','POST'])
def add_student():

    from models.db import students_collection, users_collection
    from utils.auth import hash_password

    if request.method == 'POST':
        data = request.form
        existing = students_collection.find_one({
            "student_id": data['student_id']
        })

        if existing:
            flash("Student ID already exists ❌")
            return redirect('/faculty/add-student')

        student_data = {
            "admission_no": data['admission_no'],
            "student_id": data['student_id'],
            "roll_no": data['roll_no'],
            "name": data['name'],
            "class": data['class'],
            "section": data['section'],
            "joining_date": data['joining_date'],
            "dob": data['dob'],
            "gender": data['gender'],
            "father_name": data['father_name'],
            "mother_name": data['mother_name'],
            "father_phone": data['father_phone'],
            "mother_phone": data['mother_phone'],
            "address": data['address'],
            "caste": data['caste'],
            "aadhaar": data['aadhaar'],
            "blood_group": data['blood_group'],
            "previous_school": data['previous_school'],
            "emergency_contact": data['emergency_contact']
        }

        students_collection.insert_one(student_data)

        # 🔥 Create login for student
        users_collection.insert_one({
            "user_id": data['student_id'],
            "username": data['student_id'],
            "role": "student",
            "password": hash_password("student123"),
            "first_login": True
        })

        return redirect('/faculty/manage-students')

    return render_template('faculty/add_student.html')



@faculty.route('/faculty/manage-students')
def manage_students():

    from models.db import students_collection

    students = list(students_collection.find())

    return render_template(
        'faculty/manage_students.html',
        students=students
    )


from datetime import date

@faculty.route('/faculty/view-diary')
def view_diary():

    faculty_id = session.get('user_id')

    faculty_data = faculty_collection.find_one({
        "faculty_id": faculty_id
    })

    if not faculty_data:
        return "Faculty not found"

    class_name = faculty_data['class']

    # selected date from search
    selected_date = request.args.get('date')

    # if no date selected → use today date
    if not selected_date:
        selected_date = str(date.today())

    # get only selected date diary
    diaries = list(
        diary_collection.find({
            "class": class_name,
            "date": selected_date
        })
    )

    return render_template(
        'faculty/view_diary.html',
        diaries=diaries,
        selected_date=selected_date
    )

@faculty.route('/faculty/view-results')
def view_results():

    faculty_id = session.get('user_id')

    faculty_data = faculty_collection.find_one({
        "faculty_id": faculty_id
    })

    if not faculty_data:
        return "Faculty not found ❌"

    class_name = faculty_data['class']

    # GET STUDENTS OF FACULTY CLASS
    students = list(

        students_collection.find({
            "class": class_name
        })

    )

    selected_student = request.args.get("student_id")

    results = []

    if selected_student:

        results = list(

            marks_collection.find({
                "student_id": selected_student
            })

        )

    return render_template(

        'faculty/view_results.html',

        students=students,
        results=results,
        selected_student=selected_student
    )

from flask import render_template, session
from models.db import timetable_collection
from models.db import faculty_collection

@faculty.route('/faculty/timetable')
def faculty_timetable():

    # =========================
    # LOGGED FACULTY
    # =========================

    faculty_id = session.get('user_id')

    faculty_data = faculty_collection.find_one({

        "faculty_id": faculty_id

    })

    if not faculty_data:

        return "Faculty not found"

    faculty_name = faculty_data['name']

    # =========================
    # FETCH TIMETABLES
    # =========================

    timetable_data = list(
        timetable_collection.find()
    )

    faculty_schedule = []

    # =========================
    # LOOP TIMETABLE
    # =========================

    for t in timetable_data:

        day = t.get('day')

        class_name = t.get('class')

        periods = t.get('periods', {})

        # =========================
        # LOOP PERIODS
        # =========================

        for period_name, pdata in periods.items():

            if pdata.get('faculty') == faculty_name:

                faculty_schedule.append({

                    "day": day,

                    "period": period_name,

                    "class": class_name,

                    "subject": pdata.get('subject')

                })

    # =========================
    # SORT TIMETABLE
    # =========================

    period_order = {
        "P1":1,
        "P2":2,
        "P3":3,
        "P4":4,
        "P5":5,
        "P6":6,
        "P7":7,
        "P8":8
    }

    day_order = {
        "Monday":1,
        "Tuesday":2,
        "Wednesday":3,
        "Thursday":4,
        "Friday":5,
        "Saturday":6
    }

    faculty_schedule.sort(

        key=lambda x: (

            day_order.get(x['day'], 99),

            period_order.get(x['period'], 99)

        )

    )

    # =========================
    # RENDER
    # =========================

    return render_template(

        'faculty/timetable.html',

        faculty=faculty_data,

        faculty_schedule=faculty_schedule

    )

@faculty.route('/faculty/notices')
def faculty_notices():

    notices = list(
        notice_collection.find({
            "audience": {"$in": ["teachers", "both"]}
        }).sort("created_at", -1)
    )

    return render_template(
        "faculty/notices.html",
        notices=notices
    )
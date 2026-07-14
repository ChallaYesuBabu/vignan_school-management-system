from flask import Blueprint, render_template, session, request, redirect
from models.db import students_collection
from models.diary_model import get_diary_by_class_date
from datetime import date
from models.attendance_model import get_attendance
from models.marks_model import get_marks
from models.notice_model import get_notices
from models.quiz_model import get_quiz_by_class, save_result, has_attempted
from models.db import marks_collection
from models.db import attendance_collection
from models.db import quiz_result_collection
from models.db import quiz_collection
from bson.objectid import ObjectId
from models.db import notice_collection
student = Blueprint('student', __name__, template_folder='../templates')

@student.route('/student/today-diary')
def today_diary():

    if session.get('role') != 'student':
        return redirect('/login')

    from models.db import diary_collection
    from datetime import date, timedelta

    student_id = session.get('user_id')

    student_data = students_collection.find_one({
        "student_id": student_id
    })

    if not student_data:
        return "Student not found ❌"

    class_name = student_data['class']

    # =========================
    # SELECTED DATE
    # =========================

    selected_date = request.args.get('date')

    if not selected_date:
        selected_date = str(date.today())

    # =========================
    # GET DIARY
    # =========================

    diary = diary_collection.find_one({
        "class": class_name,
        "date": selected_date
    })

    # =========================
    # LAST 7 DAYS
    # =========================

    dates = []

    for i in range(7):

        d = date.today() - timedelta(days=i)

        dates.append(str(d))

    return render_template(
        'student/view_diary.html',
        diary=diary,
        class_name=class_name,
        selected_date=selected_date,
        dates=dates
    )


from collections import defaultdict
from datetime import datetime

@student.route('/student/attendance')
def student_attendance():

    # =========================
    # CHECK STUDENT LOGIN
    # =========================

    if session.get('role') != 'student':
        return redirect('/login')

    student_id = session.get('user_id')

    # =========================
    # GET ATTENDANCE DATA
    # =========================

    attendance_data = list(

        attendance_collection.find({

            "student_id": student_id

        }).sort("date", -1)

    )

    # =========================
    # TOTAL DAYS
    # =========================

    total_days = len(attendance_data)

    # =========================
    # PRESENT DAYS
    # =========================

    present_days = len([

        a for a in attendance_data

        if a['status'].lower() == "present"

    ])

    # =========================
    # ABSENT DAYS
    # =========================

    absent_days = len([

        a for a in attendance_data

        if a['status'].lower() == "absent"

    ])

    # =========================
    # OVERALL PERCENTAGE
    # =========================

    if total_days > 0:

        overall_percentage = round(

            (present_days / total_days) * 100,
            2

        )

    else:

        overall_percentage = 0

    # =========================
    # MONTHLY SUMMARY
    # =========================

    monthly_data = defaultdict(lambda: {

        "present": 0,
        "absent": 0

    })

    for a in attendance_data:

        date_value = str(a.get('date'))

        month = date_value[:7]

        if a['status'].lower() == "present":

            monthly_data[month]['present'] += 1

        else:

            monthly_data[month]['absent'] += 1

    monthly_summary = []

    for month, data in monthly_data.items():

        total = data['present'] + data['absent']

        if total > 0:

            monthly_percentage = round(

                (data['present'] / total) * 100,
                2

            )

        else:

            monthly_percentage = 0

        monthly_summary.append({

            "month": month,

            "present": data['present'],

            "absent": data['absent'],

            "percentage": monthly_percentage

        })

    # =========================
    # SORT MONTHS DESCENDING
    # =========================

    monthly_summary = sorted(

        monthly_summary,

        key=lambda x: x['month'],

        reverse=True

    )

    # =========================
    # CURRENT MONTH %
    # =========================

    current_month = datetime.now().strftime("%Y-%m")

    current_month_data = next(

        (

            m for m in monthly_summary

            if m['month'] == current_month

        ),

        None

    )

    if current_month_data:

        current_month_percentage = current_month_data['percentage']

    else:

        current_month_percentage = 0

    # =========================
    # RENDER TEMPLATE
    # =========================

    return render_template(

        'student/attendance.html',

        overall_percentage=overall_percentage,

        current_month_percentage=current_month_percentage,

        total_present=present_days,

        total_absent=absent_days,

        monthly_summary=monthly_summary

    )


@student.route('/student/view-marks')
def view_marks():

    if session.get('role') != 'student':
        return redirect('/login')

    student_id = session.get('user_id')

    # =========================
    # STUDENT DATA
    # =========================

    student_data = students_collection.find_one({
        "student_id": student_id
    })

    if not student_data:
        return "Student not found ❌"

    # =========================
    # MARKS
    # =========================

    marks_data = list(

        marks_collection.find({
            "student_id": student_id
        })

    )

    # =========================
    # RENDER
    # =========================

    return render_template(

        'student/view_marks.html',

        marks_data=marks_data,

        student_class=student_data['class']
    )


@student.route('/student/notices')
def student_notices():

    notices = list(
        notice_collection.find({
            "audience": {"$in": ["students", "both"]}
        }).sort("created_at", -1)
    )

    return render_template(
        "student/notices.html",
        notices=notices
    )

from datetime import datetime

@student.route('/student/quiz')
def student_quiz():

    student_id = session.get('user_id')

    student_data = students_collection.find_one({
        "student_id": student_id
    })

    if not student_data:
        return "Student not found"

    class_name = student_data['class']

    quizzes = list(
        quiz_collection.find({
            "class": class_name
        })
    )

    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M")

    return render_template(
        'student/quiz_list.html',
        quizzes=quizzes,
        current_date=current_date,
        current_time=current_time
    )


@student.route('/student/attempt-quiz/<quiz_id>', methods=['GET', 'POST'])
def attempt_quiz(quiz_id):

    student_id = session.get('user_id')

    student_data = students_collection.find_one({
        "student_id": student_id
    })

    if not student_data:
        return "Student not found"

    quiz = quiz_collection.find_one({
        "_id": ObjectId(quiz_id)
    })

    if not quiz:
        return "Quiz not found"

    # Check already attempted

    existing = quiz_result_collection.find_one({
        "student_id": student_id,
        "quiz_id": quiz_id
    })

    if existing:
        return "You already attempted this quiz ❌"

    # Check quiz timing

    current_datetime = datetime.now()

    quiz_start = datetime.strptime(
        quiz['quiz_date'] + " " + quiz['start_time'],
        "%Y-%m-%d %H:%M"
    )

    quiz_end = datetime.strptime(
        quiz['quiz_date'] + " " + quiz['end_time'],
        "%Y-%m-%d %H:%M"
    )

    if current_datetime < quiz_start:
        return "Quiz has not started yet ⏰"

    if current_datetime > quiz_end:
        return "Quiz time is over ❌"

    # Submit quiz

    if request.method == 'POST':

        score = 0

        for i, q in enumerate(quiz['questions']):

            selected = request.form.get(f"q{i}")

            if selected == q['answer']:
                score += 1

        result_data = {

            "student_id": student_id,
            "quiz_id": quiz_id,
            "score": score,
            "total": len(quiz['questions']),
            "submitted_at": datetime.now()

        }

        quiz_result_collection.insert_one(result_data)

        return render_template(
            'student/quiz_result.html',
            score=score,
            total=len(quiz['questions'])
        )

    return render_template(
        'student/quiz.html',
        quiz=quiz
    )

# =========================
# STUDENT DASHBOARD
# =========================
@student.route('/student')
def student_dashboard():

    # 🔒 Protect route
    if session.get('role') != 'student':
        return redirect('/login')

    student_id = session.get('user_id')

    student_data = students_collection.find_one({
        "student_id": student_id
    })

    if not student_data:
        return "Student not found ❌"

    return render_template(
        'student/student_dashboard.html',
        student=student_data
    )
# =========================
# STUDENT PROFILE
# =========================
@student.route('/student/profile')
def student_profile():

    if session.get('role') != 'student':
        return redirect('/login')

    student_id = session.get('user_id')

    student_data = students_collection.find_one({
        "student_id": student_id
    })

    return render_template(
        'student/profile.html',
        student=student_data
    )
@student.route('/student/leaderboard')
def leaderboard():

    all_marks = list(marks_collection.find())

    leaderboard_dict = {}

    # =========================
    # CALCULATE TOTALS
    # =========================

    for mark_doc in all_marks:

        student_id = mark_doc['student_id']

        if student_id not in leaderboard_dict:

            leaderboard_dict[student_id] = {

                "student_name": mark_doc['student_name'],
                "class": mark_doc['class'],
                "total_marks": 0,
                "max_marks": 0

            }

        marks = mark_doc.get("marks", {})

        student_class = int(mark_doc['class'])

        # =========================
        # MAX MARKS
        # =========================

        if student_class <= 5:

            fa_max = 25
            sa_max = 50

        else:

            fa_max = 35
            sa_max = 100

        # =========================
        # ADD MARKS
        # =========================

        for exam, value in marks.items():

            leaderboard_dict[student_id]["total_marks"] += value

            if exam.startswith("FA"):

                leaderboard_dict[student_id]["max_marks"] += fa_max

            elif exam.startswith("SA"):

                leaderboard_dict[student_id]["max_marks"] += sa_max

    # =========================
    # FINAL LIST
    # =========================

    leaderboard = []

    for student_id, data in leaderboard_dict.items():

        if data["max_marks"] > 0:

            percentage = (
                data["total_marks"] /
                data["max_marks"]
            ) * 100

        else:

            percentage = 0

        leaderboard.append({

            "student_name": data["student_name"],
            "class": data["class"],
            "total_marks": data["total_marks"],
            "percentage": round(percentage, 2)

        })

    # =========================
    # SORT
    # =========================

    leaderboard.sort(
        key=lambda x: x['percentage'],
        reverse=True
    )

    # =========================
    # RENDER
    # =========================

    return render_template(

        'student/leaderboard.html',

        leaderboard=leaderboard

    )

from models.db import timetable_collection
from flask import render_template, session

@student.route('/student/timetable')
def student_timetable():

    # =========================
    # LOGGED STUDENT
    # =========================

    student_id = session.get('user_id')

    student_data = students_collection.find_one({

        "student_id": student_id

    })

    if not student_data:

        return redirect('/login')

    student_class = str(
        student_data['class']
    )

    # =========================
    # SECTION
    # =========================

    if student_class in [

        'PreKG',
        'LKG',
        'UKG',
        '1',
        '2',
        '3',
        '4'

    ]:

        section = "Lower Section"

    else:

        section = "Higher Section"

    # =========================
    # FETCH TIMETABLE
    # =========================

    timetable = list(

        timetable_collection.find({

            "class": student_class

        })

    )

    # =========================
    # DAY SORTING
    # =========================

    day_order = {

        "Monday": 1,
        "Tuesday": 2,
        "Wednesday": 3,
        "Thursday": 4,
        "Friday": 5,
        "Saturday": 6

    }

    timetable.sort(

        key=lambda x:

        day_order.get(
            x.get('day'),
            99
        )

    )

    # =========================
    # RENDER
    # =========================

    return render_template(

        'student/timetable.html',

        student=student_data,

        student_class=student_class,

        section=section,

        timetable=timetable

    )

@student.route('/student/quiz-result')
def quiz_result():

    student_id = session.get('user_id')

    results = list(

        quiz_result_collection.find({

            "student_id": student_id

        })

    )

    for r in results:

        quiz = quiz_collection.find_one({

            "_id": ObjectId(r['quiz_id'])

        })

        if quiz:

            r['quiz_title'] = quiz['quiz_title']

        else:

            r['quiz_title'] = "Quiz"

    return render_template(

        'student/quiz_result.html',

        results=results

    )
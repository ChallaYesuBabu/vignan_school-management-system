from flask import Blueprint, render_template, request, redirect, flash
from models.student_model import create_student
from models.db import users_collection
from utils.auth import hash_password
from utils.validators import is_valid_aadhaar
from models.notice_model import add_notice
from models.db import students_collection
from models.db import faculty_collection,db
from flask import session
from bson.objectid import ObjectId
from models.db import password_request_collection

admin = Blueprint('admin', __name__, template_folder='../templates')
# =========================
# ADMIN DASHBOARD
# =========================
@admin.route('/admin')
def admin_dashboard():
    return render_template('admin/admin_dashboard.html')
# =========================
# CREATE STUDENT
# =========================
@admin.route('/admin/create-student', methods=['GET', 'POST'])
def add_student():

    if request.method == 'POST':
        data = request.form   # ✅ define here

        if not is_valid_aadhaar(data['aadhaar']):
            flash("Invalid Aadhaar")
            return redirect('/admin/create-student')

        student_data = {   # ✅ MOVE INSIDE FUNCTION
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

        create_student(student_data)

        users_collection.insert_one({
            "user_id": data['student_id'],
            "username": data['student_id'],
            "role":"student",
            "password": hash_password("student123"),
            "first_login": True
            
        })

        flash("Student Created Successfully")

    return render_template('admin/create_student.html')


@admin.route('/admin/add-notice', methods=['GET', 'POST'])
def add_notice_route():

    if request.method == 'POST':
        data = request.form

        notice_data = {
            "title": data['title'],
            "content": data['content']
        }

        add_notice(notice_data)

        return "Notice Added Successfully ✅"

    return render_template('admin/add_notice.html')
# =========================
# CREATE FACULTY
# ========================
# =========================
# CREATE FACULTY
# =========================
@admin.route('/admin/create-faculty', methods=['GET', 'POST'])
def create_faculty():

    if session.get('role') != 'admin':
        return redirect('/login')

    from utils.auth import hash_password
    from models.db import (
        faculty_collection,
        users_collection
    )

    if request.method == 'POST':

        data = request.form

        # =========================
        # CHECK EXISTING FACULTY
        # =========================

        existing = faculty_collection.find_one({
            "faculty_id": data['faculty_id']
        })

        if existing:
            return "Faculty ID already exists ❌"

        # =========================
        # FACULTY DATA
        # =========================

        faculty_data = {

            "faculty_id": data['faculty_id'],

            "name": data['name'],

            "subject": data['subject'],

            "class": data['class'],

            "role": data['role'],

            "phone": data['phone']
        }

        # SAVE FACULTY
        faculty_collection.insert_one(
            faculty_data
        )

        # =========================
        # CREATE LOGIN
        # =========================

        users_collection.insert_one({

            "user_id": data['faculty_id'],

            "username": data['faculty_id'],

            "password": hash_password("faculty123"),

            "role": "faculty",

            "first_login": True
        })

        return redirect('/admin/manage-faculty')

    return render_template(
        'admin/create_faculty.html'
    )

#manage-student

@admin.route('/admin/manage-students')
def manage_students():

    students = list(students_collection.find())

    return render_template('admin/manage_students.html', students=students)

#manage-faculty

@admin.route('/admin/manage-faculty')
def manage_faculty():

    faculty = list(faculty_collection.find())

    return render_template('admin/manage_faculty.html', faculty=faculty)

#assing class teacher

@admin.route('/admin/assign-class-teacher', methods=['GET', 'POST'])
def assign_class_teacher():

    if request.method == 'POST':
        class_name = request.form['class']
        faculty_id = request.form['faculty_id']

        db['class_teacher'].update_one(
            {"class": class_name},
            {"$set": {"faculty_id": faculty_id}},
            upsert=True
        )

    data = list(db['class_teacher'].find())
    faculty = list(faculty_collection.find())

    return render_template(
        'admin/assign_class_teacher.html',
        data=data,
        faculty=faculty
    )

@admin.route('/admin/edit-student/<id>', methods=['GET', 'POST'])
def edit_student(id):

    student = students_collection.find_one({
        "_id": ObjectId(id)
    })

    if request.method == 'POST':

        students_collection.update_one(
            {"_id": ObjectId(id)},
            {
                "$set": {
                    "name": request.form['name'],
                    "class": request.form['class'],
                    "father_name": request.form['father_name'],
                    "phone": request.form['phone']
                }
            }
        )

        flash("Student Updated Successfully ✅")

        return redirect('/admin/manage-students')

    return render_template(
        'admin/edit_student.html',
        student=student
    )

@admin.route('/admin/delete-student/<id>')
def delete_student(id):

    students_collection.delete_one({
        "_id": ObjectId(id)
    })

    flash("Student Deleted Successfully ❌")

    return redirect('/admin/manage-students')

from bson.objectid import ObjectId

# ==============================
# EDIT FACULTY
# ==============================

@admin.route('/admin/edit-faculty/<id>', methods=['GET', 'POST'])
def edit_faculty(id):

    faculty = faculty_collection.find_one({
        "_id": ObjectId(id)
    })

    if request.method == 'POST':

        updated_data = {

            "faculty_id": request.form.get('faculty_id'),
            "name": request.form.get('name'),
            "subject": request.form.get('subject'),
            "class": request.form.get('class'),
            "phone": request.form.get('phone')

        }

        faculty_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": updated_data}
        )

        return redirect('/admin/manage-faculty')

    return render_template(
        'admin/edit_faculty.html',
        faculty=faculty
    )

from models.db import timetable_collection
from models.db import faculty_collection

@admin.route('/admin/add-timetable', methods=['GET', 'POST'])
def add_timetable():

    # =========================
    # CLASSES
    # =========================

    lower_classes = [
        'PreKG',
        'LKG',
        'UKG',
        '1',
        '2',
        '3',
        '4'
    ]

    higher_classes = [
        '5',
        '6',
        '7',
        '8',
        '9',
        '10'
    ]

    # =========================
    # SAVE / UPDATE TIMETABLE
    # =========================

    if request.method == 'POST':

        section = request.form.get('section')
        day = request.form.get('day')

        # Select classes based on section
        if section == "lower":

            class_list = lower_classes

        else:

            class_list = higher_classes

        # =========================
        # LOOP CLASSES
        # =========================

        for c in class_list:

            periods = {}

            # =========================
            # LOOP PERIODS
            # =========================

            for i in range(1, 9):

                subject = request.form.get(
                    f'{section}_{c}_subject_{i}'
                )

                faculty = request.form.get(
                    f'{section}_{c}_faculty_{i}'
                )

                periods[f'P{i}'] = {

                    "subject": subject,
                    "faculty": faculty

                }

            # =========================
            # CLEAN DATA STRUCTURE
            # =========================

            timetable_data = {

                "section": section,
                "class": c,
                "day": day,
                "periods": periods

            }

            # =========================
            # CHECK EXISTING
            # =========================

            existing = timetable_collection.find_one({

                "class": c,
                "day": day

            })

            # =========================
            # UPDATE
            # =========================

            if existing:

                timetable_collection.update_one(

                    {
                        "_id": existing["_id"]
                    },

                    {
                        "$set": timetable_data
                    }

                )

            # =========================
            # INSERT
            # =========================

            else:

                timetable_collection.insert_one(
                    timetable_data
                )

        flash("Timetable Saved Successfully ✅")

    # =========================
    # FACULTIES
    # =========================

    faculties = list(
        faculty_collection.find()
    )

    # =========================
    # SAVED CHECK
    # =========================

    saved = timetable_collection.count_documents({}) > 0

    return render_template(

        'admin/add_timetable.html',

        faculties=faculties,

        saved=saved,

        lower_classes=lower_classes,

        higher_classes=higher_classes

    )


# ===========================================
# PASSWORD RESET REQUESTS
# ===========================================

@admin.route('/admin/password-requests')
def password_requests():

    if session.get("role") != "admin":
        return redirect("/admin-login")

    requests = list(
        password_request_collection.find().sort("_id", -1)
    )

    return render_template(

        "admin/password_requests.html",

        requests=requests

    )

# ===========================================
# APPROVE PASSWORD REQUEST
# ===========================================

from bson import ObjectId
from flask import flash, redirect, session
from utils.auth import hash_password

@admin.route('/admin/approve-password/<request_id>')
def approve_password(request_id):

    if session.get("role") != "admin":
        return redirect("/admin-login")

    request_data = password_request_collection.find_one({
        "_id": ObjectId(request_id)
    })

    if not request_data:
        flash("Request not found")
        return redirect("/admin/password-requests")

    user_id = request_data["user_id"]
    role = request_data["role"]

    # Default passwords (hashed)
    student_password = hash_password("student123")
    faculty_password = hash_password("faculty123")

    # ==========================
    # STUDENT
    # ==========================

    if role == "student":

        students_collection.update_one(
            {
                "student_id": user_id
            },
            {
                "$set": {
                    "password": student_password,
                    "first_login": True
                }
            }
        )

        users_collection.update_one(
            {
                "user_id": user_id
            },
            {
                "$set": {
                    "password": student_password,
                    "first_login": True
                }
            }
        )

    # ==========================
    # FACULTY
    # ==========================

    elif role == "faculty":

        faculty_collection.update_one(
            {
                "faculty_id": user_id
            },
            {
                "$set": {
                    "password": faculty_password,
                    "first_login": True
                }
            }
        )

        users_collection.update_one(
            {
                "user_id": user_id
            },
            {
                "$set": {
                    "password": faculty_password,
                    "first_login": True
                }
            }
        )

    # Remove the request after approval
    password_request_collection.delete_one({
        "_id": ObjectId(request_id)
    })

    flash("Password reset successfully.")

    return redirect("/admin/password-requests")

# ===========================================
# REJECT PASSWORD REQUEST
# ===========================================

@admin.route('/admin/reject-password/<request_id>')
def reject_password(request_id):

    if session.get("role") != "admin":
        return redirect("/admin-login")

    password_request_collection.update_one(

        {

            "_id": ObjectId(request_id)

        },

        {

            "$set": {

                "status": "Rejected"

            }

        }

    )

    flash("Request rejected.")

    return redirect("/admin/password-requests")
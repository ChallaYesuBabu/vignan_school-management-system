from flask import Blueprint, render_template, request, redirect, session, flash
from models.db import users_collection
from utils.auth import verify_password, hash_password
from models.db import password_request_collection
from models.db import students_collection
from models.db import faculty_collection,gallery_collection
from config import Config

auth = Blueprint('auth', __name__, template_folder='../templates')


@auth.route('/login', methods=['GET', 'POST'])
def login():

    # 🔥 ADD THIS CHECK
    if session.get('role'):
        if session['role'] == 'admin':
            return redirect('/admin')
        elif session['role'] == 'faculty':
            return redirect('/faculty')
        elif session['role'] == 'student':
            return redirect('/student')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form.get('role')

        user = users_collection.find_one({
            "username": username,
            "role": role
        })

        if user and verify_password(password, user['password']):
            session['user_id'] = user['user_id']
            session['role'] = role

            if user.get('first_login', True):
                return redirect('/change-password')

            if role == "admin":
                return redirect('/admin')
            elif role == "faculty":
                return redirect('/faculty')
            elif role == "student":
                return redirect('/student')

        return "Invalid Login ❌"

    return render_template('login.html')

@auth.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users_collection.find_one({
            "username": username,
            "role": "admin"
        })
        print(user)
        print(verify_password(password, user["password"]) if user else "No user")
        if user and verify_password(password, user['password']):
            session['user_id'] = user['user_id']
            session['role'] = "admin"
            return redirect('/admin')

        return "Invalid Admin Login ❌"

    return render_template('admin_login.html')

@auth.route('/admin-forgot-password', methods=['GET', 'POST'])
def admin_forgot_password():

    if request.method == "POST":

        username = request.form["username"].strip()
        secret_code = request.form["secret_code"].strip()
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        # Password match
        if new_password != confirm_password:
            flash("Passwords do not match ❌")
            return redirect("/admin-forgot-password")

        # Secret code verification
        if secret_code != Config.ADMIN_RESET_CODE:
            flash("Invalid Secret Admin Reset Code ❌")
            return redirect("/admin-forgot-password")

        # Find admin
        admin = users_collection.find_one({
            "username": username,
            "role": "admin"
        })

        if not admin:
            flash("Admin username not found ❌")
            return redirect("/admin-forgot-password")

        # Update password
        users_collection.update_one(
            {"_id": admin["_id"]},
            {
                "$set": {
                    "password": hash_password(new_password),
                    "first_login": False
                }
            }
        )

        flash("Password changed successfully. Please login.")
        return redirect("/admin-login")

    return render_template("admin_forgot_password.html")
# =========================
# CHANGE PASSWORD
# =========================
@auth.route('/change-password', methods=['GET', 'POST'])
def change_password():

    user_id = session.get('user_id')
    role = session.get('role')

    if not user_id:
        return redirect('/login')

    if request.method == 'POST':

        new_password = request.form['new_password']
        hashed_password = hash_password(new_password)

        # Update users collection
        users_collection.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "password": hashed_password,
                    "first_login": False
                }
            }
        )

        # Update student collection
        if role == "student":

            students_collection.update_one(
                {"student_id": user_id},
                {
                    "$set": {
                        "password": hashed_password,
                        "first_login": False
                    }
                }
            )

        # Update faculty collection
        elif role == "faculty":

            faculty_collection.update_one(
                {"faculty_id": user_id},
                {
                    "$set": {
                        "password": hashed_password,
                        "first_login": False
                    }
                }
            )

        flash("Password changed successfully. Please login again.")

        session.clear()

        return redirect('/login')

    return render_template("change_password.html")

# ==========================================
# FORGOT PASSWORD
# ==========================================

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():

    if request.method == 'POST':

        role = request.form.get('role')
        user_id = request.form.get('user_id').strip()

        # -----------------------
        # STUDENT
        # -----------------------

        if role == "student":

            user = students_collection.find_one({
                "student_id": user_id
            })

            if not user:

                flash("Student ID not found ❌")
                return redirect('/forgot-password?role=student')

            existing = password_request_collection.find_one({

                "user_id": user_id,
                "status": "Pending"

            })

            if existing:

                flash("Password reset request already sent.")
                return redirect('/forgot-password?role=student')

            password_request_collection.insert_one({

                "user_id": user_id,
                "name": user["name"],
                "role": "student",
                "status": "Pending"

            })

            flash("Request sent successfully. Wait for Admin approval ✅")

            return redirect('/login')

        # -----------------------
        # FACULTY
        # -----------------------

        elif role == "faculty":

            user = faculty_collection.find_one({
                "faculty_id": user_id
            })

            if not user:

                flash("Faculty ID not found ❌")
                return redirect('/forgot-password?role=faculty')

            existing = password_request_collection.find_one({

                "user_id": user_id,
                "status": "Pending"

            })

            if existing:

                flash("Password reset request already sent.")
                return redirect('/forgot-password?role=faculty')

            password_request_collection.insert_one({

                "user_id": user_id,
                "name": user["name"],
                "role": "faculty",
                "status": "Pending"

            })

            flash("Request sent successfully. Wait for Admin approval ✅")

            return redirect('/login')

    role = request.args.get("role")

    return render_template(

        "forgot_password.html",

        role=role

    )
@auth.route('/gallery')
def public_gallery():

    photos = list(gallery_collection.find())

    return render_template(
        'gallery.html',
        photos=photos
    )

# =========================
# LOGOUT
# =========================
@auth.route('/logout')
def logout():
    session.clear()
    return redirect('/login')
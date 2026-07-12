from flask import Flask
from config import Config
from routes.auth_routes import auth
from routes.admin_routes import admin
from routes.faculty_routes import faculty
from routes.student_routes import student
from flask import redirect

app = Flask(__name__)
app.config.from_object(Config)

# REGISTER ALL BLUEPRINTS FIRST ✅
app.register_blueprint(auth)
app.register_blueprint(admin)
app.register_blueprint(faculty)
app.register_blueprint(student)

# =========================
# HOME ROUTE
# =========================
from flask import redirect

@app.route('/')
def home():
    return redirect('/login')

# =========================
# TEST ROUTE
# =========================
@app.route('/test')
def test():
    return {"status": "Working"}


# =========================
# RUN APP
# =========================
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)


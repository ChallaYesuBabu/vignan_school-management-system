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

@app.route("/sitemap.xml")
def sitemap():
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">

    <url>
        <loc>https://vignan-school-management-system.onrender.com/</loc>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>

    <url>
        <loc>https://vignan-school-management-system.onrender.com/login</loc>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>

    <url>
        <loc>https://vignan-school-management-system.onrender.com/gallery</loc>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>

</urlset>
"""
    return Response(xml, mimetype="application/xml")

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


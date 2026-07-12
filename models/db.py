from pymongo import MongoClient
from config import Config

client = MongoClient(Config.MONGO_URI)

db = client["school_db"]

# Collections
students_collection = db["students"]
faculty_collection = db["faculty"]
diary_collection = db["diary"]
attendance_collection = db["attendance"]
marks_collection = db["marks"]
quiz_collection = db["quiz"]
notice_collection = db["notice"]
users_collection = db["users"]
result_collection = db["results"]
quiz_result_collection = db['quiz_results']
timetable_collection = db['timetable']
password_request_collection = db["password_requests"]
from models.db import db

def get_assigned_class(faculty_id):
    data = db['class_teacher'].find_one({"faculty_id": faculty_id})
    return data['class'] if data else None
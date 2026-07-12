from models.db import students_collection

def create_student(data):
    return students_collection.insert_one(data)
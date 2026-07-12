from models.db import marks_collection

def add_marks(data):
    marks_collection.update_one(
        {
            "student_id": data['student_id'],
            "subject": data['subject']
        },
        {"$set": data},
        upsert=True
    )

def get_marks(student_id):
    return list(marks_collection.find({"student_id": student_id}))
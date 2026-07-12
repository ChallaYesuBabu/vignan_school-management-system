from models.db import attendance_collection

# Add / Update attendance for a student on a date
def mark_attendance(data):
    attendance_collection.update_one(
        {
            "student_id": data['student_id'],
            "date": data['date']
        },
        {"$set": data},
        upsert=True   # prevents duplicate
    )


# Get attendance of a student
def get_attendance(student_id):
    return list(attendance_collection.find({"student_id": student_id}))
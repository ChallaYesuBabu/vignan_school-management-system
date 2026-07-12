from models.db import quiz_collection, result_collection

# Create quiz
def create_quiz(data):
    quiz_collection.insert_one(data)

# Get quiz by class
def get_quiz_by_class(class_name):
    return quiz_collection.find_one({"class": class_name})

# Save result
def save_result(data):
    result_collection.insert_one(data)

# Check if already attempted
def has_attempted(student_id, quiz_id):
    return result_collection.find_one({
        "student_id": student_id,
        "quiz_id": quiz_id
    })
from models.db import diary_collection

def add_diary(data):
    existing = diary_collection.find_one({
        "class": data['class'],
        "date": data['date'],
        "subject": data['subject']
    })

    if existing:
        return False

    diary_collection.insert_one(data)
    return True


# ✅ ADD THIS FUNCTION (missing one)
def get_diary_by_class_date(class_name, date):
    return list(diary_collection.find({
        "class": class_name,
        "date": date
    }))
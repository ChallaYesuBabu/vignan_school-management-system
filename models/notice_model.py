from models.db import notice_collection
from datetime import datetime

def add_notice(data):
    data['created_at'] = datetime.now()
    notice_collection.insert_one(data)

def get_notices():
    return list(notice_collection.find().sort("created_at", -1))
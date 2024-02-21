from main import db
from main import PhoneNumbers
from main import app

with app.app_context():
    db.create_all()
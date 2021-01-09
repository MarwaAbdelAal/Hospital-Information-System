from datetime import datetime
from his import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(doctor_id):
    return Doctor.query.get(int(doctor_id))

class Doctor(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    mobile_number = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(6), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    patients = db.relationship('Patient', backref='author', lazy=True)

    def __repr__(self):
        return f"Doctor('{self.username}', '{self.email}', '{self.image_file}', '{self.mobile_number}', '{self.gender}', '{self.age}')"

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    mobile_number = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)

    def __repr__(self):
        return f"Patient('{self.username}', '{self.email}', '{self.image_file}', '{self.mobile_number}', '{self.gender}', '{self.age}')"


class ContactUs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mobile_number = db.Column(db.Integer, nullable=False)
    subject = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"Message('{self.name}', '{self.email}', '{self.mobile_number}', '{self.subject}', '{self.message}')"

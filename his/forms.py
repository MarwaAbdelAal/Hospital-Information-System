from datetime import datetime, date, time
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, MultipleFileField, DateTimeField
from wtforms.fields.core import SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from his.models import User, Appointment

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password',validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(), EqualTo('password')])
    mobile_number = StringField('Mobile Number', validators=[DataRequired(), Length(11)])
    national_id = StringField('National ID Number', validators=[DataRequired(), Length(14)])
    gender = StringField('Gender', validators=[DataRequired()])
    age = StringField('Age', validators=[DataRequired()])
    salary = StringField('Salary', validators=[DataRequired()])
    picture = FileField('Choose Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    scans = MultipleFileField('Upload your scans', validators=[FileAllowed(['jpg', 'png', 'jpeg'])]) ## move to UpdateAccount
    medical_history = TextAreaField('Medical History', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        doctor = User.query.filter_by(username=username.data).first()
        if doctor:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        doctor = User.query.filter_by(email=email.data).first()
        if doctor:
            raise ValidationError('That email is taken. Please choose a different one.')

    def validate_national_id(self, national_id):
        doctor = User.query.filter_by(national_id=national_id.data).first()
        if doctor:
            raise ValidationError('That national ID is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password',validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class AppointmentForm(FlaskForm):
    # available doctor appointments
    # def __init__(self, formdata, **kwargs):
    #     super().__init__(formdata=formdata, **kwargs)
    #     self.
    available_drs = [(doc.id, doc.username) for doc in User.query.filter_by(role='doctor')]
    available_dates = [(i, f'{i:2d}:00') for i in range(9, 18)]
 
    doctor_id = SelectField('Doctor', choices=available_drs, validators=[DataRequired()])
    hour = SelectField('Time', choices=available_dates, validators=[DataRequired()])
    submit = SubmitField('Reserve')

    def validate_hour(self, hour):
        # check if dr is available at that time
        appointment_time = datetime.combine(date.today(), time(int(hour.data)))
        # query appointment for any for the current doctor
        reserved = Appointment.query.filter_by(doctor_id=int(self.doctor_id.data), datetime=appointment_time).first()
        if reserved:
            dr = User.query.get(int(self.doctor_id.data))
            raise ValidationError(f'Dr {dr.username} is not available at that time. Please choose a different one.')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    mobile_number = StringField('Mobile Number', validators=[DataRequired(), Length(11)])
    gender = StringField('Gender', validators=[DataRequired()])
    age = StringField('Age', validators=[DataRequired()])
    national_id = StringField('National ID Number', validators=[DataRequired(), Length(14)])
    scans = MultipleFileField('Upload your scans', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    medical_history = TextAreaField('Medical History', validators=[DataRequired()])
    salary = StringField('Salary', validators=[DataRequired()])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')
    
    def validate_national_id(self, national_id):
        if national_id.data != current_user.national_id:
            user = User.query.filter_by(national_id=national_id.data).first()
            if user:
                raise ValidationError('That national ID is taken. Please choose a different one.')

class ContactUsForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    mobile_number = StringField('Mobile Number', validators=[DataRequired(), Length(11)])
    subject = StringField('Subject', validators=[DataRequired()])
    message = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Send Message')

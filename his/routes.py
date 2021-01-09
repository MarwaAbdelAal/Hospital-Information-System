import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from his import app, db, bcrypt
from his.forms import RegistrationForm, LoginForm, ContactUsForm, UpdateAccountForm, PatientForm
from his.models import Doctor, Patient, ContactUs
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/doctors")
def doctors():
    doctors = Doctor.query.all()
    return render_template('doctors.html', doctors=doctors)

@app.route("/patients")
@login_required
def patients():
    patients = Patient.query.all()
    return render_template('patients.html', patients=patients)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        doctor = Doctor(username=form.username.data, email=form.email.data, password=hashed_password, mobile_number=form.mobile_number.data, gender=form.gender.data, age=form.age.data)
        db.session.add(doctor)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        doctor = Doctor.query.filter_by(email=form.email.data).first()
        if doctor and bcrypt.check_password_hash(doctor.password, form.password.data):
            login_user(doctor, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.mobile_number = form.mobile_number.data
        current_user.gender = form.gender.data
        current_user.age = form.age.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.mobile_number.data = current_user.mobile_number
        form.gender.data = current_user.gender
        form.age.data = current_user.age
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)

@app.route("/patient/new", methods=['GET', 'POST'])
@login_required
def new_patient():
    form = PatientForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        patient = Patient(username=form.username.data, email=form.email.data, password=hashed_password, mobile_number=form.mobile_number.data, gender=form.gender.data, age=form.age.data, author=current_user)
        db.session.add(patient)
        db.session.commit()
        flash('Your patient has been added!', 'success')
        return redirect(url_for('home'))
    return render_template('new_patient.html', title='New Patient', form=form, legend='New Patient')

@app.route("/patient/<int:patient_id>")
def patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    return render_template('patient.html', title=patient.username, patient=patient)

@app.route("/patient/<int:patient_id>/update", methods=['GET', 'POST'])
@login_required
def update_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    if patient.author != current_user:
        abort(403)
    form = PatientForm()
    if form.validate_on_submit():
        patient.username = form.username.data
        patient.email = form.email.data
        patient.mobile_number = form.mobile_number.data
        patient.gender = form.gender.data
        patient.age = form.age.data
        db.session.commit()
        flash('Patient Info has been updated!', 'success')
        return redirect(url_for('patient', patient_id=patient.id))
    elif request.method == 'GET':
        form.username.data = patient.username
        form.email.data = patient.email
        form.mobile_number.data = patient.mobile_number
        form.gender.data = patient.gender
        form.age.data = patient.age
    return render_template('new_patient.html', title='Update Patient', form=form, legend='Update patient')

@app.route("/patient/<int:patient_id>/delete", methods=['POST'])
@login_required
def delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    if patient.author != current_user:
        abort(403)
    db.session.delete(patient)
    db.session.commit()
    flash('Your patient has been deleted!', 'success')
    return redirect(url_for('patients'))

@app.route("/doctor/<string:username>")
def doctor_patients(username):
    doctor = Doctor.query.filter_by(username=username).first_or_404()
    patients = Patient.query.filter_by(author=doctor)
    return render_template('doctor_patients.html', patients=patients, doctor=doctor)

@app.route("/message")
@login_required
def message():
    messages = ContactUs.query.all()
    return render_template('messages.html', messages=messages)

@app.route("/contact_us", methods=['GET', 'POST'])
def contact_us():
    form = ContactUsForm()
    if form.validate_on_submit():
        comment = ContactUs(name=form.name.data, email=form.email.data, mobile_number=form.mobile_number.data, subject=form.subject.data, message=form.message.data)
        db.session.add(comment)
        db.session.commit()
        flash(f'Message sent from {form.name.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('contact_us.html', title='Contact Us', form=form)
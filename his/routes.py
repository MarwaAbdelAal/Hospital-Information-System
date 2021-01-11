import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from his import app, db, bcrypt
from his.forms import RegistrationForm, LoginForm, ContactUsForm, UpdateAccountForm, AppointmentForm
from his.models import CTScan, User, ContactUs
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
    doctors = User.query.filter_by(role='doctor')
    return render_template('doctors.html', doctors=doctors)

@app.route("/patients")
@login_required
def patients():
    patients = []
    if current_user.role == 'doctor':
        patients = User.query.filter_by(role='patient', doctor_id=current_user.id)
    elif current_user.role == 'admin':
        patients = User.query.filter_by(role='patient')
    return render_template('patients.html', patients=patients)

@app.route("/register", methods=['GET', 'POST'])
def register():
    """register for patients
    """
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        picture_file=None
        if form.picture.data:
            picture_file = save_picture(form.picture.data)

        user = User(username=form.username.data, email=form.email.data, national_id=form.national_id.data,
        password=hashed_password, mobile_number=form.mobile_number.data,
        gender=form.gender.data, age=form.age.data, role='patient', image_file=picture_file)
        scans = []
        if form.scans.data:
            for image in form.scans.data:
                if isinstance(image, str):
                    continue
                picture_file = save_picture(image)
                scan_obj = CTScan(image_file=picture_file, patient_id=user.id)
                scans.append(scan_obj)
        db.session.add(user)
        db.session.add_all(scans)
        db.session.commit()
        flash('Your patient account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/register_doctor", methods=['GET', 'POST'])
@login_required
def register_doctor():
    """register for doctors
    """
    if current_user.role != 'admin':
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password,
        mobile_number=form.mobile_number.data,gender=form.gender.data, age=form.age.data, role='doctor')
        db.session.add(user)
        db.session.commit()
        flash('A new doctor has been added! He is now able to log in', 'success')
        return redirect(url_for('doctors'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
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


@app.route("/patient/<int:patient_id>")
@login_required
def patient(patient_id):
    patient = User.query.filter_by(id=patient_id, role='patient').first_or_404()
    doctor = User.query.filter_by(id=patient.doctor_id, role='doctor').first_or_404()
    return render_template('patient.html', title=patient.username, patient=patient, doctor=doctor)


@app.route("/patient/<int:patient_id>/delete", methods=['POST'])
@login_required
def delete_patient(patient_id):
    patient = User.query.get_or_404(patient_id)
    if patient.author != current_user:
        abort(403)
    db.session.delete(patient)
    db.session.commit()
    flash('Your patient has been deleted!', 'success')
    return redirect(url_for('patients'))

@app.route("/doctor/<string:username>")
@login_required
def doctor_patients(username):
    ########## Can't get patients of each doctor in doctor_patients ###########
    if current_user.role == 'admin':
        doctor = User.query.filter_by(username=username, role='doctor').first_or_404()
        return render_template('doctor_patients.html', patients=doctor.patients, doctor=doctor)
    else:
        return redirect(url_for('home'))

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

@app.route("/reserve_appointment", methods=['GET', 'POST'])
def reserve_appointment():
    """Reserve new appointment
    """
    if not current_user.is_authenticated:
        return redirect(url_for('home'))
    form = AppointmentForm()
    if form.validate_on_submit():
        print(f'got appointment data !!\n dr {form.doctor_id.data}\n')
        # user = User(username=form.username.data, email=form.email.data, national_id=form.national_id.data,
        # password=hashed_password, mobile_number=form.mobile_number.data,
        # gender=form.gender.data, age=form.age.data, role='patient', image_file=picture_file)
        # scans = []
        # if form.scans.data:
        #     for image in form.scans.data:
        #         if isinstance(image, str):
        #             continue
        #         picture_file = save_picture(image)
        #         scan_obj = CTScan(image_file=picture_file, patient_id=user.id)
        #         scans.append(scan_obj)
        # db.session.add(user)
        # db.session.add_all(scans)
        # db.session.commit()
        # flash('Your patient account has been created! You are now able to log in', 'success')
        # return redirect(url_for('login'))
    return render_template('reserve_appointment.html', title='Reserve Appointment', form=form)

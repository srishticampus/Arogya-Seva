from flask import Flask, abort, render_template, redirect, url_for, flash, request, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from functools import wraps
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'chocolate'  # Required for flashing messages
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app,db)

# ---------- DATABASE MODELS ----------
class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    experience = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(200), nullable=True)

    appointments = relationship("AppointmentSlot", backref="doctor", lazy=True)

class AppointmentSlot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    date = db.Column(db.String(10), nullable=False)  # Format: YYYY-MM-DD
    time_slot = db.Column(db.String(10), nullable=False)  # Example: "10:00 AM"
    status = db.Column(db.String(10), default="available")  # "available" or "booked"

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(100), nullable=False)
    patient_email = db.Column(db.String(100), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    time_slot = db.Column(db.String(10), nullable=False)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Specialization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)

    def __init__(self, name, description):
        self.name = name
        self.description = description


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    patient_name = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)


# ---------- ROUTES ----------


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/")
def home():
    return render_template("index.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if the user is an admin
        if email == "admin@example.com" and password == "admin123":
            session['user_id'] = 0  # Arbitrary ID for the admin (not in your User model)
            session['user_role'] = "admin"
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_dashboard'))

        # Check if the user is a patient (Normal User)
        user = Patient.query.filter_by(email=email).first()

        if user:
            if check_password_hash(user.password, password):  # Compare hashed passwords

                session['email'] = user.email
                session['user_id'] = user.id
                session['user_name'] = user.first_name
                flash(f'Welcome, {user.first_name}!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Incorrect password. Try again!', 'danger')
        else:
            flash('User not found. Please register first.', 'danger')

    return render_template('login.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        dob = request.form['dob']
        gender = request.form['gender']
        blood_group = request.form['blood_group']
        phone = request.form['phone']
        email = request.form['email']
        password = request.form['password']

        # Convert the dob string to a datetime.date object
        if dob:
            dob = datetime.strptime(dob, '%Y-%m-%d').date()

        # Check if the user already exists
        existing_user = Patient.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please log in.', 'danger')
            return redirect(url_for('login'))

        # Create a new User instance
        new_user = Patient(
            first_name=first_name,
            last_name=last_name,
            dob=dob,
            gender=gender,
            blood_group=blood_group,
            phone=phone,
            email=email
        )
        new_user.set_password(password)  # Hashing the password before storing

        # Save the user to the database
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')



@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/specialization')
def specialization():
    specializations = Specialization.query.all()
    return render_template('specialization.html', specializations=specializations)


@app.route('/learn_more/<int:specialization_id>')
def learn_more(specialization_id):
    specialization = Specialization.query.get_or_404(specialization_id)
    return render_template('learn_more.html', specialization=specialization)



@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/doctor')
def doctor():
    doctors = Doctor.query.all()  # Fetch all doctors from the database
    return render_template('doctor.html', doctors=doctors)

@app.route('/doctor/<int:doctor_id>')
def doctor_profile(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    slots = AppointmentSlot.query.filter_by(doctor_id=doctor_id, status="available").all()
    reviews = Review.query.filter_by(doctor_id=doctor_id).all()
    return render_template('doctor_profile.html', doctor=doctor, slots=slots, reviews=reviews)

@app.route('/doctor/<int:doctor_id>/add_review', methods=['POST'])
@login_required
def add_review(doctor_id):
    rating = int(request.form.get('rating'))
    comment = request.form.get('comment')
    patient_name = session.get('user_name')  # Assuming session stores patient's name

    if not rating or rating < 1 or rating > 5:
        flash("Please provide a valid rating between 1 and 5.", "danger")
        return redirect(url_for('doctor_profile', doctor_id=doctor_id))

    new_review = Review(doctor_id=doctor_id, patient_name=patient_name, rating=rating, comment=comment)
    db.session.add(new_review)
    db.session.commit()

    flash("Your review has been submitted successfully!", "success")
    return redirect(url_for('doctor_profile', doctor_id=doctor_id))



@app.route('/book_appointment/<int:doctor_id>', methods=['GET', 'POST'])
@login_required
def book_appointment(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    slots = AppointmentSlot.query.filter_by(doctor_id=doctor_id, status="available").all()

    if request.method == 'POST':
        patient_name = session.get('user_name')
        patient_email = session.get('email')
        date = request.form.get('date')
        time_slot = request.form.get('time_slot')

        if not date or not time_slot:
            flash("Please select a date and time slot.", "warning")
            return redirect(url_for('book_appointment', doctor_id=doctor_id))

        # Check if slot exists
        slot = AppointmentSlot.query.filter_by(doctor_id=doctor_id, date=date, time_slot=time_slot, status="available").first()

        if not slot:
            flash("This time slot is no longer available. Please try a different slot.", "danger")
            return redirect(url_for('book_appointment', doctor_id=doctor_id))

        try:
            # Create new appointment
            new_appointment = Appointment(
                patient_name=patient_name,
                patient_email=patient_email,
                doctor_id=doctor_id,
                date=date,
                time_slot=time_slot
            )
            db.session.add(new_appointment)

            # Mark slot as booked
            slot.status = "booked"
            db.session.commit()

            flash("Your appointment has been confirmed.", "success")
            return redirect(url_for('doctor_profile', doctor_id=doctor_id))

        except Exception as e:
            db.session.rollback()
            flash("An error occurred while booking your appointment. Please try again.", "danger")
            print(f"Database Error: {e}")  # Log error for debugging
            return redirect(url_for('book_appointment', doctor_id=doctor_id))

    return render_template('book_appointment.html', doctor=doctor, slots=slots)



def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_role") == "admin":  # Check if the user is logged in as admin
            flash("Access denied. Please log in as admin.", "danger")
            return redirect(url_for("login"))  # Redirect to common login page

        allowed_admin_routes = ["admin_dashboard", "add_doctor", "add_slots", "admin_logout"]

        if request.endpoint not in allowed_admin_routes:
            flash("Admins can only manage doctors and slots.", "danger")
            return redirect(url_for("admin_dashboard"))

        return f(*args, **kwargs)
    return decorated_function



@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Admin logged out successfully.', 'info')
    return redirect(url_for('home'))

@app.route('/admin/add_doctor', methods=['GET', 'POST'])
@admin_required
def add_doctor():
    if request.method == 'POST':
        name = request.form['name']
        specialization = request.form['specialization']
        experience = request.form['experience']
        image = request.form['image'] if request.form['image'] else "doctornew.jpg"

        new_doctor = Doctor(name=name, specialization=specialization, experience=experience, image=image)
        db.session.add(new_doctor)
        db.session.commit()
        flash('Doctor added successfully!', 'success')
        return redirect(url_for('doctor'))  # Redirect to the doctor list

    return render_template('add_doctor.html')  # Create this HTML form

@app.route('/admin/add_slots', methods=['GET', 'POST'])
def add_slot():
    from datetime import datetime
    doctors = Doctor.query.all()  # Fetch all doctors for selection
    slots = AppointmentSlot.query.all()  # Fetch all slots

    current_date = datetime.now().strftime('%Y-%m-%d')  # Current date for date picker restriction

    if request.method == 'POST':
        doctor_id = request.form['doctor_id']
        date = request.form['date']
        time_slot = request.form['time_slot']

        # Check if the slot already exists
        existing_slot = AppointmentSlot.query.filter_by(doctor_id=doctor_id, date=date, time_slot=time_slot).first()
        if existing_slot:
            flash("This slot already exists!", "warning")
        else:
            new_slot = AppointmentSlot(doctor_id=doctor_id, date=date, time_slot=time_slot, status="available")
            db.session.add(new_slot)
            db.session.commit()
            flash("Time slot added successfully!", "success")

    return render_template('add_slots.html', doctors=doctors, slots=slots, current_date=current_date)




@app.route('/admin/delete_slot/<int:slot_id>', methods=['POST'])
def delete_slot(slot_id):
    print(f"Attempting to delete slot with ID: {slot_id}")  # Debug message

    slot = AppointmentSlot.query.get(slot_id)
    if slot:
        db.session.delete(slot)
        db.session.commit()
        flash("Slot deleted successfully!", "success")
        print("Slot deleted successfully")  # Debug message
    else:
        flash("Slot not found!", "danger")
        print("Slot not found")  # Debug message

    return redirect(url_for('add_slot'))  # Redirect back to the add slots page








# @app.route('/admin/delete_doctor/<int:doctor_id>', methods=['POST'])
# @admin_required
# def delete_doctor(doctor_id):
#     doctor = Doctor.query.get_or_404(doctor_id)
#     db.session.delete(doctor)
#     db.session.commit()
#     flash('Doctor removed successfully!', 'danger')
#     return redirect(url_for('doctor'))

@app.route('/add_specialization', methods=['GET', 'POST'])
def add_specialization():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')

        if not name or not description:
            flash("Both fields are required", "danger")
            return redirect(url_for('add_specialization'))

        specialization = Specialization(name=name, description=description)
        db.session.add(specialization)
        try:
            db.session.commit()
            flash("Specialization added successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", "danger")

    return render_template('add_specialization.html')



@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    return render_template('admin_dashboard.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('is_admin', None)

    flash('Logged out successfully.', 'info')
    return redirect(url_for('home'))

@app.route('/check_session')
def check_session():
    return f"Name: {session.get('user_name')}, Email: {session.get('email')}, User ID: {session.get('user_id')}"


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    patient = Patient.query.filter_by(id=session['user_id']).first()

    if request.method == 'POST':
        patient.first_name = request.form['first_name']
        patient.last_name = request.form['last_name']
        patient.dob = request.form['dob']
        patient.gender = request.form['gender']
        patient.blood_group = request.form['blood_group']
        patient.phone = request.form['phone']

        db.session.commit()
        flash("Profile updated successfully!", "success")

    # Fetch previous and upcoming appointments
    upcoming_appointments = db.session.query(Appointment, Doctor).join(Doctor).filter(
        Appointment.patient_email == patient.email,
        Appointment.date >= datetime.now().strftime('%Y-%m-%d')
    ).all()

    previous_appointments = db.session.query(Appointment, Doctor).join(Doctor).filter(
        Appointment.patient_email == patient.email,
        Appointment.date < datetime.now().strftime('%Y-%m-%d')
    ).all()

    return render_template('profile.html', patient=patient, upcoming_appointments=upcoming_appointments, previous_appointments=previous_appointments)

@app.route('/cancel_appointment/<int:appointment_id>', methods=['POST'])
@login_required
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)

    # Only allow the patient who booked the appointment to cancel it
    if appointment.patient_email != session.get('email'):
        flash("You are not authorized to cancel this appointment.", "danger")
        return redirect(url_for('profile'))

    try:
        # Find the corresponding slot and mark it as available
        slot = AppointmentSlot.query.filter_by(
            doctor_id=appointment.doctor_id,
            date=appointment.date,
            time_slot=appointment.time_slot
        ).first()

        if slot:
            slot.status = "available"  # Mark the slot as available again

        # Remove the appointment from the database
        db.session.delete(appointment)
        db.session.commit()

        flash("Appointment cancelled successfully!", "success")
        return redirect(url_for('profile'))

    except Exception as e:
        db.session.rollback()
        flash("An error occurred while cancelling the appointment. Please try again.", "danger")
        print(f"Database Error: {e}")
        return redirect(url_for('profile'))




# Run database setup
with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)

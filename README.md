# Arogya Seva  
Arogya Seva is a healthcare management web application built using Flask, providing patients with a convenient way to book doctor appointments, leave reviews, and manage their profiles. Administrators can manage doctors, available slots, and view appointments.

## Table of Contents  
- [Features](#features)  
- [Technologies Used](#technologies-used)  
- [Usage](#usage)  
- [Folder Structure](#folder-structure)  

---

## Features  
### For Patients:  
- User Authentication (Registration, Login, Logout)  
- Profile Management  
- View Doctors and Specializations  
- Book Appointments (Only for logged-in users)  
- View Upcoming and Previous Appointments  
- Leave Reviews for Doctors  
- View Reviews left by other patients  

### For Admins:  
- Admin Dashboard  
- Add Doctors and Manage Specializations  
- Add, Edit, and Delete Appointment Slots  
- View All Appointments  
- Manage Users  

---

## Technologies Used  
- **Backend:** Flask (Python)  
- **Database:** SQLite (db.sqlite3)  
- **Frontend:** HTML, CSS, Bootstrap (For styling and responsiveness)  
- **Session Management:** Flask-Session  
- **Password Hashing:** Werkzeug's generate_password_hash() and check_password_hash()  

---

## Usage  
1. **Admin Panel:**  
   - Go to `/admin_dashboard` to access the admin panel.  
   - Add doctors, create slots, and manage users.  

2. **Patient Panel:**  
   - Register or login to your account.  
   - Browse available doctors and specializations.  
   - Book appointments and leave reviews for doctors.  
   - View and manage your profile.  

---

## Folder Structure  
```
Arogya-Seva/
├── static/             # Static files (CSS, JS, Images)
├── templates/          # HTML templates
├── main.py             # Flask application
├── models.py           # Database models
├── requirements.txt     # List of dependencies
├── README.md            # Project Documentation
├── db.sqlite3           # SQLite Database File
```

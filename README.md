LMS Project 🎓

A Learning Management System (LMS) built with Django that provides a platform for managing courses, assignments, users, notifications, and messaging.

🚀 Features

- User authentication and authorization
- Custom user model
- Course management
- Assignment management
- User dashboard
- Notifications system
- Messaging system between users
- Admin panel management
- Media file handling
- Responsive UI using Bootstrap 5
- Django Crispy Forms integration

---

🛠️ Technologies Used

- Python
- Django
- SQLite Database
- HTML5 / CSS3
- Bootstrap 5
- Django Crispy Forms
- JavaScript

---

📂 Project Structure

lms_project/
│
├── accounts/          # User authentication and custom user model
├── courses/           # Course management
├── assignments/       # Assignment management
├── notifications/     # Notification system
├── messaging/         # User messaging system
├── adminpanel/        # Custom admin features
│
├── lms_project/       # Main Django project settings
│
├── templates/         # HTML templates
├── static/            # Static files (CSS, JS, images)
├── media/             # Uploaded files
│
├── manage.py
├── requirements.txt
├── .env
└── README.md

---

⚙️ Installation

1. Clone the repository

git clone https://github.com/your-username/lms-project.git

Go into the project directory:

cd lms-project

---

2. Create a virtual environment

python -m venv venv

Activate it:

Windows

venv\Scripts\activate

Linux / macOS

source venv/bin/activate

---

3. Install dependencies

pip install -r requirements.txt

---

4. Configure environment variables

Create a ".env" file in the project root:

SECRET_KEY=your-secret-key
DEBUG=True

---

5. Apply database migrations

python manage.py makemigrations

python manage.py migrate

---

6. Create admin user

python manage.py createsuperuser

---

7. Run the development server

python manage.py runserver

Open your browser:

http://127.0.0.1:8000/

---

👤 User Roles

The system supports different user interactions:

- Students can view courses and assignments.
- Users can communicate through messaging.
- Admins can manage system data through the admin panel.

---

🔐 Environment Variables

Sensitive information is stored in ".env":

Variable| Description
SECRET_KEY| Django security key
DEBUG| Development mode setting

The ".env" file is excluded from Git using ".gitignore".

---

📌 Future Improvements

- REST API using Django REST Framework
- Online course enrollment system
- Payment integration
- Advanced permissions
- PostgreSQL database support
- Docker deployment
- Production deployment

---

📄 License

This project is created for learning and portfolio purposes.
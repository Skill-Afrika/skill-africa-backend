# skill-africa-backend
Backend part of skill Africa branding

## Basic Django Setup Guide
This will guide you on getting started on the Skill Africa Backend part

## Installation

1. Clone the repository to your PC:

 `git clone https://github.com/Skill-Afrika/skill-africa-backend.git`

 2. Open the project in your preferred code editor and create  a virtual environment and activate it:
 ```bash
 python -m vevn vevn
 venv\Scripts\activate.bat
 ```
 3. Install the required packages using the following command:

 ```bash
 pip install -r requirements.txt
 ```
 4. Run Migrations to setup initial database schema:
 ```bash
 python manage.py runmigrations
 python manage.py migate
 ```
 5. Start the development server
 ```bash
 python manage.py runsever
 ```
 6. Create accounts app using and add the app to the project INSTALLED_APPS in skill_africa/settings.py
 ```bash
 python manage.py createapp accounts
 INSTALLED_APPS =
 [
    ...
    'accounts',
]
 ```
 7. Create superuser to access the django admin and follow the instructions
 ```bash
 python manage.py createsuperuser
 ```
 8. Set up CORS Header to allow Cross-Origin Resources Sharing. Install django-cors-header and add it to your INSTALLED_APP and configure middleware in the settings.py
 ```bash
 INSTALLED_APP = 
 [
    ...,
    'corsheader',
 ]
 MIDDLEWARE = 
 [
    'corsheaders.middleware.CorsMiddleware'
 ]
 CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',  # Add your frontend URL here
]
```


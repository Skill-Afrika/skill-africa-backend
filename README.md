# skill-africa-backend

Backend part of Skill Africa branding

## Basic Django Setup Guide

This will guide you on getting started on the Skill Africa Backend part

## Installation

1. Clone the repository to your PC:

```bash
git clone https://github.com/Skill-Afrika/skill-africa-backend.git
```

2. Open the project in your preferred code editor and create a virtual environment and activate it:

```bash
python -m venv venv
venv\Scripts\activate.bat
```

3. Install the required packages using the following command:

```bash
pip install -r requirements.txt
```

4. Set up your dotenv file to manage environment variables:

   - Create a file named `.env` in the root directory of the project.
   - Add the following variables to the `.env` file:
     ```plaintext
     SECRET_KEY=your_secret_key_here
     REFRESH_TOKEN_LIFETIME_DAYS=7
     ACCESS_TOKEN_LIFETIME_HOURS=24
     ```

5. Run Migrations to set up the initial database schema:

```bash
python manage.py makemigrations
python manage.py migrate
```

6. Start the development server:

```bash
python manage.py runserver
```

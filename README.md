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
        SECRET_KEY=iZfkT41muRKOhBn7MSShrR7bx0x8thAorazQikq65wLgwSVrMwACNY6xsj9VuuEZ0AKpHQtt8iFYSxMRUE4SF1gfcVNkBLNRqLBo
        DATABASE_URL=postgresql://skill_afrika:MO91YuwcAr2B8UvLmnA7Nsonx4REDm7j@dpg-crg97qd6l47c73dtl3og-a/skill_afrika_t56u
        REFRESH_TOKEN_LIFETIME_DAYS=7
        ACCESS_TOKEN_LIFETIME_HOURS=24
        MAILCHIMP_API_KEY=md-nXOYM71MRBIYqy0IhxY5cQ
        DEBUG=TRUE
        REDIS_LOCATION=redis://default:qc986b4pxP2BrJWd6nsGP107aPS0c33X@redis-16075.c8.us-east-1-4.ec2.redns.redis-cloud.com:16075
        GOOGLE_CLIENT_SECRET_JSON='{"web":{"client_id":"308478738375-6pqe98ism65mlvhv3nth9qejqmf6ijt7.apps.googleusercontent.com","project_id":"skill-afrika","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_secret":"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","redirect_uris":["http://127.0.0.1:8000/api/v1/sso/google_sso/callback/"],"javascript_origins":["http://127.0.0.1:8000"]}}'
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

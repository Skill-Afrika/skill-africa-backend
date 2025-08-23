# Skill Africa Backend Stack 

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/Skill-Afrika/skill-africa-backend/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![Django Version](https://img.shields.io/badge/django-4.2%2B-blue)](https://www.djangoproject.com/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

The **Skill Africa Backend** is the server-side component of the Skill Africa platform, a web application designed to empower users through skill development and training. Built with Django and PostgreSQL, it provides a robust API for user management, authentication (including Google SSO), and integration with third-party services like Mailchimp and Redis.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Project](#running-the-project)
- [Testing](#testing)
- [Tooling](#tooling)
- [Contributing](#contributing)
- [License](#license)

## Features

- RESTful API for user management and skill tracking.
- Google SSO integration for secure authentication.
- Mailchimp integration for email campaigns.
- Redis for caching and performance optimization.
- PostgreSQL as the primary database.
- Environment variable management with `python-dotenv`.
- Scalable architecture hosted on Render.

## Prerequisites
## Architecture

The Skill Africa Backend is a Django-based REST API with integrations for authentication, email, caching, and database storage. Below is the architecture diagram:

```mermaid
classDiagram
    class Client {
        Frontend / Mobile Apps
        Sends HTTP Requests
    }
    class API {
        Django REST Framework
        /api/v1/ Endpoints
        User Management
        Skill Tracking
    }
    class Application {
        Django Application
        Business Logic
        Authentication
    }
    class GoogleSSO {
        OAuth 2.0
        User Authentication
    }
    class Mailchimp {
        Email Campaigns
        API Integration
    }
    class Redis {
        Caching Layer
        Session Management
    }
    class PostgreSQL {
        Database
        User Data
        Skill Data
    }
    class Render {
        Cloud Hosting
        Deployment
    }
    Client --> API : HTTP Requests
    API --> Application : Handles Requests
    Application --> GoogleSSO : Authenticates Users
    Application --> Mailchimp : Sends Emails
    Application --> Redis : Caches Data
    Application --> PostgreSQL : Stores Data
    Application --> Render : Deployed On
 ```

Before setting up the project, ensure you have the following installed:
- **Python** (3.8 or higher)
- **Git**
- **PostgreSQL** (local or cloud-based, e.g., Render)
- **Redis** (local or cloud-based, e.g., Redis Cloud)
- A code editor (e.g., VS Code, PyCharm)
- (Optional) Docker for containerized development

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Skill-Afrika/skill-africa-backend.git
   cd skill-africa-backend
   ```

2. Create and Activate a Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate.bat
```

3. Install the required packages using the following command:

```bash
pip install -r requirements.txt # On Windows: venv\Scripts\activate
```
## Configuration
1. Set up your dotenv file to manage environment variables:

   - Create a file named `.env` in the root directory of the project.
   - Add the following variables to the `.env` file:
     ```plaintext
        SECRET_KEY=iZfkT41muRKOhBn7MSShrR7bx0x8thAorazQikq65wLgwSVrMwACNY6xsj9VuuEZ0AKpHQtt8iFYSxMRUE4SF1gfcVNkBLNRqLBo
        DATABASE_URL=postgresql://skill_afrika:ozA65p5qOOAivCZ6NhzZYA1UM7zGFuRO@dpg-d2kpedp5pdvs739tmmcg-a.oregon-postgres.render.com/skill_afrika_5asd        REFRESH_TOKEN_LIFETIME_DAYS=7
        ACCESS_TOKEN_LIFETIME_HOURS=24
        MAILCHIMP_API_KEY=md-nXOYM71MRBIYqy0IhxY5cQ
        DEBUG=TRUE
        REDIS_LOCATION=redis://default:qc986b4pxP2BrJWd6nsGP107aPS0c33X@redis-16075.c8.us-east-1-4.ec2.redns.redis-cloud.com:16075
        GOOGLE_CLIENT_SECRET_JSON='{"web":{"client_id":"308478738375-6pqe98ism65mlvhv3nth9qejqmf6ijt7.apps.googleusercontent.com","project_id":"skill-afrika","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_secret":"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","redirect_uris":["http://127.0.0.1:8000/api/v1/sso/google_sso/callback/"],"javascript_origins":["http://127.0.0.1:8000"]}}'
    ```

2. Run Migrations to set up the initial database schema:

```bash
python manage.py makemigrations
python manage.py migrate
```
3. Testing

```bash
pip install coverage
coverage run manage.py test
coverage report
```

4. Start the development server:

```bash
python manage.py runserver
```
## Tooling 
The project uses the following tools to maintain code quality:
Black: Code formatter for consistent style
```bash
black .
```
Flake8: Linter for catching code issues
```bash
flake8 .
```
isort: Sorts imports for consistency.
```bash
isort .
```
##  contributing 
see Contributing.Md

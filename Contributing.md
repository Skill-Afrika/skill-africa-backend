# Contributing to Skill Africa Backend

Thank you for considering contributing to the **Skill Africa Backend**! We welcome contributions from the community to help improve this project, which powers a platform for skill development and training. This document outlines the process for contributing code, reporting issues, and suggesting features.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Branching Strategy](#branching-strategy)
- [Development Setup](#development-setup)
- [Code Style and Quality](#code-style-and-quality)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)
- [Requesting Features](#requesting-features)

## Code of Conduct

We are committed to fostering an inclusive and respectful community. By participating, you agree to:
- Be respectful and considerate in all interactions.
- Avoid harassment, discrimination, or offensive behavior.
- Provide constructive feedback and maintain a positive attitude.

## How to Contribute

We welcome contributions in the form of bug fixes, new features, documentation improvements, and more. To contribute:

1. **Fork the Repository**:
   - Fork the [Skill-Afrika/skill-africa-backend](https://github.com/Skill-Afrika/skill-africa-backend) repository to your GitHub account.

2. **Clone Your Fork**:
   ```bash
   git clone https://github.com/YOUR-USERNAME/skill-africa-backend.git
   cd skill-africa-backend
   ```
3. **Create a Branch:**
   Create a new branch for your changes:
      ```bash
      git checkout -b feature/your-feature-name
     ```
   - Use descriptive branch names (e.g., fix/bug-description, feature/add-endpoint).

4. **Make Changes:**
    Implement your changes, adhering to the Code Style and Quality guidelines
    Write or update tests as needed (see Testing).
   
5. **Commit Changes:**
   Use clear, concise commit messages:

6.  **Create a Branch**:
    
      ```bash
      git checkout -b feature/your-feature-name
      ```   
    *   Use descriptive branch names (e.g., fix/bug-description, feature/add-endpoint).
        
7.  **Make Changes**:
    
    *   Implement your changes, adhering to the Code Style and Quality guidelines.
        
    *   Write or update tests as needed (see Testing).
        
8.  **Commit Changes**
    ```bash
    git commit -m "Add feature: description of changes
     ```
        
9. **push your branch**
    ```bash
      git push origin feature/your-feature-name
    
10.  **Open a Pull Request**:
    
    *   Go to the original repository and open a pull request (PR) from your branch.
        
    *   Provide a clear title and description of your changes, referencing any related issues (e.g., Fixes #123).

## Branching Strategy
We use a Gitflow-based branching strategy to manage code changes effectively. The diagram below illustrates the workflow:
 ```mermaid
  gitGraph
   commit id: "Initial"
   branch develop
   checkout develop
   commit id: "Dev Start"
   branch feature/login
   checkout feature/login
   commit id: "Login Feature"
   checkout develop
   merge feature/login id: "Merge Login"
   branch feature/profile
   checkout feature/profile
   commit id: "Profile Feature"
   checkout develop
   merge feature/profile id: "Merge Profile"
   branch release/v1.0
   checkout release/v1.0
   commit id: "Release Prep"
   checkout main
   merge release/v1.0 id: "Release v1.0" tag: "v1.0"
   checkout develop
   merge release/v1.0
   branch hotfix/bugfix
   checkout hotfix/bugfix
   commit id: "Bug Fix"
   checkout main
   merge hotfix/bugfix id: "Hotfix Merge" tag: "v1.0.1"
   checkout develop
   merge hotfix/bugfix
 ```



##  Development Setup

To set up the project locally, follow the steps in the README.md and Configuration sections. Key steps include:

*   python -m venv venvsource venv/bin/activate # On Windows: venv\\Scripts\\activatepip install -r requirements.txt
    
*   Set up environment variables in a .env file (see README.md).
    
*   python manage.py makemigrationspython manage.py migrate
    
*   python manage.py runserver
    

## Code Style and Quality

To maintain consistency and quality, adhere to the following tools and guidelines:

*   black .
    
*   flake8 .
    
*   isort .
    
*   **pre-commit**: Automatically runs linters and formatters before commits.
    
    *   Install: pip install pre-commit
        
    *   Set up: pre-commit install
        
*   **Commit Messages**: Follow the Conventional Commits format, e.g., fix: resolve login bug or feat: add user profile endpoint.
    

Ensure all code passes linting and formatting checks before submitting a PR.

## Testing

All contributions must include tests to ensure functionality and prevent regressions. The project uses pytest-django for testing.

*   python manage.py test
    
*   pip install coveragecoverage run manage.py testcoverage report
    
*   pytest
    

Write unit tests for new features and update existing tests as needed. Aim for high test coverage.

## Submitting Changes

When submitting a pull request:

*   Reference any related issues (e.g., Fixes #123).
    
*   Describe the purpose of your changes and how they were tested.
    
*   Ensure all tests pass and code adheres to style guidelines.
    
*   Be responsive to feedback during the PR review process.
    

Maintainers will review your PR and may request changes before merging.

## Reporting Issues


If you find a bug or issue:

1.  Check the issue tracker to see if it’s already reported.
    
2.  Open a new issue with:
    
    *   A clear title and description.
        
    *   Steps to reproduce the issue.
        
    *   Expected and actual behavior.
        
    *   Relevant logs or screenshots.
        

## Requesting Features


To suggest a new feature:

1.  Open an issue in the issue tracker.
    
2.  Use the feature request template (if available) or provide:
    
    *   A clear description of the feature.
        
    *   Use cases or benefits.
        
    *   Any relevant examples or references.
        

We’ll review feature requests and discuss implementation feasibility.

Thank you for contributing to Skill Africa Backend! Your efforts help make this project better for everyone.

© 2025 Skill Afrika







   

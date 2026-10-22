# infosys-maritime-ai
# 🔐 Infosys Springboard – User Authentication Module

## 📌 Project Overview

The User Authentication Module is a Python-based web application developed as part of Infosys Springboard Milestone 1. It provides user registration, login, password recovery, and an administrative dashboard.

The application is built using Streamlit and includes password hashing, JWT-based authentication, and email OTP verification for password recovery.

## ✨ Features

- **User Registration:** Create an account with a username, email, password, and security question.
- **User Login:** Authenticate using a username or registered email address and password.
- **Password Security:** Store passwords using bcrypt hashing.
- **JWT Authentication:** Manage authenticated user sessions using JSON Web Tokens.
- **Forgot Password:** Recover access using a security question or email OTP.
- **Email OTP Verification:** Send a one-time password to the registered email address.
- **Password Reset:** Set a new password after successful verification.
- **Admin Login:** Provide a separate administrative login.
- **Admin Dashboard:** View registered usernames, email addresses, and total user count.
- **Search Users:** Search registered users by username or email.
- **Refresh Users:** Reload the registered-users table.
- **Delete Users:** Allow the administrator to remove registered accounts.
- **Logout:** End the user or admin session.

## 🛠️ Technologies Used

- Python
- Streamlit
- bcrypt
- PyJWT
- SMTP and Gmail for email OTP delivery
- JSON for local user data storage
- Google Colab for development

## 📂 Project Structure

```text
user-authentication-module/
├── app.py
├── README.md
├── requirements.txt
└── users.json          # Local data file; do not publish real user data
```

`app_backup.py` may be kept separately as a backup and does not need to be deployed.

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd user-authentication-module
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with your repository's URL.

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Configure the following secrets in your deployment platform:

- `JWT_SECRET` — secret used to sign JWT tokens.
- `EMAIL_ADDRESS` — Gmail address used to send OTP emails.
- `EMAIL_PASSWORD` — Gmail App Password.
- `ADMIN_USERNAME` — administrator username.
- `ADMIN_PASSWORD` — administrator password.

Do not commit actual secrets or passwords to GitHub.

### 4. Run the application locally

```bash
streamlit run app.py
```

The application will normally be available at:

```text
http://localhost:8501
```

## 🔑 Password Requirements

Passwords must contain at least:

- 8 characters
- One uppercase letter
- One lowercase letter
- One number
- One special character

## 🔒 Security Features

- bcrypt password hashing.
- JWT-based user authentication.
- Security-question verification.
- Time-limited email OTPs.
- Separate administrator authentication.
- Environment variables for sensitive configuration.

**Security note:** This project is intended for learning and demonstration. The current JSON-based database is not suitable for production use with real users. A persistent database, stronger account-recovery protections, rate limiting, and additional session and access-control safeguards are recommended before public deployment.

## 🧪 Testing

The following features should be tested before submission:

- User registration and duplicate-account validation.
- Successful and unsuccessful login attempts.
- Password recovery through security questions.
- Email OTP delivery, verification, and expiration.
- Password reset and login with the new password.
- User logout.
- Admin login and logout.
- Viewing, searching, refreshing, and deleting registered users.

## 🚀 Deployment

The application can be deployed on a hosting platform that supports Python and Streamlit, such as Streamlit Community Cloud.

Configure all secrets through the hosting platform's secret-management settings. Do not upload real credentials or private user data to the public repository.

## 🎯 Project Objective

The objective of this project is to demonstrate the implementation of a user authentication system with secure password storage, account recovery, session management, and administrator controls using Python.

## 👩‍💻 Project Information

- **Project:** User Authentication Module
- **Program:** Infosys Springboard
- **Milestone:** Milestone 1
- **Language:** Python
- **Framework:** Streamlit

---

*Developed for learning and demonstration purposes.*


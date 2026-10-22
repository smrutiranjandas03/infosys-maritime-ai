
%%writefile app.py

import os
import re
import json
import time
import secrets
import hashlib
import smtplib
import bcrypt
import jwt
import streamlit as st

from email.message import EmailMessage
from datetime import datetime, timedelta, timezone

# ---------------------------------------
# 1. PAGE CONFIGURATION
# ---------------------------------------

st.set_page_config(
    page_title="Infosys Authentication",
    page_icon="🔐",
    layout="centered"
)

DB_FILE = "users.json"
JWT_SECRET = os.environ.get("JWT_SECRET", "")
EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS", "")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "")

# ADD THESE TWO LINES HERE
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")

# ---------------------------------------
# 2. DATABASE FUNCTIONS
# ---------------------------------------
  

# ---------------------------------------
# 2. DATABASE FUNCTIONS
# ---------------------------------------

if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump({}, f)


def load_users():
    with open(DB_FILE, "r") as f:
        return json.load(f)


def save_users(users):
    with open(DB_FILE, "w") as f:
        json.dump(users, f, indent=4)


def find_username(identifier, users):
    identifier = identifier.strip().casefold()

    for username, data in users.items():
        if (
            username.casefold() == identifier
            or data.get("email", "").casefold() == identifier
        ):
            return username

    return None


# ---------------------------------------
# 3. VALIDATION AND PASSWORD SECURITY
# ---------------------------------------

def valid_email(email):
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return bool(re.fullmatch(pattern, email))


def valid_password(password):
    return (
        len(password) >= 8
        and bool(re.search(r"[A-Z]", password))
        and bool(re.search(r"[a-z]", password))
        and bool(re.search(r"\d", password))
        and bool(re.search(r"[^A-Za-z0-9]", password))
    )


def hash_password(password):
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def verify_password(password, hashed_password):
    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


def reset_password(username, new_password):
    users = load_users()
    users[username]["password"] = hash_password(new_password)
    save_users(users)

    # Invalidate any recovery OTP after a successful reset.
    for key in (
        "otp_hash", "otp_expiry", "otp_username",
        "otp_attempts", "otp_verified_username"
    ):
        st.session_state.pop(key, None)

    st.session_state["recovery_username"] = None
    st.session_state["recovery_method"] = None


# ---------------------------------------
# 4. JWT FUNCTIONS
# ---------------------------------------

def create_token(username):
    if not JWT_SECRET:
        raise RuntimeError("JWT_SECRET is not configured.")

    payload = {
        "username": username,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1)
    }

    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def verify_token(token):
    if not JWT_SECRET:
        return None

    try:
        return jwt.decode(
            token,
            JWT_SECRET,
            algorithms=["HS256"]
        )
    except jwt.InvalidTokenError:
        return None


# ---------------------------------------
# 5. EMAIL OTP FUNCTION
# ---------------------------------------

def send_otp_email(recipient, otp):
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        raise RuntimeError(
            "Email configuration is missing. Check Colab Secrets."
        )

    message = EmailMessage()
    message["Subject"] = "Your Infosys Authentication Password Reset OTP"
    message["From"] = EMAIL_ADDRESS
    message["To"] = recipient
    message.set_content(
        f"""Hello,

Your password-reset OTP is: {otp}

This code expires in 5 minutes.
Do not share this code with anyone.

If you did not request a password reset, you can ignore this email.
"""
    )

    with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(message)


# ---------------------------------------
# 6. PAGE HEADER
# ---------------------------------------

st.title("🔐 Infosys Springboard")
st.subheader("User Authentication Module")

# ---------------------------------------
# 7. CHECK JWT LOGIN SESSION
# ---------------------------------------

token = st.session_state.get("jwt_token")
session_data = verify_token(token) if token else None

if session_data:
    username = session_data.get("username")
    users = load_users()

    if username in users:
        st.success(f"Welcome, {username}!")
        st.write("You are successfully logged in.")
        st.write("Email:", users[username]["email"])

        if st.button("Logout"):
            st.session_state.pop("jwt_token", None)
            st.rerun()
    else:
        st.session_state.pop("jwt_token", None)
        st.warning("Account not found. Please log in again.")
        st.rerun()

else:
    # -----------------------------------
    # 8. MAIN NAVIGATION
    # -----------------------------------

    page = st.radio(
        "Choose an option",
        ["Login", "Signup", "Forgot Password", "Admin Login"],
        horizontal=True
    )

    # -----------------------------------
    # 9. SIGNUP
    # -----------------------------------

    if page == "Signup":
        st.header("Create an Account")

        with st.form("signup_form"):
            username = st.text_input("Username").strip()
            email = st.text_input("Email address").strip().lower()
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input(
                "Confirm password", type="password"
            )

            security_question = st.selectbox(
                "Choose a security question",
                [
                    "What was the name of your first school?",
                    "What is your favourite childhood nickname?",
                    "What was the name of your first pet?"
                ]
            )

            security_answer = st.text_input(
                "Security answer", type="password"
            )

            submitted = st.form_submit_button(
                "Create Account",
                use_container_width=True
            )

        if submitted:
            users = load_users()

            if not all([
                username, email, password,
                confirm_password, security_answer.strip()
            ]):
                st.error("Please fill in all required fields.")

            elif len(username) < 3:
                st.error("Username must contain at least 3 characters.")

            elif username.casefold() in {
                name.casefold() for name in users
            }:
                st.error("Username already exists.")

            elif any(
                data.get("email", "").casefold() == email
                for data in users.values()
            ):
                st.error("An account with this email already exists.")

            elif not valid_email(email):
                st.error("Please enter a valid email address.")

            elif not valid_password(password):
                st.error(
                    "Password must contain at least 8 characters, "
                    "uppercase and lowercase letters, a number, "
                    "and a special character."
                )

            elif password != confirm_password:
                st.error("Passwords do not match.")

            else:
                users[username] = {
                    "email": email,
                    "password": hash_password(password),
                    "security_question": security_question,
                    "security_answer": hash_password(
                        security_answer.strip().casefold()
                    )
                }

                save_users(users)
                st.success(
                    "Account created successfully! Please select Login."
                )

    # -----------------------------------
    # 10. LOGIN
    # -----------------------------------

    elif page == "Login":
        st.header("Login")

        with st.form("login_form"):
            identifier = st.text_input("Username or email")
            password = st.text_input("Password", type="password")

            submitted = st.form_submit_button(
                "Login",
                use_container_width=True
            )

        if submitted:
            users = load_users()
            username = find_username(identifier, users)

            if (
                username
                and verify_password(password, users[username]["password"])
            ):
                if not JWT_SECRET:
                    st.error("JWT_SECRET is not configured.")
                else:
                    st.session_state["jwt_token"] = create_token(username)
                    st.rerun()
            else:
                st.error("Invalid username/email or password.")

    # -----------------------------------
    # 11. FORGOT PASSWORD
    # -----------------------------------

    elif page == "Forgot Password":
        st.header("Reset Your Password")

        method = st.radio(
            "Choose a recovery method",
            ["Security Question", "Email OTP"],
            horizontal=False
        )

        # Clear the selected recovery flow when the method changes.
        previous_method = st.session_state.get("recovery_method")

        if previous_method != method:
            st.session_state["recovery_method"] = method
            st.session_state["recovery_username"] = None
            st.session_state.pop("otp_hash", None)
            st.session_state.pop("otp_expiry", None)
            st.session_state.pop("otp_username", None)
            st.session_state.pop("otp_attempts", None)
            st.session_state.pop("otp_verified_username", None)

        users = load_users()

        # --------------------------------
        # METHOD A: SECURITY QUESTION
        # --------------------------------

        if method == "Security Question":
            with st.form("find_security_account"):
                identifier = st.text_input("Username or registered email")
                find_account = st.form_submit_button("Find Account")

            if find_account:
                username = find_username(identifier, load_users())

                if username:
                    st.session_state["recovery_username"] = username
                else:
                    st.session_state["recovery_username"] = None
                    st.error("No matching account was found.")

            recovery_username = st.session_state.get("recovery_username")

            if recovery_username and recovery_username in load_users():
                current_users = load_users()
                question = current_users[recovery_username].get(
                    "security_question"
                )

                st.info(f"Security question: {question}")

                with st.form("security_reset_form"):
                    answer = st.text_input(
                        "Your security answer", type="password"
                    )
                    new_password = st.text_input(
                        "New password", type="password"
                    )
                    confirm_new_password = st.text_input(
                        "Confirm new password", type="password"
                    )

                    reset_clicked = st.form_submit_button(
                        "Reset Password"
                    )

                if reset_clicked:
                    stored_answer = current_users[
                        recovery_username
                    ].get("security_answer", "")

                    answer_ok = False
                    if stored_answer:
                        try:
                            answer_ok = verify_password(
                                answer.strip().casefold(), stored_answer
                            )
                        except (ValueError, TypeError):
                            answer_ok = False

                    if not answer.strip():
                        st.error("Please enter your security answer.")
                    elif not answer_ok:
                        st.error("Incorrect security answer.")
                    elif not valid_password(new_password):
                        st.error(
                            "New password must contain at least 8 "
                            "characters, uppercase and lowercase letters, "
                            "a number, and a special character."
                        )
                    elif new_password != confirm_new_password:
                        st.error("Passwords do not match.")
                    else:
                        reset_password(recovery_username, new_password)
                        st.success(
                            "Password reset successfully. Select Login."
                        )

        # --------------------------------
        # METHOD B: EMAIL OTP
        # --------------------------------

        elif method == "Email OTP":
            st.write(
                "Enter the email address registered to your account. "
                "We'll send a one-time code if the account is found."
            )

            with st.form("send_otp_form"):
                email = st.text_input("Registered email address")
                send_clicked = st.form_submit_button("Send OTP")

            if send_clicked:
                email = email.strip().lower()
                current_users = load_users()

                username = next(
                    (
                        name for name, data in current_users.items()
                        if data.get("email", "").casefold() == email
                    ),
                    None
                )

                if not valid_email(email):
                    st.error("Please enter a valid email address.")
                elif username is None:
                    st.error(
                        "If the address belongs to a registered account, "
                        "an OTP can be sent. Check the address and try again."
                    )
                else:
                    otp = f"{secrets.randbelow(1_000_000):06d}"

                    try:
                        send_otp_email(email, otp)

                        st.session_state["otp_hash"] = hashlib.sha256(
                            otp.encode()
                        ).hexdigest()
                        st.session_state["otp_expiry"] = time.time() + 300
                        st.session_state["otp_username"] = username
                        st.session_state["otp_attempts"] = 0
                        st.session_state.pop(
                            "otp_verified_username", None
                        )

                        st.success(
                            "If delivery succeeds, an OTP has been sent. "
                            "It expires in 5 minutes."
                        )
                    except Exception:
                        st.error(
                            "The OTP email could not be sent. Check the "
                            "email configuration in Colab and try again."
                        )

            # OTP verification form
            if st.session_state.get("otp_hash"):
                with st.form("verify_otp_form"):
                    entered_otp = st.text_input(
                        "Enter the 6-digit OTP",
                        max_chars=6
                    )
                    verify_clicked = st.form_submit_button("Verify OTP")

                if verify_clicked:
                    if time.time() > st.session_state.get(
                        "otp_expiry", 0
                    ):
                        st.error("OTP expired. Please request a new one.")
                        for key in (
                            "otp_hash", "otp_expiry", "otp_username",
                            "otp_attempts"
                        ):
                            st.session_state.pop(key, None)

                    elif st.session_state.get("otp_attempts", 0) >= 5:
                        st.error(
                            "Too many attempts. Request a new OTP."
                        )
                        for key in (
                            "otp_hash", "otp_expiry", "otp_username",
                            "otp_attempts"
                        ):
                            st.session_state.pop(key, None)

                    else:
                        st.session_state["otp_attempts"] = (
                            st.session_state.get("otp_attempts", 0) + 1
                        )

                        entered_hash = hashlib.sha256(
                            entered_otp.encode()
                        ).hexdigest()

                        if (
                            len(entered_otp) == 6
                            and secrets.compare_digest(
                                entered_hash,
                                st.session_state["otp_hash"]
                            )
                        ):
                            st.session_state["otp_verified_username"] = (
                                st.session_state["otp_username"]
                            )
                            st.success(
                                "OTP verified. You can now set a new password."
                            )
                        else:
                            st.error("Invalid OTP.")

            # New password form after successful OTP verification
            verified_username = st.session_state.get(
                "otp_verified_username"
            )

            if verified_username:
                if time.time() > st.session_state.get("otp_expiry", 0):
                    st.error("OTP verification expired. Request a new OTP.")
                    for key in (
                        "otp_hash", "otp_expiry", "otp_username",
                        "otp_attempts", "otp_verified_username"
                    ):
                        st.session_state.pop(key, None)
                else:
                    with st.form("otp_new_password_form"):
                        new_password = st.text_input(
                            "New password", type="password"
                        )
                        confirm_new_password = st.text_input(
                            "Confirm new password", type="password"
                        )
                        reset_clicked = st.form_submit_button(
                            "Reset Password"
                        )

                    if reset_clicked:
                        if not valid_password(new_password):
                            st.error(
                                "New password must contain at least 8 "
                                "characters, uppercase and lowercase "
                                "letters, a number, and a special character."
                            )
                        elif new_password != confirm_new_password:
                            st.error("Passwords do not match.")
                        else:
                            reset_password(
                                verified_username, new_password
                            )
                            st.success(
                                "Password reset successfully. Select Login."
                            )


    elif page == "Admin Login":
        st.header("Admin Login")

        if st.session_state.get("admin_logged_in", False):
            st.success("Admin login successful!")
            st.subheader("Registered Users")
            users = load_users()

            col1, col2 = st.columns(2)

            with col1:
                  st.metric("Total Registered Users", len(users))

            with col2:
                  st.metric("Admin Status", "Logged In")
            if st.button("Refresh Users"):
                st.rerun()

            users = load_users()

            if users:
                user_rows = [
                    {
                        "Username": username,
                        "Email": data.get("email", "")
                    }
                    for username, data in users.items()
                ]
                
                search_text = st.text_input(
                    "Search by username or email",
                    key="search_registered_users"
                ).strip().casefold()

                filtered_rows = [
                    row for row in user_rows
                    if search_text in row["Username"].casefold()
                    or search_text in row["Email"].casefold()
                ]

                st.dataframe(
                    filtered_rows,
                    use_container_width=True,
                    hide_index=True
                )

                st.dataframe(
                    user_rows,
                    use_container_width=True,
                    hide_index=True
                )
                st.write("Total registered users:", len(user_rows))

                st.divider()
                st.subheader("Delete a Registered User")

                user_to_delete = st.selectbox(
                    "Select username to delete",
                    list(users.keys()),
                    key="delete_user_select"
                )

                confirm_delete = st.checkbox(
                    f"I confirm deletion of '{user_to_delete}'",
                    key="confirm_delete_user"
                )

                if st.button("Delete User", type="primary"):
                    if confirm_delete:
                        users.pop(user_to_delete, None)
                        save_users(users)
                        st.session_state.pop("delete_user_select", None)
                        st.session_state.pop("confirm_delete_user", None)
                        st.success(
                            f"User '{user_to_delete}' deleted successfully."
                        )
                        st.rerun()
                    else:
                        st.warning("Please confirm before deleting.")
            else:
                st.info("No registered users found.")

            if st.button("Admin Logout"):
                st.session_state.pop("admin_logged_in", None)
                st.rerun()

        else:
            with st.form("admin_login_form"):
                admin_username = st.text_input("Admin username")
                admin_password = st.text_input(
                    "Admin password",
                    type="password"
                )
                admin_submitted = st.form_submit_button(
                    "Admin Login",
                    use_container_width=True
                )

            if admin_submitted:
                if not ADMIN_USERNAME or not ADMIN_PASSWORD:
                    st.error("Admin credentials are not configured.")
                elif (
                    secrets.compare_digest(admin_username, ADMIN_USERNAME)
                    and secrets.compare_digest(admin_password, ADMIN_PASSWORD)
                ):
                    st.session_state["admin_logged_in"] = True
                    st.rerun()
                else:
                    st.error("Invalid admin username or password.")


st.caption("Infosys Springboard | Milestone 1")


                       

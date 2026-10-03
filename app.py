from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("CAM_SECRET_KEY")

# ===========================
# Authorized Users
# ===========================

USERS = {
    "manohargulla2002@gmail.com": "scrypt:32768:8:1$wHnNMQ94FU2UdMOU$380c977a24e64ed64d03ac36c9df41a13eaedae52cfba1ccea702a6d3ce2893eab3e4a41aa35099652f66ddb88c1c133726d1c78e6cb12c6de0c1dc7ade7c01a",
    "employee1@gmail.com": "scrypt:32768:8:1$SJbFKiQYpuN19bY8$2486a9a1051eec69e2a13f4a71f314a50eacf59863ec8675909bd65d036393abc4741096981cd314efe2f3ecc069417b91d43a7ec66ae9e0bbd5890a8df08149",
    "employee2@gmail.com": "scrypt:32768:8:1$Z96fCCi2f9W7jo7X$21a8dbc1d70db485e6213303aed68383a70cd76c6253d67d91e46bd7d92ceed79c1fab16016995acfb7a24d2616cc81b80406afcc272e7109cb935fbee5a268f",
    "employee3@gmail.com": "scrypt:32768:8:1$YZj5pK6GsnLNW6ma$8ce56826a65e22bee0b232d8c38dfa85dbed6cfe9aa6cb92dcddf1d7edfd1bb23995bc933c4d4f7782d0606cfd7a363e1a843161c8100fb8c331f5e75475a515",
    "employee4@gmail.com": "scrypt:32768:8:1$RGs5spTNQeOAgTzK$4f5c49d8b5bcfb94047674482f8722ef173b2b557a7bd44f2d5ab5ecd0af0a0e3c57ac486b16ed282890d63a568168c4ece6ef79ee70a6ff4f0fec3e82a08d52",
    "employee5@gmail.com": "scrypt:32768:8:1$qtQECKNNax4p4sip$6f0e9a843254790934c4a8c4c35dbd5bc890a667db3d205f4e178ea68b3fb0f0e16f21209c2ca7decf137930c95f984502063a7d98a8647a95c3476dd01151b2",
    "employee6@gmail.com": "scrypt:32768:8:1$NnfTe789mRSxo97r$0d795ca3702055453699d51c0c3efcadcfaf424d415e5772b116596feda0d6ef0313ecb24f9d9167651d44b18199dfa13681ef277155b61d150456b50d5db477",
    "employee7@gmail.com": "scrypt:32768:8:1$uUFiW9bx0nJJH0wb$4eb5043755b91d3d8e3ce3a762639b7be0cbf882007a9e59064bc0ad7a4928fccd9d6d36f22ce828ee2bf377af01aef2261ae8a59bec5fd8a057727bc4ee986e",
    "employee8@gmail.com": "scrypt:32768:8:1$SK7Gdk3bgwqIH1rZ$d6227c3891491e7499eec608eacecc76eb94964c1a11747b7290f4d481e0b2c81be65eb534efa9054157c7ec17e08fabddf3c84a48bab77d070ccfa7c3420d06",
    "employee9@gmail.com": "scrypt:32768:8:1$B8DMf4QU9lpTLDJw$9a693ecb24bff9733ebb323809ec4062235493501339ee026956caa7d9ced8aa709a16e2e0d3b901e8d9e1e560b517703a581d9b51c225f6c920f6fa2f19e92d"
    }

# ===========================
# Users Allowed to Access Secure Files
# ===========================

FILE_ACCESS_USERS = [

    "manohargulla2002@gmail.com",

    "employee1@gmail.com",

    "employee4@gmail.com"

]

# Maximum failed attempts
MAX_ATTEMPTS = 5

# Lock duration in minutes
LOCK_TIME = 15

# Store failed attempts
FAILED_ATTEMPTS ={}

# Store locked accounts
LOCKED_USERS = {}

# ===========================
# Admin User
# ===========================

ADMIN_EMAIL = "manohargulla2002@gmail.com"

# ===========================
# Login Log Function
# ===========================

def write_log(email, status, ip):

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("logs/login.log", "a") as file:
        file.write(
            f"{current_time} | Email: {email} | Status: {status} | IP: {ip}\n"
        )

# ===========================
# File Download Log Function
# ===========================

def write_file_log(email, filename, status, ip):

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("logs/file_access.log", "a") as file:

        file.write(
            f"{current_time} | Email: {email} | File: {filename} | Status: {status} | IP: {ip}\n"
        )

# ===========================
# Home Page
# ===========================
# ===========================
# Dashboard Statistics
# ===========================

def get_dashboard_stats():

    success = 0
    failed = 0
    locked = 0
    unauthorized = 0

    try:

        with open("logs/login.log", "r") as file:

            for line in file:

                if "Status: SUCCESS" in line:
                    success += 1

                elif "FAILED LOGIN" in line:
                    failed += 1

                elif "ACCOUNT LOCKED" in line:
                    locked += 1

                elif "UNAUTHORIZED EMAIL ATTEMPT" in line:
                    unauthorized += 1

    except FileNotFoundError:
        pass

    return success, failed, locked, unauthorized
@app.route('/')
def home():
    return render_template("login.html")

# ===========================
# Login Authentication
# ===========================

@app.route('/login', methods=['POST'])
def login():

    email = request.form['email']
    password = request.form['password']

    ip = request.remote_addr

    # Check if email is authorized
    if email not in USERS:

        write_log(email, "UNAUTHORIZED EMAIL ATTEMPT", ip)

        return render_template(
            "login.html",
            error="Unauthorized Email Address"
        )

    # Check if account is locked
    if email in LOCKED_USERS:

        unlock_time = LOCKED_USERS[email]

        if datetime.now() < unlock_time:

            remaining = int((unlock_time - datetime.now()).total_seconds() / 60) + 1

            write_log(email, "LOGIN BLOCKED (ACCOUNT LOCKED)", ip)

            return render_template(
                "login.html",
                error=f"Account Locked. Try again in {remaining} minute(s)."
            )

        else:
            del LOCKED_USERS[email]
            FAILED_ATTEMPTS[email] = 0

    # Correct Password
    if check_password_hash(USERS[email], password):

        FAILED_ATTEMPTS[email] = 0

        write_log(email, "SUCCESS", ip)

        session["email"] = email

        return redirect(url_for("dashboard"))

    # Wrong Password
    FAILED_ATTEMPTS[email] = FAILED_ATTEMPTS.get(email, 0) + 1

    attempts = FAILED_ATTEMPTS[email]

    if attempts >= MAX_ATTEMPTS:

        LOCKED_USERS[email] = datetime.now() + timedelta(minutes=LOCK_TIME)

        write_log(email, "ACCOUNT LOCKED", ip)

        return render_template(
            "login.html",
            error="Account Locked for 15 Minutes."
        )

    write_log(email, f"FAILED LOGIN (Attempt {attempts})", ip)

    remaining = MAX_ATTEMPTS - attempts

    return render_template(
        "login.html",
        error=f"Invalid Password. {remaining} attempt(s) remaining."
    )

# ===========================
# Dashboard Page
# ===========================

@app.route('/dashboard')
def dashboard():

    email = session.get("email")
    if not email:
        return redirect(url_for("home"))

    success, failed, locked, unauthorized = get_dashboard_stats()

    return render_template(
        "dashboard.html",
        email=email,
        success=success,
        failed=failed,
        locked=locked,
        unauthorized=unauthorized
    )

# ===========================
# Admin Dashboard
# ===========================

@app.route('/admin')
def admin():

    email = session.get("email")

    if not email:
        return redirect(url_for("home"))

    # Only Admin Can Access
    if email != ADMIN_EMAIL:
        return render_template(
            "access_denied.html",
            email=email
        )

    success, failed, locked, unauthorized = get_dashboard_stats()

    return render_template(
        "admin_dashboard.html",
        email=email,
        total_users=len(USERS),
        locked_users=len(LOCKED_USERS),
        success=success,
        failed=failed,
        unauthorized=unauthorized,
        users=USERS,
        locked_accounts=LOCKED_USERS
    )
# ===========================
# Lock User
# ===========================

@app.route('/lock_user/<email>')
def lock_user(email):

    admin = session.get("email")

    if admin != ADMIN_EMAIL:
        return redirect(url_for("home"))
    #prevent admin from locking themselves
    if email == ADMIN_EMAIL:
        return redirect(url_for("admin"))

    LOCKED_USERS[email] = datetime.now() + timedelta(minutes=LOCK_TIME)

    return redirect(url_for("admin"))
# ===========================
# Unlock User
# ===========================

@app.route('/unlock_user/<email>')
def unlock_user(email):

    admin = session.get("email")

    if admin != ADMIN_EMAIL:
        return redirect(url_for("home"))

    if email in LOCKED_USERS:
        del LOCKED_USERS[email]

    FAILED_ATTEMPTS[email] = 0

    return redirect(url_for("admin"))
    #admin account should never be unlocked manually
    if email == ADMIN_EMAIL:
        return redirect(url_for("admin"))
# ===========================
# Reset Password
# ===========================

@app.route('/reset_password/<email>', methods=['GET', 'POST'])
def reset_password(email):

    admin = session.get("email")

    if admin != ADMIN_EMAIL:
        return redirect(url_for("home"))

    if request.method == "POST":

        new_password = request.form["password"]

        USERS[email] = generate_password_hash(new_password)

        return redirect(url_for("admin"))

    return render_template(
        "reset_password.html",
        user=email
    )
# ===========================
# Security Status
# ===========================

@app.route('/security_status')
def security_status():

    email = session.get("email")

    # User must be logged in
    if not email:
        return redirect(url_for("home"))

    # Get authentication statistics
    success, failed, locked, unauthorized = get_dashboard_stats()

    # Check whether login logging is working
    login_logging = os.path.exists("logs/login.log")

    # Check whether secure documents directory exists
    secure_files = os.path.isdir("secure_documents")

    # Authentication protection
    authentication_protection = True

    # Failed login protection
    failed_login_protection = MAX_ATTEMPTS > 0

    # Account lockout protection
    account_lockout = (
        MAX_ATTEMPTS > 0 and
        LOCK_TIME > 0
    )

    # Unauthorized email detection
    unauthorized_detection = True

    # File access control
    file_access_control = len(FILE_ACCESS_USERS) > 0

    # Determine overall security status
    if (
        authentication_protection
        and failed_login_protection
        and account_lockout
        and unauthorized_detection
        and secure_files
        and file_access_control
        and login_logging
    ):
        overall_status = "SYSTEM SECURE"
        overall_color = "green"
    else:
        overall_status = "SECURITY WARNING"
        overall_color = "orange"

    return render_template(
        "security_status.html",

        email=email,

        success=success,
        failed=failed,
        locked=locked,
        unauthorized=unauthorized,

        authentication_protection=authentication_protection,
        failed_login_protection=failed_login_protection,
        account_lockout=account_lockout,
        unauthorized_detection=unauthorized_detection,

        secure_files=secure_files,
        file_access_control=file_access_control,
        login_logging=login_logging,

        overall_status=overall_status,
        overall_color=overall_color
    )
# ===========================
# Reports Page
# ===========================

@app.route('/reports')
def reports():

    email = session.get("email")

    # User must be logged in
    if not email:
        return redirect(url_for("home"))

    return render_template(
        "reports.html",
        email=email
    )
# ===========================
# Security Summary Report
# ===========================

@app.route('/report/security_summary')
def security_summary_report():

    email = session.get("email")

    # User must be logged in
    if not email:
        return redirect(url_for("home"))

    # Get authentication statistics
    success, failed, locked, unauthorized = get_dashboard_stats()

    # Total registered users
    total_users = len(USERS)

    # Currently locked users
    locked_users = len(LOCKED_USERS)

    # Determine overall security status
    if unauthorized > 0 or locked_users > 0:
        overall_status = "SECURITY EVENTS DETECTED"
    else:
        overall_status = "SYSTEM SECURE"

    return render_template(
        "security_summary_report.html",
        email=email,
        total_users=total_users,
        locked_users=locked_users,
        success=success,
        failed=failed,
        locked=locked,
        unauthorized=unauthorized,
        overall_status=overall_status
    )
# ===========================
# Authentication Report
# ===========================

@app.route('/report/authentication')
def authentication_report():

    email = session.get("email")

    # User must be logged in
    if not email:
        return redirect(url_for("home"))

    logs = []

    success = 0
    failed = 0
    locked = 0
    unauthorized = 0

    try:

        with open("logs/login.log", "r") as file:

            for line in reversed(file.readlines()):

                parts = line.strip().split(" | ")

                if len(parts) != 4:
                    continue

                event_time = parts[0]
                user_email = parts[1].replace("Email: ", "")
                status = parts[2].replace("Status: ", "")
                ip = parts[3].replace("IP: ", "")

                # Count authentication events
                if status == "SUCCESS":
                    success += 1

                elif status == "FAILED LOGIN":
                    failed += 1

                elif status == "ACCOUNT LOCKED":
                    locked += 1

                elif status == "UNAUTHORIZED EMAIL ATTEMPT":
                    unauthorized += 1

                # Add event to report
                logs.append({
                    "time": event_time,
                    "email": user_email,
                    "status": status,
                    "ip": ip
                })

    except FileNotFoundError:
        pass

    total_events = success + failed + locked + unauthorized

    return render_template(
        "authentication_report.html",
        email=email,
        logs=logs,
        total_events=total_events,
        success=success,
        failed=failed,
        locked=locked,
        unauthorized=unauthorized
    )

# ===========================
# Secure Files
# ===========================

@app.route('/secure_files')
def secure_files():

    email = session.get("email")

    if not email:
        return redirect(url_for("home"))

    if email not in FILE_ACCESS_USERS:
        return render_template(
            "access_denied.html",
            email=email
        )

    return render_template(
        "secure_files.html",
        email=email
    )
# ===========================
# Download Secure Files
# ===========================

@app.route('/download/<filename>')
def download_file(filename):

    email = session.get("email")

    # User must be logged in
    if not email:
        return redirect(url_for("home"))

    # Check file permission
    if email not in FILE_ACCESS_USERS:
        return render_template(
            "access_denied.html",
            email=email
        )

    ip = request.remote_addr

    write_file_log(
        email,
        filename,
        "DOWNLOADED",
        ip
    )

    return send_from_directory(
        "secure_documents",
        filename,
        as_attachment=True
    )


# ===========================
# Login History Page
# ===========================

@app.route('/login_history')
def login_history():

    logs = []

    search = request.args.get("search", "").lower()

    try:

        with open("logs/login.log", "r") as file:

            for line in reversed(file.readlines()):

                parts = line.strip().split(" | ")

                if len(parts) == 4:

                    email = parts[1].replace("Email: ", "")

                    if search and search not in email.lower():
                        continue

                    logs.append({
                        "time": parts[0],
                        "email": email,
                        "status": parts[2].replace("Status: ", ""),
                        "ip": parts[3].replace("IP: ", "")
                    })

    except FileNotFoundError:
        pass

    return render_template(
        "login_history.html",
        logs=logs,
        search=search
    )


# ===========================
# Run Flask
# ===========================

# ===========================
# File Access Report
# ===========================

@app.route('/report/file_access')
def file_access_report():

    email = session.get("email")

    # User must be logged in
    if not email:
        return redirect(url_for("home"))

    logs = []

    total_downloads = 0
    unique_users = set()
    unique_files = set()

    try:

        with open("logs/file_access.log", "r") as file:

            for line in reversed(file.readlines()):

                parts = line.strip().split(" | ")

                if len(parts) == 5:

                    time = parts[0]

                    user = parts[1].replace("Email: ", "")

                    filename = parts[2].replace("File: ", "")

                    status = parts[3].replace("Status: ", "")

                    ip = parts[4].replace("IP: ", "")

                    # Statistics
                    if status == "DOWNLOADED":
                        total_downloads += 1

                    unique_users.add(user)

                    unique_files.add(filename)

                    logs.append({
                        "time": time,
                        "email": user,
                        "filename": filename,
                        "status": status,
                        "ip": ip
                    })

    except FileNotFoundError:

        pass

    return render_template(
        "file_access_report.html",
        logs=logs,
        total_downloads=total_downloads,
        unique_users=len(unique_users),
        unique_files=len(unique_files)
    )
# ===========================
# User Security Report
# ===========================

@app.route('/report/user_security')
def user_security_report():

    email = session.get("email")

    # User must be logged in
    if not email:
        return redirect(url_for("home"))

    # ===========================
    # Calculate Statistics
    # ===========================

    total_users = len(USERS)

    locked_users = len(LOCKED_USERS)

    active_users = total_users - locked_users

    admin_users = 0

    file_access_users = len(FILE_ACCESS_USERS)

    restricted_users = 0

    users = []

    # ===========================
    # Build User Security Data
    # ===========================

    for user in USERS:

        # Determine Role

        if user == ADMIN_EMAIL:

            role = "Administrator"

            admin_users += 1

        else:

            role = "Employee"

        # Determine Account Status

        if user in LOCKED_USERS:

            account_status = "Locked"

            security_status = "Attention Required"

        else:

            account_status = "Active"

            security_status = "Protected"

        # Determine File Access

        if user in FILE_ACCESS_USERS:

            file_access = "Allowed"

        else:

            file_access = "Restricted"

            restricted_users += 1

        users.append({

            "email": user,

            "role": role,

            "account_status": account_status,

            "file_access": file_access,

            "security_status": security_status

        })

    return render_template(

        "user_security_report.html",

        users=users,

        total_users=total_users,

        active_users=active_users,

        locked_users=locked_users,

        admin_users=admin_users,

        file_access_users=file_access_users,

        restricted_users=restricted_users

    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)



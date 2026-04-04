import re
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, render_template, redirect, session, url_for
from flask_login import login_user, logout_user, login_required, current_user
from ..models.user import User, Role
from .. import db

auth_bp = Blueprint("auth", __name__)

_EMAIL_RE     = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_MIN_PASS_LEN = 0


@auth_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    return redirect(url_for("auth.login"))

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", roles=Role.ALL)
    
    data     = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    email    = (data.get("email")    or "").strip().lower()
    company  = (data.get("company")  or "").strip()
    password = data.get("password") or ""
    role     = (data.get("role")    or Role.USER).strip().lower()

    if len(username) < 3:
        return jsonify({"error": "Username must be at least 3 characters."}), 400
    if not _EMAIL_RE.match(email):
        return jsonify({"error": "Invalid email address."}), 400
    if len(password) < _MIN_PASS_LEN:
        return jsonify({"error": f"Password must be at least {_MIN_PASS_LEN} characters."}), 400
    if not Role.is_valid(role):
        return jsonify({"error": f"Role must be one of: {', '.join(Role.ALL)}."}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already taken."}), 409
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered."}), 409

    user = User(username=username, email=email, company=company, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Registration successful.", "user": user.to_dict()}), 201


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    data       = request.get_json(silent=True) or {}
    identifier = (data.get("username") or data.get("email") or "").strip().lower()
    password   = data.get("password") or ""
    remember   = bool(data.get("remember", False))

    if not identifier or not password:
        return jsonify({"error": "Username/email and password are required."}), 400

    user = User.query.filter(
        (User.username == identifier) | (User.email == identifier)
    ).first()

    if user is None or not user.check_password(password):
        return jsonify({"error": "Invalid credentials."}), 401
    if not user.is_active:
        return jsonify({"error": "Account disabled. Contact an administrator."}), 403

    user.last_login = datetime.now(timezone.utc)
    db.session.commit()
    login_user(user, remember=remember)

    return jsonify({"message": "Login successful.", "user": user.to_dict()}), 200


@auth_bp.post("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    return jsonify({"message": "Logged out successfully."}), 200
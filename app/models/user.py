from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db


class Role:
    CUSTOMER   = "customer"
    TECHNICIAN = "technician"
    MANAGER    = "manager"
    ADMIN  = "admin"

    ALL    = [CUSTOMER, TECHNICIAN, MANAGER, ADMIN]
    _LEVEL = {CUSTOMER: 0, TECHNICIAN: 1, MANAGER: 2, ADMIN: 3}

    @classmethod
    def is_valid(cls, role):
        return role in cls.ALL

    @classmethod
    def has_permission(cls, user_role, required_role):
        return cls._LEVEL.get(user_role, -1) >= cls._LEVEL.get(required_role, 999)


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80),  unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    company       = db.Column(db.String(120), nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role          = db.Column(db.String(20),  nullable=False, default=Role.CUSTOMER)
    active        = db.Column(db.Boolean, default=True, nullable=False)
    created_at    = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_login    = db.Column(db.DateTime, nullable=True)

    @property
    def is_active(self):
        return self.active

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == Role.ADMIN

    def is_editor_or_above(self):
        return Role.has_permission(self.role, Role.EDITOR)

    def to_dict(self):
        return {
            "id":         self.id,
            "username":   self.username,
            "email":      self.email,
            "company":    self.company,
            "role":       self.role,
            "active":     self.active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }
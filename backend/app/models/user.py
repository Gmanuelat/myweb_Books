"""
User model
"""
from datetime import datetime
from flask_login import UserMixin
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app import db, login_manager

ph = PasswordHasher()


class User(UserMixin, db.Model):
    """User account model"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Preferences stored as JSON
    preferences = db.Column(db.JSON, default=dict)

    # Relationships
    library_items = db.relationship('UserLibrary', back_populates='user', lazy='dynamic',
                                     cascade='all, delete-orphan')
    reading_progress = db.relationship('ReadingProgress', back_populates='user', lazy='dynamic',
                                        cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', back_populates='user', lazy='dynamic',
                                 cascade='all, delete-orphan')
    reading_goals = db.relationship('ReadingGoal', back_populates='user', lazy='dynamic',
                                     cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = ph.hash(password)

    def check_password(self, password):
        """Verify password"""
        try:
            ph.verify(self.password_hash, password)
            # Rehash if needed (argon2 auto-upgrade)
            if ph.check_needs_rehash(self.password_hash):
                self.password_hash = ph.hash(password)
            return True
        except VerifyMismatchError:
            return False

    def get_preference(self, key, default=None):
        """Get a user preference"""
        if self.preferences is None:
            return default
        return self.preferences.get(key, default)

    def set_preference(self, key, value):
        """Set a user preference"""
        if self.preferences is None:
            self.preferences = {}
        self.preferences[key] = value

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'displayName': self.display_name,
            'preferences': self.preferences or {},
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))

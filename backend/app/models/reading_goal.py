"""
Reading Goal model - tracks user's yearly reading goals
"""
from datetime import datetime
from app import db


class ReadingGoal(db.Model):
    """User's yearly reading goals"""
    __tablename__ = 'reading_goals'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'),
                        nullable=False, index=True)

    year = db.Column(db.Integer, nullable=False)
    target_books = db.Column(db.Integer, default=12)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='reading_goals')

    # Unique constraint - one goal per user per year
    __table_args__ = (
        db.UniqueConstraint('user_id', 'year', name='unique_user_year_goal'),
    )

    def to_dict(self, include_stats=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'userId': self.user_id,
            'year': self.year,
            'targetBooks': self.target_books,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
        }
        return data

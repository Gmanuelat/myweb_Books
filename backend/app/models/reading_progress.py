"""
Reading Progress model - tracks user's reading position in a book
"""
from datetime import datetime
from app import db


class ReadingProgress(db.Model):
    """Track reading progress per user per book"""
    __tablename__ = 'reading_progress'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'),
                        nullable=False, index=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id', ondelete='CASCADE'),
                        nullable=False, index=True)

    # Progress tracking
    last_page = db.Column(db.Integer, default=1)
    last_cfi = db.Column(db.String(500), nullable=True)  # EPUB CFI location
    percentage = db.Column(db.Float, default=0.0)

    # Timestamps
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_read_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='reading_progress')
    book = db.relationship('Book', back_populates='reading_progress')

    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('user_id', 'book_id', name='unique_user_book_progress'),
    )

    def to_dict(self, include_book=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'userId': self.user_id,
            'bookId': self.book_id,
            'lastPage': self.last_page,
            'lastCfi': self.last_cfi,
            'percentage': self.percentage,
            'startedAt': self.started_at.isoformat() if self.started_at else None,
            'lastReadAt': self.last_read_at.isoformat() if self.last_read_at else None,
        }
        if include_book and self.book:
            data['book'] = self.book.to_dict()
        return data

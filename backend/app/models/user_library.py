"""
User Library model - tracks which books a user has in their library
"""
from datetime import datetime
from enum import Enum
from app import db


class LibraryStatus(str, Enum):
    """Reading status enum"""
    WANT_TO_READ = 'want_to_read'
    READING = 'reading'
    FINISHED = 'finished'


class UserLibrary(db.Model):
    """User's library - books they're tracking"""
    __tablename__ = 'user_library'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'),
                        nullable=False, index=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id', ondelete='CASCADE'),
                        nullable=False, index=True)

    status = db.Column(db.Enum(LibraryStatus), default=LibraryStatus.WANT_TO_READ)

    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    finished_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    user = db.relationship('User', back_populates='library_items')
    book = db.relationship('Book', back_populates='library_items')

    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('user_id', 'book_id', name='unique_user_book'),
    )

    def to_dict(self, include_book=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'userId': self.user_id,
            'bookId': self.book_id,
            'status': self.status.value,
            'addedAt': self.added_at.isoformat() if self.added_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
            'finishedAt': self.finished_at.isoformat() if self.finished_at else None,
        }
        if include_book and self.book:
            data['book'] = self.book.to_dict()
        return data

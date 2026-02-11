"""
Favorite model - tracks user's favorite books
"""
from datetime import datetime
from app import db


class Favorite(db.Model):
    """User's favorite books"""
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'),
                        nullable=False, index=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id', ondelete='CASCADE'),
                        nullable=False, index=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='favorites')
    book = db.relationship('Book', back_populates='favorites')

    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('user_id', 'book_id', name='unique_user_favorite'),
    )

    def to_dict(self, include_book=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'userId': self.user_id,
            'bookId': self.book_id,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }
        if include_book and self.book:
            data['book'] = self.book.to_dict()
        return data

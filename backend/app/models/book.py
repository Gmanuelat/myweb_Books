"""
Book model
"""
from datetime import datetime
from app import db


class Book(db.Model):
    """Book metadata model"""
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    year = db.Column(db.Integer, nullable=True)
    language = db.Column(db.String(50), default='English')
    description = db.Column(db.Text, nullable=True)

    # File information
    cover_path = db.Column(db.String(255), nullable=True)
    file_path = db.Column(db.String(255), nullable=True)
    file_format = db.Column(db.String(20), default='epub')
    total_pages = db.Column(db.Integer, default=0)

    # Metadata
    source_url = db.Column(db.String(500), nullable=True)
    license = db.Column(db.String(100), default='Public Domain')
    genres = db.Column(db.JSON, default=list)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    library_items = db.relationship('UserLibrary', back_populates='book', lazy='dynamic')
    reading_progress = db.relationship('ReadingProgress', back_populates='book', lazy='dynamic')
    favorites = db.relationship('Favorite', back_populates='book', lazy='dynamic')

    def to_dict(self, include_file_path=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'slug': self.slug,
            'title': self.title,
            'author': self.author,
            'year': self.year,
            'language': self.language,
            'description': self.description,
            'coverPath': self.cover_path,
            'totalPages': self.total_pages,
            'sourceUrl': self.source_url,
            'license': self.license,
            'genres': self.genres or [],
        }
        if include_file_path:
            data['filePath'] = self.file_path
            data['fileFormat'] = self.file_format
        return data

    def __repr__(self):
        return f'<Book {self.slug}: {self.title}>'

#!/usr/bin/env python3
"""
Database seeding script
Loads books from seed_library.json into the database
"""
import os
import sys
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Book


# Mapping of book IDs from seed_library.json to file slugs
BOOK_SLUG_MAP = {
    1: 'pride_and_prejudice',
    2: 'moby_dick',
    3: 'frankenstein',
    4: 'dracula',
    5: 'sherlock_holmes',
    6: 'alice_in_wonderland',
    7: 'great_gatsby',
    8: 'dorian_gray',
    9: 'tale_of_two_cities',
    10: 'jane_eyre',
    11: 'wuthering_heights',
    12: 'crime_and_punishment',
    13: 'tom_sawyer',
    14: 'huckleberry_finn',
    15: 'war_and_peace',
    16: 'count_of_monte_cristo',
    17: 'wizard_of_oz',
    18: 'treasure_island',
    19: 'jekyll_and_hyde',
    20: 'little_women',
}

# Genre assignments based on book content
BOOK_GENRES = {
    'pride_and_prejudice': ['Classic', 'Romance', 'Fiction'],
    'moby_dick': ['Classic', 'Adventure', 'Fiction'],
    'frankenstein': ['Classic', 'Gothic', 'Horror', 'Science Fiction'],
    'dracula': ['Classic', 'Gothic', 'Horror'],
    'sherlock_holmes': ['Classic', 'Mystery', 'Fiction'],
    'alice_in_wonderland': ['Classic', 'Fantasy', 'Fiction'],
    'great_gatsby': ['Classic', 'Literary Fiction'],
    'dorian_gray': ['Classic', 'Gothic', 'Literary Fiction'],
    'tale_of_two_cities': ['Classic', 'Historical Fiction'],
    'jane_eyre': ['Classic', 'Romance', 'Gothic'],
    'wuthering_heights': ['Classic', 'Romance', 'Gothic'],
    'crime_and_punishment': ['Classic', 'Literary Fiction'],
    'tom_sawyer': ['Classic', 'Adventure', 'Fiction'],
    'huckleberry_finn': ['Classic', 'Adventure', 'Fiction'],
    'war_and_peace': ['Classic', 'Historical Fiction', 'Literary Fiction'],
    'count_of_monte_cristo': ['Classic', 'Adventure', 'Fiction'],
    'wizard_of_oz': ['Classic', 'Fantasy', 'Fiction'],
    'treasure_island': ['Classic', 'Adventure', 'Fiction'],
    'jekyll_and_hyde': ['Classic', 'Gothic', 'Horror'],
    'little_women': ['Classic', 'Fiction'],
}


def get_epub_path(slug, books_dir):
    """Check if EPUB file exists and return path"""
    epub_path = os.path.join(books_dir, f'{slug}.epub')
    if os.path.exists(epub_path):
        return f'books/{slug}.epub'
    return None


def seed_books():
    """Load books from seed_library.json"""
    # Get paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(script_dir)
    project_root = os.path.dirname(backend_dir)
    seed_file = os.path.join(project_root, 'seed_library.json')
    books_dir = os.path.join(project_root, 'books')

    # Load seed data
    print(f"Loading seed data from: {seed_file}")
    with open(seed_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    books_data = data.get('books', [])
    print(f"Found {len(books_data)} books in seed file")

    # Create app context
    app = create_app()

    with app.app_context():
        # Create tables if they don't exist
        db.create_all()

        added = 0
        updated = 0

        for book_data in books_data:
            book_id = book_data['id']
            slug = BOOK_SLUG_MAP.get(book_id)

            if not slug:
                print(f"  WARNING: No slug mapping for book ID {book_id}: {book_data['title']}")
                continue

            # Check for existing book
            existing = Book.query.filter_by(slug=slug).first()

            # Get file path
            file_path = get_epub_path(slug, books_dir)

            book_attrs = {
                'slug': slug,
                'title': book_data['title'],
                'author': book_data['author'],
                'year': book_data.get('year'),
                'language': book_data.get('language', 'English'),
                'description': book_data.get('description'),
                'source_url': book_data.get('source_url'),
                'license': book_data.get('license', 'Public Domain'),
                'file_path': file_path,
                'file_format': 'epub' if file_path else None,
                'genres': BOOK_GENRES.get(slug, ['Classic', 'Fiction']),
            }

            if existing:
                # Update existing book
                for key, value in book_attrs.items():
                    setattr(existing, key, value)
                updated += 1
                print(f"  Updated: {book_data['title']} ({slug})")
            else:
                # Create new book
                book = Book(**book_attrs)
                db.session.add(book)
                added += 1
                print(f"  Added: {book_data['title']} ({slug})")

        db.session.commit()
        print(f"\nSeeding complete: {added} added, {updated} updated")


def create_test_user():
    """Create a test user for development"""
    from app.models import User

    app = create_app()

    with app.app_context():
        # Check if test user exists
        existing = User.query.filter_by(email='test@example.com').first()
        if existing:
            print("Test user already exists")
            return

        user = User(
            email='test@example.com',
            display_name='Test User',
            preferences={'font': 'Inter', 'fontSize': 16}
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        print("Created test user: test@example.com / password123")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Seed the database')
    parser.add_argument('--test-user', action='store_true',
                        help='Also create a test user')

    args = parser.parse_args()

    seed_books()

    if args.test_user:
        create_test_user()

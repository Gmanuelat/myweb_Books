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
    21: 'don_quixote',
    22: 'the_odyssey',
    23: 'hamlet',
    24: 'romeo_and_juliet',
    25: 'macbeth',
    26: 'gullivers_travels',
    27: 'robinson_crusoe',
    28: 'oliver_twist',
    29: 'great_expectations',
    30: 'david_copperfield',
    31: 'sense_and_sensibility',
    32: 'emma',
    33: 'northanger_abbey',
    34: 'anna_karenina',
    35: 'brothers_karamazov',
    36: 'middlemarch',
    37: 'tess_of_the_durbervilles',
    38: 'far_from_the_madding_crowd',
    39: 'les_miserables',
    40: 'hunchback_of_notre_dame',
    41: 'twenty_thousand_leagues',
    42: 'around_the_world_in_80_days',
    43: 'journey_to_center_of_earth',
    44: 'time_machine',
    45: 'war_of_the_worlds',
    46: 'invisible_man',
    47: 'scarlet_letter',
    48: 'red_badge_of_courage',
    49: 'call_of_the_wild',
    50: 'white_fang',
    51: 'kidnapped',
    52: 'jungle_book',
    53: 'importance_of_being_earnest',
    54: 'three_musketeers',
    55: 'pinocchio',
    56: 'ethan_frome',
    57: 'portrait_of_a_lady',
    58: 'turn_of_the_screw',
    59: 'the_awakening',
    60: 'candide',
    61: 'death_of_ivan_ilyich',
    62: 'notes_from_underground',
    63: 'heart_of_darkness',
    64: 'secret_garden',
    65: 'phantom_of_the_opera',
    66: 'kim',
    67: 'anne_of_green_gables',
    68: 'connecticut_yankee',
    69: 'prince_and_the_pauper',
    70: 'twenty_years_after',
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
    'don_quixote': ['Classic', 'Adventure', 'Satire', 'Fiction'],
    'the_odyssey': ['Classic', 'Epic', 'Adventure', 'Mythology'],
    'hamlet': ['Classic', 'Drama', 'Tragedy'],
    'romeo_and_juliet': ['Classic', 'Drama', 'Romance', 'Tragedy'],
    'macbeth': ['Classic', 'Drama', 'Tragedy'],
    'gullivers_travels': ['Classic', 'Satire', 'Adventure', 'Fantasy'],
    'robinson_crusoe': ['Classic', 'Adventure', 'Fiction'],
    'oliver_twist': ['Classic', 'Fiction', 'Social Commentary'],
    'great_expectations': ['Classic', 'Fiction', 'Literary Fiction'],
    'david_copperfield': ['Classic', 'Fiction', 'Literary Fiction'],
    'sense_and_sensibility': ['Classic', 'Romance', 'Fiction'],
    'emma': ['Classic', 'Romance', 'Comedy', 'Fiction'],
    'northanger_abbey': ['Classic', 'Gothic', 'Satire', 'Romance'],
    'anna_karenina': ['Classic', 'Romance', 'Literary Fiction', 'Tragedy'],
    'brothers_karamazov': ['Classic', 'Literary Fiction', 'Philosophical'],
    'middlemarch': ['Classic', 'Literary Fiction', 'Social Commentary'],
    'tess_of_the_durbervilles': ['Classic', 'Tragedy', 'Literary Fiction'],
    'far_from_the_madding_crowd': ['Classic', 'Romance', 'Fiction'],
    'les_miserables': ['Classic', 'Historical Fiction', 'Literary Fiction'],
    'hunchback_of_notre_dame': ['Classic', 'Historical Fiction', 'Romance', 'Tragedy'],
    'twenty_thousand_leagues': ['Classic', 'Science Fiction', 'Adventure'],
    'around_the_world_in_80_days': ['Classic', 'Adventure', 'Fiction'],
    'journey_to_center_of_earth': ['Classic', 'Science Fiction', 'Adventure'],
    'time_machine': ['Classic', 'Science Fiction'],
    'war_of_the_worlds': ['Classic', 'Science Fiction'],
    'invisible_man': ['Classic', 'Science Fiction', 'Horror'],
    'scarlet_letter': ['Classic', 'Literary Fiction', 'Historical Fiction'],
    'red_badge_of_courage': ['Classic', 'Historical Fiction', 'War'],
    'call_of_the_wild': ['Classic', 'Adventure', 'Fiction'],
    'white_fang': ['Classic', 'Adventure', 'Fiction'],
    'kidnapped': ['Classic', 'Adventure', 'Historical Fiction'],
    'jungle_book': ['Classic', 'Adventure', 'Fantasy', 'Fiction'],
    'importance_of_being_earnest': ['Classic', 'Drama', 'Comedy', 'Satire'],
    'three_musketeers': ['Classic', 'Adventure', 'Historical Fiction'],
    'pinocchio': ['Classic', 'Fantasy', 'Fiction', 'Children'],
    'ethan_frome': ['Classic', 'Tragedy', 'Literary Fiction'],
    'portrait_of_a_lady': ['Classic', 'Literary Fiction', 'Fiction'],
    'turn_of_the_screw': ['Classic', 'Gothic', 'Horror', 'Mystery'],
    'the_awakening': ['Classic', 'Literary Fiction', 'Fiction'],
    'candide': ['Classic', 'Satire', 'Philosophical', 'Fiction'],
    'death_of_ivan_ilyich': ['Classic', 'Literary Fiction', 'Philosophical'],
    'notes_from_underground': ['Classic', 'Literary Fiction', 'Philosophical'],
    'heart_of_darkness': ['Classic', 'Literary Fiction', 'Adventure'],
    'secret_garden': ['Classic', 'Fiction', 'Children'],
    'phantom_of_the_opera': ['Classic', 'Gothic', 'Romance', 'Mystery'],
    'kim': ['Classic', 'Adventure', 'Historical Fiction'],
    'anne_of_green_gables': ['Classic', 'Fiction', 'Children'],
    'connecticut_yankee': ['Classic', 'Satire', 'Science Fiction', 'Adventure'],
    'prince_and_the_pauper': ['Classic', 'Historical Fiction', 'Adventure'],
    'twenty_years_after': ['Classic', 'Adventure', 'Historical Fiction'],
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

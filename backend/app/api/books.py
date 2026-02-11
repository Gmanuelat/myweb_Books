"""
Books API routes
"""
from flask import Blueprint, request, jsonify
from flask_login import current_user

from app.models import Book, Favorite

bp = Blueprint('books', __name__)


@bp.route('', methods=['GET'])
def list_books():
    """List all books with optional filtering"""
    # Query parameters
    search = request.args.get('search', '').strip()
    author = request.args.get('author', '').strip()
    year_from = request.args.get('yearFrom', type=int)
    year_to = request.args.get('yearTo', type=int)
    genre = request.args.get('genre', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('perPage', 50, type=int)

    # Limit per_page
    per_page = min(per_page, 100)

    # Build query
    query = Book.query

    if search:
        search_term = f'%{search}%'
        query = query.filter(
            (Book.title.ilike(search_term)) |
            (Book.author.ilike(search_term)) |
            (Book.description.ilike(search_term))
        )

    if author:
        query = query.filter(Book.author.ilike(f'%{author}%'))

    if year_from:
        query = query.filter(Book.year >= year_from)

    if year_to:
        query = query.filter(Book.year <= year_to)

    if genre:
        query = query.filter(Book.genres.contains([genre]))

    # Order by title
    query = query.order_by(Book.title)

    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    # Get user's favorites if logged in
    user_favorites = set()
    if current_user.is_authenticated:
        user_favorites = {f.book_id for f in current_user.favorites}

    # Build response
    books = []
    for book in pagination.items:
        book_dict = book.to_dict()
        book_dict['isFavorite'] = book.id in user_favorites
        books.append(book_dict)

    return jsonify({
        'books': books,
        'total': pagination.total,
        'page': pagination.page,
        'perPage': pagination.per_page,
        'totalPages': pagination.pages,
        'hasNext': pagination.has_next,
        'hasPrev': pagination.has_prev
    })


@bp.route('/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """Get a single book by ID"""
    book = Book.query.get_or_404(book_id)

    book_dict = book.to_dict(include_file_path=True)

    # Add favorite status if logged in
    if current_user.is_authenticated:
        is_fav = Favorite.query.filter_by(
            user_id=current_user.id,
            book_id=book.id
        ).first() is not None
        book_dict['isFavorite'] = is_fav

    return jsonify(book_dict)


@bp.route('/slug/<slug>', methods=['GET'])
def get_book_by_slug(slug):
    """Get a single book by slug"""
    book = Book.query.filter_by(slug=slug).first_or_404()

    book_dict = book.to_dict(include_file_path=True)

    # Add favorite status if logged in
    if current_user.is_authenticated:
        is_fav = Favorite.query.filter_by(
            user_id=current_user.id,
            book_id=book.id
        ).first() is not None
        book_dict['isFavorite'] = is_fav

    return jsonify(book_dict)


@bp.route('/authors', methods=['GET'])
def list_authors():
    """Get list of unique authors"""
    authors = (
        Book.query
        .with_entities(Book.author)
        .distinct()
        .order_by(Book.author)
        .all()
    )
    return jsonify({'authors': [a[0] for a in authors]})


@bp.route('/genres', methods=['GET'])
def list_genres():
    """Get list of unique genres"""
    # Since genres is a JSON array, we need to handle this differently
    # For now, return a static list based on common genres
    genres = [
        'Fiction',
        'Classic',
        'Gothic',
        'Horror',
        'Romance',
        'Adventure',
        'Mystery',
        'Fantasy',
        'Science Fiction',
        'Historical Fiction',
        'Literary Fiction'
    ]
    return jsonify({'genres': genres})

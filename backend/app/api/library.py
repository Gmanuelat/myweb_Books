"""
User Library API routes (favorites, progress, goals)
"""
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from app import db
from app.models import (
    Book, UserLibrary, LibraryStatus,
    ReadingProgress, Favorite, ReadingGoal
)

bp = Blueprint('library', __name__)


# ============================================================
# LIBRARY DASHBOARD
# ============================================================

@bp.route('/library', methods=['GET'])
@login_required
def get_library():
    """Get user's complete library data for dashboard"""
    user_id = current_user.id
    current_year = datetime.now().year

    # Get library items by status
    currently_reading = (
        UserLibrary.query
        .filter_by(user_id=user_id, status=LibraryStatus.READING)
        .all()
    )

    finished_books = (
        UserLibrary.query
        .filter_by(user_id=user_id, status=LibraryStatus.FINISHED)
        .order_by(UserLibrary.finished_at.desc())
        .limit(20)
        .all()
    )

    want_to_read = (
        UserLibrary.query
        .filter_by(user_id=user_id, status=LibraryStatus.WANT_TO_READ)
        .order_by(UserLibrary.added_at.desc())
        .all()
    )

    # Get favorites
    favorites = (
        Favorite.query
        .filter_by(user_id=user_id)
        .order_by(Favorite.created_at.desc())
        .all()
    )

    # Get reading progress for currently reading books
    progress_map = {}
    if currently_reading:
        book_ids = [item.book_id for item in currently_reading]
        progress_items = (
            ReadingProgress.query
            .filter(ReadingProgress.user_id == user_id)
            .filter(ReadingProgress.book_id.in_(book_ids))
            .all()
        )
        progress_map = {p.book_id: p for p in progress_items}

    # Get current year's goal
    goal = ReadingGoal.query.filter_by(user_id=user_id, year=current_year).first()

    # Count books finished this year
    year_start = datetime(current_year, 1, 1)
    books_finished_this_year = (
        UserLibrary.query
        .filter_by(user_id=user_id, status=LibraryStatus.FINISHED)
        .filter(UserLibrary.finished_at >= year_start)
        .count()
    )

    # Build response
    def format_reading_item(item):
        data = item.to_dict(include_book=True)
        if item.book_id in progress_map:
            progress = progress_map[item.book_id]
            data['progress'] = {
                'lastPage': progress.last_page,
                'lastCfi': progress.last_cfi,
                'percentage': progress.percentage,
                'lastReadAt': progress.last_read_at.isoformat() if progress.last_read_at else None
            }
        return data

    return jsonify({
        'currentlyReading': [format_reading_item(item) for item in currently_reading],
        'finished': [item.to_dict(include_book=True) for item in finished_books],
        'wantToRead': [item.to_dict(include_book=True) for item in want_to_read],
        'favorites': [f.to_dict(include_book=True) for f in favorites],
        'stats': {
            'totalBooks': len(currently_reading) + len(finished_books) + len(want_to_read),
            'currentlyReading': len(currently_reading),
            'finished': len(finished_books),
            'favorites': len(favorites),
            'wantToRead': len(want_to_read),
        },
        'goal': {
            'year': current_year,
            'target': goal.target_books if goal else 0,
            'completed': books_finished_this_year,
            'progress': (
                round((books_finished_this_year / goal.target_books) * 100)
                if goal and goal.target_books > 0
                else 0
            )
        }
    })


# ============================================================
# FAVORITES
# ============================================================

@bp.route('/favorites', methods=['GET'])
@login_required
def get_favorites():
    """Get user's favorite books"""
    favorites = (
        Favorite.query
        .filter_by(user_id=current_user.id)
        .order_by(Favorite.created_at.desc())
        .all()
    )
    return jsonify({
        'favorites': [f.to_dict(include_book=True) for f in favorites]
    })


@bp.route('/favorites/<int:book_id>', methods=['POST'])
@login_required
def toggle_favorite(book_id):
    """Toggle a book's favorite status"""
    book = Book.query.get_or_404(book_id)

    existing = Favorite.query.filter_by(
        user_id=current_user.id,
        book_id=book_id
    ).first()

    if existing:
        # Remove from favorites
        db.session.delete(existing)
        db.session.commit()
        return jsonify({
            'isFavorite': False,
            'message': 'Removed from favorites'
        })
    else:
        # Add to favorites
        favorite = Favorite(user_id=current_user.id, book_id=book_id)
        db.session.add(favorite)
        db.session.commit()
        return jsonify({
            'isFavorite': True,
            'message': 'Added to favorites'
        })


@bp.route('/favorites/<int:book_id>', methods=['DELETE'])
@login_required
def remove_favorite(book_id):
    """Remove a book from favorites"""
    favorite = Favorite.query.filter_by(
        user_id=current_user.id,
        book_id=book_id
    ).first()

    if favorite:
        db.session.delete(favorite)
        db.session.commit()

    return jsonify({'message': 'Removed from favorites'})


# ============================================================
# READING PROGRESS
# ============================================================

@bp.route('/progress/<int:book_id>', methods=['GET'])
@login_required
def get_progress(book_id):
    """Get reading progress for a book"""
    book = Book.query.get_or_404(book_id)

    progress = ReadingProgress.query.filter_by(
        user_id=current_user.id,
        book_id=book_id
    ).first()

    if not progress:
        return jsonify({
            'bookId': book_id,
            'lastPage': 1,
            'lastCfi': None,
            'percentage': 0,
            'lastReadAt': None,
            'totalPages': book.total_pages
        })

    return jsonify({
        'bookId': book_id,
        'lastPage': progress.last_page,
        'lastCfi': progress.last_cfi,
        'percentage': progress.percentage,
        'lastReadAt': progress.last_read_at.isoformat() if progress.last_read_at else None,
        'totalPages': book.total_pages
    })


@bp.route('/progress/<int:book_id>', methods=['PATCH'])
@login_required
def update_progress(book_id):
    """Update reading progress for a book"""
    book = Book.query.get_or_404(book_id)
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Get or create progress
    progress = ReadingProgress.query.filter_by(
        user_id=current_user.id,
        book_id=book_id
    ).first()

    if not progress:
        progress = ReadingProgress(
            user_id=current_user.id,
            book_id=book_id
        )
        db.session.add(progress)

    # Update fields
    if 'lastPage' in data:
        progress.last_page = data['lastPage']

    if 'lastCfi' in data:
        progress.last_cfi = data['lastCfi']

    if 'percentage' in data:
        progress.percentage = data['percentage']

    progress.last_read_at = datetime.utcnow()

    # Auto-update library status to "reading" if not already
    library_item = UserLibrary.query.filter_by(
        user_id=current_user.id,
        book_id=book_id
    ).first()

    if not library_item:
        library_item = UserLibrary(
            user_id=current_user.id,
            book_id=book_id,
            status=LibraryStatus.READING
        )
        db.session.add(library_item)
    elif library_item.status == LibraryStatus.WANT_TO_READ:
        library_item.status = LibraryStatus.READING

    db.session.commit()

    return jsonify({
        'message': 'Progress updated',
        'lastPage': progress.last_page,
        'lastCfi': progress.last_cfi,
        'percentage': progress.percentage,
        'lastReadAt': progress.last_read_at.isoformat()
    })


# ============================================================
# LIBRARY STATUS
# ============================================================

@bp.route('/library/<int:book_id>', methods=['GET'])
@login_required
def get_library_item(book_id):
    """Get library status for a book"""
    book = Book.query.get_or_404(book_id)

    item = UserLibrary.query.filter_by(
        user_id=current_user.id,
        book_id=book_id
    ).first()

    if not item:
        return jsonify({
            'bookId': book_id,
            'inLibrary': False,
            'status': None
        })

    return jsonify({
        'bookId': book_id,
        'inLibrary': True,
        'status': item.status.value,
        'addedAt': item.added_at.isoformat() if item.added_at else None,
        'finishedAt': item.finished_at.isoformat() if item.finished_at else None
    })


@bp.route('/library/<int:book_id>', methods=['PATCH'])
@login_required
def update_library_status(book_id):
    """Update library status for a book"""
    book = Book.query.get_or_404(book_id)
    data = request.get_json()

    if not data or 'status' not in data:
        return jsonify({'error': 'Status required'}), 400

    status_str = data['status']
    try:
        status = LibraryStatus(status_str)
    except ValueError:
        return jsonify({
            'error': f'Invalid status. Must be one of: {[s.value for s in LibraryStatus]}'
        }), 400

    # Get or create library item
    item = UserLibrary.query.filter_by(
        user_id=current_user.id,
        book_id=book_id
    ).first()

    if not item:
        item = UserLibrary(
            user_id=current_user.id,
            book_id=book_id
        )
        db.session.add(item)

    item.status = status

    # Set finished_at if marking as finished
    if status == LibraryStatus.FINISHED:
        item.finished_at = datetime.utcnow()
    else:
        item.finished_at = None

    db.session.commit()

    return jsonify({
        'message': 'Library status updated',
        'status': item.status.value,
        'finishedAt': item.finished_at.isoformat() if item.finished_at else None
    })


@bp.route('/library/<int:book_id>', methods=['DELETE'])
@login_required
def remove_from_library(book_id):
    """Remove a book from user's library"""
    item = UserLibrary.query.filter_by(
        user_id=current_user.id,
        book_id=book_id
    ).first()

    if item:
        db.session.delete(item)
        db.session.commit()

    return jsonify({'message': 'Removed from library'})


# ============================================================
# READING GOALS
# ============================================================

@bp.route('/goals', methods=['GET'])
@login_required
def get_goals():
    """Get user's reading goals"""
    current_year = datetime.now().year

    # Get current year's goal
    goal = ReadingGoal.query.filter_by(
        user_id=current_user.id,
        year=current_year
    ).first()

    # Count books finished this year
    year_start = datetime(current_year, 1, 1)
    books_finished = (
        UserLibrary.query
        .filter_by(user_id=current_user.id, status=LibraryStatus.FINISHED)
        .filter(UserLibrary.finished_at >= year_start)
        .count()
    )

    return jsonify({
        'year': current_year,
        'target': goal.target_books if goal else 0,
        'completed': books_finished,
        'progress': (
            round((books_finished / goal.target_books) * 100)
            if goal and goal.target_books > 0
            else 0
        )
    })


@bp.route('/goals', methods=['PATCH'])
@login_required
def update_goal():
    """Update reading goal for current year"""
    data = request.get_json()

    if not data or 'target' not in data:
        return jsonify({'error': 'Target required'}), 400

    target = data['target']
    if not isinstance(target, int) or target < 1 or target > 365:
        return jsonify({'error': 'Target must be between 1 and 365'}), 400

    current_year = datetime.now().year

    # Get or create goal
    goal = ReadingGoal.query.filter_by(
        user_id=current_user.id,
        year=current_year
    ).first()

    if not goal:
        goal = ReadingGoal(
            user_id=current_user.id,
            year=current_year
        )
        db.session.add(goal)

    goal.target_books = target
    db.session.commit()

    # Get completed count
    year_start = datetime(current_year, 1, 1)
    books_finished = (
        UserLibrary.query
        .filter_by(user_id=current_user.id, status=LibraryStatus.FINISHED)
        .filter(UserLibrary.finished_at >= year_start)
        .count()
    )

    return jsonify({
        'message': 'Goal updated',
        'year': current_year,
        'target': goal.target_books,
        'completed': books_finished,
        'progress': round((books_finished / goal.target_books) * 100) if goal.target_books > 0 else 0
    })


# ============================================================
# RECENTLY READ
# ============================================================

@bp.route('/recent', methods=['GET'])
@login_required
def get_recent():
    """Get recently read books"""
    limit = request.args.get('limit', 10, type=int)
    limit = min(limit, 50)

    recent = (
        ReadingProgress.query
        .filter_by(user_id=current_user.id)
        .order_by(ReadingProgress.last_read_at.desc())
        .limit(limit)
        .all()
    )

    return jsonify({
        'books': [p.to_dict(include_book=True) for p in recent]
    })

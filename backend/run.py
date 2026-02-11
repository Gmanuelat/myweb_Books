"""
Application entry point
"""
import os
from app import create_app, db
from app.models import User, Book, UserLibrary, ReadingProgress, Favorite, ReadingGoal

app = create_app()


@app.shell_context_processor
def make_shell_context():
    """Make models available in flask shell"""
    return {
        'db': db,
        'User': User,
        'Book': Book,
        'UserLibrary': UserLibrary,
        'ReadingProgress': ReadingProgress,
        'Favorite': Favorite,
        'ReadingGoal': ReadingGoal
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))  # Default to 5001 (5000 often used by AirPlay on macOS)
    app.run(host='0.0.0.0', port=port, debug=True)

# MyWeb Books

A web application for reading public domain books online. Features user authentication, reading progress tracking, favorites, and reading goals.

## Architecture

- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Backend**: Python Flask + MySQL
- **EPUB Reader**: epub.js library
- **Authentication**: Session-based with Flask-Login
- **Password Hashing**: Argon2

## Project Structure

```
myweb_Books/
├── backend/                    # Flask API backend
│   ├── app/
│   │   ├── api/               # API routes
│   │   │   ├── auth.py        # Authentication endpoints
│   │   │   ├── books.py       # Books endpoints
│   │   │   └── library.py     # User library endpoints
│   │   ├── models/            # SQLAlchemy models
│   │   └── __init__.py        # App factory
│   ├── migrations/            # SQL migration files
│   ├── scripts/               # Utility scripts
│   │   ├── init_db.py         # Initialize database
│   │   └── seed_db.py         # Seed books from JSON
│   ├── config.py              # Configuration
│   ├── requirements.txt       # Python dependencies
│   └── run.py                 # Entry point
├── books/                     # EPUB files
├── css/                       # Stylesheets
├── js/                        # JavaScript
│   ├── api.js                 # API client
│   └── app.js                 # Main app logic
├── index.html                 # Home page
├── reader.html                # EPUB reader
├── my-books.html              # User dashboard
├── login.html                 # Login page
├── signup.html                # Signup page
├── styles.css                 # Main styles
└── seed_library.json          # Book metadata
```

## Setup Instructions

### Prerequisites

- Python 3.9+
- MySQL 8.0+ (or MariaDB)
- Node.js (optional, for serving frontend)

### 1. Database Setup

```bash
# Log into MySQL
mysql -u root -p

# Create database
CREATE DATABASE myweb_books CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Or run the migration file
mysql -u root -p < backend/migrations/001_initial_schema.sql
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file and configure
cp .env.example .env
# Edit .env with your database credentials

# Initialize database tables
python scripts/init_db.py

# Seed books from JSON
python scripts/seed_db.py

# (Optional) Create test user
python scripts/seed_db.py --test-user
# Creates: test@example.com / password123

# Start development server
python run.py
```

The backend will run at `http://localhost:5000`

### 3. Frontend Setup

For development, you can use Python's built-in server:

```bash
# From the project root (not backend)
cd /path/to/myweb_Books
python -m http.server 8080
```

Or use any static file server like `live-server`:

```bash
npm install -g live-server
live-server --port=8080
```

The frontend will be available at `http://localhost:8080`

### 4. API Configuration

Update the API base URL in `js/api.js` if needed:

```javascript
const API = {
    BASE_URL: 'http://localhost:5000/api',
    // ...
};
```

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup` | Register new user |
| POST | `/api/auth/login` | Log in |
| POST | `/api/auth/logout` | Log out |
| GET | `/api/auth/me` | Get current user |
| PATCH | `/api/auth/me` | Update profile |

### Books

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/books` | List all books |
| GET | `/api/books/:id` | Get book by ID |
| GET | `/api/books/slug/:slug` | Get book by slug |

### User Library

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/me/library` | Get dashboard data |
| PATCH | `/api/me/library/:bookId` | Update book status |
| DELETE | `/api/me/library/:bookId` | Remove from library |

### Favorites

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/me/favorites` | Get favorites |
| POST | `/api/me/favorites/:bookId` | Toggle favorite |

### Reading Progress

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/me/progress/:bookId` | Get progress |
| PATCH | `/api/me/progress/:bookId` | Update progress |

### Reading Goals

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/me/goals` | Get current goal |
| PATCH | `/api/me/goals` | Update goal |

## Features

### Reader Features
- EPUB rendering with epub.js
- Page navigation (arrows, keyboard, swipe)
- Reading progress saved automatically
- Font selection (8 fonts available)
- Font size controls
- Line height options
- Theme selection (Light, Sepia, Dark)
- Fullscreen mode

### Library Features
- Currently Reading with progress tracking
- Favorites
- Finished books
- Want to Read list
- Yearly reading goals with progress

## Production Deployment

### Backend (Render/Fly.io/VPS)

1. Set production environment variables:
```bash
FLASK_ENV=production
SECRET_KEY=<random-64-char-string>
DATABASE_URL=mysql+pymysql://user:pass@host/db
FRONTEND_URL=https://your-domain.com
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_SAMESITE=Strict
```

2. Use gunicorn for production:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### Frontend (Static Hosting)

1. Update `js/api.js` with production API URL
2. Deploy to Netlify, Vercel, or any static host
3. Configure CORS on backend to allow frontend domain

### Security Recommendations

- Use HTTPS everywhere
- Set strong SECRET_KEY in production
- Enable rate limiting (Flask-Limiter)
- Validate all user inputs
- Keep dependencies updated
- Use environment variables for secrets
- Enable CORS only for specific origins

## Development

### Adding New Books

1. Add EPUB file to `books/` folder
2. Add metadata to `seed_library.json`
3. Add slug mapping in `scripts/seed_db.py`
4. Run `python scripts/seed_db.py`

### Database Migrations

For schema changes, create a new migration file:
```bash
backend/migrations/002_add_feature.sql
```

## License

Books are public domain from Project Gutenberg. Application code is open source.

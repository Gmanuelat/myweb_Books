/**
 * MyWeb Books - Main Application JavaScript
 * Handles feature cards, favorites, reading goals, and UI interactions
 */

// ============================================================
// FAVORITES SYSTEM
// ============================================================

const Favorites = {
    STORAGE_KEY: 'myweb_favorites',

    /**
     * Get all favorite books
     * @returns {Array} Array of favorite book objects
     */
    getAll() {
        try {
            return JSON.parse(localStorage.getItem(this.STORAGE_KEY)) || [];
        } catch (e) {
            console.warn('Error reading favorites:', e);
            return [];
        }
    },

    /**
     * Add a book to favorites
     * @param {Object} book - Book object with id, title, author, year, coverClass
     * @returns {boolean} Success status
     */
    add(book) {
        try {
            const favorites = this.getAll();

            // Check if already exists
            if (favorites.some(f => f.id === book.id)) {
                return false;
            }

            favorites.push({
                ...book,
                addedAt: Date.now()
            });

            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(favorites));
            this.dispatchEvent('add', book);
            return true;
        } catch (e) {
            console.error('Error adding favorite:', e);
            return false;
        }
    },

    /**
     * Remove a book from favorites
     * @param {string} bookId - Book identifier
     * @returns {boolean} Success status
     */
    remove(bookId) {
        try {
            const favorites = this.getAll();
            const filtered = favorites.filter(f => f.id !== bookId);

            if (filtered.length === favorites.length) {
                return false; // Book wasn't in favorites
            }

            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(filtered));
            this.dispatchEvent('remove', { id: bookId });
            return true;
        } catch (e) {
            console.error('Error removing favorite:', e);
            return false;
        }
    },

    /**
     * Toggle a book's favorite status
     * @param {Object} book - Book object
     * @returns {boolean} New favorite status (true = now favorite)
     */
    toggle(book) {
        if (this.isFavorite(book.id)) {
            this.remove(book.id);
            return false;
        } else {
            this.add(book);
            return true;
        }
    },

    /**
     * Check if a book is in favorites
     * @param {string} bookId - Book identifier
     * @returns {boolean}
     */
    isFavorite(bookId) {
        return this.getAll().some(f => f.id === bookId);
    },

    /**
     * Get favorites count
     * @returns {number}
     */
    count() {
        return this.getAll().length;
    },

    /**
     * Clear all favorites
     */
    clear() {
        localStorage.removeItem(this.STORAGE_KEY);
        this.dispatchEvent('clear', null);
    },

    /**
     * Dispatch custom event for favorites changes
     */
    dispatchEvent(action, data) {
        window.dispatchEvent(new CustomEvent('favoritesChanged', {
            detail: { action, data }
        }));
    }
};

// ============================================================
// READING GOALS SYSTEM
// ============================================================

const ReadingGoals = {
    STORAGE_KEY: 'myweb_reading_goals',

    /**
     * Get current year's goal data
     * @returns {Object} Goal object with target, completed, year
     */
    getCurrentGoal() {
        try {
            const data = JSON.parse(localStorage.getItem(this.STORAGE_KEY)) || {};
            const currentYear = new Date().getFullYear();

            return data[currentYear] || {
                target: 0,
                completed: 0,
                year: currentYear,
                booksCompleted: []
            };
        } catch (e) {
            console.warn('Error reading goals:', e);
            return { target: 0, completed: 0, year: new Date().getFullYear(), booksCompleted: [] };
        }
    },

    /**
     * Set yearly reading goal
     * @param {number} target - Number of books to read
     * @returns {boolean} Success status
     */
    setGoal(target) {
        try {
            const data = JSON.parse(localStorage.getItem(this.STORAGE_KEY)) || {};
            const currentYear = new Date().getFullYear();

            data[currentYear] = {
                ...data[currentYear],
                target: parseInt(target, 10) || 0,
                year: currentYear,
                completed: data[currentYear]?.completed || 0,
                booksCompleted: data[currentYear]?.booksCompleted || []
            };

            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(data));
            this.dispatchEvent('goalSet', data[currentYear]);
            return true;
        } catch (e) {
            console.error('Error setting goal:', e);
            return false;
        }
    },

    /**
     * Mark a book as completed for the goal
     * @param {Object} book - Book object
     * @returns {boolean} Success status
     */
    markCompleted(book) {
        try {
            const data = JSON.parse(localStorage.getItem(this.STORAGE_KEY)) || {};
            const currentYear = new Date().getFullYear();

            if (!data[currentYear]) {
                data[currentYear] = {
                    target: 0,
                    completed: 0,
                    year: currentYear,
                    booksCompleted: []
                };
            }

            // Check if book already completed this year
            if (data[currentYear].booksCompleted.some(b => b.id === book.id)) {
                return false;
            }

            data[currentYear].booksCompleted.push({
                id: book.id,
                title: book.title,
                completedAt: Date.now()
            });
            data[currentYear].completed = data[currentYear].booksCompleted.length;

            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(data));
            this.dispatchEvent('bookCompleted', data[currentYear]);
            return true;
        } catch (e) {
            console.error('Error marking book completed:', e);
            return false;
        }
    },

    /**
     * Get progress percentage
     * @returns {number} Progress percentage (0-100)
     */
    getProgress() {
        const goal = this.getCurrentGoal();
        if (goal.target === 0) return 0;
        return Math.min(100, Math.round((goal.completed / goal.target) * 100));
    },

    /**
     * Prompt user to set a reading goal
     */
    promptForGoal() {
        const currentGoal = this.getCurrentGoal();
        const currentYear = new Date().getFullYear();

        const defaultValue = currentGoal.target > 0 ? currentGoal.target : 12;
        const input = prompt(
            `Set your ${currentYear} reading goal.\n\nHow many books do you want to read this year?`,
            defaultValue
        );

        if (input === null) return; // User cancelled

        const target = parseInt(input, 10);

        if (isNaN(target) || target < 1) {
            alert('Please enter a valid number greater than 0.');
            return;
        }

        if (target > 365) {
            alert('That\'s an ambitious goal! Maximum is 365 books per year.');
            return;
        }

        this.setGoal(target);
        this.showGoalConfirmation(target);
    },

    /**
     * Show confirmation after setting goal
     */
    showGoalConfirmation(target) {
        const currentGoal = this.getCurrentGoal();
        const remaining = target - currentGoal.completed;

        let message = `Your reading goal is set to ${target} books for ${currentGoal.year}!`;

        if (currentGoal.completed > 0) {
            message += `\n\nYou've already completed ${currentGoal.completed} book(s).`;
            if (remaining > 0) {
                message += `\n${remaining} more to go!`;
            } else {
                message += `\nCongratulations, you've reached your goal!`;
            }
        }

        alert(message);
    },

    /**
     * Dispatch custom event for goal changes
     */
    dispatchEvent(action, data) {
        window.dispatchEvent(new CustomEvent('readingGoalChanged', {
            detail: { action, data }
        }));
    }
};

// ============================================================
// READING PROGRESS SYSTEM
// ============================================================

const ReadingProgress = {
    STORAGE_KEY: 'myweb_reading_progress',

    /**
     * Get all reading progress
     * @returns {Object} Progress data keyed by book slug
     */
    getAll() {
        try {
            return JSON.parse(localStorage.getItem(this.STORAGE_KEY)) || {};
        } catch (e) {
            return {};
        }
    },

    /**
     * Get progress for a specific book
     * @param {string} bookSlug - Book identifier
     * @returns {Object|null} Progress data or null
     */
    get(bookSlug) {
        return this.getAll()[bookSlug] || null;
    },

    /**
     * Get recently read books (sorted by last read date)
     * @param {number} limit - Maximum number of books to return
     * @returns {Array} Array of progress objects with book slugs
     */
    getRecentlyRead(limit = 5) {
        const all = this.getAll();
        return Object.entries(all)
            .map(([slug, data]) => ({ slug, ...data }))
            .sort((a, b) => b.lastRead - a.lastRead)
            .slice(0, limit);
    }
};

// ============================================================
// FEATURE CARDS FUNCTIONALITY
// ============================================================

const FeatureCards = {
    /**
     * Initialize feature card click handlers
     */
    init() {
        const featureCards = document.querySelectorAll('.feature-card');

        featureCards.forEach((card, index) => {
            // Add cursor pointer and hover effect
            card.style.cursor = 'pointer';

            card.addEventListener('click', () => {
                this.handleCardClick(index);
            });

            // Add keyboard accessibility
            card.setAttribute('tabindex', '0');
            card.setAttribute('role', 'button');

            card.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.handleCardClick(index);
                }
            });
        });
    },

    /**
     * Handle feature card click based on index
     * @param {number} index - Card index (0, 1, or 2)
     */
    handleCardClick(index) {
        switch (index) {
            case 0: // "Read Free Library Books Online"
                this.navigateToBrowse();
                break;
            case 1: // "Set a Yearly Reading Goal"
                ReadingGoals.promptForGoal();
                break;
            case 2: // "Keep Track of your Favorite Books"
                this.navigateToMyBooks();
                break;
        }
    },

    /**
     * Navigate to browse/library section
     */
    navigateToBrowse() {
        // Scroll to the first books section
        const booksSection = document.querySelector('.books-section');
        if (booksSection) {
            booksSection.scrollIntoView({ behavior: 'smooth' });
        } else {
            // If no section, navigate to browse page
            window.location.href = 'browse.html';
        }
    },

    /**
     * Navigate to My Books page
     */
    navigateToMyBooks() {
        window.location.href = 'my-books.html';
    }
};

// ============================================================
// BOOK CARDS - ADD FAVORITE BUTTONS
// ============================================================

const BookCards = {
    /**
     * Initialize book cards with favorite buttons
     */
    init() {
        const bookCards = document.querySelectorAll('.book-card');

        bookCards.forEach(card => {
            this.addFavoriteButton(card);
        });
    },

    /**
     * Extract book data from a book card element
     * @param {HTMLElement} card - Book card element
     * @returns {Object} Book data
     */
    getBookData(card) {
        const cover = card.querySelector('.book-cover');
        const title = card.querySelector('h4')?.textContent || 'Unknown';
        const author = card.querySelector('.book-author')?.textContent || 'Unknown';
        const year = card.querySelector('.book-year')?.textContent || '';
        const readLink = card.querySelector('.btn-read');

        // Generate ID from title (lowercase, underscores)
        const id = title.toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '');

        // Get cover class for styling
        const coverClass = Array.from(cover?.classList || [])
            .find(c => c !== 'book-cover' && c !== 'book-cover-content') || '';

        // Get reader link
        const readerUrl = readLink?.getAttribute('href') || '';

        return { id, title, author, year, coverClass, readerUrl };
    },

    /**
     * Add favorite button to a book card
     * @param {HTMLElement} card - Book card element
     */
    addFavoriteButton(card) {
        const bookData = this.getBookData(card);

        // Create favorite button
        const favBtn = document.createElement('button');
        favBtn.className = 'btn-favorite';
        favBtn.setAttribute('aria-label', 'Add to favorites');
        favBtn.setAttribute('title', 'Add to favorites');

        // Set initial state
        const isFav = Favorites.isFavorite(bookData.id);
        favBtn.innerHTML = this.getHeartIcon(isFav);
        if (isFav) {
            favBtn.classList.add('is-favorite');
        }

        // Click handler
        favBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();

            const nowFavorite = Favorites.toggle(bookData);
            favBtn.innerHTML = this.getHeartIcon(nowFavorite);
            favBtn.classList.toggle('is-favorite', nowFavorite);

            // Show feedback
            this.showFeedback(favBtn, nowFavorite ? 'Added to favorites!' : 'Removed from favorites');
        });

        // Add button to card
        const cover = card.querySelector('.book-cover');
        if (cover) {
            cover.style.position = 'relative';
            cover.appendChild(favBtn);
        }
    },

    /**
     * Get heart icon SVG
     * @param {boolean} filled - Whether heart should be filled
     * @returns {string} SVG HTML
     */
    getHeartIcon(filled) {
        if (filled) {
            return `<svg viewBox="0 0 24 24" fill="#e94560" stroke="#e94560" stroke-width="2">
                <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
            </svg>`;
        }
        return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
        </svg>`;
    },

    /**
     * Show temporary feedback message
     * @param {HTMLElement} element - Element to show feedback near
     * @param {string} message - Feedback message
     */
    showFeedback(element, message) {
        // Remove existing feedback
        const existing = document.querySelector('.favorite-feedback');
        if (existing) existing.remove();

        const feedback = document.createElement('div');
        feedback.className = 'favorite-feedback';
        feedback.textContent = message;
        document.body.appendChild(feedback);

        // Position near the button
        const rect = element.getBoundingClientRect();
        feedback.style.position = 'fixed';
        feedback.style.left = `${rect.left + rect.width / 2}px`;
        feedback.style.top = `${rect.top - 40}px`;
        feedback.style.transform = 'translateX(-50%)';

        // Animate and remove
        setTimeout(() => {
            feedback.classList.add('fade-out');
            setTimeout(() => feedback.remove(), 300);
        }, 1500);
    }
};

// ============================================================
// SEARCH FUNCTIONALITY
// ============================================================

const Search = {
    init() {
        const searchInput = document.querySelector('.search-bar input');
        if (!searchInput) return;

        searchInput.addEventListener('input', (e) => {
            this.handleSearch(e.target.value);
        });

        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.handleSearch(e.target.value);
            }
        });
    },

    handleSearch(query) {
        const normalizedQuery = query.toLowerCase().trim();
        const bookCards = document.querySelectorAll('.book-card');

        bookCards.forEach(card => {
            const title = card.querySelector('h4')?.textContent.toLowerCase() || '';
            const author = card.querySelector('.book-author')?.textContent.toLowerCase() || '';

            const matches = !normalizedQuery ||
                title.includes(normalizedQuery) ||
                author.includes(normalizedQuery);

            card.style.display = matches ? '' : 'none';
        });
    }
};

// ============================================================
// INITIALIZATION
// ============================================================

document.addEventListener('DOMContentLoaded', () => {
    // Initialize all modules
    FeatureCards.init();
    BookCards.init();
    Search.init();

    // Add dynamic styles for favorite buttons
    const style = document.createElement('style');
    style.textContent = `
        .btn-favorite {
            position: absolute;
            top: 8px;
            right: 8px;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background: rgba(0, 0, 0, 0.6);
            border: none;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 6px;
            transition: all 0.2s ease;
            z-index: 10;
        }

        .btn-favorite:hover {
            background: rgba(0, 0, 0, 0.8);
            transform: scale(1.1);
        }

        .btn-favorite svg {
            width: 100%;
            height: 100%;
            color: #fff;
        }

        .btn-favorite.is-favorite svg {
            color: #e94560;
        }

        .favorite-feedback {
            background: #e94560;
            color: #fff;
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 0.85rem;
            font-weight: 500;
            z-index: 10000;
            pointer-events: none;
            animation: fadeIn 0.2s ease;
        }

        .favorite-feedback.fade-out {
            animation: fadeOut 0.3s ease forwards;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateX(-50%) translateY(10px); }
            to { opacity: 1; transform: translateX(-50%) translateY(0); }
        }

        @keyframes fadeOut {
            from { opacity: 1; transform: translateX(-50%) translateY(0); }
            to { opacity: 0; transform: translateX(-50%) translateY(-10px); }
        }

        .feature-card {
            transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
            border: 2px solid transparent;
        }

        .feature-card:hover {
            border-color: #e94560;
        }

        .feature-card:focus {
            outline: none;
            border-color: #e94560;
            box-shadow: 0 0 0 3px rgba(233, 69, 96, 0.3);
        }
    `;
    document.head.appendChild(style);
});

// Export modules for use in other files
window.MyWebBooks = {
    Favorites,
    ReadingGoals,
    ReadingProgress
};

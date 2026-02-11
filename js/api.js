/**
 * MyWeb Books - API Client
 * Handles all communication with the backend
 */

const API = {
    // Base URL - change this based on environment
    BASE_URL: 'http://localhost:5001/api',

    // Current user cache
    _currentUser: null,
    _authChecked: false,

    /**
     * Make an API request
     */
    async request(endpoint, options = {}) {
        const url = `${this.BASE_URL}${endpoint}`;

        const config = {
            credentials: 'include', // Include cookies for session auth
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        if (options.body && typeof options.body === 'object') {
            config.body = JSON.stringify(options.body);
        }

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new APIError(data.error || 'Request failed', response.status, data);
            }

            return data;
        } catch (error) {
            if (error instanceof APIError) throw error;
            throw new APIError(error.message || 'Network error', 0);
        }
    },

    // ============================================================
    // AUTHENTICATION
    // ============================================================

    async signup(email, password, displayName = '') {
        const data = await this.request('/auth/signup', {
            method: 'POST',
            body: { email, password, displayName }
        });
        this._currentUser = data.user;
        this._authChecked = true;
        window.dispatchEvent(new CustomEvent('authChanged', { detail: { user: data.user } }));
        return data;
    },

    async login(email, password, remember = true) {
        const data = await this.request('/auth/login', {
            method: 'POST',
            body: { email, password, remember }
        });
        this._currentUser = data.user;
        this._authChecked = true;
        window.dispatchEvent(new CustomEvent('authChanged', { detail: { user: data.user } }));
        return data;
    },

    async logout() {
        try {
            await this.request('/auth/logout', { method: 'POST' });
        } catch (e) {
            // Ignore logout errors
        }
        this._currentUser = null;
        this._authChecked = true;
        window.dispatchEvent(new CustomEvent('authChanged', { detail: { user: null } }));
    },

    async getCurrentUser() {
        if (this._authChecked && this._currentUser !== undefined) {
            return this._currentUser;
        }

        try {
            const data = await this.request('/auth/me');
            this._currentUser = data.authenticated ? data.user : null;
            this._authChecked = true;
            return this._currentUser;
        } catch (e) {
            this._currentUser = null;
            this._authChecked = true;
            return null;
        }
    },

    async updateProfile(updates) {
        const data = await this.request('/auth/me', {
            method: 'PATCH',
            body: updates
        });
        this._currentUser = data.user;
        return data;
    },

    isLoggedIn() {
        return this._currentUser !== null;
    },

    // ============================================================
    // BOOKS
    // ============================================================

    async getBooks(params = {}) {
        const query = new URLSearchParams();
        if (params.search) query.set('search', params.search);
        if (params.author) query.set('author', params.author);
        if (params.genre) query.set('genre', params.genre);
        if (params.page) query.set('page', params.page);
        if (params.perPage) query.set('perPage', params.perPage);

        const queryString = query.toString();
        return this.request(`/books${queryString ? '?' + queryString : ''}`);
    },

    async getBook(bookId) {
        return this.request(`/books/${bookId}`);
    },

    async getBookBySlug(slug) {
        return this.request(`/books/slug/${slug}`);
    },

    // ============================================================
    // USER LIBRARY
    // ============================================================

    async getLibrary() {
        return this.request('/me/library');
    },

    async updateLibraryStatus(bookId, status) {
        return this.request(`/me/library/${bookId}`, {
            method: 'PATCH',
            body: { status }
        });
    },

    async removeFromLibrary(bookId) {
        return this.request(`/me/library/${bookId}`, { method: 'DELETE' });
    },

    // ============================================================
    // FAVORITES
    // ============================================================

    async getFavorites() {
        return this.request('/me/favorites');
    },

    async toggleFavorite(bookId) {
        return this.request(`/me/favorites/${bookId}`, { method: 'POST' });
    },

    async removeFavorite(bookId) {
        return this.request(`/me/favorites/${bookId}`, { method: 'DELETE' });
    },

    // ============================================================
    // READING PROGRESS
    // ============================================================

    async getProgress(bookId) {
        return this.request(`/me/progress/${bookId}`);
    },

    async updateProgress(bookId, progress) {
        return this.request(`/me/progress/${bookId}`, {
            method: 'PATCH',
            body: progress
        });
    },

    async getRecentlyRead(limit = 10) {
        return this.request(`/me/recent?limit=${limit}`);
    },

    // ============================================================
    // READING GOALS
    // ============================================================

    async getGoals() {
        return this.request('/me/goals');
    },

    async updateGoal(target) {
        return this.request('/me/goals', {
            method: 'PATCH',
            body: { target }
        });
    }
};


/**
 * Custom API Error class
 */
class APIError extends Error {
    constructor(message, status, data = {}) {
        super(message);
        this.name = 'APIError';
        this.status = status;
        this.data = data;
    }

    isAuthError() {
        return this.status === 401;
    }
}


/**
 * Auth UI Helper - manages login/logout UI state
 */
const AuthUI = {
    init() {
        // Check auth status on page load
        this.checkAuth();

        // Listen for auth changes
        window.addEventListener('authChanged', (e) => {
            this.updateUI(e.detail.user);
        });
    },

    async checkAuth() {
        const user = await API.getCurrentUser();
        this.updateUI(user);
        return user;
    },

    updateUI(user) {
        // Update navbar buttons
        const navRight = document.querySelector('.nav-right');
        if (!navRight) return;

        // Find or create auth buttons container
        let authContainer = navRight.querySelector('.auth-buttons');
        if (!authContainer) {
            authContainer = document.createElement('div');
            authContainer.className = 'auth-buttons';
            navRight.appendChild(authContainer);
        }

        // Remove old signup button if exists
        const oldSignup = navRight.querySelector('.btn-signup');
        if (oldSignup) oldSignup.remove();

        if (user) {
            // Logged in - show user menu
            authContainer.innerHTML = `
                <div class="user-menu">
                    <button class="user-menu-btn" id="user-menu-btn">
                        <span class="user-avatar">${this.getInitials(user)}</span>
                        <span class="user-name">${user.displayName || user.email.split('@')[0]}</span>
                    </button>
                    <div class="user-dropdown" id="user-dropdown">
                        <a href="my-books.html">My Books</a>
                        <button id="logout-btn">Log Out</button>
                    </div>
                </div>
            `;

            // Toggle dropdown
            const menuBtn = document.getElementById('user-menu-btn');
            const dropdown = document.getElementById('user-dropdown');

            menuBtn?.addEventListener('click', (e) => {
                e.stopPropagation();
                dropdown.classList.toggle('show');
            });

            document.addEventListener('click', () => {
                dropdown?.classList.remove('show');
            });

            // Logout handler
            document.getElementById('logout-btn')?.addEventListener('click', async () => {
                await API.logout();
                window.location.href = 'index.html';
            });
        } else {
            // Logged out - show login/signup buttons
            authContainer.innerHTML = `
                <a href="login.html" class="btn-login">Log In</a>
                <a href="signup.html" class="btn-signup">Sign Up</a>
            `;
        }
    },

    getInitials(user) {
        if (user.displayName) {
            return user.displayName.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
        }
        return user.email[0].toUpperCase();
    },

    requireAuth(redirectUrl = null) {
        if (!API.isLoggedIn()) {
            const redirect = redirectUrl || window.location.href;
            window.location.href = `login.html?redirect=${encodeURIComponent(redirect)}`;
            return false;
        }
        return true;
    }
};


// Export for use in other scripts
window.API = API;
window.APIError = APIError;
window.AuthUI = AuthUI;

/**
 * Modal System
 * Custom modals to replace browser prompts
 */

const Modal = {
    // Currently open modal
    current: null,

    /**
     * Create and show a modal
     */
    create(options) {
        const {
            title = 'Modal',
            content = '',
            onSave = null,
            onCancel = null,
            saveText = 'Save',
            cancelText = 'Cancel',
            showCancel = true
        } = options;

        // Create backdrop
        const backdrop = document.createElement('div');
        backdrop.className = 'modal-backdrop';
        backdrop.id = 'modal-backdrop';

        // Create modal
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.id = 'modal';
        modal.innerHTML = `
            <div class="modal-header">
                <h2 class="modal-title">${title}</h2>
                <button class="modal-close" aria-label="Close">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M18 6L6 18M6 6l12 12"/>
                    </svg>
                </button>
            </div>
            <div class="modal-body">
                ${content}
            </div>
            <div class="modal-footer">
                ${showCancel ? `<button class="modal-btn modal-btn-secondary" id="modal-cancel">${cancelText}</button>` : ''}
                <button class="modal-btn modal-btn-primary" id="modal-save">${saveText}</button>
            </div>
        `;

        // Add to DOM
        document.body.appendChild(backdrop);
        document.body.appendChild(modal);

        // Prevent body scroll
        document.body.style.overflow = 'hidden';

        // Animate in
        requestAnimationFrame(() => {
            backdrop.classList.add('open');
            modal.classList.add('open');
        });

        // Store reference
        this.current = { backdrop, modal, onSave, onCancel };

        // Event handlers
        const closeModal = () => this.close();

        backdrop.addEventListener('click', closeModal);
        modal.querySelector('.modal-close').addEventListener('click', closeModal);

        if (showCancel) {
            modal.querySelector('#modal-cancel').addEventListener('click', () => {
                if (onCancel) onCancel();
                this.close();
            });
        }

        modal.querySelector('#modal-save').addEventListener('click', () => {
            if (onSave) {
                const result = onSave();
                if (result !== false) {
                    this.close();
                }
            } else {
                this.close();
            }
        });

        // Escape key
        const handleEscape = (e) => {
            if (e.key === 'Escape') {
                closeModal();
                document.removeEventListener('keydown', handleEscape);
            }
        };
        document.addEventListener('keydown', handleEscape);

        // Focus first input
        const firstInput = modal.querySelector('input, select, textarea');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 100);
        }

        return modal;
    },

    /**
     * Close current modal
     */
    close() {
        if (!this.current) return;

        const { backdrop, modal } = this.current;

        backdrop.classList.remove('open');
        modal.classList.remove('open');

        setTimeout(() => {
            backdrop.remove();
            modal.remove();
            document.body.style.overflow = '';
            this.current = null;
        }, 200);
    },

    /**
     * Get value from modal input
     */
    getValue(id) {
        const input = document.getElementById(id);
        return input ? input.value : null;
    }
};


/**
 * Goal Modal - Set yearly reading goal
 */
const GoalModal = {
    STORAGE_KEY: 'myweb_reading_goal',

    /**
     * Get current goal from localStorage
     */
    getGoal() {
        try {
            const data = localStorage.getItem(this.STORAGE_KEY);
            if (data) {
                const parsed = JSON.parse(data);
                const currentYear = new Date().getFullYear();
                if (parsed.year === currentYear) {
                    return parsed;
                }
            }
        } catch (e) {}
        return { year: new Date().getFullYear(), target: 0, completed: 0 };
    },

    /**
     * Save goal to localStorage
     */
    saveGoal(target) {
        const goal = this.getGoal();
        goal.target = parseInt(target, 10) || 0;
        goal.year = new Date().getFullYear();
        localStorage.setItem(this.STORAGE_KEY, JSON.stringify(goal));

        // Also try to save to API if logged in
        if (window.API && API.isLoggedIn()) {
            API.updateGoal(goal.target).catch(() => {});
        }

        // Dispatch event
        window.dispatchEvent(new CustomEvent('goalUpdated', { detail: goal }));

        return goal;
    },

    /**
     * Mark a book as completed
     */
    markCompleted(bookId) {
        const goal = this.getGoal();
        if (!goal.completedBooks) goal.completedBooks = [];
        if (!goal.completedBooks.includes(bookId)) {
            goal.completedBooks.push(bookId);
            goal.completed = goal.completedBooks.length;
            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(goal));
        }
        return goal;
    },

    /**
     * Get progress percentage
     */
    getProgress() {
        const goal = this.getGoal();
        if (!goal.target) return 0;
        return Math.min(100, Math.round((goal.completed / goal.target) * 100));
    },

    /**
     * Open goal setting modal
     */
    open() {
        const currentGoal = this.getGoal();
        const currentYear = new Date().getFullYear();

        const content = `
            <p class="modal-description">
                Set your reading goal for ${currentYear}. Challenge yourself to read more books this year!
            </p>
            <div class="modal-input-group">
                <label class="modal-label" for="goal-input">Number of books</label>
                <input
                    type="number"
                    id="goal-input"
                    class="modal-input"
                    value="${currentGoal.target || 12}"
                    min="1"
                    max="365"
                    placeholder="12"
                >
                <p class="modal-input-hint">Recommended: 12-24 books per year (1-2 per month)</p>
            </div>
            <div class="goal-modal-preview" id="goal-preview">
                <span class="goal-modal-preview-icon">📚</span>
                <span class="goal-modal-preview-text">
                    That's about <strong id="books-per-month">1</strong> book per month
                </span>
            </div>
        `;

        const modal = Modal.create({
            title: `${currentYear} Reading Goal`,
            content,
            saveText: 'Set Goal',
            onSave: () => {
                const value = parseInt(document.getElementById('goal-input').value, 10);
                if (isNaN(value) || value < 1 || value > 365) {
                    const input = document.getElementById('goal-input');
                    input.style.borderColor = 'var(--error)';
                    input.focus();
                    return false;
                }
                this.saveGoal(value);
                this.showConfirmation(value);
                return true;
            }
        });

        // Update preview on input
        const input = document.getElementById('goal-input');
        const preview = document.getElementById('books-per-month');

        const updatePreview = () => {
            const value = parseInt(input.value, 10) || 0;
            const perMonth = (value / 12).toFixed(1);
            preview.textContent = perMonth;
            input.style.borderColor = '';
        };

        input.addEventListener('input', updatePreview);
        updatePreview();

        // Enter key submits
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                document.getElementById('modal-save').click();
            }
        });
    },

    /**
     * Show confirmation toast
     */
    showConfirmation(target) {
        const toast = document.createElement('div');
        toast.className = 'toast toast-success';
        toast.innerHTML = `
            <span class="toast-icon">✓</span>
            <span class="toast-message">Goal set to ${target} books!</span>
        `;
        toast.style.cssText = `
            position: fixed;
            bottom: 24px;
            left: 50%;
            transform: translateX(-50%);
            background: var(--success, #2ed573);
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 8px;
            z-index: 1100;
            animation: slideUp 0.3s ease;
        `;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'fadeOut 0.3s ease forwards';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
};


// Add toast animations
const toastStyles = document.createElement('style');
toastStyles.textContent = `
    @keyframes slideUp {
        from { transform: translateX(-50%) translateY(20px); opacity: 0; }
        to { transform: translateX(-50%) translateY(0); opacity: 1; }
    }
    @keyframes fadeOut {
        from { opacity: 1; }
        to { opacity: 0; }
    }
`;
document.head.appendChild(toastStyles);


// Export
window.Modal = Modal;
window.GoalModal = GoalModal;

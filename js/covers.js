/**
 * Book Cover Generator
 * Generates beautiful book covers using Canvas
 */

const CoverGenerator = {
    // Color palettes for different genres/moods
    palettes: {
        classic: [
            { bg: ['#8b4513', '#654321'], border: '#a0522d', text: '#f5f0e6' },
            { bg: ['#2d4a3e', '#1a332a'], border: '#3d6a56', text: '#e8f5e9' },
            { bg: ['#4a1c1c', '#2d0f0f'], border: '#6b2626', text: '#fce4ec' },
            { bg: ['#1a365d', '#0d1b2a'], border: '#2c5282', text: '#e3f2fd' },
            { bg: ['#5c4033', '#3d2b22'], border: '#7a5545', text: '#efebe9' }
        ],
        gothic: [
            { bg: ['#1a1a2e', '#0f0f1a'], border: '#3d3d5c', text: '#e8e8e8' },
            { bg: ['#2d1b1b', '#1a0f0f'], border: '#4a2c2c', text: '#ffcdd2' },
            { bg: ['#1b2d1b', '#0f1a0f'], border: '#2c4a2c', text: '#c8e6c9' }
        ],
        romance: [
            { bg: ['#c17f59', '#8b5a3c'], border: '#d4956a', text: '#fff8e1' },
            { bg: ['#6b4c6e', '#4a3450'], border: '#8a6390', text: '#f3e5f5' },
            { bg: ['#c9a227', '#8b7000'], border: '#d4af37', text: '#1a1a1a' }
        ],
        adventure: [
            { bg: ['#2c5364', '#1c3a47'], border: '#3d6b7f', text: '#e0f7fa' },
            { bg: ['#3d5a3d', '#2a402a'], border: '#4a704a', text: '#e8f5e9' },
            { bg: ['#5d4e37', '#3d3225'], border: '#7a6548', text: '#efebe9' }
        ],
        default: [
            { bg: ['#4a4a6a', '#2d2d4a'], border: '#5a5a7a', text: '#e8e8f0' },
            { bg: ['#3d5a6a', '#2a404a'], border: '#4a6a7a', text: '#e0f0f5' },
            { bg: ['#5a4a3d', '#402a20'], border: '#6a5a4a', text: '#f5ebe0' }
        ]
    },

    // Genre to palette mapping
    genreMap: {
        'gothic': 'gothic',
        'horror': 'gothic',
        'romance': 'romance',
        'adventure': 'adventure',
        'mystery': 'gothic',
        'fantasy': 'adventure',
        'classic': 'classic',
        'fiction': 'default'
    },

    /**
     * Get a consistent color palette for a book
     */
    getPalette(title, genres = []) {
        // Determine palette type from genre
        let paletteType = 'default';
        for (const genre of genres) {
            const mapped = this.genreMap[genre.toLowerCase()];
            if (mapped) {
                paletteType = mapped;
                break;
            }
        }

        const palette = this.palettes[paletteType] || this.palettes.default;

        // Use title hash to pick consistent color
        let hash = 0;
        for (let i = 0; i < title.length; i++) {
            hash = ((hash << 5) - hash) + title.charCodeAt(i);
            hash = hash & hash;
        }

        return palette[Math.abs(hash) % palette.length];
    },

    /**
     * Generate a cover image as data URL
     */
    generate(options) {
        const {
            title = 'Untitled',
            author = 'Unknown',
            year = '',
            width = 200,
            height = 300,
            genres = []
        } = options;

        const canvas = document.createElement('canvas');
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');

        const palette = this.getPalette(title, genres);

        // Background gradient
        const gradient = ctx.createLinearGradient(0, 0, width, height);
        gradient.addColorStop(0, palette.bg[0]);
        gradient.addColorStop(1, palette.bg[1]);
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, width, height);

        // Subtle texture pattern
        this.addTexture(ctx, width, height);

        // Border
        const borderWidth = 4;
        ctx.strokeStyle = palette.border;
        ctx.lineWidth = borderWidth;
        ctx.strokeRect(
            borderWidth / 2,
            borderWidth / 2,
            width - borderWidth,
            height - borderWidth
        );

        // Inner decorative border
        ctx.strokeStyle = palette.border;
        ctx.lineWidth = 1;
        ctx.strokeRect(12, 12, width - 24, height - 24);

        // Decorative corners
        this.drawCorners(ctx, width, height, palette.border);

        // Year (top)
        if (year) {
            ctx.fillStyle = palette.text;
            ctx.globalAlpha = 0.7;
            ctx.font = `${Math.floor(width * 0.07)}px 'Plus Jakarta Sans', sans-serif`;
            ctx.textAlign = 'center';
            ctx.fillText(year.toString(), width / 2, height * 0.12);
            ctx.globalAlpha = 1;
        }

        // Title
        ctx.fillStyle = palette.text;
        ctx.textAlign = 'center';

        const titleFontSize = this.calculateFontSize(title, width * 0.75, height * 0.25, ctx);
        ctx.font = `bold ${titleFontSize}px 'Libre Baskerville', Georgia, serif`;

        const titleLines = this.wrapText(ctx, title, width * 0.75);
        const titleStartY = height * 0.35;
        const titleLineHeight = titleFontSize * 1.3;

        titleLines.forEach((line, i) => {
            ctx.fillText(line, width / 2, titleStartY + (i * titleLineHeight));
        });

        // Decorative line
        const lineY = titleStartY + (titleLines.length * titleLineHeight) + 15;
        ctx.strokeStyle = palette.border;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(width * 0.25, lineY);
        ctx.lineTo(width * 0.75, lineY);
        ctx.stroke();

        // Author
        ctx.fillStyle = palette.text;
        ctx.globalAlpha = 0.85;
        const authorFontSize = Math.floor(width * 0.075);
        ctx.font = `italic ${authorFontSize}px 'Libre Baskerville', Georgia, serif`;

        const authorLines = this.wrapText(ctx, author, width * 0.75);
        const authorStartY = lineY + 30;

        authorLines.forEach((line, i) => {
            ctx.fillText(line, width / 2, authorStartY + (i * authorFontSize * 1.3));
        });

        ctx.globalAlpha = 1;

        return canvas.toDataURL('image/png');
    },

    /**
     * Add subtle texture
     */
    addTexture(ctx, width, height) {
        ctx.globalAlpha = 0.03;
        for (let i = 0; i < 1000; i++) {
            const x = Math.random() * width;
            const y = Math.random() * height;
            const size = Math.random() * 2;
            ctx.fillStyle = Math.random() > 0.5 ? '#fff' : '#000';
            ctx.fillRect(x, y, size, size);
        }
        ctx.globalAlpha = 1;
    },

    /**
     * Draw decorative corners
     */
    drawCorners(ctx, width, height, color) {
        const size = 20;
        const offset = 8;

        ctx.strokeStyle = color;
        ctx.lineWidth = 1.5;

        // Top-left
        ctx.beginPath();
        ctx.moveTo(offset, offset + size);
        ctx.lineTo(offset, offset);
        ctx.lineTo(offset + size, offset);
        ctx.stroke();

        // Top-right
        ctx.beginPath();
        ctx.moveTo(width - offset - size, offset);
        ctx.lineTo(width - offset, offset);
        ctx.lineTo(width - offset, offset + size);
        ctx.stroke();

        // Bottom-left
        ctx.beginPath();
        ctx.moveTo(offset, height - offset - size);
        ctx.lineTo(offset, height - offset);
        ctx.lineTo(offset + size, height - offset);
        ctx.stroke();

        // Bottom-right
        ctx.beginPath();
        ctx.moveTo(width - offset - size, height - offset);
        ctx.lineTo(width - offset, height - offset);
        ctx.lineTo(width - offset, height - offset - size);
        ctx.stroke();
    },

    /**
     * Calculate optimal font size for text
     */
    calculateFontSize(text, maxWidth, maxHeight, ctx) {
        let fontSize = 24;
        const minSize = 12;
        const maxSize = 32;

        for (fontSize = maxSize; fontSize >= minSize; fontSize--) {
            ctx.font = `bold ${fontSize}px 'Libre Baskerville', Georgia, serif`;
            const lines = this.wrapText(ctx, text, maxWidth);
            const totalHeight = lines.length * fontSize * 1.3;

            if (totalHeight <= maxHeight) {
                return fontSize;
            }
        }

        return minSize;
    },

    /**
     * Wrap text to fit width
     */
    wrapText(ctx, text, maxWidth) {
        const words = text.split(' ');
        const lines = [];
        let currentLine = '';

        for (const word of words) {
            const testLine = currentLine ? `${currentLine} ${word}` : word;
            const metrics = ctx.measureText(testLine);

            if (metrics.width > maxWidth && currentLine) {
                lines.push(currentLine);
                currentLine = word;
            } else {
                currentLine = testLine;
            }
        }

        if (currentLine) {
            lines.push(currentLine);
        }

        return lines.slice(0, 4); // Max 4 lines
    },

    /**
     * Generate and apply cover to an element
     */
    applyTo(element, options) {
        const dataUrl = this.generate(options);
        element.style.backgroundImage = `url(${dataUrl})`;
        element.style.backgroundSize = 'cover';
        element.style.backgroundPosition = 'center';
    },

    /**
     * Create an img element with generated cover
     */
    createImage(options) {
        const img = document.createElement('img');
        img.src = this.generate(options);
        img.alt = `Cover of ${options.title}`;
        return img;
    }
};


/**
 * Book Card Component
 * Creates a book card with generated or real cover
 */
const BookCard = {
    /**
     * Create a book card element
     */
    create(book, options = {}) {
        const {
            showFavorite = true,
            linkToReader = true,
            onFavoriteClick = null
        } = options;

        const card = document.createElement('div');
        card.className = 'book-card';
        card.dataset.bookId = book.id;
        card.dataset.bookSlug = book.slug;

        // Generate cover
        const coverUrl = CoverGenerator.generate({
            title: book.title,
            author: book.author,
            year: book.year,
            genres: book.genres || [],
            width: 200,
            height: 300
        });

        const readerUrl = `reader.html?id=${book.id}&slug=${book.slug}&title=${encodeURIComponent(book.title)}`;

        card.innerHTML = `
            <div class="book-cover" style="background-image: url(${coverUrl});">
                ${showFavorite ? `
                    <button class="btn-favorite" aria-label="Add to favorites">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
                        </svg>
                    </button>
                ` : ''}
            </div>
            ${linkToReader ? `<a href="${readerUrl}" class="btn-read">Read</a>` : ''}
        `;

        // Favorite button handler
        if (showFavorite) {
            const favBtn = card.querySelector('.btn-favorite');
            favBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();

                if (onFavoriteClick) {
                    onFavoriteClick(book, favBtn);
                } else {
                    // Default toggle behavior
                    const isFav = favBtn.classList.toggle('is-favorite');
                    const svg = favBtn.querySelector('svg');
                    svg.setAttribute('fill', isFav ? 'var(--accent-primary)' : 'none');
                }
            });

            // Set initial state if book is favorited
            if (book.isFavorite) {
                favBtn.classList.add('is-favorite');
                favBtn.querySelector('svg').setAttribute('fill', 'var(--accent-primary)');
            }
        }

        return card;
    },

    /**
     * Render a grid of book cards
     */
    renderGrid(container, books, options = {}) {
        container.innerHTML = '';

        books.forEach(book => {
            const card = this.create(book, options);
            container.appendChild(card);
        });
    }
};


// Export
window.CoverGenerator = CoverGenerator;
window.BookCard = BookCard;

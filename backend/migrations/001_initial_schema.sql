-- MyWeb Books Database Schema
-- Run this to set up the database from scratch

-- Create database
CREATE DATABASE IF NOT EXISTS myweb_books
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE myweb_books;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    display_name VARCHAR(100),
    preferences JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Books table
CREATE TABLE IF NOT EXISTS books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    slug VARCHAR(100) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    year INT,
    language VARCHAR(50) DEFAULT 'English',
    description TEXT,
    cover_path VARCHAR(255),
    file_path VARCHAR(255),
    file_format VARCHAR(20) DEFAULT 'epub',
    total_pages INT DEFAULT 0,
    source_url VARCHAR(500),
    license VARCHAR(100) DEFAULT 'Public Domain',
    genres JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_slug (slug),
    INDEX idx_author (author),
    INDEX idx_year (year)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- User Library table (tracks which books user is reading/finished/wants to read)
CREATE TABLE IF NOT EXISTS user_library (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    book_id INT NOT NULL,
    status ENUM('want_to_read', 'reading', 'finished') DEFAULT 'want_to_read',
    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    finished_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_book (user_id, book_id),
    INDEX idx_user_status (user_id, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Reading Progress table
CREATE TABLE IF NOT EXISTS reading_progress (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    book_id INT NOT NULL,
    last_page INT DEFAULT 1,
    last_cfi VARCHAR(500),
    percentage FLOAT DEFAULT 0,
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_read_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_book_progress (user_id, book_id),
    INDEX idx_user_recent (user_id, last_read_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Favorites table
CREATE TABLE IF NOT EXISTS favorites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    book_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_favorite (user_id, book_id),
    INDEX idx_user_favorites (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Reading Goals table
CREATE TABLE IF NOT EXISTS reading_goals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    year INT NOT NULL,
    target_books INT DEFAULT 12,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_year_goal (user_id, year),
    INDEX idx_user_year (user_id, year)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

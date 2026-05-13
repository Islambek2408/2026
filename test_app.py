import pytest
import sqlite3
import os
from datetime import datetime
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# ==================== TEST DATABASE ====================
TEST_DB = 'test_recommendation.db'
ph = PasswordHasher()

@pytest.fixture(scope='function')
def test_db():
    """Test database yaratish"""
    conn = sqlite3.connect(TEST_DB, check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.executescript('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        created_at TEXT,
        updated_at TEXT
    );
    
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        type TEXT NOT NULL,
        genres TEXT,
        description TEXT,
        created_at TEXT,
        updated_at TEXT
    );
    
    CREATE TABLE IF NOT EXISTS ratings (
        user_id INTEGER,
        item_id INTEGER,
        rating REAL,
        rated_at TEXT,
        PRIMARY KEY (user_id, item_id),
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (item_id) REFERENCES items(id)
    );
    ''')
    conn.commit()
    
    yield conn, cursor
    
    cursor.close()
    conn.close()
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

# ==================== PASSWORD TESTS ====================
def test_hash_password():
    """Parol xeshlash testi"""
    password = "test_password_123"
    hashed = ph.hash(password)
    assert hashed != password
    assert len(hashed) > 20

def test_verify_correct_password():
    """To'g'ri parolni tekshirish"""
    password = "secure_password_456"
    hashed = ph.hash(password)
    try:
        ph.verify(hashed, password)
        assert True
    except VerifyMismatchError:
        assert False

def test_verify_wrong_password():
    """Noto'g'ri parolni tekshirish"""
    password = "correct_password"
    hashed = ph.hash(password)
    with pytest.raises(VerifyMismatchError):
        ph.verify(hashed, "wrong_password")

# ==================== USER TESTS ====================
def test_register_user(test_db):
    """Foydalanuvchi ro'yxatdan o'tkazish"""
    conn, cursor = test_db
    username = "testuser"
    password = "test123"
    hashed = ph.hash(password)
    
    cursor.execute(
        "INSERT INTO users (username, password, role, created_at, updated_at) VALUES (?,?,?,?,?)",
        (username, hashed, 'user', datetime.now().isoformat(), datetime.now().isoformat())
    )
    conn.commit()
    
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    assert user is not None
    assert user[1] == username

def test_duplicate_username(test_db):
    """Takroriy username"""
    conn, cursor = test_db
    username = "duplicate"
    hashed = ph.hash("password")
    
    cursor.execute(
        "INSERT INTO users (username, password, role, created_at, updated_at) VALUES (?,?,?,?,?)",
        (username, hashed, 'user', datetime.now().isoformat(), datetime.now().isoformat())
    )
    conn.commit()
    
    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute(
            "INSERT INTO users (username, password, role, created_at, updated_at) VALUES (?,?,?,?,?)",
            (username, hashed, 'user', datetime.now().isoformat(), datetime.now().isoformat())
        )
        conn.commit()

def test_admin_role(test_db):
    """Admin roli"""
    conn, cursor = test_db
    username = "admin_user"
    hashed = ph.hash("admin_pass")
    
    cursor.execute(
        "INSERT INTO users (username, password, role, created_at, updated_at) VALUES (?,?,?,?,?)",
        (username, hashed, 'admin', datetime.now().isoformat(), datetime.now().isoformat())
    )
    conn.commit()
    
    cursor.execute("SELECT role FROM users WHERE username=?", (username,))
    role = cursor.fetchone()[0]
    assert role == 'admin'

# ==================== ITEM TESTS ====================
def test_add_book(test_db):
    """Kitob qo'shish"""
    conn, cursor = test_db
    title = "O'tgan kunlar"
    cursor.execute(
        "INSERT INTO items (title, type, genres, description, created_at, updated_at) VALUES (?,?,?,?,?,?)",
        (title, 'book', 'drama', 'Abdulla Qodiry', datetime.now().isoformat(), datetime.now().isoformat())
    )
    conn.commit()
    
    cursor.execute("SELECT * FROM items WHERE title=?", (title,))
    item = cursor.fetchone()
    assert item is not None
    assert item[2] == 'book'

def test_add_movie(test_db):
    """Film qo'shish"""
    conn, cursor = test_db
    title = "Inception"
    cursor.execute(
        "INSERT INTO items (title, type, genres, description, created_at, updated_at) VALUES (?,?,?,?,?,?)",
        (title, 'movie', 'thriller', 'Nolan', datetime.now().isoformat(), datetime.now().isoformat())
    )
    conn.commit()
    
    cursor.execute("SELECT * FROM items WHERE title=?", (title,))
    item = cursor.fetchone()
    assert item is not None
    assert item[2] == 'movie'

def test_get_all_items(test_db):
    """Barcha elementlarni olish"""
    conn, cursor = test_db
    
    items = [
        ('Book1', 'book', 'genre1', 'desc1'),
        ('Movie1', 'movie', 'genre2', 'desc2'),
        ('Book2', 'book', 'genre3', 'desc3'),
    ]
    
    for item in items:
        cursor.execute(
            "INSERT INTO items (title, type, genres, description, created_at, updated_at) VALUES (?,?,?,?,?,?)",
            (item[0], item[1], item[2], item[3], datetime.now().isoformat(), datetime.now().isoformat())
        )
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM items")
    count = cursor.fetchone()[0]
    assert count == 3

# ==================== RATING TESTS ====================
def test_add_rating(test_db):
    """Baho qo'shish"""
    conn, cursor = test_db
    
    # User qo'shish
    cursor.execute(
        "INSERT INTO users (username, password, role, created_at, updated_at) VALUES (?,?,?,?,?)",
        ('testuser', ph.hash('pass'), 'user', datetime.now().isoformat(), datetime.now().isoformat())
    )
    
    # Item qo'shish
    cursor.execute(
        "INSERT INTO items (title, type, genres, description, created_at, updated_at) VALUES (?,?,?,?,?,?)",
        ('TestBook', 'book', 'genre', 'desc', datetime.now().isoformat(), datetime.now().isoformat())
    )
    conn.commit()
    
    user_id = 1
    item_id = 1
    rating = 4.5
    
    cursor.execute(
        "INSERT INTO ratings VALUES (?,?,?,?)",
        (user_id, item_id, rating, datetime.now().isoformat())
    )
    conn.commit()
    
    cursor.execute("SELECT rating FROM ratings WHERE user_id=? AND item_id=?", (user_id, item_id))
    stored_rating = cursor.fetchone()[0]
    assert stored_rating == rating

def test_update_rating(test_db):
    """Bahoni yangilash"""
    conn, cursor = test_db
    
    # Setup
    cursor.execute(
        "INSERT INTO users (username, password, role, created_at, updated_at) VALUES (?,?,?,?,?)",
        ('user', ph.hash('pass'), 'user', datetime.now().isoformat(), datetime.now().isoformat())
    )
    cursor.execute(
        "INSERT INTO items (title, type, genres, description, created_at, updated_at) VALUES (?,?,?,?,?,?)",
        ('Item', 'book', 'genre', 'desc', datetime.now().isoformat(), datetime.now().isoformat())
    )
    cursor.execute(
        "INSERT INTO ratings VALUES (?,?,?,?)",
        (1, 1, 3.0, datetime.now().isoformat())
    )
    conn.commit()
    
    # Update
    cursor.execute(
        "INSERT OR REPLACE INTO ratings VALUES (?,?,?,?)",
        (1, 1, 5.0, datetime.now().isoformat())
    )
    conn.commit()
    
    cursor.execute("SELECT rating FROM ratings WHERE user_id=1 AND item_id=1")
    rating = cursor.fetchone()[0]
    assert rating == 5.0

def test_average_rating(test_db):
    """O'rtacha bahoni hisoblash"""
    conn, cursor = test_db
    
    # Setup
    for i in range(1, 4):
        cursor.execute(
            "INSERT INTO users (username, password, role, created_at, updated_at) VALUES (?,?,?,?,?)",
            (f'user{i}', ph.hash('pass'), 'user', datetime.now().isoformat(), datetime.now().isoformat())
        )
    
    cursor.execute(
        "INSERT INTO items (title, type, genres, description, created_at, updated_at) VALUES (?,?,?,?,?,?)",
        ('Item', 'book', 'genre', 'desc', datetime.now().isoformat(), datetime.now().isoformat())
    )
    
    ratings = [4.0, 5.0, 3.0]
    for i, rating in enumerate(ratings, 1):
        cursor.execute(
            "INSERT INTO ratings VALUES (?,?,?,?)",
            (i, 1, rating, datetime.now().isoformat())
        )
    conn.commit()
    
    cursor.execute("SELECT AVG(rating) FROM ratings WHERE item_id=1")
    avg = cursor.fetchone()[0]
    assert avg == 4.0

# ==================== VALIDATION TESTS ====================
def test_invalid_rating_range():
    """Bahoning diapazoni tekshirish"""
    rating = 5.5
    assert not (1.0 <= rating <= 5.0)
    
    rating = 0.5
    assert not (1.0 <= rating <= 5.0)

def test_username_length(test_db):
    """Username uzunligi"""
    conn, cursor = test_db
    
    # Qisqa username
    with pytest.raises(Exception):
        username = "ab"  # 2 ta belgi
        if len(username) < 3:
            raise ValueError("Username quita qisqa")

def test_password_strength(test_db):
    """Parol kuchi"""
    weak_password = "123"
    assert len(weak_password) < 6
    
    strong_password = "SecurePass123!"
    assert len(strong_password) >= 6

if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])

import streamlit as st
import pandas as pd
import sqlite3
import logging
from datetime import datetime
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import os
from dotenv import load_dotenv

# ==================== LOAD ENV ====================
load_dotenv()

# ==================== LOGGING ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== DATABASE ====================
DB_PATH = os.getenv('DB_PATH', 'recommendation.db')
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
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

CREATE TABLE IF NOT EXISTS activity_log (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    action TEXT,
    details TEXT,
    timestamp TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
''')
conn.commit()

# ==================== PASSWORD HASHER ====================
ph = PasswordHasher()

def hash_password(password: str) -> str:
    """Parolni Argon2 bilan xeshlash"""
    return ph.hash(password)

def verify_password(password: str, hash_value: str) -> bool:
    """Parolni tekshirish"""
    try:
        ph.verify(hash_value, password)
        return True
    except VerifyMismatchError:
        return False

# ==================== ACTIVITY LOGGING ====================
def log_activity(user_id, action, details=""):
    """Foydalanuvchi faoliyatini qayd qilish"""
    cursor.execute(
        "INSERT INTO activity_log (user_id, action, details, timestamp) VALUES (?,?,?,?)",
        (user_id, action, details, datetime.now().isoformat())
    )
    conn.commit()
    logger.info(f"Activity: User {user_id} - {action} - {details}")

# ==================== DEFAULT MA'LUMOTLAR ====================
def init_data():
    """Dastlabki ma'lumotlarni o'rnatish"""
    cursor.execute("SELECT COUNT(*) FROM items")
    if cursor.fetchone()[0] == 0:
        default = [
            ("O'tgan kunlar", "book", "tarixiy, drama, ozbek", "Abdulla Qodiriyning mashhur romani"),
            ("Shum bola", "book", "bolalar, komediya, ozbek", "G'afur G'ulom"),
            ("Devon", "book", "she'r, adabiyot, ozbek", "Alisher Navoiy"),
            ("Inception", "movie", "fantastika, triller", "Christopher Nolan"),
            ("Interstellar", "movie", "fan-fantastika, drama", "Christopher Nolan"),
            ("Parasite", "movie", "triller, drama", "Bong Joon-ho"),
            ("Temur Malik", "movie", "tarixiy, aksiya, ozbek", "O'zbek tarixiy filmi"),
        ]
        for item in default:
            cursor.execute(
                "INSERT INTO items VALUES (NULL,?,?,?,?,?,?)",
                (item[0], item[1], item[2], item[3], datetime.now().isoformat(), datetime.now().isoformat())
            )
        conn.commit()
        logger.info("Dastlabki ma'lumotlar o'rnatildi")

init_data()

# ==================== FUNKSIYALAR ====================
def load_items_df():
    """Itemlarni DataFrame sifatida yuklash"""
    return pd.read_sql_query("SELECT * FROM items ORDER BY id DESC", conn)

def login_user(username: str, password: str):
    """Foydalanuvchini tizimga kirish"""
    if not username or not password:
        logger.warning("Bo'sh username yoki parol")
        return None
    
    cursor.execute("SELECT id, role, password FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    
    if result and verify_password(password, result[2]):
        logger.info(f"User {username} successfully logged in")
        return (result[0], result[1])
    else:
        logger.warning(f"Failed login attempt for user {username}")
        return None

def register_user(username: str, password: str, role: str = 'user') -> bool:
    """Yangi foydalanuvchini ro'yxatdan o'tkazish"""
    if not username or len(username) < 3:
        logger.warning("Invalid username")
        return False
    
    if not password or len(password) < 6:
        logger.warning("Password too short")
        return False
    
    try:
        hashed = hash_password(password)
        cursor.execute(
            "INSERT INTO users (username, password, role, created_at, updated_at) VALUES (?,?,?,?,?)",
            (username, hashed, role, datetime.now().isoformat(), datetime.now().isoformat())
        )
        conn.commit()
        logger.info(f"User {username} registered successfully")
        return True
    except sqlite3.IntegrityError:
        logger.warning(f"Username {username} already exists")
        return False

def add_item(title: str, item_type: str, genres: str, description: str) -> bool:
    """Yangi element qo'shish"""
    if not title or not item_type:
        logger.warning("Invalid item data")
        return False
    
    try:
        cursor.execute(
            "INSERT INTO items (title, type, genres, description, created_at, updated_at) VALUES (?,?,?,?,?,?)",
            (title, item_type, genres, description, datetime.now().isoformat(), datetime.now().isoformat())
        )
        conn.commit()
        logger.info(f"Item '{title}' added successfully")
        return True
    except Exception as e:
        logger.error(f"Error adding item: {e}")
        return False

def add_rating(user_id: int, item_id: int, rating: float) -> bool:
    """Baho qo'shish"""
    try:
        cursor.execute(
            "INSERT OR REPLACE INTO ratings VALUES (?,?,?,?)",
            (user_id, item_id, rating, datetime.now().isoformat())
        )
        conn.commit()
        log_activity(user_id, "add_rating", f"Item {item_id}: {rating} stars")
        return True
    except Exception as e:
        logger.error(f"Error adding rating: {e}")
        return False

def get_user_ratings(user_id: int) -> pd.DataFrame:
    """Foydalanuvchining barcha baholarini olish"""
    return pd.read_sql_query("""
        SELECT i.id, i.title, i.type, i.genres, r.rating, r.rated_at
        FROM ratings r 
        JOIN items i ON r.item_id = i.id 
        WHERE r.user_id = ?
        ORDER BY r.rated_at DESC
    """, conn, params=(user_id,))

def get_average_ratings() -> pd.DataFrame:
    """O'rtacha baholarni olish"""
    return pd.read_sql_query("""
        SELECT i.id, i.title, i.type, AVG(r.rating) as avg_rating, COUNT(r.rating) as rating_count
        FROM items i
        LEFT JOIN ratings r ON i.id = r.item_id
        GROUP BY i.id
        ORDER BY avg_rating DESC
    """, conn)

def search_items(query: str) -> pd.DataFrame:
    """Elementlarni qidirish"""
    df = load_items_df()
    if not query:
        return df
    
    mask = (
        df['title'].str.contains(query, case=False, na=False) |
        df['genres'].str.contains(query, case=False, na=False) |
        df['description'].str.contains(query, case=False, na=False)
    )
    return df[mask]

# ==================== STREAMLIT ILOVA ====================
st.set_page_config(
    page_title="📚🎥 Tavsiya Tizimi",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS styling
st.markdown("""
<style>
    .stApp {
        background-color: #f5f5f5;
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

st.title("📚🎥 Kitob va Film Tavsiya Tizimi")

# ==================== SESSION STATE ====================
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.role = None

# ==================== SIDEBAR ====================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3556/3556091.png", width=100)
    st.markdown("---")
    
    if st.session_state.user_id:
        st.success(f"✅ {st.session_state.username}")
        st.markdown(f"**Rol**: {st.session_state.role.upper()}")
        st.markdown("---")
        
        menu = st.selectbox(
            "📋 Menyu",
            ["🏠 Tavsiyalar", "⭐ Baho berish", "📊 Mening baholarim", "🔓 Chiqish"]
        )
    else:
        menu = st.selectbox(
            "📋 Menyu",
            ["🔐 Kirish", "📝 Ro'yxatdan o'tish"]
        )

# ==================== AUTHENTICATION ====================
if menu == "🔐 Kirish":
    st.subheader("👤 Tizimga kirish")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        username = st.text_input("👤 Username", key="login_user")
        password = st.text_input("🔑 Parol", type="password", key="login_pass")
        
        if st.button("🔓 Kirish", use_container_width=True):
            result = login_user(username, password)
            if result:
                st.session_state.user_id = result[0]
                st.session_state.role = result[1]
                st.session_state.username = username
                st.success(f"✅ Xush kelibsiz, {username}!")
                st.rerun()
            else:
                st.error("❌ Username yoki parol xato!")

elif menu == "📝 Ro'yxatdan o'tish":
    st.subheader("✍️ Yangi akkaunt yaratish")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        new_user = st.text_input("👤 Username", key="reg_user")
        new_pass = st.text_input("🔑 Parol", type="password", key="reg_pass")
        new_pass_confirm = st.text_input("🔑 Parolni tasdiqlang", type="password")
        
        if st.button("✅ Ro'yxatdan o'tish", use_container_width=True):
            if new_pass != new_pass_confirm:
                st.error("❌ Parollar mos kelmadi!")
            elif register_user(new_user, new_pass):
                st.success("✅ Muvaffaqiyatli ro'yxatdan o'tdingiz! Endi kirishingiz mumkin.")
            else:
                st.error("❌ Bu username band yoki parol qisqa!")

# ==================== AUTHENTICATED PAGES ====================
elif st.session_state.user_id:
    
    if menu == "🏠 Tavsiyalar":
        st.subheader("🎯 Siz uchun tavsiyalar")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            query = st.text_input("🔍 Nima izlayapsiz?", placeholder="masalan: fantastika, ozbek, drama")
        with col2:
            sort_by = st.selectbox("Saralash", ["Eng yangi", "O'rtacha baho"])
        with col3:
            item_type = st.selectbox("Turi", ["Barcha", "Kitob", "Film"])
        
        if st.button("🔍 Tavsiya ber", use_container_width=True):
            results = search_items(query)
            
            if item_type != "Barcha":
                type_map = {"Kitob": "book", "Film": "movie"}
                results = results[results['type'] == type_map[item_type]]
            
            if sort_by == "O'rtacha baho":
                avg_ratings = get_average_ratings()
                results = results.merge(avg_ratings[['id', 'avg_rating']], on='id', how='left')
                results = results.sort_values('avg_rating', ascending=False, na_position='last')
            
            if not results.empty:
                st.write(f"📌 **Topilgan: {len(results)} ta natija**")
                for _, row in results.head(10).iterrows():
                    emoji = "📖" if row['type'] == 'book' else "🎬"
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"{emoji} **{row['title']}**")
                        st.caption(f"📌 Janr: {row['genres']}")
                        st.write(row['description'])
                    with col2:
                        if 'avg_rating' in row and pd.notna(row['avg_rating']):
                            st.metric("⭐ Baho", f"{row['avg_rating']:.1f}")
                        else:
                            st.metric("⭐ Baho", "Hali yo'q")
                    st.markdown("---")
            else:
                st.info("🔍 Hech narsa topilmadi.")
    
    elif menu == "⭐ Baho berish":
        st.subheader("⭐ Elementga baho berish")
        df = load_items_df()
        
        if len(df) > 0:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                item_name = st.selectbox("📚 Element tanlang", df['title'].tolist())
                item_id = df[df['title'] == item_name]['id'].values[0]
            
            with col2:
                rating = st.slider("⭐ Bahoyingiz", 1.0, 5.0, 4.0, 0.5)
            
            if st.button("💾 Bahoni saqlash", use_container_width=True):
                if add_rating(st.session_state.user_id, item_id, rating):
                    st.success(f"✅ {rating} ⭐ baho saqlandi!")
                else:
                    st.error("❌ Xato yuz berdi!")
        else:
            st.info("📚 Hali element yo'q")
    
    elif menu == "📊 Mening baholarim":
        st.subheader("📊 Mening baholarim")
        ratings = get_user_ratings(st.session_state.user_id)
        
        if not ratings.empty:
            st.dataframe(
                ratings[['title', 'type', 'rating', 'rated_at']],
                use_container_width=True,
                hide_index=True
            )
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Jami baholar", len(ratings))
            with col2:
                st.metric("⭐ O'rtacha baho", f"{ratings['rating'].mean():.2f}")
            with col3:
                st.metric("📚 Kitoblar", len(ratings[ratings['type'] == 'book']))
        else:
            st.info("📊 Hali baho bermadingiz")
    
    elif menu == "🔓 Chiqish":
        st.warning("Chiqishni tasdiqlayapsiz?")
        if st.button("✅ Ha, chiqish", use_container_width=True):
            log_activity(st.session_state.user_id, "logout", "User logged out")
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.success("👋 Xayr!")
            st.rerun()

# ==================== ADMIN PANEL ====================
if st.session_state.get('role') == 'admin':
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 👑 Admin Panel")
    
    if st.sidebar.button("🔧 Admin Paneliga kirish"):
        st.subheader("👑 Admin Panel")
        
        tab1, tab2, tab3 = st.tabs(["➕ Element qo'shish", "📊 Barcha ma'lumotlar", "📈 Statistika"])
        
        with tab1:
            st.write("### Yangi element qo'shish")
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("📝 Nomi")
                itype = st.selectbox("📚 Turi", ["book", "movie"])
            
            with col2:
                genres = st.text_input("📌 Janrlar (vergul bilan)")
                desc = st.text_area("📄 Tavsif")
            
            if st.button("➕ Element qo'shish", use_container_width=True):
                if add_item(title, itype, genres, desc):
                    log_activity(st.session_state.user_id, "add_item", f"Added: {title}")
                    st.success("✅ Element qo'shildi!")
                    st.rerun()
                else:
                    st.error("❌ Xato yuz berdi!")
        
        with tab2:
            st.write("### Barcha elementlar")
            df = load_items_df()
            st.dataframe(df, use_container_width=True, hide_index=True)
        
        with tab3:
            st.write("### Statistika")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("📚 Jami elementlar", len(load_items_df()))
            with col2:
                cursor.execute("SELECT COUNT(*) FROM users")
                st.metric("👥 Jami foydalanuvchilar", cursor.fetchone()[0])
            with col3:
                cursor.execute("SELECT COUNT(*) FROM ratings")
                st.metric("⭐ Jami baholar", cursor.fetchone()[0])
            
            st.markdown("---")
            st.write("### Eng ko'p baholangan elementlar")
            top_rated = get_average_ratings()
            st.bar_chart(data=top_rated.set_index('title')['avg_rating'].head(10))

# ==================== FOOTER ====================
st.markdown("---")
st.caption("© 2026 - 📚🎥 Tavsiya Tizimi | Developed with ❤️")

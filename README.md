# 📚🎥 Kitob va Film Tavsiya Tizimi

O'zbek tilida Streamlit asosida yaratilgan zamonaviy tavsiya tizimi.

## ✨ Xususiyatlar

### 🔐 Xavfsizlik
- ✅ **Argon2 Hashing** - Zamonaviy parol xeshlash
- ✅ **Input Validation** - Barcha kiruvchi ma'lumotlarni tekshirish
- ✅ **SQL Injection Himoyasi** - Parametrli so'rovlar
- ✅ **Activity Logging** - Barcha amallar qayd qilinadi

### 👥 Foydalanuvchi Imkoniyatlari
- ✅ **Login/Register** - Xavfsiz autentifikatsiya
- ✅ **Tavsiyalar Qidirish** - Filtr va saralash
- ✅ **Rating Tizimi** - 1-5 yulduzli baho
- ✅ **Shaxsiy Dashboard** - O'z baholarini ko'rish

### 👑 Admin Panel
- ✅ **Kontentni Boshqarish** - Kitob/film qo'shish
- ✅ **Statistika** - Grafikalarga ko'rish
- ✅ **Activity Monitoring** - Foydalanuvchi faoliyati

### 📊 Database
- ✅ **Foreign Keys** - Ma'lumot yaxlitligi
- ✅ **Timestamps** - Yaratish/o'zgarish vaqtlari
- ✅ **Activity Log** - Audit tizimi

## 🚀 Ishga Tushirish

### 1. Zarur Kutubxonalarni O'rnatish
```bash
pip install -r requirements.txt
```

### 2. Environment Fayilni Yaratish
```bash
cp .env.example .env
```

### 3. Streamlit Ilovasini Ishga Tushirish
```bash
streamlit run app.py
```

### 4. Testlarni Ishga Tushirish
```bash
pytest test_app.py -v
```

## 📝 Test Akkountlar

**Admin Akkaunt:**
- Username: `admin`
- Password: `admin123`

**Yangi Akkaunt Yaratish:**
- Ro'yxatdan o'tish orqali yangi akkaunt yarating
- Username minimalum 3 ta belgi
- Parol minimalum 6 ta belgi

## 📁 Loyiha Tuzilishi

```
.
├── app.py                 # Asosiy Streamlit ilova
├── test_app.py           # Unit testlar
├── requirements.txt      # Python kutubxonalari
├── .env.example          # Environment template
├── .streamlit/
│   └── config.toml       # Streamlit konfiguratsiyasi
├── .gitignore            # Git ignor fayllar
├── pyproject.toml        # Loyiha metadata
└── README.md             # Bu fayl
```

## 🔧 Konfiguratsiya

### .env Fayli
```env
DB_PATH=recommendation.db
LOG_LEVEL=INFO
```

### .streamlit/config.toml
```toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#F5F5F5"
secondaryBackgroundColor = "#FFFFFF"
textColor = "#262730"
```

## 🎯 Foydalanish Qo'llanmasi

### 1. Login/Register
- "Kirish" yoki "Ro'yxatdan o'tish" bo'limiga o'ting
- Hisob yarating yoki mavjud hisobga kiring

### 2. Tavsiyalar Qidirish
- "Tavsiyalar" bo'limida qidiruv so'zini kiriting
- Sarala: "Eng yangi" yoki "O'rtacha baho"
- Turi: "Barcha", "Kitob" yoki "Film"

### 3. Baho Berish
- "Baho berish" bo'limiga o'ting
- Element tanlang va baho kiriting
- "Bahoni saqlash" tugmasini bosing

### 4. Admin Panel (Admin uchun)
- Sidebar da "🔧 Admin Paneliga kirish" tugmasini bosing
- **Elementlar qo'shish**: Yangi kitob/film qo'shish
- **Barcha ma'lumotlar**: Barcha elementlarni ko'rish
- **Statistika**: Grafikalarga ko'rish

## 🧪 Testing

Unit testlar `pytest` bilan yozilgan:

```bash
# Barcha testlarni ishga tushirish
pytest test_app.py -v

# Coverage bilan
pytest test_app.py --cov=app -v
```

## 📊 Database Schema

### users
```sql
id              INTEGER PRIMARY KEY
username        TEXT UNIQUE NOT NULL
password        TEXT NOT NULL (Argon2 hashed)
role            TEXT DEFAULT 'user'
created_at      TEXT (ISO format)
updated_at      TEXT (ISO format)
```

### items
```sql
id              INTEGER PRIMARY KEY
title           TEXT NOT NULL
type            TEXT NOT NULL (book/movie)
genres          TEXT
description     TEXT
created_at      TEXT (ISO format)
updated_at      TEXT (ISO format)
```

### ratings
```sql
user_id         INTEGER (FK)
item_id         INTEGER (FK)
rating          REAL (1.0-5.0)
rated_at        TEXT (ISO format)
PRIMARY KEY (user_id, item_id)
```

### activity_log
```sql
id              INTEGER PRIMARY KEY
user_id         INTEGER (FK)
action          TEXT (login, logout, add_rating, etc)
details         TEXT
timestamp       TEXT (ISO format)
```

## 🔒 Xavfsizlik Tavsiyalari

1. **Parol Xeshlash**: Hamma parollar Argon2 bilan xeshlangan
2. **Input Validation**: Barcha kiruvchi ma'lumotlar tekshiriladi
3. **SQL Injection**: Parametrli so'rovlar ishlatiladi
4. **Logging**: Barcha muhim amallar qayd qilinadi
5. **Session Management**: Sessiya xavfsiz boshqariladi

## 🐛 Bug Reports

Agar bug topgan bo'lsangiz, iltimos:
1. Xatoning tavsifini yozing
2. Takrorlash qadamlarini ko'rsiting
3. Expected vs actual natijani taqqoslang
4. GitHub Issues ga xabar bering

## 📝 Litsenziya

MIT License - Bepul foydalanish mumkin

## 👨‍💻 Muallif

**Islambek2408**
- GitHub: [@Islambek2408](https://github.com/Islambek2408)
- Email: doniyorivich24@gmail.com

---

**© 2026** - Kitob va Film Tavsiya Tizimi | Made with ❤️

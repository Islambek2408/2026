# 🚀 Production Deployment

## 📌 Streamlit Cloud (Eng oson)

### 1. GitHub-ga push qiling
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### 2. [Streamlit Cloud](https://streamlit.io/cloud) ga o'ting

### 3. "New app" tugmasini bosing

### 4. Repository tanlang:
- Repository: `Islambek2408/2026`
- Branch: `main`
- Main file path: `app.py`

### 5. Deploy tugmasini bosing

✅ **3-5 daqiqadan keyin live bo'ladi!**

URL: `https://[yourname]-2026-[random].streamlit.app`

---

## 🐳 Docker bilan

### 1. Dockerfile yaratish

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]
```

### 2. Docker image yaratish
```bash
docker build -t recommendation-app .
```

### 3. Container ishga tushirish
```bash
docker run -p 8501:8501 recommendation-app
```

---

## ☁️ Heroku bilan

### 1. Procfile yaratish
```
web: streamlit run app.py --logger.level=error
```

### 2. runtime.txt yaratish
```
python-3.10.0
```

### 3. Heroku CLI o'rnatish
```bash
https://devcenter.heroku.com/articles/heroku-cli
```

### 4. Deploy qilish
```bash
heroku login
heroku create your-app-name
git push heroku main
```

---

## 🔧 Environment Variables

`.env` faylida:
```env
DB_PATH=/tmp/recommendation.db
LOG_LEVEL=INFO
```

Streamlit Cloud-da:
1. Settings → Secrets
2. Ko'rsatilgan variable larni qo'shing

---

## 📊 Monitoring

- Streamlit Cloud: Built-in logs
- Docker: `docker logs [container_id]`
- Heroku: `heroku logs --tail`

---

## 🔐 Production Sozlamalari

```toml
[server]
headless = true
runOnSave = false
maxUploadSize = 200

[client]
showErrorDetails = false

[logger]
level = "error"
```

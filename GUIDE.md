# Playto Community Feed - Complete Guide

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Manual Setup](#manual-setup)
3. [Running the Application](#running-the-application)
4. [Testing](#testing)
5. [Docker Deployment](#docker-deployment)
6. [Production Deployment](#production-deployment)
7. [API Documentation](#api-documentation)
8. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### Using the Setup Script (Windows)

```powershell
# Run the automated setup script
.\setup.ps1
```

This will:
- Check Python and Node.js installations
- Set up backend virtual environment
- Install all dependencies
- Run database migrations
- Optionally create a superuser

### Manual Quick Start

```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser  # Optional
python manage.py runserver

# Frontend (in a new terminal)
cd frontend
npm install
npm run dev
```

---

## 🛠️ Manual Setup

### Prerequisites

- **Python 3.10+** ([Download](https://www.python.org/downloads/))
- **Node.js 18+** ([Download](https://nodejs.org/))
- **Git** ([Download](https://git-scm.com/))
- **PostgreSQL** (Optional, for production)

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**
   ```bash
   # Copy the example file
   copy .env.example .env  # Windows
   # cp .env.example .env  # macOS/Linux
   
   # Edit .env and update values if needed
   ```

6. **Run migrations**
   ```bash
   python manage.py migrate
   ```

7. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

8. **Load sample data (optional)**
   ```bash
   # You can create sample data through the admin panel or API
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   # .env file already exists with default values
   # Update VITE_API_URL if backend is on different host
   ```

---

## ▶️ Running the Application

### Development Mode

**Backend** (Terminal 1):
```bash
cd backend
venv\Scripts\activate  # Activate virtual environment
python manage.py runserver
```
Backend runs on: http://localhost:8000

**Frontend** (Terminal 2):
```bash
cd frontend
npm run dev
```
Frontend runs on: http://localhost:5173

### Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000/api
- **Admin Panel**: http://localhost:8000/admin

### Creating Test Users

**Option 1: Through the UI**
1. Go to http://localhost:5173
2. Click "Sign Up"
3. Fill in the registration form

**Option 2: Through Django Admin**
1. Go to http://localhost:8000/admin
2. Log in with superuser credentials
3. Create users under "Authentication and Authorization"

**Option 3: Using Django Shell**
```bash
python manage.py shell
```
```python
from django.contrib.auth.models import User
User.objects.create_user('testuser', 'test@example.com', 'password123')
```

---

## 🧪 Testing

### Backend Tests

```bash
cd backend
python manage.py test
```

**Run specific test cases:**
```bash
# Test leaderboard
python manage.py test community.tests.LeaderboardTestCase

# Test race conditions
python manage.py test community.tests.RaceConditionTestCase

# Test comment tree
python manage.py test community.tests.CommentTreeTestCase
```

**Test with coverage:**
```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

### Frontend Tests

```bash
cd frontend
npm run test  # If tests are configured
```

### Manual Testing Checklist

- [ ] User registration works
- [ ] User login/logout works
- [ ] Create post works
- [ ] Like/unlike post works
- [ ] Create comment works
- [ ] Reply to comment works
- [ ] Like/unlike comment works
- [ ] Leaderboard updates correctly
- [ ] Karma calculation is accurate
- [ ] No duplicate likes possible
- [ ] Comment threading displays correctly

---

## 🐳 Docker Deployment

### Using Docker Compose

1. **Build and start all services**
   ```bash
   docker-compose up --build
   ```

2. **Run migrations**
   ```bash
   docker-compose exec backend python manage.py migrate
   ```

3. **Create superuser**
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

4. **Access the application**
   - Frontend: http://localhost:5173
   - Backend: http://localhost:8000

### Individual Docker Commands

**Backend only:**
```bash
cd backend
docker build -t playto-backend .
docker run -p 8000:8000 playto-backend
```

**Frontend only:**
```bash
cd frontend
docker build -t playto-frontend .
docker run -p 5173:5173 playto-frontend
```

---

## 🌐 Production Deployment

### Backend (Railway/Render)

1. **Prepare for production**
   - Set `DEBUG=False` in environment variables
   - Set secure `SECRET_KEY`
   - Configure `ALLOWED_HOSTS`
   - Set up PostgreSQL database

2. **Environment Variables**
   ```
   DEBUG=False
   SECRET_KEY=<generate-secure-key>
   ALLOWED_HOSTS=yourdomain.com
   DB_NAME=playto_prod
   DB_USER=postgres
   DB_PASSWORD=<secure-password>
   DB_HOST=<database-host>
   DB_PORT=5432
   CORS_ALLOWED_ORIGINS=https://yourdomain.com
   ```

3. **Update settings.py for PostgreSQL**
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': config('DB_NAME'),
           'USER': config('DB_USER'),
           'PASSWORD': config('DB_PASSWORD'),
           'HOST': config('DB_HOST'),
           'PORT': config('DB_PORT'),
       }
   }
   ```

4. **Deploy**
   - Push to GitHub
   - Connect repository to Railway/Render
   - Configure environment variables
   - Deploy

### Frontend (Vercel)

1. **Update environment variables**
   ```
   VITE_API_URL=https://your-backend-url.com/api
   ```

2. **Build command**
   ```bash
   npm run build
   ```

3. **Deploy**
   - Push to GitHub
   - Connect repository to Vercel
   - Configure environment variables
   - Deploy

---

## 📚 API Documentation

### Authentication Endpoints

**Register**
```http
POST /api/auth/register/
Content-Type: application/json

{
  "username": "newuser",
  "email": "user@example.com",
  "password": "password123",
  "password_confirm": "password123"
}
```

**Login**
```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "user",
  "password": "password123"
}
```

**Logout**
```http
POST /api/auth/logout/
```

**Get Current User**
```http
GET /api/auth/me/
```

### Post Endpoints

**List Posts**
```http
GET /api/posts/
GET /api/posts/?page=2
```

**Get Post Detail**
```http
GET /api/posts/{id}/
```

**Create Post**
```http
POST /api/posts/
Content-Type: application/json

{
  "content": "This is my post content"
}
```

**Like/Unlike Post**
```http
POST /api/posts/{id}/like/
```

### Comment Endpoints

**Create Comment**
```http
POST /api/comments/
Content-Type: application/json

{
  "post": 1,
  "content": "This is a comment"
}
```

**Create Reply**
```http
POST /api/comments/
Content-Type: application/json

{
  "post": 1,
  "parent": 5,
  "content": "This is a reply"
}
```

**Like/Unlike Comment**
```http
POST /api/comments/{id}/like/
```

### Leaderboard Endpoint

**Get Leaderboard**
```http
GET /api/leaderboard/
```

Response:
```json
[
  {
    "id": 1,
    "username": "topuser",
    "email": "top@example.com",
    "karma_24h": 125,
    "post_karma_24h": 100,
    "comment_karma_24h": 25
  }
]
```

---

## 🔧 Troubleshooting

### Backend Issues

**Problem: `ModuleNotFoundError: No module named 'django'`**
```bash
# Solution: Activate virtual environment and install dependencies
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

**Problem: Database migration errors**
```bash
# Solution: Delete db.sqlite3 and migrations, start fresh
rm db.sqlite3
python manage.py makemigrations
python manage.py migrate
```

**Problem: CORS errors**
```bash
# Solution: Check CORS_ALLOWED_ORIGINS in settings.py
# Make sure it includes your frontend URL
```

### Frontend Issues

**Problem: `Cannot find module` errors**
```bash
# Solution: Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

**Problem: API calls failing**
```bash
# Solution: Check VITE_API_URL in .env
# Make sure backend is running
# Check browser console for CORS errors
```

**Problem: Blank page**
```bash
# Solution: Check browser console for errors
# Verify backend is running and accessible
```

### Docker Issues

**Problem: Container won't start**
```bash
# Solution: Check logs
docker-compose logs backend
docker-compose logs frontend

# Rebuild containers
docker-compose down
docker-compose up --build
```

**Problem: Database connection errors**
```bash
# Solution: Wait for database to be ready
# Check docker-compose.yml health checks
# Verify environment variables
```

---

## 📊 Performance Tips

1. **Enable PostgreSQL in production** for better performance
2. **Use Redis for caching** leaderboard results (5-minute cache)
3. **Enable gzip compression** on the server
4. **Use CDN** for static assets
5. **Implement pagination** for large feeds
6. **Add database indexes** on frequently queried fields

---

## 🔐 Security Checklist

- [ ] `DEBUG=False` in production
- [ ] Secure `SECRET_KEY` generated
- [ ] HTTPS enabled
- [ ] CORS properly configured
- [ ] Database credentials secured
- [ ] Regular security updates
- [ ] Input validation on all forms
- [ ] Rate limiting on API endpoints

---

## 📝 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [React Documentation](https://react.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Vite Documentation](https://vitejs.dev/)

---

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the EXPLAINER.md for technical details
3. Check the test suite for examples
4. Review the code comments

---

**Built with ❤️ for the Playto Engineering Challenge**

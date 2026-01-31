# Playto Community Feed

A full-stack community feed application with threaded discussions and a dynamic leaderboard.

## Tech Stack

- **Backend:** Django 5.0 & Django REST Framework
- **Frontend:** React 18 with Vite & Tailwind CSS
- **Database:** PostgreSQL (SQLite for development)

## Features

- 📝 **Community Feed:** Create and view text posts with like counts
- 💬 **Threaded Comments:** Nested comment threads (Reddit-style)
- 🎮 **Gamification System:**
  - Post likes = 5 Karma
  - Comment likes = 1 Karma
- 🏆 **Dynamic Leaderboard:** Top 5 users by Karma earned in the last 24 hours

## Technical Highlights

- **Optimized N+1 Queries:** Efficient comment tree fetching using `select_related` and `prefetch_related`
- **Race Condition Handling:** Database-level constraints and atomic transactions prevent double-likes
- **Complex Aggregation:** Dynamic 24-hour leaderboard calculation from activity history

## Local Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL (optional, SQLite works for development)

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Load sample data (optional)
python manage.py loaddata sample_data.json

# Run development server
python manage.py runserver
```

Backend will be available at `http://localhost:8000`

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will be available at `http://localhost:5173`

## API Endpoints

### Posts
- `GET /api/posts/` - List all posts
- `POST /api/posts/` - Create a new post
- `GET /api/posts/{id}/` - Get post details with comment tree
- `POST /api/posts/{id}/like/` - Like/unlike a post

### Comments
- `POST /api/comments/` - Create a comment or reply
- `POST /api/comments/{id}/like/` - Like/unlike a comment

### Leaderboard
- `GET /api/leaderboard/` - Get top 5 users by 24h karma

### Users
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login user
- `GET /api/auth/me/` - Get current user profile

## Docker Setup (Optional)

```bash
# Build and run with Docker Compose
docker-compose up --build

# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser
```

## Testing

```bash
# Backend tests
cd backend
python manage.py test

# Frontend tests
cd frontend
npm run test
```

## Project Structure

```
playto/
├── backend/
│   ├── community/          # Main Django app
│   │   ├── models.py       # Database models
│   │   ├── serializers.py  # DRF serializers
│   │   ├── views.py        # API views
│   │   └── tests.py        # Unit tests
│   ├── config/             # Django settings
│   └── manage.py
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API services
│   │   ├── hooks/          # Custom hooks
│   │   └── App.jsx
│   └── package.json
├── docker-compose.yml
├── README.md
└── EXPLAINER.md
```

## Environment Variables

### Backend (.env)
```
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@localhost:5432/playto
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000/api
```

## License

MIT

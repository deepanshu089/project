# Deployment Guide - Playto Community Feed

This guide covers deploying the Playto Community Feed to production using free-tier services.

## 🎯 Deployment Stack

- **Backend**: Railway or Render (Free tier)
- **Frontend**: Vercel (Free tier)
- **Database**: Railway PostgreSQL or Render PostgreSQL (Free tier)

---

## 🚂 Option 1: Railway Deployment

### Backend Deployment on Railway

1. **Create Railway Account**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Select the `backend` folder as root

3. **Add PostgreSQL Database**
   - Click "New" → "Database" → "PostgreSQL"
   - Railway will automatically create and link the database

4. **Configure Environment Variables**
   - Go to your backend service → "Variables"
   - Add the following:
   ```
   DEBUG=False
   SECRET_KEY=<generate-a-secure-random-key>
   ALLOWED_HOSTS=.railway.app
   CORS_ALLOWED_ORIGINS=https://your-frontend-url.vercel.app
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   ```

5. **Update settings.py for Railway**
   Add to `backend/config/settings.py`:
   ```python
   import dj_database_url
   
   # Use DATABASE_URL if available (Railway)
   if 'DATABASE_URL' in os.environ:
       DATABASES['default'] = dj_database_url.config(
           conn_max_age=600,
           conn_health_checks=True,
       )
   ```

6. **Add to requirements.txt**
   ```
   dj-database-url>=2.1.0
   psycopg2-binary>=2.9.9
   gunicorn>=21.2.0
   ```

7. **Create Procfile**
   Create `backend/Procfile`:
   ```
   web: gunicorn config.wsgi --bind 0.0.0.0:$PORT
   ```

8. **Deploy**
   - Push changes to GitHub
   - Railway will automatically deploy
   - Run migrations: `railway run python manage.py migrate`
   - Create superuser: `railway run python manage.py createsuperuser`

### Frontend Deployment on Vercel

1. **Create Vercel Account**
   - Go to [vercel.com](https://vercel.com)
   - Sign up with GitHub

2. **Import Project**
   - Click "Add New" → "Project"
   - Import your GitHub repository
   - Set root directory to `frontend`

3. **Configure Build Settings**
   - Framework Preset: Vite
   - Build Command: `npm run build`
   - Output Directory: `dist`

4. **Environment Variables**
   ```
   VITE_API_URL=https://your-backend.railway.app/api
   ```

5. **Deploy**
   - Click "Deploy"
   - Vercel will build and deploy automatically

6. **Update Backend CORS**
   - Copy your Vercel URL
   - Update `CORS_ALLOWED_ORIGINS` in Railway backend variables
   - Redeploy backend

---

## 🎨 Option 2: Render Deployment

### Backend on Render

1. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub

2. **Create PostgreSQL Database**
   - Dashboard → "New" → "PostgreSQL"
   - Name: `playto-db`
   - Free tier selected
   - Create database
   - Copy the "Internal Database URL"

3. **Create Web Service**
   - Dashboard → "New" → "Web Service"
   - Connect your repository
   - Settings:
     - Name: `playto-backend`
     - Root Directory: `backend`
     - Environment: `Python 3`
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `gunicorn config.wsgi:application`

4. **Environment Variables**
   ```
   DEBUG=False
   SECRET_KEY=<generate-secure-key>
   ALLOWED_HOSTS=.onrender.com
   DATABASE_URL=<internal-database-url>
   CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app
   PYTHON_VERSION=3.12.0
   ```

5. **Deploy**
   - Click "Create Web Service"
   - After deployment, run migrations in Shell:
     ```bash
     python manage.py migrate
     python manage.py createsuperuser
     ```

### Frontend on Vercel

Same as Railway option above.

---

## 🔧 Post-Deployment Tasks

### 1. Run Migrations

**Railway:**
```bash
railway run python manage.py migrate
```

**Render:**
Use the Shell tab in Render dashboard:
```bash
python manage.py migrate
```

### 2. Create Superuser

**Railway:**
```bash
railway run python manage.py createsuperuser
```

**Render:**
```bash
python manage.py createsuperuser
```

### 3. Load Sample Data (Optional)

```bash
python manage.py shell < create_sample_data.py
```

### 4. Test the Deployment

1. Visit your frontend URL
2. Register a new user
3. Create a post
4. Like the post
5. Add a comment
6. Check the leaderboard

---

## 🔐 Security Checklist

- [ ] `DEBUG=False` in production
- [ ] Secure `SECRET_KEY` generated (use `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`)
- [ ] `ALLOWED_HOSTS` configured correctly
- [ ] `CORS_ALLOWED_ORIGINS` set to frontend URL only
- [ ] Database credentials secured
- [ ] HTTPS enabled (automatic on Railway/Render/Vercel)
- [ ] Environment variables not committed to Git

---

## 📊 Monitoring

### Railway
- View logs in the Railway dashboard
- Monitor deployments
- Check resource usage

### Render
- View logs in the Logs tab
- Monitor deployments
- Check metrics

### Vercel
- View deployment logs
- Monitor analytics
- Check performance metrics

---

## 🐛 Troubleshooting

### Issue: Static files not loading

**Solution:**
Add to `settings.py`:
```python
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Whitenoise for static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

Add to `requirements.txt`:
```
whitenoise>=6.6.0
```

### Issue: Database connection errors

**Solution:**
- Verify `DATABASE_URL` is set correctly
- Check database is running
- Ensure `psycopg2-binary` is installed

### Issue: CORS errors

**Solution:**
- Verify `CORS_ALLOWED_ORIGINS` includes your frontend URL
- Check for trailing slashes
- Ensure `django-cors-headers` is installed and configured

### Issue: 502 Bad Gateway

**Solution:**
- Check application logs
- Verify `gunicorn` is installed
- Check `Procfile` or start command is correct

---

## 🔄 Continuous Deployment

Both Railway and Render support automatic deployments:

1. **Enable Auto-Deploy**
   - Automatically deploy on push to main branch
   - Configure in platform settings

2. **Branch Deployments**
   - Create preview deployments for pull requests
   - Test before merging

3. **Rollback**
   - Both platforms support instant rollback
   - Revert to previous deployment if issues occur

---

## 💰 Cost Considerations

### Free Tier Limits

**Railway:**
- $5 free credit per month
- 500 hours of usage
- 1GB RAM per service

**Render:**
- Free tier available
- 750 hours per month
- 512MB RAM
- Spins down after inactivity

**Vercel:**
- Unlimited deployments
- 100GB bandwidth per month
- Serverless functions included

### Scaling Up

When you need more resources:
- Railway: Pay-as-you-go pricing
- Render: Paid plans from $7/month
- Vercel: Pro plan from $20/month

---

## 📝 Environment Variables Reference

### Backend

```bash
# Required
DEBUG=False
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Hosts
ALLOWED_HOSTS=.railway.app,.onrender.com
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app

# Optional
PYTHON_VERSION=3.12.0
```

### Frontend

```bash
# Required
VITE_API_URL=https://your-backend.railway.app/api
```

---

## 🎉 Success!

Your Playto Community Feed is now live! Share the URL and start building your community.

**Next Steps:**
1. Share with friends for testing
2. Monitor performance and errors
3. Gather user feedback
4. Iterate and improve

---

## 📚 Additional Resources

- [Railway Documentation](https://docs.railway.app/)
- [Render Documentation](https://render.com/docs)
- [Vercel Documentation](https://vercel.com/docs)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/)

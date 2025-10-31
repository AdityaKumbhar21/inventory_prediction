# Quick Deployment Guide - Render + Vercel

This is a quick reference for deploying the Inventory Prediction System on Render (backend) and Vercel (frontend).

## Prerequisites
- [ ] GitHub account
- [ ] Render account (https://render.com)
- [ ] Vercel account (https://vercel.com)
- [ ] Repository pushed to GitHub
- [ ] Models trained and in `models/` directory

---

## Step 1: Deploy Backend to Render

### 1.1 Update CORS Settings
Edit `backend/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.vercel.app",  # Allow all Vercel domains
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 1.2 Commit and Push
```bash
git add backend/main.py
git commit -m "Update CORS for Vercel"
git push origin main
```

### 1.3 Deploy on Render
1. Go to https://render.com/dashboard
2. Click **"New +"** → **"Web Service"**
3. Click **"Build and deploy from a Git repository"**
4. Select your `inventory_prediction` repository
5. Configure:
   - **Name**: `inventory-prediction-api`
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: Free

6. Add Environment Variables (optional):
   - Click **"Advanced"**
   - Add: `PYTHON_VERSION` = `3.9.16`

7. Click **"Create Web Service"**

### 1.4 Wait for Deployment (5-10 minutes)
- Watch the build logs
- Once complete, you'll see: ✅ **Live**
- Note your URL: `https://inventory-prediction-api.onrender.com`

### 1.5 Test Backend
```bash
curl https://inventory-prediction-api.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "models_loaded": 6,
  "data_loaded": true,
  "timestamp": "2025-10-31T..."
}
```

---

## Step 2: Deploy Frontend to Vercel

### 2.1 Create Production Environment File
```bash
cd frontend

# Create .env.production with your Render backend URL
echo "REACT_APP_API_URL=https://inventory-prediction-api.onrender.com" > .env.production
```

### 2.2 Create vercel.json
```bash
cat > vercel.json << 'EOF'
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "build"
      }
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/static/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ]
}
EOF
```

### 2.3 Commit and Push
```bash
git add .
git commit -m "Add Vercel configuration"
git push origin main
```

### 2.4 Deploy on Vercel
1. Go to https://vercel.com/dashboard
2. Click **"Add New..."** → **"Project"**
3. Click **"Import"** next to your repository
4. Configure:
   - **Framework Preset**: Create React App (auto-detected)
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `build` (auto-detected)

5. Click **"Environment Variables"**
   - Add: `REACT_APP_API_URL` = `https://inventory-prediction-api.onrender.com`

6. Click **"Deploy"**

### 2.5 Wait for Deployment (2-3 minutes)
- Watch the build logs
- Once complete: 🎉 **Congratulations**
- Note your URL: `https://inventory-prediction.vercel.app`

### 2.6 Test Frontend
Open in browser: https://inventory-prediction.vercel.app

---

## Step 3: Update Backend CORS (If Needed)

If you see CORS errors, update `backend/main.py` with your exact Vercel domain:

```python
allow_origins=[
    "http://localhost:3000",
    "https://inventory-prediction.vercel.app",  # Your exact domain
    "https://*.vercel.app",
],
```

Commit and push - Render will auto-deploy.

---

## Common Issues & Solutions

### ❌ Backend: "Models not found"
**Problem**: Models not in repository  
**Solution**: Models are too large for Git. Options:
1. Train models on Render using startup script
2. Use Git LFS for large files
3. Store models in cloud storage (S3, Google Cloud Storage)

**Quick Fix**: Comment out model loading in startup:
```python
# @app.on_event("startup")
# async def startup_event():
#     # Skip model loading for now
#     pass
```

### ❌ Frontend: API Connection Failed
**Problem**: Wrong API URL  
**Solution**: Check environment variable in Vercel:
1. Dashboard → Project → Settings → Environment Variables
2. Verify: `REACT_APP_API_URL` = `https://inventory-prediction-api.onrender.com`
3. Redeploy: Dashboard → Deployments → ⋯ → Redeploy

### ❌ Backend: Free Tier Sleeping
**Problem**: Render free tier sleeps after 15 min  
**Solution**: 
- First request will take ~30 seconds (cold start)
- Upgrade to paid plan ($7/month) for always-on
- Or use a service like Koyeb/Railway with better free tier

### ❌ CORS Error in Browser
**Problem**: CORS not configured  
**Solution**: Update `backend/main.py` CORS origins and redeploy

---

## Monitoring

### Render Dashboard
- **Logs**: Dashboard → Service → Logs
- **Metrics**: CPU, Memory, Response time
- **Health**: Automatic health checks

### Vercel Dashboard
- **Analytics**: Dashboard → Project → Analytics
- **Logs**: Dashboard → Deployments → View Function Logs
- **Performance**: Real-time metrics

---

## Custom Domains (Optional)

### Add Custom Domain to Render
1. Render Dashboard → Service → Settings → Custom Domains
2. Add domain: `api.yourdomain.com`
3. Update DNS:
   ```
   Type: CNAME
   Name: api
   Value: inventory-prediction-api.onrender.com
   ```

### Add Custom Domain to Vercel
1. Vercel Dashboard → Project → Settings → Domains
2. Add domain: `yourdomain.com`
3. Follow DNS instructions (A record or CNAME)

---

## Environment Variables Reference

### Backend (Render)
```
PYTHON_VERSION=3.9.16
PYTHONUNBUFFERED=1
```

### Frontend (Vercel)
```
REACT_APP_API_URL=https://inventory-prediction-api.onrender.com
```

---

## Useful Commands

### Vercel CLI
```bash
# Install
npm install -g vercel

# Deploy
cd frontend
vercel --prod

# View logs
vercel logs

# View deployments
vercel ls
```

### Test Endpoints
```bash
# Health check
curl https://inventory-prediction-api.onrender.com/health

# List models
curl https://inventory-prediction-api.onrender.com/models

# Make prediction
curl -X POST https://inventory-prediction-api.onrender.com/predict \
  -H "Content-Type: application/json" \
  -d '{
    "store": 1,
    "item": 1,
    "date": "2025-11-01",
    "model_name": "lightgbm"
  }'
```

---

## Deployment Checklist

- [ ] Repository pushed to GitHub
- [ ] Models trained (or loading disabled)
- [ ] CORS configured in backend
- [ ] Backend deployed to Render
- [ ] Backend health check passing
- [ ] Environment variables set in Vercel
- [ ] Frontend deployed to Vercel
- [ ] Frontend loads successfully
- [ ] API connection working
- [ ] Test predictions working

---

## Next Steps

1. **Add Custom Domain** (optional)
2. **Setup Monitoring** (Sentry, LogRocket)
3. **Enable Analytics** (Google Analytics, Mixpanel)
4. **Add Authentication** (Auth0, Firebase Auth)
5. **Setup Database** (for storing predictions)
6. **Add Caching** (Redis via Render)

---

## Support

- **Render Docs**: https://render.com/docs
- **Vercel Docs**: https://vercel.com/docs
- **Project Issues**: GitHub Issues

---

**🎉 That's it! Your app is now live!**

- Frontend: https://inventory-prediction.vercel.app
- Backend: https://inventory-prediction-api.onrender.com
- API Docs: https://inventory-prediction-api.onrender.com/docs

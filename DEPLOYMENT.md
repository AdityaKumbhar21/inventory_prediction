# Deployment Guide

Complete guide for deploying the Inventory Prediction System in development and production environments.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Production Deployment](#production-deployment)
4. [API Documentation](#api-documentation)
5. [Monitoring](#monitoring)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- Python 3.8+ (for backend)
- Node.js 18+ and npm (for frontend)
- Git

### System Requirements
- **Minimum**: 2 CPU cores, 4GB RAM, 10GB storage
- **Recommended**: 4 CPU cores, 8GB RAM, 20GB storage

---

## Local Development Setup

### Backend Setup

#### 1. Navigate to Backend Directory
```bash
cd backend
```

#### 2. Create Virtual Environment
```bash
python -m venv venv

# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Verify Models and Data
Ensure you have:
- Trained models in `../models/` directory
- Processed data in `../data/processed/` directory

If models don't exist, run the Jupyter notebooks first:
```bash
cd ..
jupyter notebook
# Run: 01_data_exploration_kaggle.ipynb, 02_model_training.ipynb, 03_model_evaluation.ipynb
```

#### 5. Run Backend Server
```bash
# Development mode (with auto-reload)
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 6. Verify Backend
Open browser and navigate to:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

### Frontend Setup

#### 1. Navigate to Frontend Directory
```bash
cd frontend
```

#### 2. Install Dependencies
```bash
npm install
```

#### 3. Configure Environment
```bash
# Create .env file
echo "REACT_APP_API_URL=http://localhost:8000" > .env
```

#### 4. Run Development Server
```bash
npm start
```

Application will open at http://localhost:3000

#### 5. Build for Production
```bash
npm run build
```

Build files will be in `build/` directory.

---

## Production Deployment

### Option 1: Render (Backend) + Vercel (Frontend) - Recommended ⭐

**Best for**: Quick deployment, free tier available, automatic HTTPS, CI/CD

#### Backend Deployment on Render

##### 1. Prepare Backend for Render
```bash
cd backend

# Render uses requirements.txt from root or service directory
# Make sure requirements.txt is present
cat requirements.txt
```

##### 2. Create `render.yaml` (optional but recommended)
Create a file at project root:
```yaml
services:
  - type: web
    name: inventory-prediction-api
    env: python
    region: oregon
    plan: free
    buildCommand: pip install -r backend/requirements.txt
    startCommand: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.16
      - key: PYTHONUNBUFFERED
        value: 1
```

##### 3. Deploy to Render

**Option A: Using Render Dashboard**
1. Go to https://render.com and sign up/login
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `inventory-prediction-api`
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free (or paid for better performance)

5. Add Environment Variables:
   - `PYTHON_VERSION`: `3.9.16`
   - `PYTHONUNBUFFERED`: `1`

6. Click "Create Web Service"

**Option B: Using Render CLI**
```bash
# Install Render CLI
npm install -g render-cli

# Login
render login

# Deploy
render deploy
```

##### 4. Wait for Deployment
- Render will build and deploy your backend
- You'll get a URL like: `https://inventory-prediction-api.onrender.com`
- **Note**: Free tier services sleep after 15 minutes of inactivity

##### 5. Test Backend
```bash
# Test health endpoint
curl https://inventory-prediction-api.onrender.com/health

# View API docs
open https://inventory-prediction-api.onrender.com/docs
```

---

#### Frontend Deployment on Vercel

##### 1. Prepare Frontend for Vercel
```bash
cd frontend

# Create vercel.json configuration
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

##### 2. Update package.json
Make sure your `package.json` has the build script:
```json
{
  "scripts": {
    "build": "react-scripts build",
    "start": "react-scripts start"
  }
}
```

##### 3. Create Production Environment File
```bash
# Create .env.production
echo "REACT_APP_API_URL=https://inventory-prediction-api.onrender.com" > .env.production
```

##### 4. Deploy to Vercel

**Option A: Using Vercel Dashboard**
1. Go to https://vercel.com and sign up/login
2. Click "Add New" → "Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Create React App
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `build` (auto-detected)
   - **Install Command**: `npm install` (auto-detected)

5. Add Environment Variables:
   - `REACT_APP_API_URL`: `https://inventory-prediction-api.onrender.com`

6. Click "Deploy"

**Option B: Using Vercel CLI**
```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy from frontend directory
cd frontend
vercel --prod
```

##### 5. Wait for Deployment
- Vercel will build and deploy your frontend
- You'll get a URL like: `https://inventory-prediction.vercel.app`
- Automatic HTTPS and CDN

##### 6. Test Frontend
```bash
# Open in browser
open https://inventory-prediction.vercel.app
```

---

#### Configure CORS for Render Backend

Update `backend/main.py` to allow Vercel domain:

```python
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://inventory-prediction.vercel.app",  # Add your Vercel domain
        "https://*.vercel.app",  # Allow all Vercel preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Commit and push changes:
```bash
git add backend/main.py
git commit -m "Update CORS for Vercel frontend"
git push
```

Render will automatically redeploy.

---

#### Custom Domains (Optional)

**Render Custom Domain:**
1. Go to Render Dashboard → Your Service → Settings
2. Click "Add Custom Domain"
3. Enter your domain (e.g., `api.yourdomain.com`)
4. Add CNAME record to your DNS:
   - Type: `CNAME`
   - Name: `api`
   - Value: `inventory-prediction-api.onrender.com`

**Vercel Custom Domain:**
1. Go to Vercel Dashboard → Your Project → Settings → Domains
2. Click "Add"
3. Enter your domain (e.g., `yourdomain.com`)
4. Follow DNS configuration instructions

---

#### Monitoring & Logs

**Render:**
- View logs: Dashboard → Your Service → Logs
- Metrics: Dashboard → Your Service → Metrics
- Health checks: Automatic
- Email alerts: Configure in Settings

**Vercel:**
- View logs: Dashboard → Your Project → Deployments → View Logs
- Analytics: Dashboard → Your Project → Analytics
- Real-time logs: `vercel logs`

---

#### Automatic Deployments

Both platforms support automatic deployments:

**Render:**
- Automatically deploys on push to `main` branch
- Can configure branch-specific deployments
- Preview deployments for pull requests (paid plans)

**Vercel:**
- Automatically deploys on push to any branch
- Preview deployments for pull requests (free)
- Production deployment for `main` branch

---

#### Cost Comparison

**Free Tier Features:**

| Feature | Render Free | Vercel Free |
|---------|------------|-------------|
| **Bandwidth** | 100 GB/month | 100 GB/month |
| **Build Time** | 500 hours/month | 6,000 minutes/month |
| **Deployments** | Unlimited | Unlimited |
| **Custom Domains** | ✅ Yes | ✅ Yes |
| **SSL** | ✅ Automatic | ✅ Automatic |
| **Sleep After** | 15 min inactivity | ❌ No sleep |
| **Cold Start** | ~30 seconds | ❌ N/A |

**Paid Plans:**
- **Render**: Starting at $7/month (no sleep, better performance)
- **Vercel**: Starting at $20/month (Pro features, analytics)

---

### Option 2: Simple VPS Deployment (DigitalOcean, Linode, AWS EC2)

#### 1. Server Setup
```bash
# SSH into your server
ssh user@your-server-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.8+
sudo apt install python3 python3-pip python3-venv -y

# Install Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# Install process manager
sudo npm install -g pm2
```

#### 2. Clone Repository
```bash
cd /var/www
sudo git clone https://github.com/AdityaKumbhar21/inventory_prediction.git
cd inventory_prediction
sudo chown -R $USER:$USER .
```

#### 3. Setup Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start with PM2
pm2 start "uvicorn main:app --host 0.0.0.0 --port 8000" --name inventory-backend
pm2 save
pm2 startup
```

#### 4. Setup Frontend
```bash
cd ../frontend
npm install

# Update API URL in .env.production
echo "REACT_APP_API_URL=http://your-domain.com:8000" > .env.production

npm run build

# Serve with PM2 (serves the built static files)
pm2 serve build 3000 --name inventory-frontend --spa
pm2 save
```

#### 5. Configure Firewall
```bash
# Allow SSH, HTTP, and HTTPS
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 8000
sudo ufw allow 3000
sudo ufw enable
```

#### 6. Setup SSL (Optional)
For production, use Let's Encrypt:
```bash
sudo apt install certbot -y
# Follow certbot instructions for your web server setup
```

---

### Option 3: Heroku Deployment (Alternative)

**Note**: Heroku no longer offers free tier, but included for reference.

#### Backend on Heroku

1. **Prepare Backend**
```bash
cd backend

# Create Procfile
echo "web: uvicorn main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Create runtime.txt
echo "python-3.9.16" > runtime.txt
```

2. **Deploy to Heroku**
```bash
heroku login
heroku create inventory-prediction-api
git add .
git commit -m "Deploy backend"
git push heroku main
```

3. **Set Environment Variables**
```bash
heroku config:set PYTHONUNBUFFERED=1
```

#### Frontend on Heroku

1. **Prepare Frontend**
```bash
cd frontend

# Create static.json
echo '{"root": "build/", "routes": {"/**": "index.html"}}' > static.json

# Update .env for Heroku
echo "REACT_APP_API_URL=https://inventory-prediction-api.herokuapp.com" > .env.production
```

2. **Deploy to Heroku**
```bash
heroku create inventory-prediction-app
heroku buildpacks:set heroku/nodejs
git add .
git commit -m "Deploy frontend"
git push heroku main
```

---

### Option 4: PythonAnywhere (Free Option)

#### Backend on PythonAnywhere

1. Create account at pythonanywhere.com
2. Open Bash console
3. Clone repository:
```bash
git clone https://github.com/AdityaKumbhar21/inventory_prediction.git
cd inventory_prediction/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. Create WSGI file at `/var/www/yourusername_pythonanywhere_com_wsgi.py`:
```python
import sys
import os

path = '/home/yourusername/inventory_prediction/backend'
if path not in sys.path:
    sys.path.append(path)

os.chdir(path)

from main import app as application
```

5. Configure Web App in PythonAnywhere dashboard

#### Frontend on Vercel/Netlify

1. **Vercel:**
```bash
cd frontend
npm install -g vercel
vercel --prod
```

2. **Netlify:**
```bash
cd frontend
npm run build
# Upload build/ folder to Netlify
```

---

## API Documentation

### Base URL
```
Development: http://localhost:8000
Production: https://your-domain.com/api
```

### Endpoints

#### Health Check
```http
GET /health
```

Response:
```json
{
  "status": "healthy",
  "models_loaded": 6,
  "data_loaded": true,
  "timestamp": "2025-10-31T10:30:00"
}
```

#### List Models
```http
GET /models
```

#### Single Prediction
```http
POST /predict
Content-Type: application/json

{
  "store": 1,
  "item": 1,
  "date": "2025-11-01",
  "model_name": "lightgbm"
}
```

Response:
```json
{
  "store": 1,
  "item": 1,
  "date": "2025-11-01",
  "predicted_sales": 52.34,
  "recommended_inventory": 63,
  "confidence_lower": 42.18,
  "confidence_upper": 62.50,
  "model_used": "lightgbm"
}
```

#### Batch Prediction
```http
POST /batch-predict
Content-Type: application/json

{
  "predictions": [
    {"store": 1, "item": 1, "date": "2025-11-01", "model_name": "lightgbm"},
    {"store": 1, "item": 2, "date": "2025-11-01", "model_name": "xgboost"}
  ]
}
```

#### Analytics
```http
GET /analytics/{store}/{item}?days=90
```

#### Forecast
```http
GET /forecast/{store}/{item}?days=7&model_name=lightgbm
```

---

## Monitoring

### Health Monitoring

#### Using curl
```bash
# Check health
curl http://localhost:8000/health

# Check models
curl http://localhost:8000/models
```

#### Using Python
```python
import requests
import time

def monitor_health():
    while True:
        try:
            response = requests.get('http://localhost:8000/health')
            if response.status_code == 200:
                print(f"✓ API healthy: {response.json()}")
            else:
                print(f"✗ API unhealthy: {response.status_code}")
        except Exception as e:
            print(f"✗ API unreachable: {e}")
        
        time.sleep(60)  # Check every minute

monitor_health()
```

### Application Logs

#### Backend Logs
```bash
# PM2 logs
pm2 logs inventory-backend

# Save logs to file
pm2 logs inventory-backend > backend_logs.txt
```

#### Frontend Logs
```bash
pm2 logs inventory-frontend
```

### Performance Monitoring

Monitor with PM2:
```bash
# View stats
pm2 monit

# View list
pm2 list

# View specific app
pm2 show inventory-backend
```

---

## Troubleshooting

### Backend Issues

#### Models Not Loading
```bash
# Check models directory
ls -la ../models/

# Verify model files exist
python -c "import joblib; model = joblib.load('../models/lightgbm_model.pkl'); print('OK')"
```

**Solution**: Run Jupyter notebooks to train models first

#### Import Errors
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"
```

#### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn main:app --reload --port 8001
```

#### Permission Denied
```bash
# Fix ownership
sudo chown -R $USER:$USER /var/www/inventory_prediction

# Fix permissions
chmod -R 755 /var/www/inventory_prediction
```

### Frontend Issues

#### API Connection Failed
Check `REACT_APP_API_URL` in `.env`:
```bash
# Development
echo "REACT_APP_API_URL=http://localhost:8000" > .env

# Production
echo "REACT_APP_API_URL=https://your-domain.com/api" > .env.production
```

#### Build Errors
```bash
# Clear cache
rm -rf node_modules package-lock.json
npm install

# Clear build
rm -rf build
npm run build
```

#### Module Not Found
```bash
# Reinstall dependencies
npm install

# Check Node version
node --version  # Should be 18+
```

### PM2 Issues

#### App Not Starting
```bash
# Check logs
pm2 logs inventory-backend --lines 50

# Delete and restart
pm2 delete inventory-backend
pm2 start "uvicorn main:app --host 0.0.0.0 --port 8000" --name inventory-backend
```

#### App Crashing
```bash
# View errors
pm2 logs inventory-backend --err

# Restart app
pm2 restart inventory-backend

# Save configuration
pm2 save
```

---

## Performance Optimization

### Backend
1. **Use Gunicorn with multiple workers**:
```bash
pip install gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

2. **Enable caching**: Cache predictions for repeated requests
3. **Use async operations**: Leverage FastAPI async capabilities
4. **Model optimization**: Use ONNX runtime for faster inference

### Frontend
1. **Code splitting**: Use React lazy loading
2. **Optimize images**: Compress and use WebP
3. **CDN**: Use CloudFront or Vercel CDN for static assets
4. **Caching**: Configure proper cache headers

### Caching Static Assets
```bash
# PM2 serve automatically handles basic caching
# For production, use CDN or dedicated static hosting like Vercel
```

---

## Security Best Practices

### Backend
- [ ] Implement authentication (JWT/OAuth)
- [ ] Add rate limiting
- [ ] Enable CORS with specific origins
- [ ] Use environment variables for secrets
- [ ] Implement input validation
- [ ] Add logging and monitoring

### Frontend
- [ ] Sanitize user inputs
- [ ] Use HTTPS in production
- [ ] Implement CSP headers
- [ ] Regular dependency updates

### Infrastructure
- [ ] Use firewall rules (UFW)
```bash
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```
- [ ] Enable SSL/TLS
- [ ] Regular backups
- [ ] Monitor logs for suspicious activity

---

## Maintenance

### Regular Tasks
- **Daily**: Check logs for errors (`pm2 logs`)
- **Weekly**: Review performance metrics (`pm2 monit`)
- **Monthly**: Update dependencies
- **Quarterly**: Security audit

### Backup Strategy
```bash
# Backup models
tar -czf models_backup_$(date +%Y%m%d).tar.gz models/

# Backup data
tar -czf data_backup_$(date +%Y%m%d).tar.gz data/

# Automated backup script
echo "0 2 * * * cd /var/www/inventory_prediction && tar -czf /backups/models_\$(date +\%Y\%m\%d).tar.gz models/" | crontab -
```

### Update Application
```bash
# Pull latest changes
cd /var/www/inventory_prediction
git pull origin main

# Update backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
pm2 restart inventory-backend

# Update frontend
cd ../frontend
npm install
npm run build
pm2 restart inventory-frontend
```

---

## Support

For issues and questions:
- **GitHub Issues**: [Repository Issues](https://github.com/AdityaKumbhar21/inventory_prediction/issues)
- **Email**: your-email@example.com
- **Documentation**: Full docs at `/docs`

---

## License

This project is licensed under the MIT License - see LICENSE file for details.

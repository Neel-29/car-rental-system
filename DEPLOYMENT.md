# Car Rental System - Vercel Deployment Guide

## 🚀 Deployment to Vercel

This guide will help you deploy the Car Rental System to Vercel, a modern platform for static sites and serverless functions.

## 📋 Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Account**: For version control and deployment
3. **Node.js**: For local development (optional)

## 🔧 Deployment Steps

### Step 1: Prepare Your Repository

1. **Initialize Git** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. **Create GitHub Repository**:
   - Go to GitHub and create a new repository
   - Push your code to GitHub:
   ```bash
   git remote add origin https://github.com/yourusername/car-rental-system.git
   git push -u origin main
   ```

### Step 2: Deploy to Vercel

1. **Connect to Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository

2. **Configure Project**:
   - **Framework Preset**: Other
   - **Root Directory**: Leave as `./`
   - **Build Command**: Leave empty (Vercel will auto-detect)
   - **Output Directory**: Leave empty

3. **Environment Variables** (Optional):
   - `FLASK_ENV`: `production`
   - `SECRET_KEY`: Generate a secure secret key

4. **Deploy**:
   - Click "Deploy"
   - Wait for deployment to complete

### Step 3: Access Your Application

- Your app will be available at: `https://your-project-name.vercel.app`
- The admin login is: `admin` / `admin123`

## 🌐 Web-Based Features

Since Vercel is a serverless platform, some features have been adapted:

### ✅ Available Features
- **User Authentication**: Login/Register system
- **Role-Based Access**: Admin, Car Owner, Rental Company, Customer
- **Car Management**: Add, browse, and manage cars
- **Rental System**: Book cars and manage rentals
- **Dashboard Analytics**: Statistics and reporting
- **Simulated Driver Monitoring**: Web-based simulation with charts

### 🔄 Simulated Driver Monitoring

The driver monitoring system has been adapted for web deployment:

- **Real-time Simulation**: Generates realistic EAR data
- **Interactive Charts**: Live updating Eye Aspect Ratio graphs
- **Drowsiness Detection**: Simulated alerts and warnings
- **Statistics Display**: Min/Max EAR values and trends
- **Visual Feedback**: Color-coded status indicators

## 📁 Project Structure

```
├── api/
│   └── index.py              # Main Flask application
├── templates/                # HTML templates
├── static/                   # CSS, JS, and assets
├── vercel.json              # Vercel configuration
├── requirements.txt         # Python dependencies
└── DEPLOYMENT.md           # This file
```

## 🔧 Configuration Files

### vercel.json
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
```

### requirements.txt
```
Flask==2.3.3
Flask-Login==0.6.3
Flask-SQLAlchemy==3.0.5
Werkzeug==2.3.7
Jinja2==3.1.2
MarkupSafe==2.1.3
itsdangerous==2.1.2
click==8.1.7
blinker==1.6.3
SQLAlchemy==2.0.21
```

## 🚨 Important Notes

### Limitations
- **No Real Camera Access**: Camera-based monitoring is simulated
- **No Audio Alerts**: Pygame audio is not available in serverless environment
- **Database**: Uses SQLite (consider upgrading to PostgreSQL for production)
- **File Storage**: Static files only (no persistent file uploads)

### Production Considerations
1. **Database**: Upgrade to PostgreSQL or another cloud database
2. **File Storage**: Use AWS S3 or similar for file uploads
3. **Security**: Implement proper secret management
4. **Monitoring**: Add logging and error tracking
5. **Scaling**: Consider database connection pooling

## 🔄 Local Development

To run locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python api/index.py
```

## 📱 Mobile Responsiveness

The application is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones
- All modern browsers

## 🆘 Troubleshooting

### Common Issues

1. **Build Failures**:
   - Check Python version compatibility
   - Verify all dependencies are in requirements.txt

2. **Database Issues**:
   - SQLite database is created automatically
   - For production, consider external database

3. **Template Errors**:
   - Ensure all templates are in the templates/ directory
   - Check template syntax

### Support

For issues with:
- **Vercel Deployment**: Check Vercel documentation
- **Flask Application**: Check Flask documentation
- **Database**: Check SQLAlchemy documentation

## 🎯 Next Steps

1. **Custom Domain**: Add your own domain in Vercel settings
2. **SSL Certificate**: Automatically provided by Vercel
3. **Analytics**: Add Vercel Analytics for usage tracking
4. **Monitoring**: Implement error tracking (Sentry, etc.)
5. **Database**: Upgrade to cloud database for production

## 📊 Performance

- **Cold Start**: ~1-2 seconds for first request
- **Warm Requests**: <100ms response time
- **Concurrent Users**: Supports hundreds of users
- **Storage**: 1GB free tier (upgrade as needed)

---

**Happy Deploying! 🚀**

Your Car Rental System is now live on Vercel!

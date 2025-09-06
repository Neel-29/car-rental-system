# 🚗 Car Rental System - Vercel Deployment

A comprehensive car rental management system with driver monitoring capabilities, deployed on Vercel.

## 🌟 Features

### Core System
- **Multi-Role Authentication**: Admin, Car Owner, Rental Company, Customer
- **Car Management**: Add, browse, and manage vehicle inventory
- **Rental System**: Complete booking and management workflow
- **Commission System**: Automated profit calculations
- **Dashboard Analytics**: Real-time statistics and reporting

### Driver Monitoring (Web Simulation)
- **Real-time Simulation**: Generates realistic driver behavior data
- **Eye Aspect Ratio Tracking**: Live chart visualization
- **Drowsiness Detection**: Simulated alerts and warnings
- **Statistics Display**: Min/Max values and trend analysis
- **Visual Feedback**: Color-coded status indicators

## 🚀 Quick Start

### Option 1: Deploy to Vercel (Recommended)

1. **Fork this repository**
2. **Go to [Vercel](https://vercel.com)**
3. **Import your forked repository**
4. **Deploy with default settings**
5. **Access your app at the provided URL**

### Option 2: Local Development

```bash
# Clone the repository
git clone https://github.com/yourusername/car-rental-system.git
cd car-rental-system

# Install dependencies
pip install -r requirements.txt

# Run the application
python api/index.py
```

## 👤 Default Login

- **Username**: `admin`
- **Password**: `admin123`

## 🎯 User Roles

### Admin
- System overview and management
- User management
- Global analytics

### Car Owner
- Add and manage vehicles
- View earnings and statistics
- Monitor rentals

### Rental Company
- Manage fleet
- Process bookings
- Track commissions

### Customer
- Browse available cars
- Book rentals
- View rental history

## 📊 Driver Monitoring

The system includes a sophisticated driver monitoring simulation:

- **Real-time EAR Chart**: Live updating Eye Aspect Ratio visualization
- **Drowsiness Detection**: Simulated alerts when driver appears drowsy
- **Blink Counting**: Automatic blink detection and counting
- **Statistics**: Min/Max EAR values and trend analysis
- **Visual Alerts**: Color-coded warnings and status indicators

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Charts**: Chart.js
- **Deployment**: Vercel
- **Authentication**: Flask-Login

## 📱 Responsive Design

The application is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones
- All modern browsers

## 🔧 Configuration

### Environment Variables
- `FLASK_ENV`: Set to `production` for Vercel
- `SECRET_KEY`: Generate a secure secret key

### Database
- SQLite database is created automatically
- For production, consider upgrading to PostgreSQL

## 📈 Performance

- **Cold Start**: ~1-2 seconds
- **Response Time**: <100ms for warm requests
- **Concurrent Users**: Supports hundreds of users
- **Storage**: 1GB free tier

## 🚨 Limitations

- **No Real Camera Access**: Driver monitoring is simulated
- **No Audio Alerts**: Audio alerts not available in serverless environment
- **File Storage**: Limited to static files only

## 🔄 Updates

The system automatically updates when you push changes to your GitHub repository.

## 📞 Support

For issues or questions:
1. Check the [Deployment Guide](DEPLOYMENT.md)
2. Review Vercel documentation
3. Check Flask documentation

## 📄 License

This project is open source and available under the MIT License.

---

**Built with ❤️ for modern car rental management**

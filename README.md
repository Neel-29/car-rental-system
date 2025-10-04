# Smart Car Rental System with AI-Powered Driver Monitoring

A comprehensive car rental platform that connects car owners, rental companies, and customers while providing AI-powered driver monitoring for enhanced safety using computer vision and fatigue detection.

## 🚗 Features

### Core System Features
- **Multi-role Platform**: Support for Car Owners, Rental Companies, Customers, and System Administrators
- **Vehicle Management**: Complete CRUD operations for vehicle listings
- **Rental Management**: Booking system with automated calculations
- **Commission System**: Automated commission and handling fee calculations
- **Real-time Monitoring**: Live driver monitoring with AI-powered fatigue detection
- **Responsive Design**: Modern, mobile-friendly web interface

### AI-Powered Driver Monitoring
- **Real-time Drowsiness Detection**: Uses computer vision to detect driver fatigue
- **Eye Aspect Ratio (EAR) Analysis**: Monitors eye closure patterns
- **Instant Alerts**: Visual and audio alerts for drowsiness detection
- **Performance Analytics**: Track driver performance and safety metrics
- **Session Recording**: Store monitoring data for analysis and reporting

### User Roles & Capabilities

#### Car Owners
- List and manage their vehicles
- Set daily rental rates
- Track income and earnings
- Monitor active rentals
- View driver monitoring data

#### Rental Companies
- Manage fleet of vehicles from multiple owners
- Handle customer bookings
- Track commissions and handling fees
- Monitor driver safety
- Generate revenue reports

#### Customers
- Browse available vehicles
- Book rentals with real-time pricing
- Access driver monitoring during rentals
- View rental history
- Rate and review experiences

#### System Administrators
- Oversee entire platform
- Manage users and companies
- Monitor system performance
- Access comprehensive analytics
- Handle support requests

## 🛠️ Technology Stack

### Backend
- **Flask**: Web framework
- **SQLAlchemy**: Database ORM
- **Flask-Login**: User authentication
- **OpenCV**: Computer vision processing
- **dlib**: Facial landmark detection
- **NumPy & SciPy**: Mathematical computations

### Frontend
- **Bootstrap 5**: Responsive UI framework
- **Chart.js**: Data visualization
- **JavaScript**: Interactive features
- **HTML5/CSS3**: Modern web standards

### AI/ML Components
- **Facial Landmark Detection**: 70-point facial landmark model
- **Eye Aspect Ratio Calculation**: Real-time drowsiness detection
- **Computer Vision**: Live video processing
- **Alert System**: Multi-modal safety notifications

## 📋 Prerequisites

- Python 3.8 or higher
- Webcam or camera device
- Modern web browser with camera support
- 4GB+ RAM (for video processing)

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd car-rental-system
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Download AI Model
The system requires the dlib facial landmark predictor model. Download it from:
```bash
# Create models directory
mkdir -p Fatigue-Detection-System-Based-On-Behavioural-Characteristics-Of-Driver/models

# Download the model (you may need to find a valid download link)
# Place shape_predictor_70_face_landmarks.dat in the models directory
```

### 5. Initialize Database
```bash
python app.py
```
The application will automatically create the database and tables on first run.

### 6. Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///car_rental.db
DEBUG=True
```

### Database Configuration
The system uses SQLite by default. For production, consider using PostgreSQL or MySQL:
```python
# In app.py, update the database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/car_rental'
```

## 📱 Usage Guide

### Getting Started

1. **Register an Account**
   - Visit the homepage
   - Click "Register" and select your role
   - Fill in your details and create account

2. **Car Owners**
   - Add your vehicles with details and daily rates
   - Monitor active rentals and earnings
   - View driver monitoring data for safety

3. **Rental Companies**
   - Set up company profile
   - Manage fleet of vehicles
   - Handle customer bookings and payments
   - Monitor driver safety

4. **Customers**
   - Browse available vehicles
   - Book rentals with transparent pricing
   - Access real-time driver monitoring
   - View rental history

### Driver Monitoring System

1. **Start Monitoring**
   - Click "Start Monitoring" on active rental
   - Allow camera access when prompted
   - System will calibrate automatically

2. **Safety Features**
   - Real-time drowsiness detection
   - Visual alerts for dangerous driving
   - Performance analytics and reporting
   - Session recording and playback

3. **Monitoring Dashboard**
   - Live video feed with overlay
   - Real-time statistics (blinks, alerts, EAR)
   - Historical performance data
   - Alert management system

## 🔒 Security Features

- **Role-based Access Control**: Different permissions for each user type
- **Secure Authentication**: Password hashing and session management
- **Data Privacy**: Encrypted storage of sensitive information
- **Camera Security**: Local processing, no video data stored
- **Input Validation**: Comprehensive form validation and sanitization

## 📊 API Endpoints

### Authentication
- `POST /login` - User login
- `POST /register` - User registration
- `GET /logout` - User logout

### Car Management
- `GET /cars` - List all cars
- `POST /cars/add` - Add new car
- `PUT /cars/<id>` - Update car
- `DELETE /cars/<id>` - Delete car

### Rental Management
- `GET /rentals` - List rentals
- `POST /rentals/book` - Book rental
- `PUT /rentals/<id>/cancel` - Cancel rental

### Monitoring
- `POST /api/monitor/start/<rental_id>` - Start monitoring
- `POST /api/monitor/stop/<session_id>` - Stop monitoring
- `POST /api/monitor/process` - Process monitoring data

## 🧪 Testing

### Run Tests
```bash
# Install test dependencies
pip install pytest pytest-flask

# Run tests
pytest tests/
```

### Test Coverage
- Unit tests for all models
- Integration tests for API endpoints
- UI tests for critical user flows
- Performance tests for monitoring system

## 🚀 Deployment

### Production Setup

1. **Environment Configuration**
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY=your-production-secret-key
   ```

2. **Database Migration**
   ```bash
   flask db upgrade
   ```

3. **Web Server Setup**
   - Use Gunicorn or uWSGI for production
   - Configure Nginx as reverse proxy
   - Set up SSL certificates

4. **Monitoring Setup**
   - Configure camera access
   - Set up logging and monitoring
   - Implement backup strategies

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation wiki

## 🔮 Future Enhancements

- **Mobile App**: Native iOS and Android applications
- **Advanced AI**: Machine learning models for better detection
- **IoT Integration**: Vehicle telemetry and diagnostics
- **Payment Gateway**: Integrated payment processing
- **Multi-language Support**: Internationalization
- **Advanced Analytics**: Business intelligence dashboard
- **Blockchain Integration**: Smart contracts for rentals
- **AR/VR Features**: Virtual vehicle inspection

## 🙏 Acknowledgments

- **dlib Library**: For facial landmark detection
- **OpenCV Community**: For computer vision tools
- **Flask Community**: For the excellent web framework
- **Bootstrap Team**: For the responsive UI framework

---

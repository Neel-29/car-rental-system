from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import json
from functools import wraps
from monitoring_routes import monitoring_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///car_rental.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Register monitoring blueprint
app.register_blueprint(monitoring_bp)

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'car_owner', 'rental_company', 'customer'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    cars = db.relationship('Car', backref='owner', lazy=True)
    rentals = db.relationship('Rental', backref='customer', lazy=True)
    company = db.relationship('RentalCompany', backref='user', uselist=False)

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    license_plate = db.Column(db.String(20), unique=True, nullable=False)
    color = db.Column(db.String(20), nullable=False)
    daily_rate = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='available')  # 'available', 'rented', 'maintenance'
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rental_company_id = db.Column(db.Integer, db.ForeignKey('rental_company.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    rentals = db.relationship('Rental', backref='car', lazy=True)
    monitoring_data = db.relationship('DriverMonitoring', backref='car', lazy=True)

class RentalCompany(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    commission_rate = db.Column(db.Float, default=0.15)  # 15% commission
    handling_fee = db.Column(db.Float, default=50.0)  # $50 handling fee
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    cars = db.relationship('Car', backref='rental_company', lazy=True)
    rentals = db.relationship('Rental', backref='rental_company', lazy=True)

class Rental(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rental_company_id = db.Column(db.Integer, db.ForeignKey('rental_company.id'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    daily_rate = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    commission = db.Column(db.Float, nullable=False)
    handling_fee = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='active')  # 'active', 'completed', 'cancelled'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    monitoring_sessions = db.relationship('DriverMonitoring', backref='rental', lazy=True)

class DriverMonitoring(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rental_id = db.Column(db.Integer, db.ForeignKey('rental.id'), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_start = db.Column(db.DateTime, nullable=False)
    session_end = db.Column(db.DateTime)
    total_blinks = db.Column(db.Integer, default=0)
    drowsiness_alerts = db.Column(db.Integer, default=0)
    avg_ear = db.Column(db.Float)  # Average Eye Aspect Ratio
    status = db.Column(db.String(20), default='active')  # 'active', 'completed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Simplified Fatigue Detection (Mock for demo)
class MockFatigueDetector:
    def __init__(self):
        self.blinkCount = 0
        self.drowsy = 0
        self.avg_ear = 0.3

    def process_frame(self, frame):
        # Mock processing - in real implementation this would use OpenCV and dlib
        import random
        ear = 0.25 + random.random() * 0.1  # Simulate EAR between 0.25-0.35
        is_drowsy = ear < 0.27
        
        if is_drowsy:
            self.drowsy = 1
        else:
            self.blinkCount += 1
            self.drowsy = 0
        
        self.avg_ear = (self.avg_ear + ear) / 2
        
        return {
            "blink_count": self.blinkCount,
            "drowsy": bool(self.drowsy),
            "ear": ear,
            "landmarks": []
        }

# Initialize mock fatigue detector
fatigue_detector = MockFatigueDetector()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Role-based access control decorator
def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            if current_user.role not in roles:
                flash('Access denied. Insufficient permissions.', 'error')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('register.html')
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role=role
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif current_user.role == 'car_owner':
        return redirect(url_for('car_owner_dashboard'))
    elif current_user.role == 'rental_company':
        return redirect(url_for('rental_company_dashboard'))
    else:
        return redirect(url_for('customer_dashboard'))

# Admin Dashboard
@app.route('/admin')
@login_required
@role_required(['admin'])
def admin_dashboard():
    stats = {
        'total_users': User.query.count(),
        'total_cars': Car.query.count(),
        'total_rentals': Rental.query.count(),
        'active_rentals': Rental.query.filter_by(status='active').count(),
        'total_companies': RentalCompany.query.count()
    }
    
    recent_rentals = Rental.query.order_by(Rental.created_at.desc()).limit(10).all()
    recent_monitoring = DriverMonitoring.query.order_by(DriverMonitoring.created_at.desc()).limit(10).all()
    
    return render_template('admin_dashboard.html', stats=stats, recent_rentals=recent_rentals, recent_monitoring=recent_monitoring)

# Car Owner Dashboard
@app.route('/car_owner')
@login_required
@role_required(['car_owner'])
def car_owner_dashboard():
    cars = Car.query.filter_by(owner_id=current_user.id).all()
    active_rentals = Rental.query.join(Car).filter(Car.owner_id == current_user.id, Rental.status == 'active').all()
    
    # Calculate total income
    total_income = 0
    for rental in Rental.query.join(Car).filter(Car.owner_id == current_user.id, Rental.status == 'completed'):
        total_income += rental.total_amount - rental.commission - rental.handling_fee
    
    return render_template('car_owner_dashboard.html', cars=cars, active_rentals=active_rentals, total_income=total_income)

# Rental Company Dashboard
@app.route('/rental_company')
@login_required
@role_required(['rental_company'])
def rental_company_dashboard():
    company = RentalCompany.query.filter_by(user_id=current_user.id).first()
    if not company:
        flash('Please complete your company profile first', 'error')
        return redirect(url_for('setup_company'))
    
    cars = Car.query.filter_by(rental_company_id=company.id).all()
    active_rentals = Rental.query.filter_by(rental_company_id=company.id, status='active').all()
    
    # Calculate total revenue
    total_revenue = 0
    for rental in Rental.query.filter_by(rental_company_id=company.id, status='completed'):
        total_revenue += rental.commission + rental.handling_fee
    
    return render_template('rental_company_dashboard.html', company=company, cars=cars, active_rentals=active_rentals, total_revenue=total_revenue)

# Customer Dashboard
@app.route('/customer')
@login_required
@role_required(['customer'])
def customer_dashboard():
    active_rentals = Rental.query.filter_by(customer_id=current_user.id, status='active').all()
    rental_history = Rental.query.filter_by(customer_id=current_user.id).order_by(Rental.created_at.desc()).limit(10).all()
    
    return render_template('customer_dashboard.html', active_rentals=active_rentals, rental_history=rental_history)

# Driver Monitoring Routes
@app.route('/monitor/<int:rental_id>')
@login_required
def monitor_driver(rental_id):
    rental = Rental.query.get_or_404(rental_id)
    
    # Check if user has permission to monitor this rental
    if (current_user.role == 'customer' and rental.customer_id != current_user.id) or \
       (current_user.role == 'car_owner' and rental.car.owner_id != current_user.id) or \
       (current_user.role == 'rental_company' and rental.rental_company_id != current_user.company.id):
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('real_driver_monitoring.html', rental=rental)

@app.route('/api/monitor/start/<int:rental_id>', methods=['POST'])
@login_required
def start_monitoring(rental_id):
    rental = Rental.query.get_or_404(rental_id)
    
    # Create monitoring session
    monitoring = DriverMonitoring(
        rental_id=rental_id,
        car_id=rental.car_id,
        driver_id=rental.customer_id,
        session_start=datetime.utcnow()
    )
    
    db.session.add(monitoring)
    db.session.commit()
    
    return jsonify({"session_id": monitoring.id, "status": "started"})

@app.route('/api/monitor/stop/<int:session_id>', methods=['POST'])
@login_required
def stop_monitoring(session_id):
    monitoring = DriverMonitoring.query.get_or_404(session_id)
    monitoring.session_end = datetime.utcnow()
    monitoring.status = 'completed'
    
    db.session.commit()
    
    return jsonify({"status": "stopped"})

@app.route('/api/monitor/process', methods=['POST'])
@login_required
def process_monitoring_data():
    data = request.get_json()
    session_id = data.get('session_id')
    
    monitoring = DriverMonitoring.query.get_or_404(session_id)
    
    # Update monitoring data from frontend
    monitoring.total_blinks = data.get('blink_count', 0)
    monitoring.drowsiness_alerts = data.get('drowsiness_alerts', 0)
    monitoring.avg_ear = data.get('avg_ear', 0.0)
    
    db.session.commit()
    
    return jsonify({
        "status": "updated",
        "blink_count": monitoring.total_blinks,
        "drowsiness_alerts": monitoring.drowsiness_alerts,
        "avg_ear": monitoring.avg_ear
    })

# Car Management Routes
@app.route('/cars/add', methods=['GET', 'POST'])
@login_required
@role_required(['car_owner'])
def add_car():
    if request.method == 'POST':
        car = Car(
            make=request.form['make'],
            model=request.form['model'],
            year=int(request.form['year']),
            license_plate=request.form['license_plate'],
            color=request.form['color'],
            daily_rate=float(request.form['daily_rate']),
            owner_id=current_user.id
        )
        
        db.session.add(car)
        db.session.commit()
        
        flash('Car added successfully!', 'success')
        return redirect(url_for('car_owner_dashboard'))
    
    return render_template('add_car.html')

# Company Setup Route
@app.route('/setup_company', methods=['GET', 'POST'])
@login_required
@role_required(['rental_company'])
def setup_company():
    if request.method == 'POST':
        company = RentalCompany(
            name=request.form['name'],
            address=request.form['address'],
            phone=request.form['phone'],
            commission_rate=float(request.form['commission_rate']),
            handling_fee=float(request.form['handling_fee']),
            user_id=current_user.id
        )
        
        db.session.add(company)
        db.session.commit()
        
        flash('Company profile created successfully!', 'success')
        return redirect(url_for('rental_company_dashboard'))
    
    return render_template('setup_company.html')

# Browse Cars Route
@app.route('/cars')
@login_required
def browse_cars():
    cars = Car.query.filter_by(status='available').all()
    return render_template('browse_cars.html', cars=cars)

# Add Car to Company Fleet
@app.route('/cars/add_to_fleet/<int:car_id>', methods=['POST'])
@login_required
@role_required(['rental_company'])
def add_car_to_fleet(car_id):
    car = Car.query.get_or_404(car_id)
    company = RentalCompany.query.filter_by(user_id=current_user.id).first()
    
    if not company:
        flash('Please setup your company profile first', 'error')
        return redirect(url_for('setup_company'))
    
    if car.rental_company_id:
        flash('This car is already assigned to a rental company', 'error')
    else:
        car.rental_company_id = company.id
        db.session.commit()
        flash(f'{car.make} {car.model} added to your fleet successfully!', 'success')
    
    return redirect(url_for('browse_cars'))

# Remove Car from Company Fleet
@app.route('/cars/remove_from_fleet/<int:car_id>', methods=['POST'])
@login_required
@role_required(['rental_company'])
def remove_car_from_fleet(car_id):
    car = Car.query.get_or_404(car_id)
    company = RentalCompany.query.filter_by(user_id=current_user.id).first()
    
    if car.rental_company_id == company.id:
        car.rental_company_id = None
        db.session.commit()
        flash(f'{car.make} {car.model} removed from your fleet', 'success')
    else:
        flash('You can only remove cars from your own fleet', 'error')
    
    return redirect(url_for('rental_company_dashboard'))

# Rental Management Routes
@app.route('/rentals/book/<int:car_id>', methods=['GET', 'POST'])
@login_required
@role_required(['customer'])
def book_car(car_id):
    car = Car.query.get_or_404(car_id)
    
    if request.method == 'POST':
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
        
        # Calculate rental duration and cost
        duration = (end_date - start_date).days
        total_amount = car.daily_rate * duration
        
        # Find available rental company
        rental_company = RentalCompany.query.first()  # Simplified - in real app, you'd have logic to assign companies
        
        if rental_company:
            commission = total_amount * rental_company.commission_rate
            handling_fee = rental_company.handling_fee
            
            rental = Rental(
                car_id=car_id,
                customer_id=current_user.id,
                rental_company_id=rental_company.id,
                start_date=start_date,
                end_date=end_date,
                daily_rate=car.daily_rate,
                total_amount=total_amount,
                commission=commission,
                handling_fee=handling_fee
            )
            
            # Update car status
            car.status = 'rented'
            
            db.session.add(rental)
            db.session.commit()
            
            flash('Car booked successfully!', 'success')
            return redirect(url_for('customer_dashboard'))
        else:
            flash('No rental company available', 'error')
    
    return render_template('book_car.html', car=car)

# API Endpoints
@app.route('/api/dashboard/stats')
@login_required
def dashboard_stats():
    if current_user.role == 'admin':
        stats = {
            'total_users': User.query.count(),
            'total_cars': Car.query.count(),
            'total_rentals': Rental.query.count(),
            'active_rentals': Rental.query.filter_by(status='active').count(),
            'total_companies': RentalCompany.query.count()
        }
    elif current_user.role == 'car_owner':
        cars = Car.query.filter_by(owner_id=current_user.id).all()
        active_rentals = Rental.query.join(Car).filter(Car.owner_id == current_user.id, Rental.status == 'active').all()
        total_income = sum(rental.total_amount - rental.commission - rental.handling_fee 
                          for rental in Rental.query.join(Car).filter(Car.owner_id == current_user.id, Rental.status == 'completed'))
        
        stats = {
            'total_cars': len(cars),
            'active_rentals': len(active_rentals),
            'total_income': total_income
        }
    elif current_user.role == 'rental_company':
        company = RentalCompany.query.filter_by(user_id=current_user.id).first()
        if company:
            cars = Car.query.filter_by(rental_company_id=company.id).all()
            active_rentals = Rental.query.filter_by(rental_company_id=company.id, status='active').all()
            total_revenue = sum(rental.commission + rental.handling_fee 
                              for rental in Rental.query.filter_by(rental_company_id=company.id, status='completed'))
            
            stats = {
                'fleet_size': len(cars),
                'active_rentals': len(active_rentals),
                'total_revenue': total_revenue
            }
        else:
            stats = {'fleet_size': 0, 'active_rentals': 0, 'total_revenue': 0}
    else:  # customer
        active_rentals = Rental.query.filter_by(customer_id=current_user.id, status='active').all()
        rental_history = Rental.query.filter_by(customer_id=current_user.id).count()
        
        stats = {
            'active_rentals': len(active_rentals),
            'total_rentals': rental_history
        }
    
    return jsonify(stats)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create admin user if it doesn't exist
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@carrental.com',
                password_hash=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("✓ Admin user created: admin/admin123")
    
    print("🚗 Car Rental System Starting...")
    print("📱 Open: http://localhost:5000")
    print("👤 Login: admin/admin123")
    app.run(debug=True)

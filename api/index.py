from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime, timedelta
import json

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///car_rental.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, car_owner, rental_company, customer
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String(30), nullable=False)
    license_plate = db.Column(db.String(20), unique=True, nullable=False)
    daily_rate = db.Column(db.Float, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class RentalCompany(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_email = db.Column(db.String(120), nullable=False)
    contact_phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    commission_rate = db.Column(db.Float, default=0.15)  # 15% commission
    handling_fee = db.Column(db.Float, default=25.0)  # $25 handling fee
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Rental(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rental_company_id = db.Column(db.Integer, db.ForeignKey('rental_company.id'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    total_cost = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='active')  # active, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DriverMonitoring(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rental_id = db.Column(db.Integer, db.ForeignKey('rental.id'), nullable=False)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    total_blinks = db.Column(db.Integer, default=0)
    drowsiness_events = db.Column(db.Integer, default=0)
    avg_ear = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='active')  # active, completed, stopped

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='Username already exists')
        
        if User.query.filter_by(email=email).first():
            return render_template('register.html', error='Email already registered')
        
        user = User(username=username, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return redirect(url_for('dashboard'))
    
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

@app.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('dashboard'))
    
    stats = {
        'total_users': User.query.count(),
        'total_cars': Car.query.count(),
        'total_rentals': Rental.query.count(),
        'total_companies': RentalCompany.query.count()
    }
    
    return render_template('admin_dashboard.html', stats=stats)

@app.route('/car-owner')
@login_required
def car_owner_dashboard():
    if current_user.role != 'car_owner':
        return redirect(url_for('dashboard'))
    
    cars = Car.query.filter_by(owner_id=current_user.id).all()
    stats = {
        'total_cars': len(cars),
        'available_cars': len([c for c in cars if c.is_available]),
        'total_earnings': 0  # Calculate from rentals
    }
    
    return render_template('car_owner_dashboard.html', cars=cars, stats=stats)

@app.route('/rental-company')
@login_required
def rental_company_dashboard():
    if current_user.role != 'rental_company':
        return redirect(url_for('dashboard'))
    
    company = RentalCompany.query.filter_by(owner_id=current_user.id).first()
    if not company:
        return redirect(url_for('setup_company'))
    
    stats = {
        'total_rentals': Rental.query.filter_by(rental_company_id=company.id).count(),
        'active_rentals': Rental.query.filter_by(rental_company_id=company.id, status='active').count(),
        'total_revenue': 0  # Calculate from rentals
    }
    
    return render_template('rental_company_dashboard.html', company=company, stats=stats)

@app.route('/customer')
@login_required
def customer_dashboard():
    if current_user.role != 'customer':
        return redirect(url_for('dashboard'))
    
    rentals = Rental.query.filter_by(customer_id=current_user.id).all()
    stats = {
        'total_rentals': len(rentals),
        'active_rentals': len([r for r in rentals if r.status == 'active'])
    }
    
    return render_template('customer_dashboard.html', rentals=rentals, stats=stats)

@app.route('/setup-company', methods=['GET', 'POST'])
@login_required
def setup_company():
    if current_user.role != 'rental_company':
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        
        company = RentalCompany(
            name=name,
            contact_email=email,
            contact_phone=phone,
            address=address,
            owner_id=current_user.id
        )
        db.session.add(company)
        db.session.commit()
        
        return redirect(url_for('rental_company_dashboard'))
    
    return render_template('setup_company.html')

@app.route('/add-car', methods=['GET', 'POST'])
@login_required
def add_car():
    if current_user.role != 'car_owner':
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        make = request.form['make']
        model = request.form['model']
        year = int(request.form['year'])
        color = request.form['color']
        license_plate = request.form['license_plate']
        daily_rate = float(request.form['daily_rate'])
        
        car = Car(
            make=make,
            model=model,
            year=year,
            color=color,
            license_plate=license_plate,
            daily_rate=daily_rate,
            owner_id=current_user.id
        )
        db.session.add(car)
        db.session.commit()
        
        return redirect(url_for('car_owner_dashboard'))
    
    return render_template('add_car.html')

@app.route('/browse-cars')
@login_required
def browse_cars():
    cars = Car.query.filter_by(is_available=True).all()
    return render_template('browse_cars.html', cars=cars)

@app.route('/book-car/<int:car_id>', methods=['GET', 'POST'])
@login_required
def book_car(car_id):
    car = Car.query.get_or_404(car_id)
    
    if request.method == 'POST':
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
        rental_company_id = int(request.form['rental_company_id'])
        
        days = (end_date - start_date).days + 1
        total_cost = car.daily_rate * days
        
        rental = Rental(
            car_id=car.id,
            customer_id=current_user.id,
            rental_company_id=rental_company_id,
            start_date=start_date,
            end_date=end_date,
            total_cost=total_cost
        )
        db.session.add(rental)
        car.is_available = False
        db.session.commit()
        
        return redirect(url_for('customer_dashboard'))
    
    companies = RentalCompany.query.all()
    return render_template('book_car.html', car=car, companies=companies)

@app.route('/monitor/<int:rental_id>')
@login_required
def monitor_driver(rental_id):
    rental = Rental.query.get_or_404(rental_id)
    
    # Check if user has permission to monitor this rental
    if (current_user.role == 'customer' and rental.customer_id != current_user.id) or \
       (current_user.role == 'car_owner' and rental.car.owner_id != current_user.id) or \
       (current_user.role == 'rental_company' and rental.rental_company_id != current_user.id) or \
       current_user.role != 'admin':
        return redirect(url_for('dashboard'))
    
    return render_template('driver_monitoring_vercel.html', rental=rental)

# API Routes
@app.route('/api/dashboard/stats')
@login_required
def dashboard_stats():
    if current_user.role == 'admin':
        return jsonify({
            'total_users': User.query.count(),
            'total_cars': Car.query.count(),
            'total_rentals': Rental.query.count(),
            'total_companies': RentalCompany.query.count()
        })
    elif current_user.role == 'car_owner':
        cars = Car.query.filter_by(owner_id=current_user.id).all()
        return jsonify({
            'total_cars': len(cars),
            'available_cars': len([c for c in cars if c.is_available]),
            'total_earnings': 0
        })
    elif current_user.role == 'rental_company':
        company = RentalCompany.query.filter_by(owner_id=current_user.id).first()
        if company:
            return jsonify({
                'total_rentals': Rental.query.filter_by(rental_company_id=company.id).count(),
                'active_rentals': Rental.query.filter_by(rental_company_id=company.id, status='active').count(),
                'total_revenue': 0
            })
        return jsonify({'error': 'Company not found'})
    else:
        rentals = Rental.query.filter_by(customer_id=current_user.id).all()
        return jsonify({
            'total_rentals': len(rentals),
            'active_rentals': len([r for r in rentals if r.status == 'active'])
        })

@app.route('/api/monitor/process', methods=['POST'])
@login_required
def process_monitoring_data():
    data = request.get_json()
    
    # Store monitoring data in database
    monitoring = DriverMonitoring.query.filter_by(session_id=data.get('session_id')).first()
    if not monitoring:
        monitoring = DriverMonitoring(
            rental_id=data.get('rental_id'),
            session_id=data.get('session_id', f"session_{data.get('rental_id')}_{int(datetime.now().timestamp())}")
        )
        db.session.add(monitoring)
    
    monitoring.total_blinks = data.get('blink_count', 0)
    monitoring.drowsiness_events += 1 if data.get('drowsy') else 0
    monitoring.avg_ear = data.get('ear', 0.0)
    
    db.session.commit()
    
    return jsonify({
        "status": "updated",
        "blink_count": monitoring.total_blinks,
        "drowsiness_events": monitoring.drowsiness_events,
        "avg_ear": monitoring.avg_ear
    })

# Initialize database
def create_tables():
    with app.app_context():
        db.create_all()
        
        # Create admin user if not exists
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', email='admin@example.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)

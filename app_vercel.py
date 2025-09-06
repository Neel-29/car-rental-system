from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///car_rental.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
    role = db.Column(db.String(20), nullable=False, default='customer')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String(20), nullable=False)
    price_per_day = db.Column(db.Float, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class RentalCompany(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_info = db.Column(db.String(200), nullable=False)
    commission_rate = db.Column(db.Float, default=0.15)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Rental(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('rental_company.id'), nullable=True)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    total_cost = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DriverMonitoring(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rental_id = db.Column(db.Integer, db.ForeignKey('rental.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ear_value = db.Column(db.Float, nullable=False)
    blink_count = db.Column(db.Integer, default=0)
    drowsy = db.Column(db.Boolean, default=False)
    face_detected = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"Error loading page: {str(e)}", 500

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
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return render_template('register.html')
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role=role
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
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

@app.route('/admin')
@login_required
def admin_dashboard():
    try:
        if current_user.role != 'admin':
            flash('Access denied')
            return redirect(url_for('dashboard'))
        
        users = User.query.all()
        cars = Car.query.all()
        rentals = Rental.query.all()
        companies = RentalCompany.query.all()
        
        return render_template('admin_dashboard.html', 
                             users=users, cars=cars, rentals=rentals, companies=companies)
    except Exception as e:
        return f"Error loading admin dashboard: {str(e)}", 500

@app.route('/car_owner')
@login_required
def car_owner_dashboard():
    if current_user.role != 'car_owner':
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    cars = Car.query.filter_by(owner_id=current_user.id).all()
    rentals = Rental.query.join(Car).filter(Car.owner_id == current_user.id).all()
    
    return render_template('car_owner_dashboard.html', cars=cars, rentals=rentals)

@app.route('/rental_company')
@login_required
def rental_company_dashboard():
    if current_user.role != 'rental_company':
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    company = RentalCompany.query.filter_by(user_id=current_user.id).first()
    if not company:
        return redirect(url_for('setup_company'))
    
    rentals = Rental.query.filter_by(company_id=company.id).all()
    available_cars = Car.query.filter_by(is_available=True).all()
    
    return render_template('rental_company_dashboard.html', 
                         company=company, rentals=rentals, available_cars=available_cars)

@app.route('/customer')
@login_required
def customer_dashboard():
    if current_user.role != 'customer':
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    rentals = Rental.query.filter_by(customer_id=current_user.id).all()
    return render_template('customer_dashboard.html', rentals=rentals)

@app.route('/add_car', methods=['GET', 'POST'])
@login_required
def add_car():
    if current_user.role != 'car_owner':
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        car = Car(
            make=request.form['make'],
            model=request.form['model'],
            year=int(request.form['year']),
            color=request.form['color'],
            price_per_day=float(request.form['price_per_day']),
            owner_id=current_user.id
        )
        db.session.add(car)
        db.session.commit()
        flash('Car added successfully!')
        return redirect(url_for('car_owner_dashboard'))
    
    return render_template('add_car.html')

@app.route('/setup_company', methods=['GET', 'POST'])
@login_required
def setup_company():
    if current_user.role != 'rental_company':
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        company = RentalCompany(
            name=request.form['name'],
            contact_info=request.form['contact_info'],
            commission_rate=float(request.form['commission_rate']),
            user_id=current_user.id
        )
        db.session.add(company)
        db.session.commit()
        flash('Company setup successful!')
        return redirect(url_for('rental_company_dashboard'))
    
    return render_template('setup_company.html')

@app.route('/cars')
@login_required
def browse_cars():
    cars = Car.query.filter_by(is_available=True).all()
    return render_template('browse_cars.html', cars=cars)

@app.route('/book_car/<int:car_id>', methods=['GET', 'POST'])
@login_required
def book_car(car_id):
    car = Car.query.get_or_404(car_id)
    
    if request.method == 'POST':
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
        days = (end_date - start_date).days + 1
        total_cost = car.price_per_day * days
        
        rental = Rental(
            car_id=car.id,
            customer_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
            total_cost=total_cost
        )
        
        car.is_available = False
        db.session.add(rental)
        db.session.commit()
        
        flash(f'Car booked successfully! Total cost: ${total_cost:.2f}')
        return redirect(url_for('customer_dashboard'))
    
    return render_template('book_car.html', car=car)

@app.route('/monitor/<int:rental_id>')
@login_required
def monitor_driver(rental_id):
    rental = Rental.query.get_or_404(rental_id)
    
    # Check if user has permission to monitor this rental
    if (current_user.role == 'customer' and rental.customer_id != current_user.id) or \
       (current_user.role == 'car_owner' and rental.car.owner_id != current_user.id) or \
       (current_user.role == 'rental_company' and rental.company_id != current_user.id) or \
       (current_user.role != 'admin'):
        flash('Access denied')
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
        rentals = Rental.query.join(Car).filter(Car.owner_id == current_user.id).all()
        return jsonify({
            'total_cars': len(cars),
            'total_rentals': len(rentals),
            'available_cars': len([c for c in cars if c.is_available])
        })
    elif current_user.role == 'rental_company':
        company = RentalCompany.query.filter_by(user_id=current_user.id).first()
        if company:
            rentals = Rental.query.filter_by(company_id=company.id).all()
            return jsonify({
                'total_rentals': len(rentals),
                'company_name': company.name
            })
        return jsonify({'total_rentals': 0, 'company_name': 'Not Setup'})
    else:
        rentals = Rental.query.filter_by(customer_id=current_user.id).all()
        return jsonify({'total_rentals': len(rentals)})

@app.route('/api/monitor/process', methods=['POST'])
@login_required
def process_monitoring_data():
    data = request.get_json()
    
    monitoring = DriverMonitoring(
        rental_id=data['rental_id'],
        user_id=data['user_id'],
        ear_value=data['ear'],
        blink_count=data['blink_count'],
        drowsy=data['drowsy'],
        face_detected=data['face_detected']
    )
    
    db.session.add(monitoring)
    db.session.commit()
    
    return jsonify({'status': 'success'})

# Initialize database and create admin user
with app.app_context():
    try:
        db.create_all()
        
        # Create admin user if not exists
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@example.com',
                password_hash=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully")
    except Exception as e:
        print(f"Database initialization error: {e}")

if __name__ == '__main__':
    app.run(debug=True)

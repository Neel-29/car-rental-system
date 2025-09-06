#!/usr/bin/env python3
"""
Demo data script for Car Rental System (Simplified Version)
This script populates the database with sample data for testing.
"""

from app_simple import app, db, User, Car, RentalCompany, Rental
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

def create_demo_users():
    """Create demo users for different roles."""
    users = [
        {
            'username': 'admin',
            'email': 'admin@carrental.com',
            'password': 'admin123',
            'role': 'admin'
        },
        {
            'username': 'carowner1',
            'email': 'owner1@example.com',
            'password': 'password123',
            'role': 'car_owner'
        },
        {
            'username': 'carowner2',
            'email': 'owner2@example.com',
            'password': 'password123',
            'role': 'car_owner'
        },
        {
            'username': 'rentalcompany1',
            'email': 'company1@example.com',
            'password': 'password123',
            'role': 'rental_company'
        },
        {
            'username': 'customer1',
            'email': 'customer1@example.com',
            'password': 'password123',
            'role': 'customer'
        },
        {
            'username': 'customer2',
            'email': 'customer2@example.com',
            'password': 'password123',
            'role': 'customer'
        }
    ]
    
    for user_data in users:
        existing_user = User.query.filter_by(username=user_data['username']).first()
        if not existing_user:
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                password_hash=generate_password_hash(user_data['password']),
                role=user_data['role']
            )
            db.session.add(user)
            print(f"✓ Created user: {user_data['username']}")
        else:
            print(f"✓ User already exists: {user_data['username']}")
    
    db.session.commit()

def create_demo_companies():
    """Create demo rental companies."""
    company_data = {
        'name': 'City Car Rentals',
        'address': '123 Main Street, Downtown, City 12345',
        'phone': '+1-555-0123',
        'commission_rate': 0.15,
        'handling_fee': 50.0
    }
    
    # Get rental company user
    company_user = User.query.filter_by(role='rental_company').first()
    if company_user:
        existing_company = RentalCompany.query.filter_by(user_id=company_user.id).first()
        if not existing_company:
            company = RentalCompany(
                name=company_data['name'],
                address=company_data['address'],
                phone=company_data['phone'],
                commission_rate=company_data['commission_rate'],
                handling_fee=company_data['handling_fee'],
                user_id=company_user.id
            )
            db.session.add(company)
            print(f"✓ Created company: {company_data['name']}")
        else:
            print(f"✓ Company already exists: {company_data['name']}")
    
    db.session.commit()

def create_demo_cars():
    """Create demo cars."""
    car_models = [
        {'make': 'Toyota', 'model': 'Camry', 'year': 2022, 'color': 'Silver', 'daily_rate': 45.0},
        {'make': 'Honda', 'model': 'Civic', 'year': 2021, 'color': 'Blue', 'daily_rate': 40.0},
        {'make': 'Ford', 'model': 'Focus', 'year': 2023, 'color': 'Red', 'daily_rate': 42.0},
        {'make': 'Chevrolet', 'model': 'Malibu', 'year': 2022, 'color': 'Black', 'daily_rate': 48.0},
        {'make': 'Nissan', 'model': 'Altima', 'year': 2021, 'color': 'White', 'daily_rate': 44.0},
        {'make': 'Hyundai', 'model': 'Elantra', 'year': 2023, 'color': 'Gray', 'daily_rate': 38.0},
        {'make': 'Kia', 'model': 'Optima', 'year': 2022, 'color': 'Green', 'daily_rate': 41.0},
        {'make': 'Mazda', 'model': 'Mazda3', 'year': 2021, 'color': 'Red', 'daily_rate': 43.0}
    ]
    
    # Get car owners
    car_owners = User.query.filter_by(role='car_owner').all()
    rental_company = RentalCompany.query.first()
    
    for i, car_data in enumerate(car_models):
        # Assign cars to different owners
        owner = car_owners[i % len(car_owners)]
        
        existing_car = Car.query.filter_by(license_plate=f"ABC{1000+i}").first()
        if not existing_car:
            car = Car(
                make=car_data['make'],
                model=car_data['model'],
                year=car_data['year'],
                license_plate=f"ABC{1000+i}",
                color=car_data['color'],
                daily_rate=car_data['daily_rate'],
                owner_id=owner.id,
                rental_company_id=rental_company.id if rental_company else None,
                status='available'
            )
            db.session.add(car)
            print(f"✓ Created car: {car_data['make']} {car_data['model']}")
        else:
            print(f"✓ Car already exists: {car_data['make']} {car_data['model']}")
    
    db.session.commit()

def create_demo_rentals():
    """Create demo rentals."""
    cars = Car.query.limit(3).all()
    customers = User.query.filter_by(role='customer').all()
    rental_company = RentalCompany.query.first()
    
    if not cars or not customers or not rental_company:
        print("⚠️  Not enough data to create rentals")
        return
    
    for i, car in enumerate(cars):
        customer = customers[i % len(customers)]
        
        # Create rental for next week
        start_date = datetime.now() + timedelta(days=7)
        end_date = start_date + timedelta(days=random.randint(1, 7))
        duration = (end_date - start_date).days
        total_amount = car.daily_rate * duration
        commission = total_amount * rental_company.commission_rate
        
        existing_rental = Rental.query.filter_by(car_id=car.id, customer_id=customer.id).first()
        if not existing_rental:
            rental = Rental(
                car_id=car.id,
                customer_id=customer.id,
                rental_company_id=rental_company.id,
                start_date=start_date,
                end_date=end_date,
                daily_rate=car.daily_rate,
                total_amount=total_amount,
                commission=commission,
                handling_fee=rental_company.handling_fee,
                status='active'
            )
            
            # Update car status
            car.status = 'rented'
            
            db.session.add(rental)
            print(f"✓ Created rental: {car.make} {car.model} for {customer.username}")
        else:
            print(f"✓ Rental already exists: {car.make} {car.model}")
    
    db.session.commit()

def main():
    """Main function to create all demo data."""
    with app.app_context():
        print("🚗 Creating demo data for Car Rental System")
        print("=" * 50)
        
        # Create database tables
        db.create_all()
        print("✓ Database tables created")
        
        # Create demo data
        print("\n👥 Creating users...")
        create_demo_users()
        
        print("\n🏢 Creating companies...")
        create_demo_companies()
        
        print("\n🚗 Creating cars...")
        create_demo_cars()
        
        print("\n📅 Creating rentals...")
        create_demo_rentals()
        
        print("\n✅ Demo data creation complete!")
        print("\nDemo accounts created:")
        print("- Admin: admin / admin123")
        print("- Car Owners: carowner1, carowner2 / password123")
        print("- Rental Company: rentalcompany1 / password123")
        print("- Customers: customer1, customer2 / password123")
        
        print("\nYou can now run: python app_simple.py")

if __name__ == "__main__":
    main()

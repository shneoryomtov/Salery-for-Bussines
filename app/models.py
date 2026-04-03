from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    scenarios = db.relationship('Scenario', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Scenario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Input fields
    weekly_hours = db.Column(db.Float, nullable=False)
    work_days_per_week = db.Column(db.Integer, nullable=False)
    hourly_rate = db.Column(db.Float)
    monthly_gross = db.Column(db.Float)
    holidays_reduction = db.Column(db.Integer, default=0)
    vacation_days = db.Column(db.Integer, default=0)
    sick_days = db.Column(db.Integer, default=0)
    pension_contribution = db.Column(db.Float, default=0)  # percentage
    study_fund_contribution = db.Column(db.Float, default=0)  # percentage

    # Recognized expenses
    car_expense = db.Column(db.Float, default=0)
    fuel_expense = db.Column(db.Float, default=0)
    equipment_expense = db.Column(db.Float, default=0)
    home_office_expense = db.Column(db.Float, default=0)
    depreciation_expense = db.Column(db.Float, default=0)
    leasing_expense = db.Column(db.Float, default=0)
    recurring_expenses = db.Column(db.Float, default=0)

    # Recognition percentages
    car_recognition = db.Column(db.Float, default=0.27)
    fuel_recognition = db.Column(db.Float, default=0.27)
    equipment_recognition = db.Column(db.Float, default=0.1)
    home_office_recognition = db.Column(db.Float, default=0.25)
    depreciation_recognition = db.Column(db.Float, default=1.0)
    leasing_recognition = db.Column(db.Float, default=0.1)
    recurring_recognition = db.Column(db.Float, default=0.1)

    def __repr__(self):
        return f"Scenario('{self.title}', '{self.date_created}')"
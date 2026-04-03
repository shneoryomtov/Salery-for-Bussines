from flask import Blueprint, render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt
from app.models import User, Scenario
from app.forms import RegistrationForm, LoginForm, ScenarioForm
from app.calculator import calculator

auth = Blueprint('auth', __name__)
main = Blueprint('main', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('החשבון נוצר בהצלחה! כעת תוכל להתחבר.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', title='הרשמה', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('התחברות נכשלה. בדוק את האימייל והסיסמה.', 'danger')
    return render_template('login.html', title='התחברות', form=form)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@main.route('/')
def home():
    return render_template('home.html', title='בית')

@main.route('/dashboard')
@login_required
def dashboard():
    scenarios = Scenario.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', title='לוח בקרה', scenarios=scenarios)

@main.route('/scenario/new', methods=['GET', 'POST'])
@login_required
def new_scenario():
    form = ScenarioForm()
    if form.validate_on_submit():
        scenario = Scenario(
            title=form.title.data,
            weekly_hours=form.weekly_hours.data,
            work_days_per_week=form.work_days_per_week.data,
            hourly_rate=form.hourly_rate.data,
            monthly_gross=form.monthly_gross.data,
            holidays_reduction=form.holidays_reduction.data,
            vacation_days=form.vacation_days.data,
            sick_days=form.sick_days.data,
            pension_contribution=form.pension_contribution.data,
            study_fund_contribution=form.study_fund_contribution.data,
            car_expense=form.car_expense.data,
            fuel_expense=form.fuel_expense.data,
            equipment_expense=form.equipment_expense.data,
            home_office_expense=form.home_office_expense.data,
            depreciation_expense=form.depreciation_expense.data,
            leasing_expense=form.leasing_expense.data,
            recurring_expenses=form.recurring_expenses.data,
            author=current_user
        )
        db.session.add(scenario)
        db.session.commit()
        flash('התרחיש נשמר בהצלחה!', 'success')
        return redirect(url_for('main.scenario', scenario_id=scenario.id))
    return render_template('scenario_form.html', title='תרחיש חדש', form=form, legend='יצירת תרחיש חדש')

@main.route('/scenario/<int:scenario_id>')
@login_required
def scenario(scenario_id):
    scenario = Scenario.query.get_or_404(scenario_id)
    if scenario.author != current_user:
        abort(403)
    results = calculator.calculate(scenario)
    return render_template('scenario.html', title=scenario.title, scenario=scenario, results=results)

@main.route('/scenario/<int:scenario_id>/update', methods=['GET', 'POST'])
@login_required
def update_scenario(scenario_id):
    scenario = Scenario.query.get_or_404(scenario_id)
    if scenario.author != current_user:
        abort(403)
    form = ScenarioForm()
    if form.validate_on_submit():
        scenario.title = form.title.data
        scenario.weekly_hours = form.weekly_hours.data
        scenario.work_days_per_week = form.work_days_per_week.data
        scenario.hourly_rate = form.hourly_rate.data
        scenario.monthly_gross = form.monthly_gross.data
        scenario.holidays_reduction = form.holidays_reduction.data
        scenario.vacation_days = form.vacation_days.data
        scenario.sick_days = form.sick_days.data
        scenario.pension_contribution = form.pension_contribution.data
        scenario.study_fund_contribution = form.study_fund_contribution.data
        scenario.car_expense = form.car_expense.data
        scenario.fuel_expense = form.fuel_expense.data
        scenario.equipment_expense = form.equipment_expense.data
        scenario.home_office_expense = form.home_office_expense.data
        scenario.depreciation_expense = form.depreciation_expense.data
        scenario.leasing_expense = form.leasing_expense.data
        scenario.recurring_expenses = form.recurring_expenses.data
        db.session.commit()
        flash('התרחיש עודכן בהצלחה!', 'success')
        return redirect(url_for('main.scenario', scenario_id=scenario.id))
    elif request.method == 'GET':
        form.title.data = scenario.title
        form.weekly_hours.data = scenario.weekly_hours
        form.work_days_per_week.data = scenario.work_days_per_week
        form.hourly_rate.data = scenario.hourly_rate
        form.monthly_gross.data = scenario.monthly_gross
        form.holidays_reduction.data = scenario.holidays_reduction
        form.vacation_days.data = scenario.vacation_days
        form.sick_days.data = scenario.sick_days
        form.pension_contribution.data = scenario.pension_contribution
        form.study_fund_contribution.data = scenario.study_fund_contribution
        form.car_expense.data = scenario.car_expense
        form.fuel_expense.data = scenario.fuel_expense
        form.equipment_expense.data = scenario.equipment_expense
        form.home_office_expense.data = scenario.home_office_expense
        form.depreciation_expense.data = scenario.depreciation_expense
        form.leasing_expense.data = scenario.leasing_expense
        form.recurring_expenses.data = scenario.recurring_expenses
    return render_template('scenario_form.html', title='עדכון תרחיש', form=form, legend='עדכון תרחיש')

@main.route('/scenario/<int:scenario_id>/delete', methods=['POST'])
@login_required
def delete_scenario(scenario_id):
    scenario = Scenario.query.get_or_404(scenario_id)
    if scenario.author != current_user:
        abort(403)
    db.session.delete(scenario)
    db.session.commit()
    flash('התרחיש נמחק בהצלחה!', 'success')
    return redirect(url_for('main.dashboard'))
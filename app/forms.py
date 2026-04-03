from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User

class RegistrationForm(FlaskForm):
    username = StringField('שם משתמש', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('אימייל', validators=[DataRequired(), Email()])
    password = PasswordField('סיסמה', validators=[DataRequired()])
    confirm_password = PasswordField('אישור סיסמה', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('הרשמה')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('שם משתמש זה כבר קיים. בחר שם אחר.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('אימייל זה כבר רשום במערכת.')

class LoginForm(FlaskForm):
    email = StringField('אימייל', validators=[DataRequired(), Email()])
    password = PasswordField('סיסמה', validators=[DataRequired()])
    submit = SubmitField('התחברות')

class ScenarioForm(FlaskForm):
    title = StringField('כותרת התרחיש', validators=[DataRequired(), Length(min=1, max=100)])
    weekly_hours = FloatField('שעות עבודה שבועיות', validators=[DataRequired()])
    work_days_per_week = IntegerField('ימי עבודה בשבוע', validators=[DataRequired()])
    hourly_rate = FloatField('שכר שעתי (אופציונלי)')
    monthly_gross = FloatField('שכר ברוטו חודשי (אופציונלי)')
    holidays_reduction = IntegerField('ימי חגים והפחתות', default=0)
    vacation_days = IntegerField('ימי חופשה', default=0)
    sick_days = IntegerField('ימי מחלה', default=0)
    pension_contribution = FloatField('הפרשה לפנסיה (%)', default=0)
    study_fund_contribution = FloatField('הפרשה לקרן השתלמות (%)', default=0)
    car_expense = FloatField('הוצאות רכב', default=0)
    fuel_expense = FloatField('הוצאות דלק', default=0)
    equipment_expense = FloatField('הוצאות ציוד', default=0)
    home_office_expense = FloatField('הוצאות משרד ביתי', default=0)
    depreciation_expense = FloatField('פחת נכסים', default=0)
    leasing_expense = FloatField('הוצאות ליסינג', default=0)
    recurring_expenses = FloatField('הוצאות חוזרות', default=0)
    submit = SubmitField('שמור תרחיש')
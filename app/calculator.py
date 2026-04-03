# Calculation engine for self-employed income in Israel
# All values are estimates and should not be used for official tax purposes

class IncomeCalculator:
    def __init__(self):
        # Tax brackets for 2024 (approximate, update as needed)
        self.income_tax_brackets = [
            (0, 77400, 0.10),
            (77400, 110880, 0.14),
            (110880, 178080, 0.20),
            (178080, 247440, 0.31),
            (247440, 514920, 0.35),
            (514920, 662560, 0.47),
            (662560, float('inf'), 0.50)
        ]

        # National Insurance rates (approximate)
        self.national_insurance_rate = 0.031
        self.health_insurance_rate = 0.015

        # Other constants
        self.weeks_per_year = 52
        self.months_per_year = 12
        self.official_holidays = 9  # Approximate official holidays in Israel

    def calculate(self, scenario):
        results = {}

        # Basic inputs
        weekly_hours = scenario.weekly_hours
        work_days_per_week = scenario.work_days_per_week
        hourly_rate = scenario.hourly_rate or 0
        monthly_gross = scenario.monthly_gross or 0

        # Calculate gross income
        if monthly_gross > 0:
            annual_gross = monthly_gross * self.months_per_year
            effective_hourly_rate = annual_gross / (weekly_hours * self.weeks_per_year)
        else:
            annual_gross = hourly_rate * weekly_hours * self.weeks_per_year
            effective_hourly_rate = hourly_rate

        results['annual_gross'] = annual_gross
        results['monthly_gross'] = annual_gross / self.months_per_year
        results['effective_hourly_rate'] = effective_hourly_rate

        # Effective work days and hours
        total_work_days_year = work_days_per_week * self.weeks_per_year
        holidays_reduction = scenario.holidays_reduction
        effective_work_days = total_work_days_year - self.official_holidays - holidays_reduction
        effective_work_hours = effective_work_days * (weekly_hours / work_days_per_week)

        results['effective_work_days'] = effective_work_days
        results['effective_work_hours'] = effective_work_hours

        # Vacation and sick reserves (assuming 8.33% for vacation, 2.5% for sick)
        vacation_reserve = annual_gross * 0.0833
        sick_reserve = annual_gross * 0.025

        results['vacation_reserve'] = vacation_reserve
        results['sick_reserve'] = sick_reserve

        # Recognized expenses
        recognized_expenses = (
            scenario.car_expense * scenario.car_recognition +
            scenario.fuel_expense * scenario.fuel_recognition +
            scenario.equipment_expense * scenario.equipment_recognition +
            scenario.home_office_expense * scenario.home_office_recognition +
            scenario.depreciation_expense * scenario.depreciation_recognition +
            scenario.leasing_expense * scenario.leasing_recognition +
            scenario.recurring_expenses * scenario.recurring_recognition
        )

        results['recognized_expenses'] = recognized_expenses

        # Taxable income
        taxable_income = annual_gross - recognized_expenses - vacation_reserve - sick_reserve

        # Deductions
        pension_deduction = taxable_income * (scenario.pension_contribution / 100)
        study_fund_deduction = taxable_income * (scenario.study_fund_contribution / 100)

        taxable_income -= pension_deduction + study_fund_deduction

        results['taxable_income'] = taxable_income

        # Income tax calculation
        income_tax = self._calculate_tax(taxable_income, self.income_tax_brackets)
        results['income_tax'] = income_tax

        # National Insurance and Health
        national_insurance = taxable_income * self.national_insurance_rate
        health_insurance = taxable_income * self.health_insurance_rate

        results['national_insurance'] = national_insurance
        results['health_insurance'] = health_insurance

        # Net income
        total_deductions = income_tax + national_insurance + health_insurance + pension_deduction + study_fund_deduction
        annual_net = annual_gross - total_deductions
        monthly_net = annual_net / self.months_per_year

        results['annual_net'] = annual_net
        results['monthly_net'] = monthly_net

        # Gross needed for target net (simplified, assuming linear)
        if monthly_net > 0:
            target_gross_ratio = annual_gross / annual_net
            results['gross_for_target_net'] = lambda target_net: target_net * self.months_per_year * target_gross_ratio
        else:
            results['gross_for_target_net'] = lambda target_net: 0

        return results

    def _calculate_tax(self, income, brackets):
        tax = 0
        for min_income, max_income, rate in brackets:
            if income > min_income:
                taxable_in_bracket = min(income, max_income) - min_income
                tax += taxable_in_bracket * rate
            else:
                break
        return tax

# Global calculator instance
calculator = IncomeCalculator()
# Israeli Self-Employed Income Calculator

A personal Streamlit web application for calculating and planning income as a self-employed individual in Israel. This tool helps estimate effective income, taxes, deductions, and plan various scenarios.

## Features

- **Work Profile Management**: Define work hours, income rate, and work schedule
- **Calendar Integration**: Account for holidays, vacation days, and sick days
- **Expense Tracking**: Add and manage business expenses with tax recognition percentages
- **Pension & Study Fund**: Calculate contributions to pension plans and study funds
- **Tax Calculations**: Apply progressive tax brackets for Israeli tax system
- **National Insurance**: Calculate mandatory national insurance and health payments
- **Target Net Solver**: Find required gross income to reach a target net income
- **Scenario Save/Load**: Save and compare multiple financial scenarios
- **Detailed Explanations**: See formula breakdowns for every calculation

## Tech Stack

- **Python 3.11+**
- **Streamlit**: Web UI framework
- **Pandas & Plotly**: Data processing and visualization
- **Decimal**: Precise money calculations
- **Pydantic/Dataclasses**: Data validation and typing

## Installation

1. Clone or download this repository:
```bash
git clone git@github.com:shneoryomtov/Salery-for-Bussines.git
cd Salary-for-Business
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the App

```bash
streamlit run main.py
```

The app will open at `http://localhost:8501`

## Project Structure

```
Salary-for-Business/
├── main.py                          # Streamlit app entry point
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
├── config/
│   ├── settings_2026_israel.json   # Tax rates and holiday defaults
│   └── default_scenario.json       # Default scenario template
├── engine/
│   ├── models.py                   # Data models (dataclasses)
│   ├── calculator.py               # Main calculation pipeline
│   ├── worktime.py                 # Work hours calculations
│   ├── expenses.py                 # Expense processing
│   ├── contributions.py            # Pension/study fund calculations
│   ├── taxes.py                    # Tax and NI calculations
│   ├── solver.py                   # Binary search solver
│   ├── explain.py                  # Explanation generation
│   └── io_utils.py                 # JSON I/O utilities
├── app/
│   ├── ui.py                       # Streamlit UI components
│   └── formatters.py               # Number/currency formatters
├── tests/
│   └── test_engine.py              # Unit tests
├── saved/                          # Directory for saved scenarios
└── examples/                       # Example scenarios
```

## Configuration

Edit `config/settings_2026_israel.json` to customize:
- Income tax brackets
- National insurance rates
- Health payment rates
- Study fund ceiling
- Holiday defaults
- Tax credit point values

**IMPORTANT**: Verify that tax rates match current year regulations before relying on results.

## Core Concepts

### Work Hours Calculation

```
Daily Hours = Weekly Hours ÷ Work Days per Week
Potential Annual Hours = (Yearly Workdays - Holidays - Time Off) × Daily Hours
Effective Billable Hours = Potential Hours - Lost Hours
Annual Gross = Hourly Rate × Effective Hours (or Monthly Gross × Months)
```

### Expense Recognition

Expenses are applied with a tax recognition percentage (0-100%). This allows modeling:
- Partially deductible expenses
- Depreciation assets over multiple years
- Recurring vs. one-time costs
- Leasing payments with date ranges

### Tax Calculation

Taxes are calculated using progressive brackets. Each bracket applies only to income within its threshold range:

```
Tax = Σ[Income in bracket × Tax rate for bracket] - Tax credits
```

### Net Income Calculation

```
Net Annual = Gross Income
           - Actual Expenses (cash outflow)
           - Income Tax
           - National Insurance
           - Health Payments
           - Actual Pension/Study Fund Contributions (if cash mode)
```

**Key distinction**: Tax-deductible expenses reduce taxable income, but actual money paid for expenses also reduces net income.

## Usage Guide

### Basic Workflow

1. **Set Work Profile**: Define your work schedule and income
2. **Add Calendar Settings**: Account for holidays and time off
3. **Enter Expenses**: Add all business expenses with recognition percentages
4. **Configure Contributions**: Set pension and study fund percentages
5. **Review Results**: See detailed breakdown of gross → net
6. **Save Scenario**: Store this scenario for future reference or comparison
7. **Use Solver**: Find gross income needed for a target net income

### Scenario Comparison

Save multiple scenarios to compare:
- Different income levels
- Various expense structures
- Different work schedules
- Contribution alternatives

### Advanced Features

- **Depreciation Assets**: Calculate annual depreciation for equipment purchases
- **Leasing Payments**: Model recurring lease payments with limited date ranges
- **Multiple Scenarios**: Compare side-by-side financial outcomes
- **Tax Credits**: Apply tax credit points to reduce final tax burden

## Important Notes

⚠️ **This tool is NOT official tax advice.** It's for personal planning and estimation only.

**Before relying on results:**
- Verify all tax rates with current Israeli Tax Authority (Madatz) regulations
- Confirm pension and study fund contribution limits
- Discuss results with a professional accountant
- Update config files annually for rate changes

## Calculations are based on:
- Israeli income tax brackets (2026 sample)
- National insurance rates
- Health payment rates
- Study fund contribution ceilings
- Standard work year assumptions (260 workdays)

## Future Enhancements

- [ ] Multi-year scenario comparison
- [ ] Export to PDF/Excel reports
- [ ] Historical tracking
- [ ] Investment return modeling
- [ ] Quarterly estimation mode
- [ ] Web deployment

## License & Disclaimer

MIT License - See LICENSE file for details.

**DISCLAIMER**: This tool is provided for educational and planning purposes only. It is not an official tax calculation tool and should not replace professional tax advice. Always consult with a certified Israeli tax advisor (עו״ד מס או רואה חשבון) before making financial decisions.

## Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Created**: March 2026  
**Updated**: March 22, 2026  
**Designed for**: Israeli self-employed individuals and freelancers

# Salary Calculator for Israel - Next.js Edition

A modern web application for calculating and planning personal income as a self-employed individual in Israel.

## 🚀 Features

- **Modern React UI** with Hebrew RTL support
- **Responsive Design** works on all devices
- **Real-time Calculations** with instant results
- **Professional Formatting** for currency and percentages
- **Vercel Ready** - Deploy in one click
- **Full Calculator** for work hours, expenses, taxes, and net income

## 🛠 Tech Stack

- **Next.js 15** - React framework with App Router
- **TypeScript** - Type-safe calculations
- **Tailwind CSS** - Modern styling
- **Decimal.js** - Precise financial calculations
- **Vercel** - Serverless deployment

## 📦 Installation

```bash
# Clone the repo
git clone git@github.com:shneoryomtov/Salery-for-Bussines.git
cd Salary-for-Business

# Install dependencies
npm install

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## 🚀 Deploy to Vercel

### Option 1: Direct from GitHub (Recommended)

1. Go to [vercel.com](https://vercel.com)
2. Click "Import Project"
3. Select your GitHub repository
4. Click "Deploy"

### Option 2: Using Vercel CLI

```bash
npm install -g vercel
vercel
```

## 📝 Features

### Work Profile
- Hourly rate or monthly salary
- Flexible work schedule
- Multi-month work year support

### Calendar Management
- Holiday days tracking
- Erev holiday hours
- Vacation and sick days

### Expenses
- Add unlimited business expenses
- Tax recognition percentages
- Automatic annualization (monthly/yearly)

### Calculations
- Gross to net income breakdown
- Progressive tax calculation
- National insurance and health payments
- Pension and study fund contributions

### Results
- Summary cards with key metrics
- Detailed breakdown table
- Formula explanations
- Effective deduction rate

## 📊 Default Tax Settings (2026)

The app includes default Israeli tax rates:
- Income tax brackets (10% - 49%)
- National insurance (7.11%)
- Health payments (5.3%)
- Tax credit point value (₪2,700)
- Study fund ceiling (₪12,000)

**⚠️ Important**: Verify these match current regulations before relying on results.

## 📱 Usage

1. **Enter Work Profile** - Define your work schedule and income
2. **Add Calendar** - Account for holidays and time off
3. **List Expenses** - Add business deductions
4. **Calculate** - Get instant results
5. **Review** - See detailed breakdown and formulas

## 🔒 Privacy

- **All calculations are local** - No data sent to servers except the API calculation
- **No external storage** - Use browser localStorage for custom scenarios
- **GDPR Compliant** - No personal data collection

## 📄 Disclaimer

This tool is for **personal planning only**. It is NOT official tax advice. Always consult with a professional Israeli accountant (רואה חשבון) before making financial decisions.

## 📞 Support

For issues or questions, open an issue on GitHub.

## 📄 License

MIT License

---

**Created**: March 2026
**Version**: 1.0.0
**Target Platform**: Vercel ✨

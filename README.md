# מחשבון הכנסה לעצמאיים בישראל

אפליקציית Flask לחישוב ההכנסה הנטו של עצמאיים בישראל, כולל מיסים, ביטוח לאומי והוצאות מוכרות.

## תכונות

- הרשמה והתחברות מאובטחת
- שמירת תרחישי חישוב אישיים
- חישוב מפורט של הכנסה ברוטו ונוטו
- ממשק בעברית עם עיצוב מודרני
- מנוע חישוב מודולרי וקל לעדכון

## התקנה

1. התקן Python 3.8 או גרסה חדשה יותר
2. התקן את התלויות:
   ```bash
   pip install -r requirements.txt
   ```

## הרצה

```bash
python run.py
```

האפליקציה תרוץ בכתובת http://localhost:5000

## שימוש

1. הירשם לאפליקציה
2. התחבר
3. צור תרחיש חדש עם הפרטים שלך
4. צפה בתוצאות החישוב המפורטות

## הערות חשובות

- החישובים הם להערכה בלבד ולא מהווים ייעוץ מס
- יש לעדכן את שיעורי המס וההכרה בהוצאות בהתאם לשינויים בחוק
- התוכנה מיועדת לתכנון ותחזית, לא להגשת דוחות רשמיים

## מבנה הפרויקט

```
app/
├── __init__.py          # הגדרת האפליקציה
├── models.py            # מודלים של מסד הנתונים
├── forms.py             # טפסים
├── routes.py            # נתיבי האפליקציה
├── calculator.py        # מנוע החישוב
└── templates/           # תבניות HTML
config.py                # הגדרות
run.py                  # קובץ הרצה
requirements.txt        # תלויות
```
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

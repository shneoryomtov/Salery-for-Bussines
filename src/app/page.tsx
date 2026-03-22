'use client';

import { useState } from 'react';
import { ScenarioInput, CalculationResults, Expense } from '@/lib/types';
import { formatCurrency, formatPercentage } from '@/lib/formatters';

const DEFAULT_SCENARIO: ScenarioInput = {
  name: 'תרחיש חדש',
  workProfile: {
    year: 2026,
    workdaysPerWeek: 5,
    weeklyHours: 40,
    incomeMode: 'hourly',
    hourlyRate: 150,
    monthsPerYear: 12,
  },
  calendarSettings: {
    holidayMode: 'builtin',
    holidayDays: 15,
    erevHolidayDays: 5,
    erevHolidayHoursReduction: 4,
  },
  timeOffSettings: {
    vacationDaysPerYear: 14,
    sickDaysPerYear: 6,
    treatVacationAsLostIncome: true,
    treatSickAsLostIncome: true,
  },
  contributionSettings: {
    pensionMode: 'percentage',
    pensionValue: 5,
    studyFundMode: 'percentage',
    studyFundValue: 2,
    maximizeStudyToCeiling: true,
  },
  expenses: [],
};

export default function Home() {
  const [scenario, setScenario] = useState<ScenarioInput>(DEFAULT_SCENARIO);
  const [results, setResults] = useState<CalculationResults | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'input' | 'results'>('input');

  const handleCalculate = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/calculate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(scenario),
      });
      const data = await response.json();
      setResults(data);
      setActiveTab('results');
    } catch (error) {
      console.error('Calculation failed:', error);
      alert('שגיאה בחישוב');
    } finally {
      setLoading(false);
    }
  };

  const addExpense = () => {
    const newExpense: Expense = {
      id: Date.now().toString(),
      name: '',
      category: 'other',
      amount: 0,
      frequency: 'monthly',
      taxRecognitionPct: 100,
      expenseType: 'recurring',
    };
    setScenario({
      ...scenario,
      expenses: [...scenario.expenses, newExpense],
    });
  };

  const removeExpense = (id: string) => {
    setScenario({
      ...scenario,
      expenses: scenario.expenses.filter(e => e.id !== id),
    });
  };

  const updateExpense = (id: string, updates: Partial<Expense>) => {
    setScenario({
      ...scenario,
      expenses: scenario.expenses.map(e => (e.id === id ? { ...e, ...updates } : e)),
    });
  };

  return (
    <div className="space-y-6">
      {/* Tabs */}
      <div className="flex gap-4 border-b border-gray-200">
        <button
          onClick={() => setActiveTab('input')}
          className={`px-4 py-2 font-medium ${
            activeTab === 'input'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          📝 הזנת נתונים
        </button>
        <button
          onClick={() => setActiveTab('results')}
          className={`px-4 py-2 font-medium ${
            activeTab === 'results'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          📊 תוצאות
        </button>
      </div>

      {/* Input Tab */}
      {activeTab === 'input' && (
        <div className="bg-white rounded-lg shadow-md p-6 space-y-6">
          {/* Work Profile Section */}
          <div className="border-b pb-6">
            <h2 className="text-xl font-bold mb-4">📋 פרופיל עבודה</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">שנה</label>
                <input
                  type="number"
                  value={scenario.workProfile.year}
                  onChange={(e) =>
                    setScenario({
                      ...scenario,
                      workProfile: { ...scenario.workProfile, year: parseInt(e.target.value) },
                    })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">ימי עבודה בשבוע</label>
                <input
                  type="number"
                  step="0.5"
                  value={scenario.workProfile.workdaysPerWeek}
                  onChange={(e) =>
                    setScenario({
                      ...scenario,
                      workProfile: {
                        ...scenario.workProfile,
                        workdaysPerWeek: parseFloat(e.target.value),
                      },
                    })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">שעות עבודה בשבוע</label>
                <input
                  type="number"
                  step="1"
                  value={scenario.workProfile.weeklyHours}
                  onChange={(e) =>
                    setScenario({
                      ...scenario,
                      workProfile: {
                        ...scenario.workProfile,
                        weeklyHours: parseFloat(e.target.value),
                      },
                    })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">דרך הכנסה</label>
                <select
                  value={scenario.workProfile.incomeMode}
                  onChange={(e) =>
                    setScenario({
                      ...scenario,
                      workProfile: {
                        ...scenario.workProfile,
                        incomeMode: e.target.value as 'hourly' | 'monthly',
                      },
                    })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded"
                >
                  <option value="hourly">שיעור שעתי</option>
                  <option value="monthly">משכורת חודשית</option>
                </select>
              </div>
              {scenario.workProfile.incomeMode === 'hourly' && (
                <div>
                  <label className="block text-sm font-medium mb-1">שיעור שעתי (₪)</label>
                  <input
                    type="number"
                    value={scenario.workProfile.hourlyRate || 0}
                    onChange={(e) =>
                      setScenario({
                        ...scenario,
                        workProfile: {
                          ...scenario.workProfile,
                          hourlyRate: parseFloat(e.target.value),
                        },
                      })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded"
                  />
                </div>
              )}
              {scenario.workProfile.incomeMode === 'monthly' && (
                <div>
                  <label className="block text-sm font-medium mb-1">משכורת חודשית (₪)</label>
                  <input
                    type="number"
                    value={scenario.workProfile.monthlyGross || 0}
                    onChange={(e) =>
                      setScenario({
                        ...scenario,
                        workProfile: {
                          ...scenario.workProfile,
                          monthlyGross: parseFloat(e.target.value),
                        },
                      })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded"
                  />
                </div>
              )}
            </div>
          </div>

          {/* Calendar Section */}
          <div className="border-b pb-6">
            <h2 className="text-xl font-bold mb-4">📅 חגים וימי עבודה</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">ימי חג</label>
                <input
                  type="number"
                  value={scenario.calendarSettings.holidayDays}
                  onChange={(e) =>
                    setScenario({
                      ...scenario,
                      calendarSettings: {
                        ...scenario.calendarSettings,
                        holidayDays: parseInt(e.target.value),
                      },
                    })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">ימי ערב חג</label>
                <input
                  type="number"
                  value={scenario.calendarSettings.erevHolidayDays}
                  onChange={(e) =>
                    setScenario({
                      ...scenario,
                      calendarSettings: {
                        ...scenario.calendarSettings,
                        erevHolidayDays: parseInt(e.target.value),
                      },
                    })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded"
                />
              </div>
            </div>
          </div>

          {/* Time Off Section */}
          <div className="border-b pb-6">
            <h2 className="text-xl font-bold mb-4">🏖️ חופשה ומחלה</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">ימי חופשה</label>
                <input
                  type="number"
                  value={scenario.timeOffSettings.vacationDaysPerYear}
                  onChange={(e) =>
                    setScenario({
                      ...scenario,
                      timeOffSettings: {
                        ...scenario.timeOffSettings,
                        vacationDaysPerYear: parseInt(e.target.value),
                      },
                    })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">ימי מחלה</label>
                <input
                  type="number"
                  value={scenario.timeOffSettings.sickDaysPerYear}
                  onChange={(e) =>
                    setScenario({
                      ...scenario,
                      timeOffSettings: {
                        ...scenario.timeOffSettings,
                        sickDaysPerYear: parseInt(e.target.value),
                      },
                    })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded"
                />
              </div>
            </div>
          </div>

          {/* Contributions Section */}
          <div className="border-b pb-6">
            <h2 className="text-xl font-bold mb-4">🏢 פנסיה וקרן השתלמות</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">פנסיה (%)</label>
                <input
                  type="number"
                  step="0.5"
                  value={scenario.contributionSettings.pensionValue}
                  onChange={(e) =>
                    setScenario({
                      ...scenario,
                      contributionSettings: {
                        ...scenario.contributionSettings,
                        pensionValue: parseFloat(e.target.value),
                      },
                    })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">קרן השתלמות (%)</label>
                <input
                  type="number"
                  step="0.5"
                  value={scenario.contributionSettings.studyFundValue}
                  onChange={(e) =>
                    setScenario({
                      ...scenario,
                      contributionSettings: {
                        ...scenario.contributionSettings,
                        studyFundValue: parseFloat(e.target.value),
                      },
                    })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded"
                />
              </div>
            </div>
          </div>

          {/* Expenses Section */}
          <div>
            <h2 className="text-xl font-bold mb-4">💰 הוצאות</h2>
            <div className="space-y-3 mb-4">
              {scenario.expenses.map((expense) => (
                <div key={expense.id} className="flex gap-2 p-3 bg-gray-50 rounded">
                  <input
                    type="text"
                    placeholder="שם הוצאה"
                    value={expense.name}
                    onChange={(e) => updateExpense(expense.id, { name: e.target.value })}
                    className="flex-1 px-2 py-1 border border-gray-300 rounded text-sm"
                  />
                  <input
                    type="number"
                    placeholder="סכום"
                    value={expense.amount}
                    onChange={(e) => updateExpense(expense.id, { amount: parseFloat(e.target.value) })}
                    className="w-24 px-2 py-1 border border-gray-300 rounded text-sm"
                  />
                  <select
                    value={expense.frequency}
                    onChange={(e) =>
                      updateExpense(expense.id, { frequency: e.target.value as any })
                    }
                    className="px-2 py-1 border border-gray-300 rounded text-sm"
                  >
                    <option value="monthly">חודשי</option>
                    <option value="yearly">שנתי</option>
                    <option value="one-time">חד פעמי</option>
                  </select>
                  <button
                    onClick={() => removeExpense(expense.id)}
                    className="px-3 py-1 bg-red-500 text-white rounded text-sm hover:bg-red-600"
                  >
                    🗑️
                  </button>
                </div>
              ))}
            </div>
            <button
              onClick={addExpense}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              ➕ הוסף הוצאה
            </button>
          </div>

          {/* Calculate Button */}
          <button
            onClick={handleCalculate}
            disabled={loading}
            className="w-full px-6 py-3 bg-green-600 text-white font-bold rounded-lg hover:bg-green-700 disabled:bg-gray-400 mt-6"
          >
            {loading ? 'חישוב...' : '🧮 חשב תוצאות'}
          </button>
        </div>
      )}

      {/* Results Tab */}
      {activeTab === 'results' && results && (
        <div className="bg-white rounded-lg shadow-md p-6 space-y-6">
          <h2 className="text-2xl font-bold mb-6">📊 תוצאות החישוב</h2>

          {/* Summary Cards */}
          <div className="grid grid-cols-4 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
              <p className="text-sm text-gray-600">הכנסה ברוטו</p>
              <p className="text-lg font-bold text-blue-600">{formatCurrency(results.annualGross)}</p>
            </div>
            <div className="bg-green-50 p-4 rounded-lg border border-green-200">
              <p className="text-sm text-gray-600">הכנסה נטו</p>
              <p className="text-lg font-bold text-green-600">{formatCurrency(results.netAnnual)}</p>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
              <p className="text-sm text-gray-600">נטו חודשי</p>
              <p className="text-lg font-bold text-purple-600">{formatCurrency(results.netMonthly)}</p>
            </div>
            <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
              <p className="text-sm text-gray-600">שיעור ניכויים</p>
              <p className="text-lg font-bold text-orange-600">{formatPercentage(results.effectiveDeductionRate)}</p>
            </div>
          </div>

          {/* Breakdown Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-sm border-collapse">
              <thead className="bg-gray-100">
                <tr>
                  <th className="text-right px-4 py-2 border">תיאור</th>
                  <th className="text-left px-4 py-2 border">סכום</th>
                </tr>
              </thead>
              <tbody>
                {results.breakdown.map((row, idx) => (
                  <tr key={idx} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                    <td className="text-right px-4 py-2 border">{row.description}</td>
                    <td className="text-left px-4 py-2 border font-medium">{formatCurrency(parseFloat(row.amount as string)) || row.amount}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Explanations */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-bold mb-4">📖 הסברים ונוסחאות</h3>
            <div className="space-y-3">
              {results.explanations.map((exp, idx) => (
                <div key={idx} className="bg-gray-50 p-4 rounded-lg">
                  <p className="font-bold text-blue-600">{exp.label}</p>
                  <p className="text-sm text-gray-700 mt-1">{exp.formula}</p>
                  <p className="text-sm font-mono text-gray-600 mt-1">= {exp.value}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'results' && !results && (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <p className="text-lg text-gray-600">חישבו את התוצאות בעמוד הזנת הנתונים</p>
        </div>
      )}
    </div>
  );
}

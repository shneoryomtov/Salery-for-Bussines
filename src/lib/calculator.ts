// Calculation engine

import Decimal from 'decimal.js';
import {
  ScenarioInput,
  CalculationResults,
  TaxSettings,
  WorkProfile,
  Expense,
} from './types';

Decimal.set({ precision: 10, rounding: Decimal.ROUND_DOWN });

// Default tax settings for Israel 2026
export const DEFAULT_TAX_SETTINGS: TaxSettings = {
  incomeTaxBrackets: [
    { threshold: 0, rate: 0.1 },
    { threshold: 75000, rate: 0.14 },
    { threshold: 110000, rate: 0.205 },
    { threshold: 170000, rate: 0.23 },
    { threshold: 240000, rate: 0.3 },
    { threshold: 400000, rate: 0.35 },
    { threshold: 640000, rate: 0.49 },
  ],
  nationalInsuranceBrackets: [{ threshold: 0, rate: 0.0711 }],
  healthBrackets: [{ threshold: 0, rate: 0.053 }],
  taxCreditPointValue: 2700,
  numberOfTaxCreditPoints: 2,
  studyFundCeiling: 12000,
  yearlyWorkdayAssumption: 260,
};

export function calculateDailyHours(
  weeklyHours: number,
  workdaysPerWeek: number
): Decimal {
  if (workdaysPerWeek <= 0) return new Decimal(0);
  return new Decimal(weeklyHours).div(workdaysPerWeek);
}

export function calculateEffectiveWorkdays(
  yearlyAssumption: number,
  holidayDays: number,
  erevHolidayDays: number,
  vacationDays: number,
  treatVacationAsLost: boolean,
  sickDays: number,
  treatSickAsLost: boolean
): number {
  let removed = holidayDays + erevHolidayDays;
  if (treatVacationAsLost) removed += vacationDays;
  if (treatSickAsLost) removed += sickDays;
  return Math.max(0, yearlyAssumption - removed);
}

export function calculateLostHours(
  dailyHours: Decimal,
  holidayDays: number,
  erevHolidayDays: number,
  erevHoursReduction: number,
  vacationDays: number,
  treatVacationAsLost: boolean,
  sickDays: number,
  treatSickAsLost: boolean
) {
  const holidayLost = dailyHours.times(holidayDays);
  const erevLost = new Decimal(erevHoursReduction).times(erevHolidayDays);

  let vacationLost = new Decimal(0);
  if (treatVacationAsLost) {
    vacationLost = dailyHours.times(vacationDays);
  }

  let sickLost = new Decimal(0);
  if (treatSickAsLost) {
    sickLost = dailyHours.times(sickDays);
  }

  const totalLost = holidayLost.plus(erevLost).plus(vacationLost).plus(sickLost);

  return {
    holidayLostHours: holidayLost.toNumber(),
    erevHolidayLostHours: erevLost.toNumber(),
    vacationLostHours: vacationLost.toNumber(),
    sickLostHours: sickLost.toNumber(),
    totalLostHours: totalLost.toNumber(),
  };
}

export function calculateGrossIncome(
  workProfile: WorkProfile,
  effectiveHours: Decimal
): Decimal {
  if (workProfile.incomeMode === 'hourly' && workProfile.hourlyRate) {
    return effectiveHours.times(workProfile.hourlyRate);
  }
  if (workProfile.incomeMode === 'monthly' && workProfile.monthlyGross) {
    return new Decimal(workProfile.monthlyGross).times(workProfile.monthsPerYear);
  }
  return new Decimal(0);
}

export function annualizeExpense(expense: Expense): Decimal {
  const { amount, frequency } = expense;
  const amt = new Decimal(amount);

  if (frequency === 'monthly') return amt.times(12);
  if (frequency === 'yearly') return amt;
  return amt;
}

export function calculateRecognizedExpense(
  amount: Decimal,
  recognitionPct: number
): Decimal {
  const pct = Math.max(0, Math.min(100, recognitionPct));
  return amount.times(pct).div(100);
}

export function calculateTaxBracket(
  income: Decimal,
  brackets: Array<{ threshold: number; rate: number }>
): Decimal {
  if (brackets.length === 0 || income.lte(0)) return new Decimal(0);

  const sorted = [...brackets].sort((a, b) => a.threshold - b.threshold);
  let totalTax = new Decimal(0);

  for (let i = 0; i < sorted.length; i++) {
    const bracket = sorted[i];
    const threshold = new Decimal(bracket.threshold);
    const rate = new Decimal(bracket.rate);

    if (income.lt(threshold)) break;

    const nextThreshold =
      i + 1 < sorted.length
        ? new Decimal(sorted[i + 1].threshold)
        : new Decimal(999999999);

    const lowerBound = threshold;
    const upperBound = Decimal.min(income, nextThreshold);

    if (upperBound.gt(lowerBound)) {
      const bracketIncome = upperBound.minus(lowerBound);
      const bracketTax = bracketIncome.times(rate);
      totalTax = totalTax.plus(bracketTax);
    }
  }

  return totalTax;
}

export function calculateAll(
  scenario: ScenarioInput,
  taxSettings: TaxSettings = DEFAULT_TAX_SETTINGS
): CalculationResults {
  const { workProfile, calendarSettings, timeOffSettings, contributionSettings, expenses } = scenario;

  // Work hours calculations
  const dailyHours = calculateDailyHours(workProfile.weeklyHours, workProfile.workdaysPerWeek);
  const effectiveWorkdays = calculateEffectiveWorkdays(
    taxSettings.yearlyWorkdayAssumption,
    calendarSettings.holidayDays,
    calendarSettings.erevHolidayDays,
    timeOffSettings.vacationDaysPerYear,
    timeOffSettings.treatVacationAsLostIncome,
    timeOffSettings.sickDaysPerYear,
    timeOffSettings.treatSickAsLostIncome
  );

  const potentialHours = new Decimal(effectiveWorkdays).times(dailyHours);

  const lostHours = calculateLostHours(
    dailyHours,
    calendarSettings.holidayDays,
    calendarSettings.erevHolidayDays,
    calendarSettings.erevHolidayHoursReduction,
    timeOffSettings.vacationDaysPerYear,
    timeOffSettings.treatVacationAsLostIncome,
    timeOffSettings.sickDaysPerYear,
    timeOffSettings.treatSickAsLostIncome
  );

  const effectiveHours = potentialHours.minus(lostHours.totalLostHours);

  // Gross income
  const annualGross = calculateGrossIncome(workProfile, effectiveHours);
  const monthlyGrossEquiv = annualGross.div(12);

  // Expenses
  let totalExpenses = new Decimal(0);
  let recognizedExpenseAmt = new Decimal(0);
  for (const exp of expenses) {
    const annual = annualizeExpense(exp);
    totalExpenses = totalExpenses.plus(annual);
    const recognized = calculateRecognizedExpense(annual, exp.taxRecognitionPct);
    recognizedExpenseAmt = recognizedExpenseAmt.plus(recognized);
  }

  // Contributions
  let pensionAnnual = new Decimal(0);
  let pensionRecognized = new Decimal(0);
  if (contributionSettings.pensionMode === 'percentage') {
    pensionAnnual = annualGross.times(contributionSettings.pensionValue).div(100);
    pensionRecognized = pensionAnnual;
  } else if (contributionSettings.pensionMode === 'fixed_annual') {
    pensionAnnual = new Decimal(contributionSettings.pensionValue);
    pensionRecognized = pensionAnnual;
  } else if (contributionSettings.pensionMode === 'fixed_monthly') {
    pensionAnnual = new Decimal(contributionSettings.pensionValue).times(12);
    pensionRecognized = pensionAnnual;
  }

  let studyFundAnnual = new Decimal(0);
  let studyFundRecognized = new Decimal(0);
  if (contributionSettings.studyFundMode === 'percentage') {
    studyFundAnnual = annualGross.times(contributionSettings.studyFundValue).div(100);
  } else if (contributionSettings.studyFundMode === 'fixed_annual') {
    studyFundAnnual = new Decimal(contributionSettings.studyFundValue);
  } else if (contributionSettings.studyFundMode === 'fixed_monthly') {
    studyFundAnnual = new Decimal(contributionSettings.studyFundValue).times(12);
  }

  if (contributionSettings.maximizeStudyToCeiling) {
    studyFundAnnual = Decimal.min(studyFundAnnual, new Decimal(taxSettings.studyFundCeiling));
  }
  studyFundRecognized = studyFundAnnual;

  // Taxable income
  const totalDeductions = pensionRecognized.plus(studyFundRecognized);
  let taxableIncome = annualGross.minus(recognizedExpenseAmt).minus(totalDeductions);
  taxableIncome = Decimal.max(taxableIncome, new Decimal(0));

  // Taxes
  const incomeTax = calculateTaxBracket(taxableIncome, taxSettings.incomeTaxBrackets);
  const incomeTaxAdjusted = incomeTax.minus(
    new Decimal(taxSettings.taxCreditPointValue).times(taxSettings.numberOfTaxCreditPoints)
  );
  const incomeTaxFinal = Decimal.max(incomeTaxAdjusted, new Decimal(0));

  const ni = calculateTaxBracket(taxableIncome, taxSettings.nationalInsuranceBrackets);
  const health = calculateTaxBracket(taxableIncome, taxSettings.healthBrackets);

  // Net income
  const totalTaxesNI = incomeTaxFinal.plus(ni).plus(health);
  const netAnnual = annualGross.minus(totalExpenses).minus(totalTaxesNI);
  const netMonthly = netAnnual.div(12);

  // Effective deduction rate
  const totalDeductionsAmount = totalExpenses.plus(totalTaxesNI).plus(pensionAnnual).plus(studyFundAnnual);
  const effectiveDeductionRate = annualGross.gt(0)
    ? totalDeductionsAmount.div(annualGross).times(100)
    : new Decimal(0);

  // Build breakdown rows
  const breakdown = [
    { stage: 0, description: 'הכנסה ברוטו שנתית', amount: annualGross.toFixed(2) },
    {
      stage: 1,
      description: 'בניכוי: הוצאות בפועל',
      amount: `(${totalExpenses.toFixed(2)})`,
    },
    {
      stage: 2,
      description: 'בניכוי: מס הכנסה',
      amount: `(${incomeTaxFinal.toFixed(2)})`,
    },
    {
      stage: 3,
      description: 'בניכוי: ביטוח לאומי ובריאות',
      amount: `(${ni.plus(health).toFixed(2)})`,
    },
    { stage: 4, description: '=== הכנסה נטו שנתית ===', amount: netAnnual.toFixed(2) },
  ];

  const explanations = [
    { label: 'שעות עבודה יומיות', formula: 'שעות שבועיות / ימי עבודה', value: dailyHours.toFixed(2) },
    {
      label: 'שעות עבודה יעילות',
      formula: 'ימי עבודה יעילים × שעות יומיות',
      value: effectiveHours.toFixed(2),
    },
    {
      label: 'הכנסה ברוטו',
      formula: 'שיעור שעתי × שעות יעילות',
      value: annualGross.toFixed(2),
    },
    {
      label: 'הכנסה נטו',
      formula: 'ברוטו - הוצאות - מסים',
      value: netAnnual.toFixed(2),
    },
  ];

  return {
    dailyHours: dailyHours.toNumber(),
    effectiveWorkdaysPerYear: effectiveWorkdays,
    effectiveWorkHoursPerYear: effectiveHours.toNumber(),
    annualGross: annualGross.toNumber(),
    monthlyGrossEquivalent: monthlyGrossEquiv.toNumber(),
    holidayLostHours: lostHours.holidayLostHours,
    erevHolidayLostHours: lostHours.erevHolidayLostHours,
    vacationLostHours: lostHours.vacationLostHours,
    sickLostHours: lostHours.sickLostHours,
    totalLostHours: lostHours.totalLostHours,
    totalExpenses: totalExpenses.toNumber(),
    recognizedExpenses: recognizedExpenseAmt.toNumber(),
    pensionAnnual: pensionAnnual.toNumber(),
    studyFundAnnual: studyFundAnnual.toNumber(),
    pensionRecognized: pensionRecognized.toNumber(),
    studyFundRecognized: studyFundRecognized.toNumber(),
    taxableIncome: taxableIncome.toNumber(),
    incomeTax: incomeTaxFinal.toNumber(),
    nationalInsurance: ni.toNumber(),
    healthPayment: health.toNumber(),
    netAnnual: netAnnual.toNumber(),
    netMonthly: netMonthly.toNumber(),
    effectiveDeductionRate: effectiveDeductionRate.toNumber(),
    monthlyReserve: new Decimal(timeOffSettings.vacationDaysPerYear + timeOffSettings.sickDaysPerYear)
      .times(dailyHours)
      .div(12)
      .toNumber(),
    breakdown,
    explanations,
  };
}

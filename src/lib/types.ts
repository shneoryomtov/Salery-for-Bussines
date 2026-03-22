// Data models and types

export interface WorkProfile {
  year: number;
  workdaysPerWeek: number;
  weeklyHours: number;
  incomeMode: 'hourly' | 'monthly';
  hourlyRate?: number;
  monthlyGross?: number;
  monthsPerYear: number;
}

export interface CalendarSettings {
  holidayMode: 'builtin' | 'manual';
  holidayDays: number;
  erevHolidayDays: number;
  erevHolidayHoursReduction: number;
}

export interface TimeOffSettings {
  vacationDaysPerYear: number;
  sickDaysPerYear: number;
  treatVacationAsLostIncome: boolean;
  treatSickAsLostIncome: boolean;
}

export interface ContributionSettings {
  pensionMode: 'percentage' | 'fixed_annual' | 'fixed_monthly';
  pensionValue: number;
  studyFundMode: 'percentage' | 'fixed_annual' | 'fixed_monthly';
  studyFundValue: number;
  maximizeStudyToCeiling: boolean;
}

export interface Expense {
  id: string;
  name: string;
  category: string;
  amount: number;
  frequency: 'monthly' | 'yearly' | 'one-time';
  taxRecognitionPct: number;
  expenseType: 'recurring' | 'depreciation_asset' | 'leasing';
}

export interface ScenarioInput {
  name: string;
  workProfile: WorkProfile;
  calendarSettings: CalendarSettings;
  timeOffSettings: TimeOffSettings;
  contributionSettings: ContributionSettings;
  expenses: Expense[];
}

export interface CalculationResults {
  dailyHours: number;
  effectiveWorkdaysPerYear: number;
  effectiveWorkHoursPerYear: number;
  annualGross: number;
  monthlyGrossEquivalent: number;
  holidayLostHours: number;
  erevHolidayLostHours: number;
  vacationLostHours: number;
  sickLostHours: number;
  totalLostHours: number;
  totalExpenses: number;
  recognizedExpenses: number;
  pensionAnnual: number;
  studyFundAnnual: number;
  pensionRecognized: number;
  studyFundRecognized: number;
  taxableIncome: number;
  incomeTax: number;
  nationalInsurance: number;
  healthPayment: number;
  netAnnual: number;
  netMonthly: number;
  effectiveDeductionRate: number;
  monthlyReserve: number;
  breakdown: BreakdownRow[];
  explanations: ExplanationStep[];
}

export interface BreakdownRow {
  stage: number;
  description: string;
  amount: string | number;
}

export interface ExplanationStep {
  label: string;
  formula: string;
  value: string;
}

export interface TaxSettings {
  incomeTaxBrackets: TaxBracket[];
  nationalInsuranceBrackets: TaxBracket[];
  healthBrackets: TaxBracket[];
  taxCreditPointValue: number;
  numberOfTaxCreditPoints: number;
  studyFundCeiling: number;
  yearlyWorkdayAssumption: number;
}

export interface TaxBracket {
  threshold: number;
  rate: number;
}

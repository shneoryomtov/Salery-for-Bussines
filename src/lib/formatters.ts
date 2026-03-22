// Formatting utilities

export function formatCurrency(value: number, symbol = '₪'): string {
  return `${symbol} ${value.toLocaleString('he-IL', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

export function formatPercentage(value: number): string {
  return `${value.toFixed(1)}%`;
}

export function formatHours(value: number): string {
  return `${value.toFixed(1)} שעות`;
}

export function formatDays(value: number): string {
  return `${value} ימים`;
}

export function formatNumber(value: number, decimals = 2): string {
  return value.toLocaleString('he-IL', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
}

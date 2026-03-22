"""Formatting utilities for display."""

from decimal import Decimal


def format_currency(value: Decimal, symbol: str = "₪") -> str:
    """Format value as currency."""
    if isinstance(value, Decimal):
        value = float(value)
    return f"{symbol} {value:,.2f}"


def format_percentage(value: Decimal) -> str:
    """Format value as percentage."""
    if isinstance(value, Decimal):
        value = float(value)
    return f"{value:.1f}%"


def format_hours(value: Decimal) -> str:
    """Format value as hours."""
    if isinstance(value, Decimal):
        value = float(value)
    return f"{value:,.1f} שעות"


def format_days(value: int) -> str:
    """Format value as days."""
    return f"{value} ימים"


def format_number(value: Decimal, decimals: int = 2) -> str:
    """Format number with specified decimals."""
    if isinstance(value, Decimal):
        value = float(value)
    fmt = f"{{:,.{decimals}f}}"
    return fmt.format(value)

"""Binary search solver for target net income."""

from decimal import Decimal
import copy
from .models import ScenarioInput, SolverResult


def solve_for_target_net_annual(
    base_scenario: ScenarioInput,
    target_net_annual: Decimal,
    tolerance: Decimal = Decimal("10"),
    max_iterations: int = 50,
) -> SolverResult:
    """
    Use binary search to find gross annual income needed to achieve target net annual.
    """
    # Import here to avoid circular imports
    from .calculator import calculate_all
    
    low = Decimal("0")
    high = Decimal("10000000")
    
    for iteration in range(max_iterations):
        mid = (low + high) / Decimal("2")
        
        # Create test scenario with this gross
        test_scenario = create_scenario_with_gross(base_scenario, mid)
        result = calculate_all(test_scenario)
        
        net_diff = result.net_annual - target_net_annual
        
        if abs(net_diff) < tolerance:
            return SolverResult(
                required_gross_annual=mid,
                required_gross_monthly=mid / Decimal("12"),
                resulting_net_annual=result.net_annual,
                resulting_net_monthly=result.net_monthly,
                iterations=iteration + 1,
            )
        
        if net_diff < 0:
            low = mid
        else:
            high = mid
    
    test_scenario = create_scenario_with_gross(base_scenario, (low + high) / Decimal("2"))
    result = calculate_all(test_scenario)
    
    return SolverResult(
        required_gross_annual=(low + high) / Decimal("2"),
        required_gross_monthly=(low + high) / Decimal("24"),
        resulting_net_annual=result.net_annual,
        resulting_net_monthly=result.net_monthly,
        iterations=max_iterations,
    )


def solve_for_target_net_monthly(
    base_scenario: ScenarioInput,
    target_net_monthly: Decimal,
    tolerance: Decimal = Decimal("10"),
    max_iterations: int = 50,
) -> SolverResult:
    """
    Use binary search to find gross income needed to achieve target net monthly.
    """
    target_net_annual = target_net_monthly * Decimal("12")
    return solve_for_target_net_annual(
        base_scenario,
        target_net_annual,
        tolerance,
        max_iterations,
    )


def create_scenario_with_gross(
    base_scenario: ScenarioInput,
    gross_annual: Decimal,
) -> ScenarioInput:
    """
    Create a copy of scenario with modified gross income for solving.
    """
    new_scenario = copy.deepcopy(base_scenario)
    months_per_year = base_scenario.work_profile.months_per_year or Decimal("12")
    monthly_gross = gross_annual / months_per_year
    
    new_scenario.work_profile.income_mode = "monthly"
    new_scenario.work_profile.monthly_gross = monthly_gross
    new_scenario.work_profile.hourly_rate = None
    
    return new_scenario

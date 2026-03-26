from agents import function_tool

@function_tool
def finance_tool(
    initial_investment: float,
    monthly_expenses: float,
    expected_monthly_revenue: float,
    cac: float = 0, # Customer Acquisition Cost
    ltv: float = 0, # Lifetime Value
    growth_rate: float = 0.05,
    months: int = 12
) -> dict:
    """
    Advanced startup financial projection tool.

    Args:
        initial_investment (float): Initial amount invested.
        monthly_expenses (float): Fixed monthly expenses (rent, salaries, etc.).
        expected_monthly_revenue (float): Starting revenue per month.
        cac (float): Customer Acquisition Cost (Marketing/New Users).
        ltv (float): Expected Lifetime Value per user.
        growth_rate (float): Expected monthly growth rate in revenue (default 5%).
        months (int): Number of months for projection (default 12).
    """
    revenue_projection = []
    total_revenue = 0
    total_expenses = 0
    break_even_month = None

    revenue = expected_monthly_revenue

    for month in range(1, months + 1):
        # Expenses include fixed + variable (marketing/cac)
        # Assuming we acquire 10 new users each month as a baseline for this simple model
        marketing_cost = cac * 10 
        monthly_total_expense = monthly_expenses + marketing_cost
        total_expenses += monthly_total_expense
        
        revenue_projection.append({
            "month": month, 
            "revenue": round(revenue, 2),
            "burn_rate": round(monthly_total_expense, 2)
        })
        total_revenue += revenue

        # Check for break-even (Total Revenue >= Total Expenses + Initial Investment)
        cumulative_profit = total_revenue - (total_expenses + initial_investment)
        if cumulative_profit >= 0 and break_even_month is None:
            break_even_month = month

        # Increase revenue for next month
        revenue *= (1 + growth_rate)

    net_profit = total_revenue - (total_expenses + initial_investment)
    roi = (net_profit / initial_investment) * 100 if initial_investment > 0 else 0
    
    # Unit Economics
    unit_economics_status = "Positive" if (ltv > cac and cac > 0) else "Check CAC/LTV Ratio"

    return {
        "summary": {
            "initial_investment": initial_investment,
            "total_projected_revenue": round(total_revenue, 2),
            "total_projected_expenses": round(total_expenses, 2),
            "net_profit_loss": round(net_profit, 2),
            "roi_percent": round(roi, 2),
            "break_even_month": break_even_month or "Not reached in period"
        },
        "unit_economics": {
            "cac": cac,
            "ltv": ltv,
            "status": unit_economics_status,
            "ltv_cac_ratio": round(ltv / cac, 2) if cac > 0 else "N/A"
        },
        "burn_rate_avg": round(total_expenses / months, 2),
        "projections": revenue_projection
    }

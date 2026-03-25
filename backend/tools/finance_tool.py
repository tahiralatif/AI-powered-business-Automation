from agents import function_tool

@function_tool
def finance_tool(
    initial_investment: float,
    monthly_expenses: float,
    expected_monthly_revenue: float,
    growth_rate: float = 0.05,
    months: int = 12
) -> dict:
    """
    Simple financial projection tool for business plan.

    Args:
        initial_investment (float): Initial amount invested.
        monthly_expenses (float): Fixed monthly expenses (rent, salaries, etc.).
        expected_monthly_revenue (float): Starting revenue per month.
        growth_rate (float): Expected monthly growth rate in revenue (default 5%).
        months (int): Number of months for projection (default 12).

    Returns:
        dict: Financial projection including revenue, expenses, profit/loss, 
              break-even month, and ROI.
    """
    revenue_projection = []
    total_revenue = 0
    total_expenses = monthly_expenses * months
    break_even_month = None

    revenue = expected_monthly_revenue

    for month in range(1, months + 1):
        # Revenue grows each month
        revenue_projection.append({"month": month, "revenue": round(revenue, 2)})
        total_revenue += revenue

        # Check for break-even
        cumulative_profit = total_revenue - (total_expenses + initial_investment)
        if cumulative_profit >= 0 and break_even_month is None:
            break_even_month = month

        # Increase revenue for next month
        revenue *= (1 + growth_rate)

    net_profit = total_revenue - (total_expenses + initial_investment)
    roi = (net_profit / initial_investment) * 100 if initial_investment > 0 else None

    return {
        "initial_investment": initial_investment,
        "total_revenue": round(total_revenue, 2),
        "total_expenses": round(total_expenses, 2),
        "net_profit": round(net_profit, 2),
        "roi_percent": round(roi, 2) if roi else None,
        "break_even_month": break_even_month,
        "revenue_projection": revenue_projection
    }





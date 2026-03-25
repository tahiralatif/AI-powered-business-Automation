from agents import function_tool
from pydantic import BaseModel
from typing import List, Optional, Dict

class ResearchSummary(BaseModel):
    # Define keys you expect, or leave dynamic fields in dict (not recommended)
    summary: str
    market_size: Optional[str] = None
    competitors: Optional[List[str]] = None

class SWOT(BaseModel):
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    opportunities: Optional[List[str]] = None
    threats: Optional[List[str]] = None

class Finance(BaseModel):
    revenue: Optional[str] = None
    costs: Optional[str] = None
    profit: Optional[str] = None

@function_tool
def formatter_tool(
    business_idea: str,
    research_summary: ResearchSummary,
    swot: Optional[SWOT] = None,
    finance: Optional[Finance] = None
) -> str:
    report = []
    report.append(f"📌 **Business Idea:** {business_idea}\n")

    # Market Research
    report.append("📊 **Market Research Summary:**")
    for key, value in research_summary.dict().items():
        if value:
            report.append(f"- **{key}:** {value}")

    # SWOT Analysis
    if swot:
        report.append("\n🧩 **SWOT Analysis:**")
        for key, value in swot.dict().items():
            if value:
                report.append(f"- **{key}:**")
                for v in value:
                    report.append(f"   • {v}")

    # Finance
    if finance:
        report.append("\n💰 **Financial Overview:**")
        for key, value in finance.dict().items():
            if value:
                report.append(f"- **{key}:** {value}")

    # Closing
    report.append("\n✅ **Conclusion:** This business plan demonstrates strong market potential, "
                  "clear opportunities, and identified risks with mitigation strategies. "
                  "It is structured to attract early-stage investors and partners.")

    return "\n".join(report)

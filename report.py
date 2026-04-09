import json
from datetime import datetime
from agent import analyze_all_customers

def generate_report(results: list) -> str:
    date = datetime.now().strftime("%B %d, %Y")
    
    critical = [r for r in results if r["risk_level"] == "critical"]
    warning = [r for r in results if r["risk_level"] == "warning"]
    healthy = [r for r in results if r["risk_level"] == "healthy"]
    
    avg_score = sum(r["health_score"] for r in results) / len(results)

    report = f"""
APEX CRM — CUSTOMER HEALTH REPORT
{date}
{'='*50}

PORTFOLIO SUMMARY
  Total Accounts:    {len(results)}
  Average Score:     {avg_score:.0f}/100
  Critical:          {len(critical)} accounts
  Warning:           {len(warning)} accounts
  Healthy:           {len(healthy)} accounts

{'='*50}
🚨 IMMEDIATE ACTION REQUIRED
{'='*50}
"""
    for r in sorted(critical, key=lambda x: x["health_score"]):
        report += f"""
{r['company_name']} — Score: {r['health_score']}/100
  Concerns: {', '.join(r['top_concerns'])}
  Action:   {r['recommended_action']}
"""

    report += f"""
{'='*50}
⚠️  ACCOUNTS TO WATCH
{'='*50}
"""
    for r in sorted(warning, key=lambda x: x["health_score"]):
        report += f"""
{r['company_name']} — Score: {r['health_score']}/100
  Action: {r['recommended_action']}
"""

    report += f"""
{'='*50}
✅ HEALTHY ACCOUNTS
{'='*50}
"""
    for r in sorted(healthy, key=lambda x: x["health_score"], reverse=True):
        report += f"""
{r['company_name']} — Score: {r['health_score']}/100
  Action: {r['recommended_action']}
"""

    return report

if __name__ == "__main__":
    results = analyze_all_customers()
    report = generate_report(results)
    print(report)
    
    # save to file
    filename = f"health-report-{datetime.now().strftime('%Y-%m-%d')}.txt"
    with open(filename, "w") as f:
        f.write(report)
    print(f"\nReport saved to {filename}")
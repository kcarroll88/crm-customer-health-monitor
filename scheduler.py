import schedule
import time
from datetime import datetime
from report import generate_report
from agent import analyze_all_customers

def run_daily_report():
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M')}] Running customer health analysis...")
    results = analyze_all_customers()
    report = generate_report(results)
    
    filename = f"health-report-{datetime.now().strftime('%Y-%m-%d')}.txt"
    with open(filename, "w") as f:
        f.write(report)
    
    print(report)
    print(f"Report saved to {filename}")

# run immediately once
run_daily_report()

# then run every day at 8am
schedule.every().day.at("08:00").do(run_daily_report)

print("\nScheduler running. Reports will generate daily at 8am.")
print("Press Ctrl+C to stop.\n")

while True:
    schedule.run_pending()
    time.sleep(60)
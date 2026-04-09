import os
import json
import asyncio
import anthropic
from dotenv import load_dotenv

load_dotenv()

try:
    import streamlit as st
    api_key = st.secrets.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
except Exception:
    api_key = os.environ.get("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(api_key=api_key)

def load_customers(filepath="data/customer-data.json"):
    with open(filepath, "r") as f:
        return json.load(f)

async def analyze_customer(customer: dict) -> dict:
    prompt = f"""You are a customer success analyst for Apex CRM.

Analyze this customer account and return a health score and recommendation.

Customer Data:
{json.dumps(customer, indent=2)}

Scoring criteria:
- days_since_last_login: <7 days = healthy, 7-30 = warning, >30 = critical
- support_tickets_last_30_days: 0-2 = healthy, 3-5 = warning, >5 = critical
- email_response_rate: >70% = healthy, 40-70% = warning, <40% = critical
- nps_score: 8-10 = healthy, 5-7 = warning, 0-4 = critical
- last_communication_sentiment: positive = healthy, neutral = warning, negative = critical

Respond in this exact JSON format with no other text:
{{
    "company_name": "{customer.get('company_name')}",
    "health_score": <number 1-100>,
    "risk_level": "<healthy|warning|critical>",
    "top_concerns": ["<concern 1>", "<concern 2>"],
    "recommended_action": "<one specific action the account manager should take>",
    "urgency": "<low|medium|high>"
}}"""

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    text = response.content[0].text.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    return json.loads(text)

async def analyze_all_customers():
    customers = load_customers()
    print(f"Analyzing {len(customers)} customer accounts...")
    
    # run all customers concurrently instead of one at a time
    results = await asyncio.gather(*[
        analyze_customer(customer) for customer in customers
    ])
    
    return list(results)

def run_analysis():
    return asyncio.run(analyze_all_customers())

if __name__ == "__main__":
    results = run_analysis()
    for r in results:
        print(f"\n{r['company_name']}")
        print(f"  Health Score: {r['health_score']}/100")
        print(f"  Risk Level:   {r['risk_level']}")
        print(f"  Urgency:      {r['urgency']}")
        print(f"  Action:       {r['recommended_action']}")
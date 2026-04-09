# CRM Customer Health Monitor

An AI-powered customer health scoring dashboard for Apex CRM. Uses Claude to analyze customer accounts, flag at-risk customers, and recommend actions for account managers.

## Features

- **Health scoring** — AI-generated scores (1–100) for each customer account based on login activity, support tickets, email engagement, NPS, and sentiment
- **Risk classification** — Customers categorized as Healthy, Warning, or Critical
- **Recommended actions** — Specific next steps generated per account
- **Streamlit dashboard** — Live UI with filtering, sorting, and per-customer detail views
- **Automated reports** — Daily digest reports saved as text files
- **Scheduled analysis** — Optional daily scheduler that runs at 8am automatically

## Project Structure

```
├── app.py              # Streamlit dashboard
├── agent.py            # Claude API integration & scoring logic
├── report.py           # Text report generation
├── scheduler.py        # Daily report scheduler
├── data/
│   └── customer-data.json   # Customer records
├── requirements.txt
└── .env                # API keys (not committed)
```

## Setup

1. **Clone the repo**
   ```bash
   git clone https://github.com/kcarroll88/crm-customer-health-monitor.git
   cd crm-customer-health-monitor
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Create a `.env` file in the project root:
   ```
   ANTHROPIC_API_KEY=your_key_here
   RESEND_API_KEY=your_key_here
   ```

## Usage

### Run the dashboard
```bash
streamlit run app.py
```

### Generate a one-off report
```bash
python report.py
```

### Run the daily scheduler
```bash
python scheduler.py
```
Generates a report immediately, then repeats every day at 8am.

## Health Scoring Criteria

| Signal | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| Days since last login | < 7 | 7–30 | > 30 |
| Support tickets (30 days) | 0–2 | 3–5 | > 5 |
| Email response rate | > 70% | 40–70% | < 40% |
| NPS score | 8–10 | 5–7 | 0–4 |
| Last communication sentiment | Positive | Neutral | Negative |

## Tech Stack

- [Streamlit](https://streamlit.io) — Dashboard UI
- [Anthropic Claude](https://anthropic.com) — AI scoring & recommendations
- [python-dotenv](https://pypi.org/project/python-dotenv/) — Environment config
- [Resend](https://resend.com) — Email delivery

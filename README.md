# Contract Risk Quantification Platform

A loss modelling tool that helps lawyers and commercial teams understand the actual economic losses arising from a commercial supply relationship — before any legal or contractual analysis. It captures what is supplied, what it's used for, what can go wrong, who loses what, and how much — with unmitigated vs. mitigated views showing the value of operational risk measures.

## Architecture

- **Backend**: Python / FastAPI / SQLAlchemy / SQLite
- **Frontend**: React / TypeScript / Tailwind CSS / Recharts
- **Engine**: numpy / scipy Monte Carlo simulation
- **AI**: Claude API for failure mode generation, loss estimation, and mitigation suggestions

## Prerequisites

- Python 3.11+
- Node.js 18+
- (Optional) An [Anthropic API key](https://console.anthropic.com/) for AI-powered features

## Getting Started

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file (copy from the template):

```bash
cp .env.example .env
```

Edit `.env` to add your Anthropic API key if you want AI features:

```
ANTHROPIC_API_KEY=sk-ant-xxxxx
```

Start the backend server:

```bash
uvicorn app.main:app --reload --port 8080
```

The API will be available at `http://localhost:8080`. Swagger docs are at `http://localhost:8080/docs`.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173` and proxies API requests to the backend on port 8080.

## Usage Walkthrough

### Step 1: Create an Engagement

From the home page, click **New Engagement**. Fill in:

- **Name** — a descriptive name for the supply relationship
- **Industry** — the sector (e.g. Technology, Manufacturing)
- **Contract Value** — the total contract value (used for risk asymmetry calculations)
- **Currency** — USD, EUR, GBP, or AUD

Click **Create Engagement**, then add the **Parties** involved (buyer, supplier, third parties, end users) and the **Goods & Services** being supplied.

### Step 2: Define Failure Modes

Navigate to the **Failure Modes** step. You can:

- **Add manually** — enter a failure mode name, category, and frequency estimates (low/mid/high events per year)
- **Generate with AI** — select a goods/service and click "Generate for: [name]" to have Claude analyse the supply relationship and suggest 5–10 context-specific failure modes

Click any AI suggestion to accept it into your model. Toggle failure modes in or out with the Include/Exclude buttons.

### Step 3: Map Losses

In the **Loss Mapping** step, select each failure mode and define loss scenarios:

- **Affected party** — who bears the loss
- **Loss category** — e.g. Business Interruption, Revenue Loss, Regulatory Fines
- **Severity estimates** — low, mid, and high values in your chosen currency
- **Distribution type** — Lognormal (right-skewed, most common), Triangular, or Uniform

### Step 4: Add Mitigations

In the **Mitigations** step:

- Add operational mitigations (e.g. dual sourcing, SLAs, insurance) with their estimated cost
- **Link** each mitigation to the failure modes it addresses, specifying frequency and severity reduction factors (0–1)
- Use **AI suggestions** to generate context-specific mitigations

### Step 5: Review & Run

The **Review** step shows a summary of your model. Choose the number of Monte Carlo simulations (1,000–50,000) and click **Run Monte Carlo Simulation**.

The engine runs two simulations:
- **Unmitigated** — raw exposure without any mitigations
- **Mitigated** — exposure after applying all linked mitigations

### Step 6: Dashboard

After running, you're taken to the dashboard showing:

- **Exposure Summary** — Expected Loss, VaR (95%), TVaR (95%), VaR (99%) for both unmitigated and mitigated views
- **Risk Asymmetry** — ratio of 95th percentile loss to contract value (values > 1x mean potential losses exceed the contract value)
- **Loss Distribution Chart** — overlaid histogram of unmitigated vs. mitigated loss distributions
- **Top Scenarios** — failure modes ranked by expected loss with contribution percentages
- **Mitigation Value** — EL reduction and ROI of your mitigations
- **Exposure by Party** — how losses are distributed across affected parties

## Key Concepts

| Metric | Meaning |
|--------|---------|
| **Expected Loss (EL)** | Average annual loss across all simulations |
| **VaR (95%)** | Loss that is exceeded only 5% of the time |
| **TVaR (95%)** | Average loss in the worst 5% of scenarios |
| **Risk Asymmetry Ratio** | VaR 95% / Contract Value — how tail risk compares to what's at stake |
| **Mitigation ROI** | (EL reduction − mitigation cost) / mitigation cost |

## Running Tests

```bash
cd backend
pytest tests/ -v
```

## Project Structure

```
contract-risk-platform/
├── backend/
│   ├── app/
│   │   ├── engine/          # Monte Carlo simulation engine
│   │   ├── models/          # SQLAlchemy database models
│   │   ├── routers/         # FastAPI route handlers
│   │   ├── schemas/         # Pydantic request/response models
│   │   ├── services/        # Business logic & Claude API integration
│   │   ├── prompts/         # AI prompt templates
│   │   └── seed/            # Taxonomy constants
│   └── tests/
└── frontend/
    └── src/
        ├── api/             # Axios API client functions
        ├── components/      # Reusable UI components
        ├── pages/
        │   ├── EngagementWizard/  # 5-step input wizard
        │   └── Dashboard/         # Results visualisation
        └── types/           # TypeScript interfaces
```

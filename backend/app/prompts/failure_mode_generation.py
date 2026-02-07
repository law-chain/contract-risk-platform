"""Prompt template for generating failure modes from engagement context."""

from app.seed.failure_taxonomy import FAILURE_CATEGORIES
from app.seed.loss_taxonomy import LOSS_CATEGORIES


def build_failure_mode_prompt(
    goods_service_name: str,
    goods_service_description: str,
    use_context: str,
    supply_type: str,
    replaceability: str,
    industry: str,
    contract_value: float,
    currency: str,
    parties: list[dict],
) -> str:
    categories_str = "\n".join(f"- {c}" for c in FAILURE_CATEGORIES)
    loss_cats_str = "\n".join(f"- {c}" for c in LOSS_CATEGORIES)
    parties_str = "\n".join(
        f"- {p['name']} (role: {p['role']}, revenue: {p.get('revenue', 'N/A')})"
        for p in parties
    )

    return f"""You are an expert risk analyst specializing in commercial supply relationships.

Analyze the following supply relationship and generate 5-10 specific, realistic failure modes.

## Supply Relationship Context

**What is being supplied:** {goods_service_name}
**Description:** {goods_service_description}
**How it's used:** {use_context}
**Supply type:** {supply_type}
**Replaceability:** {replaceability}
**Industry:** {industry}
**Contract value:** {currency} {contract_value:,.0f}

**Parties involved:**
{parties_str}

## Instructions

For each failure mode, provide:
1. A specific, concrete name (not generic — tied to THIS supply relationship)
2. A description of what goes wrong and why
3. A category from the standard list
4. Frequency estimates (events per year): low, mid, high
5. For each affected party, one or more loss scenarios with severity estimates

Be specific to this actual supply relationship. Do not provide generic risk register items.

## Available failure categories:
{categories_str}

## Available loss categories:
{loss_cats_str}

## Required JSON output format:

```json
{{
  "failure_modes": [
    {{
      "name": "Specific failure mode name",
      "description": "What goes wrong and why",
      "category": "Category from list above",
      "frequency_low": 0.1,
      "frequency_mid": 0.5,
      "frequency_high": 1.5,
      "confidence": 0.7,
      "loss_scenarios": [
        {{
          "affected_party_role": "buyer",
          "loss_category": "Loss category from list above",
          "description": "How this party is affected",
          "severity_low": 5000,
          "severity_mid": 25000,
          "severity_high": 150000,
          "distribution_type": "lognormal"
        }}
      ]
    }}
  ]
}}
```

Return ONLY valid JSON, no markdown code fences or additional text."""

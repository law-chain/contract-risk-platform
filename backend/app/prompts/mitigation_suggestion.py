"""Prompt template for suggesting mitigations."""

from app.seed.mitigation_taxonomy import MITIGATION_TYPES


def build_mitigation_prompt(
    failure_modes: list[dict],
    industry: str,
    contract_value: float,
    currency: str,
) -> str:
    mit_types_str = "\n".join(f"- {m}" for m in MITIGATION_TYPES)
    fm_str = "\n".join(
        f"- **{fm['name']}** (category: {fm['category']}, "
        f"freq_mid: {fm['frequency_mid']}/yr, "
        f"EL est: {currency} {fm.get('expected_loss_est', 'N/A')}): "
        f"{fm['description']}"
        for fm in failure_modes
    )

    return f"""You are an expert in operational risk mitigation for commercial supply relationships.

## Context
**Industry:** {industry}
**Contract value:** {currency} {contract_value:,.0f}

## Failure modes to mitigate:
{fm_str}

## Available mitigation types:
{mit_types_str}

## Instructions

Suggest 3-7 practical operational mitigations. For each:
1. Be specific to these failure modes (not generic advice)
2. Estimate the cost of implementation
3. Estimate frequency reduction factor (0 to 1) for each applicable failure mode
4. Estimate severity reduction factor (0 to 1) for each applicable failure mode

Return ONLY valid JSON:

```json
{{
  "mitigations": [
    {{
      "name": "Specific mitigation name",
      "description": "What it involves and how it helps",
      "mitigation_type": "Type from list above",
      "estimated_cost": 10000,
      "confidence": 0.7,
      "applicable_failure_modes": [
        {{
          "failure_mode_name": "Name of failure mode",
          "frequency_reduction": 0.3,
          "severity_reduction": 0.2
        }}
      ]
    }}
  ]
}}
```

Return ONLY valid JSON, no markdown code fences or additional text."""

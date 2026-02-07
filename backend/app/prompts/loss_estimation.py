"""Prompt template for refining loss parameter estimates."""


def build_loss_estimation_prompt(
    failure_mode_name: str,
    failure_mode_description: str,
    loss_category: str,
    affected_party_name: str,
    affected_party_role: str,
    industry: str,
    contract_value: float,
    currency: str,
    current_low: float,
    current_mid: float,
    current_high: float,
) -> str:
    return f"""You are an expert loss quantification analyst.

Refine the loss severity estimates for the following scenario.

## Context
**Failure mode:** {failure_mode_name}
**Description:** {failure_mode_description}
**Loss category:** {loss_category}
**Affected party:** {affected_party_name} ({affected_party_role})
**Industry:** {industry}
**Contract value:** {currency} {contract_value:,.0f}

## Current estimates
- Low (p10): {currency} {current_low:,.0f}
- Mid (p50): {currency} {current_mid:,.0f}
- High (p90): {currency} {current_high:,.0f}

## Instructions

Review and refine these estimates. Consider:
1. Industry benchmarks and typical loss magnitudes
2. The contract value as context for proportionality
3. Whether the distribution shape (relationship between low/mid/high) is realistic
4. Any missing cost components in this loss category

Return ONLY valid JSON:

```json
{{
  "severity_low": 5000,
  "severity_mid": 25000,
  "severity_high": 150000,
  "distribution_type": "lognormal",
  "confidence": 0.6,
  "reasoning": "Brief explanation of the estimate basis"
}}
```

Return ONLY valid JSON, no markdown code fences or additional text."""

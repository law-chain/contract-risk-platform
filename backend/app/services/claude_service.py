"""Claude API integration for AI-powered risk analysis."""

import json
import logging
import re
from typing import Any

from anthropic import Anthropic

from app.config import settings
from app.prompts.failure_mode_generation import build_failure_mode_prompt
from app.prompts.loss_estimation import build_loss_estimation_prompt
from app.prompts.mitigation_suggestion import build_mitigation_prompt

logger = logging.getLogger(__name__)


def _repair_json(text: str) -> dict[str, Any]:
    """Try to parse JSON, repairing common issues from LLM output."""
    # Strip markdown code fences
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-z]*\n?", "", text)
        text = re.sub(r"\n?```\s*$", "", text)
        text = text.strip()

    # First try: parse as-is
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Second try: extract the first JSON object from the text
    match = re.search(r"\{", text)
    if match:
        text = text[match.start():]

    # Third try: if truncated, close open structures
    # Count unmatched braces/brackets
    open_braces = text.count("{") - text.count("}")
    open_brackets = text.count("[") - text.count("]")

    # Remove trailing comma or incomplete value
    text = re.sub(r",\s*$", "", text.rstrip())
    # Remove incomplete key-value pair at the end
    text = re.sub(r',\s*"[^"]*"\s*:\s*("[^"]*)?$', "", text)
    text = re.sub(r',\s*"[^"]*"\s*:\s*$', "", text)
    # Remove incomplete array element
    text = re.sub(r",\s*\{[^}]*$", "", text)

    # Recount after cleanup
    open_braces = text.count("{") - text.count("}")
    open_brackets = text.count("[") - text.count("]")
    text += "]" * open_brackets + "}" * open_braces

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Could not parse AI response as JSON: {e}. Response started with: {text[:200]}")


class ClaudeService:
    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-sonnet-4-5-20250929"

    def _call_claude(self, prompt: str) -> dict[str, Any]:
        """Make a Claude API call and parse the JSON response."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=8192,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text.strip()
        return _repair_json(text)

    def generate_failure_modes(
        self,
        goods_service_name: str,
        goods_service_description: str,
        use_context: str,
        supply_type: str,
        replaceability: str,
        industry: str,
        contract_value: float,
        currency: str,
        parties: list[dict],
    ) -> dict[str, Any]:
        """Generate failure modes for a supply relationship using Claude."""
        prompt = build_failure_mode_prompt(
            goods_service_name=goods_service_name,
            goods_service_description=goods_service_description,
            use_context=use_context,
            supply_type=supply_type,
            replaceability=replaceability,
            industry=industry,
            contract_value=contract_value,
            currency=currency,
            parties=parties,
        )
        return self._call_claude(prompt)

    def estimate_loss_parameters(
        self,
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
    ) -> dict[str, Any]:
        """Refine loss parameter estimates using Claude."""
        prompt = build_loss_estimation_prompt(
            failure_mode_name=failure_mode_name,
            failure_mode_description=failure_mode_description,
            loss_category=loss_category,
            affected_party_name=affected_party_name,
            affected_party_role=affected_party_role,
            industry=industry,
            contract_value=contract_value,
            currency=currency,
            current_low=current_low,
            current_mid=current_mid,
            current_high=current_high,
        )
        return self._call_claude(prompt)

    def suggest_mitigations(
        self,
        failure_modes: list[dict],
        industry: str,
        contract_value: float,
        currency: str,
    ) -> dict[str, Any]:
        """Suggest mitigations for failure modes using Claude."""
        prompt = build_mitigation_prompt(
            failure_modes=failure_modes,
            industry=industry,
            contract_value=contract_value,
            currency=currency,
        )
        return self._call_claude(prompt)

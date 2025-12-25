import json
import os
import logging
from typing import Dict, Any, List

# Configure Logging
logger = logging.getLogger(__name__)

RULES_PATH = os.path.join("data", "grading_rules.json")

class JadeGrader:
    def __init__(self):
        self.rules = self._load_rules()

    def _load_rules(self) -> Dict[str, Any]:
        try:
            with open(RULES_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load grading rules: {e}")
            return {"tiers": {}, "rules": []}

    def calculate_grade(self, features: Dict[str, Any]) -> str:
        """
        Determines the Rarity Tier (S, A, B) based on visual feature keywords.
        """
        if not self.rules:
            return "B" # Default fallback

        # Combine all feature text into one searchable string
        search_text = (
            str(features.get("color", "")) + " " + 
            str(features.get("characteristics", "")) + " " + 
            str(features.get("motif", ""))
        ).lower()

        # Iterate rules from top tier (S) down
        for rule in self.rules.get("rules", []):
            tier = rule["tier"]
            keywords = rule.get("required_keywords", [])
            
            # If no keywords required (e.g. B tier), match immediately
            if not keywords:
                return tier
            
            # Check if ANY of the keywords exist in the features
            # (Relaxed logic: Match 1 high-value keyword = Upgrade)
            for kw in keywords:
                if kw.lower() in search_text:
                    return tier
                    
        return "B" # Fallback

    def get_tier_info(self, tier_code: str) -> Dict[str, str]:
        """Returns the display name and color for a tier code."""
        return self.rules.get("tiers", {}).get(tier_code, {
            "name": "未分級 (Unranked)",
            "color": "#808080"
        })

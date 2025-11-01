from __future__ import annotations
from typing import Any, Dict, List, Optional
import math
import time

from backend.config import DEFAULT_CONFIDENCE_THRESHOLD 
EPSILON_CONF_GAIN = 0.02  # require heavy to beat light by >= 2 percentage points


# Simple per-category keyword bank (can grow later)
CATEGORIES = ["work","spam","promotions","personal","support","newsletter"]
KEYWORDS = {
    "spam":        ["congratulations","winner","$$$","click here","urgent","claim"],
    "work":        ["meeting","report","project","deadline","team","schedule"],
    "promotions":  ["offer","sale","discount","% off","limited time","deal"],
    "support":     ["help","support","issue","problem","password","reset","account"],
    "newsletter":  ["newsletter","weekly","news","update","digest"],
    # "personal": no strong keywords; it captures the remainder
}

def score_text_by_category(text: str) -> Dict[str, float]:
    """Give each class a raw score based on keyword matches."""
    t = text.lower()
    scores: Dict[str, float] = {c: 0.0 for c in CATEGORIES}
    for cat, words in KEYWORDS.items():
        hit = sum(1 for w in words if w in t)
        # small nonlinear boost so multiple hits lift confidence
        scores[cat] = hit if hit <= 1 else 1.0 + 0.5 * (hit - 1)
    # personal gets residual small base if nothing else matches
    if all(s == 0.0 for k, s in scores.items() if k != "personal"):
        scores["personal"] = 1.0
    return scores

def softmax(d: Dict[str, float], temperature: float = 1.0) -> Dict[str, float]:
    vals = list(d.values())
    if all(v == 0 for v in vals):
        return {k: 1.0 / len(d) for k in d}
    # temperature slightly smooths; 1.0 is fine
    exps = {k: math.exp(v / max(temperature, 1e-6)) for k, v in d.items()}
    Z = sum(exps.values())
    return {k: exps[k] / Z for k in d}


class IntelligentEmailAgent:
    """Minimal heuristic-based agent to emulate ML behavior with evidence-based confidence."""
    def __init__(self) -> None:
        pass

    def _classify_with_model(self, text: str, mode: str = "light") -> Dict[str, Any]:
        start = time.time()

        raw_scores = score_text_by_category(text)
        probs = softmax(raw_scores, temperature=1.0)

        # pick top-1
        category = max(probs.items(), key=lambda kv: kv[1])[0]
        confidence = float(probs[category])

        # Light vs Heavy: same class, different latency/CO2 profiles
        if mode == "light":
            co2_g = 0.002
            proc_time = max(0.02, min(0.15, len(text) / 10000))
            model_used = "agent_light"
        else:
            co2_g = 0.010
            proc_time = max(0.05, min(0.35, len(text) / 6000))
            model_used = "agent_heavy"

        elapsed = max(proc_time, time.time() - start)
        # build sorted distribution for all_predictions
        all_predictions = [
            {"category": c, "confidence": float(round(probs[c], 6))}
            for c in sorted(CATEGORIES, key=lambda x: probs[x], reverse=True)
        ]

        lvl = "high" if confidence >= 0.85 else ("medium" if confidence >= 0.7 else "low")
        result = {
            "predicted_category": category,
            "confidence": confidence,
            "all_predictions": all_predictions,
            "model_used": model_used,
            "escalated": (mode == "heavy"),
            "energy_metrics": {
                "co2_emissions_g": co2_g,
                "processing_time_seconds": elapsed,
                "co2_per_second": round(co2_g / max(elapsed, 1e-4), 6),  # renamed for clarity
            },
            "ai_insights": {
                "environmental_impact": {
                    "co2_this_classification": co2_g,
                    "impact_level": "low" if co2_g < 0.05 else "medium",
                },
                "accuracy_assessment": {
                    "confidence_level": lvl,
                    "should_review": confidence < 0.7,
                },
                "suggestions": [
                    "Use light model for routine emails",
                    "Escalate when confidence is below threshold",
                ],
            },
            "timestamp": time.time(),
            "email_text": text,
        }
        return result

    def classify_email(self, text: str, preferences: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        prefs = preferences or {}
        priority = prefs.get("priority", "balanced")
        threshold = float(prefs.get("confidence_threshold", DEFAULT_CONFIDENCE_THRESHOLD))

        # Try light first
        light_res = self._classify_with_model(text, mode="light")

        must_escalate = (
            light_res["confidence"] < threshold
            or priority == "accuracy"
            or (priority == "energy" and light_res["confidence"] < 0.75)
        )

        attempted = False
        chosen = light_res

        if must_escalate:
            attempted = True
            heavy_res = self._classify_with_model(text, mode="heavy")
            if heavy_res["confidence"] >= (light_res["confidence"] + EPSILON_CONF_GAIN):
                chosen = heavy_res
        # attach attempt flag for honest analytics
        chosen["escalation_attempted"] = attempted
        chosen["escalated"] = (chosen["model_used"] == "agent_heavy")
        return chosen


class AgentOrchestrator:
    def __init__(self) -> None:
        self.agent = IntelligentEmailAgent()

    def process_email(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        text = email_data.get("text", "")
        prefs = email_data.get("preferences", {})
        result = self.agent.classify_email(text, preferences=prefs)
        result["user_id"] = email_data.get("user_id", "anonymous")
        return result

# class IntelligentEmailAgent:
#     """Minimal heuristic-based agent to emulate ML behavior.

#     Provides a stable interface for the API and tests while
#     avoiding heavy ML dependencies.
#     """

#     def __init__(self) -> None:
#         pass

#     def _detect_category(self, text: str) -> str:
#         t = text.lower()
#         if any(w in t for w in ["congratulations", "winner", "$$$", "click here", "urgent", "claim"]):
#             return "spam"
#         if any(w in t for w in ["meeting", "report", "project", "deadline", "team", "schedule"]):
#             return "work"
#         if any(w in t for w in ["offer", "sale", "discount", "% off", "limited time", "deal"]):
#             return "promotions"
#         if any(w in t for w in ["help", "support", "issue", "problem", "password", "reset", "account"]):
#             return "support"
#         if any(w in t for w in ["newsletter", "weekly", "news", "update", "digest"]):
#             return "newsletter"
#         return "personal"

#     def _classify_with_model(self, text: str, mode: str = "light") -> Dict[str, Any]:
#         """Return a classification result using a pseudo-model.

#         - light: faster, slightly lower confidence
#         - heavy: slower, higher confidence on longer/complex text
#         """
#         start = time.time()

#         category = self._detect_category(text)
#         base_conf = 0.6
#         text_len = len(text)

#         if mode == "light":
#             confidence = min(0.9, base_conf + 0.15 + (0.1 if text_len > 80 else 0.0))
#             co2_g = 0.002
#             proc_time = max(0.02, min(0.15, text_len / 10000))
#             model_used = "agent_light"
#         else:  # heavy
#             # Heavier model yields more confidence on longer/complex text
#             confidence = min(0.98, base_conf + 0.25 + (0.15 if text_len > 200 else 0.05))
#             co2_g = 0.01
#             proc_time = max(0.05, min(0.35, text_len / 6000))
#             model_used = "agent_heavy"

#         # Simulate processing time measurement
#         elapsed = max(proc_time, time.time() - start)

#         result = {
#             "predicted_category": category,
#             "confidence": confidence,
#             "all_predictions": [
#                 {"category": category, "confidence": confidence},
#                 {"category": "personal", "confidence": 1 - confidence},
#             ],
#             "model_used": model_used,
#             "escalated": mode == "heavy",
#             "energy_metrics": {
#                 "co2_emissions_g": co2_g,
#                 "processing_time_seconds": elapsed,
#                 "energy_efficiency_score": round(co2_g / max(elapsed, 1e-4), 6),
#             },
#             "ai_insights": {
#                 "environmental_impact": {
#                     "co2_this_classification": co2_g,
#                     "impact_level": "low" if co2_g < 0.05 else "medium",
#                 },
#                 "accuracy_assessment": {
#                     "confidence_level": "high" if confidence >= 0.85 else "medium",
#                     "should_review": confidence < 0.7,
#                 },
#                 "suggestions": [
#                     "Use light model for routine emails",
#                     "Escalate only when confidence is low",
#                 ],
#             },
#             "timestamp": time.time(),
#             "email_text": text,
#         }
#         return result

#     def classify_email(self, text: str, preferences: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
#         prefs = preferences or {}
#         priority = prefs.get("priority", "balanced")
#         threshold = float(prefs.get("confidence_threshold", 0.85))

#         # Try light first
#         light_res = self._classify_with_model(text, mode="light")

#         must_escalate = (
#             light_res["confidence"] < threshold
#             or priority == "accuracy"
#             or (priority == "energy" and light_res["confidence"] < 0.75)
#         )

#         if must_escalate:
#             heavy_res = self._classify_with_model(text, mode="heavy")
#             # Prefer heavy result if more confident
#             if heavy_res["confidence"] >= light_res["confidence"]:
#                 return heavy_res
#         return light_res


# class AgentOrchestrator:
#     """Coordinates email processing across models and adds policy hooks."""

#     def __init__(self) -> None:
#         self.agent = IntelligentEmailAgent()

#     def process_email(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
#         text = email_data.get("text", "")
#         prefs = email_data.get("preferences", {})
#         result = self.agent.classify_email(text, preferences=prefs)
#         # Attach user context if needed in the future
#         result["user_id"] = email_data.get("user_id", "anonymous")
#         return result


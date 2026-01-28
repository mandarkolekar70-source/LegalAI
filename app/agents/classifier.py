from typing import Dict
import re

class CaseClassifier:
    def __init__(self):
        self.categories = [
            "Criminal", "Civil", "Family", "Property",
            "Cyber Crime", "Corporate", "Consumer", "Labor", "Others"
        ]

        self.keywords = {

            "Criminal": [
                "cheat", "fraud", "dishonest", "criminal breach",
                "intention from beginning", "misappropriation",
                "theft", "assault", "threat", "extortion"
            ],

            "Civil": [
                "agreement", "contract", "loan", "payment",
                "breach", "damages", "refund", "recovery"
            ],

            "Family": [
                "divorce", "maintenance", "alimony",
                "domestic violence", "custody", "dowry",
                "husband", "wife", "marriage"
            ],

            "Property": [
                "land", "plot", "property", "ownership",
                "sale deed", "registry", "possession",
                "encroachment", "boundary"
            ],

            "Cyber Crime": [
                "online", "scam", "phishing", "otp",
                "hacked", "cyber", "fake link", "upi fraud"
            ],

            "Corporate": [
                "company", "director", "shareholder",
                "board", "corporate", "merger",
                "share transfer"
            ],

            "Consumer": [
                "defective", "service", "refund",
                "warranty", "complaint", "consumer court"
            ],

            "Labor": [
                "salary", "termination", "employee",
                "employer", "workman", "layoff",
                "bonus", "pf", "gratuity"
            ]
        }


    def classify(self, text: str) -> Dict[str, float]:
        scores = {cat: 0.0 for cat in self.categories}
        text = text.lower()

        for cat, words in self.keywords.items():
            for w in words:
                if w in text:
                    scores[cat] += 1.0

        total = sum(scores.values())
        if total == 0:
            return {"Others": 0.6}

        # normalize
        scores = {k: round(v / total, 2) for k, v in scores.items() if v > 0}

        # dampen confidence (no 100%)
        for k in scores:
            scores[k] = min(scores[k], 0.78)

        return dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))
    
    def calculate_confidence(self, scores: Dict[str, float]) -> int:
        """
        Soft confidence calibration.
        Avoids misleading 100% outputs.
        """
        values = list(scores.values())

        if not values or len(values) == 1:
            return 70  # default uncertainty

        top = values[0]
        second = values[1]

        gap = top - second

        if gap > 0.5:
            return min(90, int(top * 100))
        elif gap > 0.25:
            return int(top * 100)
        else:
            return max(55, int(top * 100))


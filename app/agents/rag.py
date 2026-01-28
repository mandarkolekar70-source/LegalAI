from typing import Dict, Any, List, Optional


class LegalReasoningAgent:
    def __init__(self, vector_store):
        self.vector_store = vector_store

    def analyze_case_sync(
        self,
        text: str,
        primary_case: str,
        secondary_case: Optional[str] = None
    ) -> Dict[str, Any]:

        # --------- QUERY ENRICHMENT ---------
        query = f"{primary_case} legal dispute"
        if secondary_case:
            query += f" with possible {secondary_case} liability"

        query += f": {text}"

        results = self.vector_store.search(query, k=3)

        # --------- PRECEDENTS ---------
        similar_cases: List[Dict[str, Any]] = []
        for r in results:
            similar_cases.append({
                "pdf_name": r.get("source", "Unknown PDF"),
                "summary": r.get("text", "")[:300] + "...",
                "relevance": r.get("relevance", "N/A")
            })

        # --------- LEGAL OPINION ---------
        explanation = self._legal_opinion(
            text, primary_case, secondary_case
        )

        return {
            "case_nature": {
                "primary": primary_case,
                "secondary": secondary_case
            },
            "legal_opinion": explanation,
            "similar_precedents": similar_cases
        }

    # --------- LAWYER-STYLE OPINION ---------
    def _legal_opinion(self, text: str, primary: str, secondary: Optional[str]) -> str:
        opinion = (
            "Nature of Dispute:\n"
            "The matter arises from a transaction between private parties involving "
            "financial obligations and subsequent non-performance.\n\n"
        )

        if primary == "Civil":
            opinion += (
                "Civil Liability:\n"
                "The facts disclose a prima facie case of breach of contractual obligations. "
                "Civil remedies such as recovery of money, damages, or specific performance "
                "may be maintainable subject to proof.\n\n"
            )

        if secondary == "Criminal":
            opinion += (
                "Criminal Liability:\n"
                "Judicial precedents establish that a purely civil dispute may assume a "
                "criminal character where dishonest intention existed at the inception "
                "of the transaction. The existence of documentary evidence and witness "
                "testimony strengthens the criminal law dimension.\n\n"
            )

        opinion += (
            "Preliminary Legal Opinion:\n"
            "The complainant may consider initiating appropriate civil proceedings. "
            "Simultaneously, if evidence supports the allegation of fraudulent intent "
            "from the outset, criminal remedies may also be explored. Final outcomes "
            "remain subject to judicial scrutiny and appreciation of evidence."
        )

        return opinion

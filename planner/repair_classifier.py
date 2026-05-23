"""Failure classification for Isabelle repair prompts."""

from __future__ import annotations
import re
from dataclasses import dataclass


FAILURE_UNDEFINED_FACT = "undefined_fact"
FAILURE_SYNTAX_ERROR = "syntax_error"
FAILURE_TYPE_ERROR = "type_error"
FAILURE_ARITHMETIC_ASSOC = "arithmetic_associativity"
FAILURE_LEFTOVER_SORRY = "leftover_sorry"
FAILURE_UNKNOWN = "unknown"


@dataclass
class FailureDiagnosis:
    kind: str = FAILURE_UNKNOWN
    repair_hint: str = ""
    matched_evidence: str = ""


_RE_UNDEFINED_FACT = re.compile(
    r'Undefined fact:\s*"([^"]+)"|Undefined fact:\s*(\S+)',
    re.IGNORECASE,
)
_RE_TYPE_ERROR = re.compile(
    r"Type unification failed|Inner syntax error.+expected.+type|Type error\b",
    re.IGNORECASE | re.DOTALL,
)
_RE_SYNTAX_ERROR = re.compile(
    r"Inner syntax error|Outer syntax error|Bad input|Unexpected end of input",
    re.IGNORECASE,
)
_RE_ARITH_ASSOC_LHS = re.compile(r"\([^()]*[+*]\s*[^()]*\)\s*[+*]")
_RE_ARITH_ASSOC_RHS = re.compile(r"[+*]\s*\([^()]*[+*]\s*[^()]*\)")
_RE_LIST_OP = re.compile(
    r"@|#|\b(rev|map|filter|length|take|drop|concat|zip|distinct|"
    r"hd|tl|sum_list|foldr|foldl)\b")


def _has_leftover_sorry(proof_text: str) -> bool:
    if not proof_text:
        return False
    return "sorry" in proof_text


def _looks_like_arithmetic_assoc(residual_goal: str) -> bool:
    """Conservative: only True when goal looks like associativity AND is not list-shaped."""
    if not residual_goal:
        return False
    if _RE_LIST_OP.search(residual_goal):
        return False
    if (_RE_ARITH_ASSOC_LHS.search(residual_goal)
        or _RE_ARITH_ASSOC_RHS.search(residual_goal)):
        return True
    return False


def classify_isabelle_failure(*, errors: list, state: str, goal: str,
                              proof_text: str) -> FailureDiagnosis:
    """Classify the failure represented by the given Isabelle errors and state."""
    err_text = "\n".join(str(e) for e in (errors or []))

    # 1. Undefined fact - very high confidence.
    m = _RE_UNDEFINED_FACT.search(err_text)
    if m:
        fact = (m.group(1) or m.group(2) or "").strip()
        return FailureDiagnosis(
            kind=FAILURE_UNDEFINED_FACT,
            repair_hint=(
                f'The proof references a fact name ("{fact}") that Isabelle '
                f"cannot resolve. This is usually a hallucinated lemma name. "
                f"Consider whether a different known library lemma covers the "
                f"same content, or rewrite the step without naming the fact."
            ),
            matched_evidence=m.group(0)[:120],
        )

    # 2. Type errors - high confidence.
    m = _RE_TYPE_ERROR.search(err_text)
    if m:
        return FailureDiagnosis(
            kind=FAILURE_TYPE_ERROR,
            repair_hint=(
                "Isabelle reports a type mismatch. Check whether a variable "
                "or expression has been used at the wrong type, or whether "
                "an explicit type annotation is needed."
            ),
            matched_evidence=m.group(0)[:120],
        )

    # 3. Syntax errors.
    m = _RE_SYNTAX_ERROR.search(err_text)
    if m:
        return FailureDiagnosis(
            kind=FAILURE_SYNTAX_ERROR,
            repair_hint=(
                "Isabelle cannot parse the proof text near the failure point. "
                "Common causes: stray punctuation, an unclosed quote, or a "
                "missing 'qed' / 'done'. Re-read the failing block carefully "
                "and check structural keywords are balanced."
            ),
            matched_evidence=m.group(0)[:120],
        )

    # 4. Arithmetic associativity - low confidence; gated tightly.
    residual_haystack = (state or "") + "\n" + (goal or "")
    if _looks_like_arithmetic_assoc(residual_haystack):
        return FailureDiagnosis(
            kind=FAILURE_ARITHMETIC_ASSOC,
            repair_hint=(
                "The remaining subgoal looks like it may involve arithmetic "
                "associativity or commutativity over natural numbers or "
                "integers. If the goal is genuinely of that shape, "
                "'simp add: ac_simps' or 'simp add: algebra_simps' often "
                "closes it; otherwise prefer the proof shape the model "
                "would normally choose."
            ),
            matched_evidence=residual_haystack[:120].strip(),
        )

    # 5. Leftover sorry.
    if _has_leftover_sorry(proof_text) and not err_text.strip():
        return FailureDiagnosis(
            kind=FAILURE_LEFTOVER_SORRY,
            repair_hint=(
                "The proof outline parses and verifies structurally but contains "
                "a 'sorry' placeholder. Focus the repair on filling the placeholder "
                "with an actual proof step rather than restructuring the surrounding "
                "block."
            ),
            matched_evidence="sorry present",
        )

    # 6. Default UNKNOWN.
    return FailureDiagnosis(kind=FAILURE_UNKNOWN, repair_hint="", matched_evidence="")


def failure_prompt_text(failure: FailureDiagnosis) -> str:
    """Render diagnosis as prompt-ready string. UNKNOWN returns empty string."""
    if failure.kind == FAILURE_UNKNOWN or not failure.repair_hint:
        return ""
    return f"FAILURE_KIND: {failure.kind}\nDIAGNOSIS: {failure.repair_hint}"
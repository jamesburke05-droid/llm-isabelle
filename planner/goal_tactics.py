"""Goal-shape-aware tactic selection for the planner pre-pass and fill-phase ranker.

Two public entry points:

  - goal_aware_finishers(goal, free_vars): returns an ordered list of tactic
    strings to try in the one-shot pre-pass, ordered by the apparent shape
    of the goal. The set of tactics returned is a superset of what the
    previous hard-coded pre-pass tried, so worst-case behaviour is "same
    set of attempts, reordered".

  - rank_finisher_for_goal(goal, tactic): returns an integer score used to
    sort finisher candidates in the fill phase. When the goal shape is
    "unknown", the returned scores match _fin_priority's old behaviour
    exactly so unknown-shape goals are bit-identical to today.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class GoalShape:
    """Conservative shape classification. Most fields default to False;
    a goal can match more than one shape simultaneously."""
    list_op: bool = False
    arithmetic: bool = False
    arithmetic_assoc: bool = False
    inequality: bool = False
    set_op: bool = False
    induction_likely: bool = False
    universal: bool = False


def analyse_goal_shape(goal: str) -> GoalShape:
    """Inspect a goal string and return a shape classification."""
    if not goal:
        return GoalShape()
    g = goal
    list_ops = re.compile(
        r"\b(rev|map|filter|length|take|drop|hd|tl|concat|zip|distinct|"
        r"remdups|replicate|set|sum_list|foldr|foldl)\b")
    appends = re.compile(r"@|#")
    has_plus = "+" in g
    has_star_arith = bool(re.search(r"(?<![A-Za-z])\*(?![A-Za-z])", g))
    has_minus = bool(re.search(r"\s-\s", g))
    ineq = re.compile(r"<=|>=|<|>")
    set_op = re.compile(
        r"[\u2200\u2203\u2208\u2229\u222a]|"
        r"\b(insert|Pow|subset|Union|Inter)\b|"
        r"\\<inter>|\\<union>|\\<subseteq>|\\<in>")
    universal_re = re.compile(
        r"\\<forall>|\\<exists>|\bALL\b|\bEX\b|\u2200|\u2203")
    shape = GoalShape()
    if list_ops.search(g) or appends.search(g):
        shape.list_op = True
    if has_plus or has_star_arith or has_minus:
        has_numeric_tag = bool(re.search(r"::\s*(nat|int|real|rat)", g))
        if has_numeric_tag or not shape.list_op:
            shape.arithmetic = True
        if (re.search(r"\([^()]+[+*\-]\s*[^()]+\)\s*[+*\-]", g)
            or re.search(r"[+*\-]\s*\([^()]+[+*\-]\s*[^()]+\)", g)):
            shape.arithmetic_assoc = True
    if ineq.search(g):
        shape.inequality = True
    if set_op.search(g):
        shape.set_op = True
    if universal_re.search(g):
        shape.universal = True
    if shape.list_op or shape.arithmetic:
        shape.induction_likely = True
    return shape


_DEFAULT_NON_INDUCT = [
    "by simp", "by auto",
    "by (simp add: ac_simps)", "by (simp add: algebra_simps)",
    "by linarith", "by force", "by blast",
    "by (metis rev_map)", "by (metis map_append)",
    "by (metis rev_append)", "by (metis append_assoc)",
    "by (metis length_rev)", "by (metis length_map)",
    "by (metis length_append)", "by (metis rev_rev_ident)",
]


def _list_first():
    return [
        "by simp", "by auto",
        "by (metis map_append)", "by (metis rev_append)",
        "by (metis append_assoc)", "by (metis length_append)",
        "by (metis length_map)", "by (metis length_rev)",
        "by (metis rev_map)", "by (metis rev_rev_ident)",
        "by force", "by blast",
        "by (simp add: ac_simps)", "by (simp add: algebra_simps)",
        "by linarith",
    ]


def _arithmetic_first():
    return [
        "by simp", "by auto", "by linarith",
        "by (simp add: ac_simps)", "by (simp add: algebra_simps)",
        "by force", "by blast",
        "by (metis append_assoc)", "by (metis map_append)",
        "by (metis rev_append)", "by (metis length_append)",
        "by (metis length_map)", "by (metis length_rev)",
        "by (metis rev_map)", "by (metis rev_rev_ident)",
    ]


def _arithmetic_assoc_first():
    return [
        "by simp",
        "by (simp add: ac_simps)", "by (simp add: algebra_simps)",
        "by auto", "by linarith", "by force", "by blast",
        "by (metis append_assoc)", "by (metis map_append)",
        "by (metis rev_append)", "by (metis length_append)",
        "by (metis length_map)", "by (metis length_rev)",
        "by (metis rev_map)", "by (metis rev_rev_ident)",
    ]


def _inequality_first():
    return [
        "by simp", "by linarith", "by auto", "by force",
        "by (simp add: ac_simps)", "by (simp add: algebra_simps)",
        "by blast",
        "by (metis append_assoc)", "by (metis map_append)",
        "by (metis rev_append)", "by (metis length_append)",
        "by (metis length_map)", "by (metis length_rev)",
        "by (metis rev_map)", "by (metis rev_rev_ident)",
    ]


def _set_first():
    return [
        "by simp", "by auto", "by blast", "by force",
        "by (simp add: ac_simps)", "by (simp add: algebra_simps)",
        "by linarith",
        "by (metis append_assoc)", "by (metis map_append)",
        "by (metis rev_append)", "by (metis length_append)",
        "by (metis length_map)", "by (metis length_rev)",
        "by (metis rev_map)", "by (metis rev_rev_ident)",
    ]


def goal_aware_finishers(goal: str, free_vars: list) -> list:
    """Return an ordered list of one-shot pre-pass tactic candidates."""
    shape = analyse_goal_shape(goal)
    if shape.arithmetic_assoc:
        base = _arithmetic_assoc_first()
    elif shape.inequality:
        base = _inequality_first()
    elif shape.arithmetic and not shape.list_op:
        base = _arithmetic_first()
    elif shape.list_op:
        base = _list_first()
    elif shape.set_op:
        base = _set_first()
    else:
        base = list(_DEFAULT_NON_INDUCT)
    if free_vars:
        v0 = free_vars[0]
        for inner in ["auto", "simp_all"]:
            base.append(f"by (induct {v0}) {inner}")
        if len(free_vars) >= 2:
            others = " ".join(free_vars[1:])
            for inner in ["auto", "simp_all"]:
                base.append(f"by (induct {v0} arbitrary: {others}) {inner}")
    return base


_OLD_PRIORITY_MAP = {
    "done": 0, "by simp": 1, "by auto": 2, "by linarith": 3,
    "by force": 4, "by blast": 5, "by fastforce": 6, "by arith": 7,
}


def _old_priority(s: str) -> int:
    """Reproduces _fin_priority from driver.py exactly."""
    s = (s or "").strip()
    if s in _OLD_PRIORITY_MAP:
        return _OLD_PRIORITY_MAP[s]
    if s.startswith("by (simp add:"): return 8
    if s.startswith("by (auto"): return 9
    if s.startswith("by (metis") or s.startswith("by metis"): return 10
    if s.startswith("by (smt") or s.startswith("by smt"): return 11
    if s.startswith("by ("): return 12
    if s.startswith("by "): return 13
    return 99


def rank_finisher_for_goal(goal: str, tactic: str) -> int:
    """Return a sort score for `tactic` given the current `goal` context.
    Lower is better. When the goal shape is unknown, returns the old
    _fin_priority score so behaviour is bit-identical to today."""
    shape = analyse_goal_shape(goal)
    base = _old_priority(tactic)
    if not any([shape.list_op, shape.arithmetic, shape.arithmetic_assoc,
                shape.inequality, shape.set_op]):
        return base
    s = (tactic or "").strip()
    bonus = 0
    if shape.list_op:
        if "metis" in s and any(lem in s for lem in
                ["map_append", "rev_append", "append_assoc",
                 "length_append", "length_map", "length_rev",
                 "rev_map", "rev_rev_ident"]):
            bonus -= 3
    if shape.arithmetic_assoc:
        if "ac_simps" in s or "algebra_simps" in s:
            bonus -= 2
    if shape.inequality:
        if s == "by linarith":
            bonus -= 3
        if s == "by arith":
            bonus -= 1
    if shape.arithmetic and not shape.list_op:
        if s == "by linarith":
            bonus -= 1
    return base + bonus
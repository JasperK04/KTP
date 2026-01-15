from unittest.mock import MagicMock

from src.rule_model import ForwardChainingEngine, RuleBase


def make_rule(rule_id, condition_returns):
    rule = MagicMock()
    rule.id = rule_id
    rule.condition = MagicMock(return_value=condition_returns)
    rule.action = MagicMock()
    return rule


# ─────────────────────────────────────────────
# 1. SINGLE RULE INFERENCE
# ─────────────────────────────────────────────


def test_single_rule_inference():
    task = MagicMock()

    rule = make_rule("r1", True)
    engine = ForwardChainingEngine(RuleBase([rule]))

    engine.infer(task)

    rule.condition.assert_called()
    rule.action.assert_called_once_with(task)
    assert engine.fired_rules == {"r1"}


# ─────────────────────────────────────────────
# 2. MULTI RULE INFERENCE (FORWARD CHAINING)
# ─────────────────────────────────────────────


def test_multi_rule_inference():
    task = MagicMock()

    rule1 = make_rule("r1", True)
    rule2 = make_rule("r2", True)

    engine = ForwardChainingEngine(RuleBase([rule1, rule2]))
    engine.infer(task)

    rule1.action.assert_called_once_with(task)
    rule2.action.assert_called_once_with(task)
    assert engine.fired_rules == {"r1", "r2"}


# ─────────────────────────────────────────────
# 3. NO REFIRING
# ─────────────────────────────────────────────


def test_rule_fires_only_once():
    task = MagicMock()

    rule = make_rule("r1", True)
    engine = ForwardChainingEngine(RuleBase([rule]))

    engine.infer(task)
    engine.infer(task)

    rule.action.assert_called_once()
    assert engine.fired_rules == {"r1"}


# ─────────────────────────────────────────────
# 4. RULE ORDER INDEPENDENCE
# ─────────────────────────────────────────────


def test_rule_order_independence():
    task = MagicMock()

    rule_a = make_rule("a", True)
    rule_b = make_rule("b", True)

    engine1 = ForwardChainingEngine(RuleBase([rule_a, rule_b]))
    engine1.infer(task)

    engine2 = ForwardChainingEngine(RuleBase([rule_b, rule_a]))
    engine2.infer(task)

    assert engine1.fired_rules == engine2.fired_rules == {"a", "b"}

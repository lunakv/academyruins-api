from sqlalchemy.orm import Session

import app.database.operations as ops
from app.database.models import CrDiff
from app.utils.response_models import DiffSetCodes, TraceDiffRule, TraceItem, TraceItemAction


def create_cr_trace(db: Session, rule_id: str) -> list[TraceItem]:
    trace = []
    current_diff = ops.get_cr_diff(db, None, None)
    while current_diff:
        change = try_get_diff_change(current_diff, rule_id)
        if change:
            trace.append(change)
            if change.action == TraceItemAction.created:
                break
            rule_id = change.old.ruleNum

        current_diff = ops.get_cr_diff(db, None, current_diff.source.set_code)

    return trace


def try_get_diff_change(diff: CrDiff, rule_id: str) -> TraceItem | None:
    change = changes_to_trace_item(diff, rule_id) or moves_to_trace_item(diff, rule_id) or None
    if not change:
        return None

    return change


def moves_to_trace_item(diff: CrDiff, rule_id: str) -> TraceItem | None:
    matched_move = [m for m in diff.moves if m[1] == rule_id]
    if not matched_move:
        return None

    match = matched_move[0]
    return TraceItem(
        action=TraceItemAction.moved,
        old=TraceDiffRule(ruleNum=match[0], ruleText=None),
        new=TraceItemAction(ruleNum=match[1], ruleText=None),
        diff=get_trace_diff_metadata(diff),
    )


def changes_to_trace_item(diff: CrDiff, rule_id: str) -> TraceItem | None:
    matched_change = [c for c in diff.changes if c["new"] and c["new"]["ruleNum"] == rule_id]
    if not matched_change:
        return None

    match = matched_change[0]
    old = TraceDiffRule(**match["old"]) if match.get("old") else None
    return TraceItem(
        action=get_change_action(match),
        old=old,
        new=TraceDiffRule(ruleNum=match["new"]["ruleNum"], ruleText=match["new"]["ruleText"]),
        diff=get_trace_diff_metadata(diff),
    )


def get_change_action(change) -> TraceItemAction:
    if not change.get("old"):
        return TraceItemAction.created
    if change["old"]["ruleNum"] == change["new"]["ruleNum"]:
        return TraceItemAction.edited
    if not change["old"].get("ruleText") and not change["new"].get("ruleText"):
        return TraceItemAction.moved
    return TraceItemAction.replaced


def get_trace_diff_metadata(diff: CrDiff) -> DiffSetCodes:
    return DiffSetCodes(sourceCode=diff.source.set_code, destCode=diff.dest.set_code)

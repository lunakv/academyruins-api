from src.database.models import CrDiffItem, DiffItemKind
from src.utils.response_models import CRDiffMetadata, TraceDiffRule, TraceItem, TraceItemAction


def format_trace_item(db_item: CrDiffItem) -> TraceItem:
    return TraceItem(
        action=get_change_action(db_item),
        old=TraceDiffRule(ruleNum=db_item.old_number, ruleText=db_item.old_text) if db_item.old_number else None,
        new=TraceDiffRule(ruleNum=db_item.new_number, ruleText=db_item.new_text),
        diff=get_trace_diff_metadata(db_item),
    )


def get_change_action(change: CrDiffItem) -> TraceItemAction:
    if change.kind == DiffItemKind.addition:
        return TraceItemAction.created
    if change.kind == DiffItemKind.move:
        return TraceItemAction.moved
    if change.old_number == change.new_number:
        return TraceItemAction.edited
    return TraceItemAction.replaced


def get_trace_diff_metadata(diff_item: CrDiffItem) -> CRDiffMetadata:
    diff = diff_item.diff
    return CRDiffMetadata(
        source_code=diff.source.set_code,
        source_set=diff.source.set_name,
        dest_code=diff.dest.set_code,
        dest_set=diff.dest.set_name,
    )

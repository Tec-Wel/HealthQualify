"""ModelQual deterministic offline evaluation of supplied synthetic predictions.

Computes metrics only; does not determine clinical acceptability.
"""
from __future__ import annotations

def score_classifier(rows: list[dict], positive_label: str = "positive") -> dict:
    if not isinstance(rows,list) or not rows or len(rows)>100_000:
        raise ValueError("Nonempty bounded evaluation dataset required")
    tp=fp=tn=fn=0
    for row in rows:
        if not isinstance(row,dict) or "truth" not in row or "prediction" not in row:
            raise ValueError("Each row needs truth and prediction")
        truth,pred=row["truth"],row["prediction"]
        if type(truth) is not str or type(pred) is not str:
            raise ValueError("Labels must be strings")
        if truth==positive_label and pred==positive_label:tp+=1
        elif truth!=positive_label and pred==positive_label:fp+=1
        elif truth!=positive_label and pred!=positive_label:tn+=1
        else:fn+=1
    n=len(rows)
    return {"cases":n,"tp":tp,"fp":fp,"tn":tn,"fn":fn,
            "accuracy":(tp+tn)/n,
            "sensitivity":tp/(tp+fn) if tp+fn else None,
            "specificity":tn/(tn+fp) if tn+fp else None,
            "positive_predictive_value":tp/(tp+fp) if tp+fp else None,
            "approved":False,
            "warning":"Metrics are observations on supplied data; clinical acceptability requires approved context-specific criteria."}

def compare_model_versions(old: dict, new: dict) -> dict:
    if old.get("dataset_id")!=new.get("dataset_id") or not old.get("dataset_id"):
        raise ValueError("Cannot compare scores on different or unspecified datasets")
    old_metrics=score_classifier(old["rows"])
    new_metrics=score_classifier(new["rows"])
    return {"dataset_id":old["dataset_id"],"old":old_metrics,"new":new_metrics,
            "accuracy_delta":new_metrics["accuracy"]-old_metrics["accuracy"],
            "requires_review":True,"approved":False}

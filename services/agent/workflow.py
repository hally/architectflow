"""Deterministic LangGraph architecture-selection proof of concept.

No LLM, AWS credentials, Terraform apply, or deployment authorization.
Unclear requests require clarification rather than silently choosing a blueprint.
"""
import os
import re
from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class ArchitectureState(TypedDict, total=False):
    requirements: str
    category: str
    recommended_blueprint: str | None
    explanation: str
    next_action: str


STORAGE_TERMS = ("document", "documents", "file", "files", "bucket", "storage", "object storage", "s3", "upload")
API_TERMS = ("api", "rest api", "web api", "endpoint", "lambda", "api gateway", "backend api")


def classify(state: ArchitectureState) -> dict:
    text = " ".join(state.get("requirements", "").lower().split())
    storage = any(re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", text) for term in STORAGE_TERMS)
    api = any(re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", text) for term in API_TERMS)
    if storage and api:
        category = "multiple"
    elif storage:
        category = "storage"
    elif api:
        category = "api"
    else:
        category = "unknown"
    return {"category": category}


def choose_path(state: ArchitectureState) -> str:
    return state["category"] if state["category"] in {"storage", "api"} else "clarify"


def recommend_storage(state: ArchitectureState) -> dict:
    return {
        "recommended_blueprint": "secure-storage",
        "explanation": "Document/object storage requirements match the existing private S3 blueprint.",
        "next_action": "Request and Terraform-source policy checks are still required.",
    }


def recommend_api(state: ArchitectureState) -> dict:
    return {
        "recommended_blueprint": "serverless-api",
        "explanation": "API requirements match the serverless API catalog entry; its Terraform blueprint is not implemented yet.",
        "next_action": "Blueprint cannot advance until infrastructure validation is implemented.",
    }


def clarify(state: ArchitectureState) -> dict:
    reason = (
        "Request mentions both storage and API needs; choose which component to provision first."
        if state["category"] == "multiple"
        else "Specify whether you need document/object storage or a REST API."
    )
    return {
        "recommended_blueprint": None,
        "explanation": reason,
        "next_action": "Clarify requirements; no blueprint selected.",
    }


def build_graph():
    workflow = StateGraph(ArchitectureState)
    workflow.add_node("classify", classify)
    workflow.add_node("storage", recommend_storage)
    workflow.add_node("api", recommend_api)
    workflow.add_node("clarify", clarify)
    workflow.add_edge(START, "classify")
    workflow.add_conditional_edges("classify", choose_path, {
        "storage": "storage",
        "api": "api",
        "clarify": "clarify",
    })
    for node in ("storage", "api", "clarify"):
        workflow.add_edge(node, END)
    return workflow.compile()


architecture_graph = build_graph()


def recommend(requirements: str, *, bedrock_client=None) -> ArchitectureState:
    """Optional Bedrock classification followed by deterministic catalog routing.

    Bedrock cannot select arbitrary resources or override mixed-workload safeguards.
    If Bedrock is unavailable or malformed, use the verified local classifier.
    """
    if not isinstance(requirements, str):
        raise TypeError("requirements must be text")
    baseline = architecture_graph.invoke({"requirements": requirements})
    baseline["method"] = "LangGraph / deterministic rules v1"
    if not os.environ.get("BEDROCK_MODEL_ID"):
        return baseline

    try:
        from services.agent.bedrock_adapter import classify_with_bedrock
        category = classify_with_bedrock(requirements, client=bedrock_client)
        selected = category["category"]
        # Known mixed-workload requirements must not be silently simplified.
        if baseline["category"] == "multiple" and selected != "multiple":
            return {**baseline, "method": "LangGraph / deterministic guardrail (Bedrock disagreement)"}
        # A disagreement on an unambiguous known category also fails safe.
        if baseline["category"] in {"storage", "api"} and selected != baseline["category"]:
            return {**baseline, "method": "LangGraph / deterministic fallback (Bedrock disagreement)"}

        if selected == "storage":
            result = recommend_storage({"category": selected})
        elif selected == "api":
            result = recommend_api({"category": selected})
        else:
            result = clarify({"category": selected})
        return {
            **baseline, **result, "category": selected,
            "method": "LangGraph / Bedrock-assisted classification (OPA independent)",
        }
    except Exception:
        return {**baseline, "method": "LangGraph / deterministic fallback (Bedrock unavailable)"}


if __name__ == "__main__":
    import json
    examples = [
        "I need private encrypted document storage for an internal team.",
        "We need a REST API with scalable endpoints.",
        "We need an API that uploads documents to S3.",
        "Please build infrastructure for our team.",
    ]
    for example in examples:
        result = recommend(example)
        print(json.dumps({
            "request": example,
            "category": result["category"],
            "blueprint": result["recommended_blueprint"],
            "explanation": result["explanation"],
            "next_action": result["next_action"],
        }, indent=2))

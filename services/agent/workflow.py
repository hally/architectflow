"""Deterministic LangGraph architecture-selection proof of concept.

No LLM, AWS credentials, Terraform apply, or deployment authorization.
Unclear requests require clarification rather than silently choosing a blueprint.
"""
import re
from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class ArchitectureState(TypedDict, total=False):
    requirements: str
    category: str
    recommended_blueprint: str | None
    explanation: str
    next_action: str


STORAGE_TERMS = ("document", "file", "bucket", "object storage", "s3", "upload")
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


def recommend(requirements: str) -> ArchitectureState:
    if not isinstance(requirements, str):
        raise TypeError("requirements must be text")
    return architecture_graph.invoke({"requirements": requirements})


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

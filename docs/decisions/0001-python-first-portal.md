# ADR 0001 — Python-first portal

**Status:** Accepted

## Decision

Use Flask, Jinja2 and Bootstrap for the self-service portal instead of React/Next.js. Keep workflow and integration services primarily in Python.

## Why

The project prioritizes enterprise architecture, LangGraph, OPA and Terraform learning. A familiar Python stack reduces unrelated frontend complexity. The interface may later be enhanced with HTMX where justified.

## Consequences

The initial portal will be server-rendered; richer interactive behavior can be introduced incrementally.

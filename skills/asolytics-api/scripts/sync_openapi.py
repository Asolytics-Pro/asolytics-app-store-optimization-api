#!/usr/bin/env python3

from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DOCS_URL = "https://app.asolytics.pro/api/public-api/documentation"
OPENAPI_URL = "https://app.asolytics.pro/api/public-api/docs?public-api-docs.json"
USER_AGENT = "asolytics-api-skill/sync_openapi (+https://github.com/Asolytics-Pro/asolytics-app-store-optimization-api)"
TIMEOUT = 30
ROOT = Path(__file__).resolve().parents[1]
REF_DIR = ROOT / "references"
OPENAPI_PATH = REF_DIR / "openapi.json"
ENDPOINTS_PATH = REF_DIR / "endpoints.md"


class SyncError(Exception):
    """A user-facing failure with a clear, actionable message."""


def fetch_spec() -> dict:
    request = Request(OPENAPI_URL, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urlopen(request, timeout=TIMEOUT) as response:
            status = getattr(response, "status", 200)
            if status != 200:
                raise SyncError(f"OpenAPI URL returned HTTP {status}. The spec endpoint may have moved.")
            raw = response.read()
    except HTTPError as exc:
        raise SyncError(
            f"OpenAPI URL returned HTTP {exc.code} ({exc.reason}). "
            "The spec endpoint may have moved, or access is now restricted (e.g. Cloudflare).\n"
            f"  URL: {OPENAPI_URL}"
        ) from exc
    except URLError as exc:
        raise SyncError(
            f"Could not reach the OpenAPI URL ({exc.reason}). Check your connection or the URL.\n"
            f"  URL: {OPENAPI_URL}"
        ) from exc
    except TimeoutError as exc:
        raise SyncError(f"Timed out after {TIMEOUT}s fetching the OpenAPI spec.\n  URL: {OPENAPI_URL}") from exc

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        preview = raw[:200].decode("utf-8", "replace").strip()
        raise SyncError(
            "The OpenAPI URL did not return valid JSON (it may now serve an HTML page, "
            "a login wall, or a Cloudflare challenge).\n"
            f"  URL: {OPENAPI_URL}\n"
            f"  First bytes: {preview!r}"
        ) from exc


def format_schema(schema: dict) -> str:
    if not schema:
        return "object"
    if "$ref" in schema:
        return schema["$ref"].split("/")[-1]
    if schema.get("type") == "array":
        item = schema.get("items", {})
        return f"array<{format_schema(item)}>"
    return schema.get("type", "object")


def resolve_ref(spec: dict, obj: dict) -> dict:
    ref = obj.get("$ref")
    if not ref or not ref.startswith("#/"):
        return obj
    for key in ref[2:].split("/"):
        spec = spec[key]
    return spec


def render_param(param: dict) -> str:
    schema = param.get("schema", {})
    bits = [f"`{param['name']}`", f"in `{param['in']}`", format_schema(schema)]
    if param.get("required"):
        bits.append("required")
    if "enum" in schema:
        bits.append("enum: " + ", ".join(map(str, schema["enum"])))
    if "maxItems" in schema:
        bits.append(f"maxItems={schema['maxItems']}")
    return " - ".join(bits)


def render_request_body(schema: dict) -> list[str]:
    if not schema:
        return ["- Request body present but schema was not resolved."]
    lines: list[str] = []
    required = set(schema.get("required", []))
    for name, prop in schema.get("properties", {}).items():
        label = f"`{name}`"
        if name in required:
            label += " required"
        line = f"- {label}: {format_schema(prop)}"
        if "enum" in prop:
            line += " (" + ", ".join(map(str, prop["enum"])) + ")"
        if prop.get("description"):
            line += f" — {prop['description']}"
        lines.append(line)
    return lines or ["- Request body is defined but has no top-level properties."]


def build_markdown(spec: dict) -> str:
    info = spec.get("info", {})
    groups: dict[str, list[tuple[str, str, dict]]] = defaultdict(list)

    for path, path_item in spec.get("paths", {}).items():
        for method, operation in path_item.items():
            if method.startswith("x-"):
                continue
            tag = operation.get("tags", ["Untagged"])[0]
            groups[tag].append((path, method.upper(), operation))

    lines = [
        "# Asolytics Public API Endpoints",
        "",
        f"- Source docs: `{DOCS_URL}`",
        f"- Source OpenAPI: `{OPENAPI_URL}`",
        f"- Generated from spec version: `{info.get('version', 'unknown')}`",
        f"- Generated at: `{datetime.now(timezone.utc).isoformat()}`",
        "",
        "## Authentication",
        "",
        "- Header: `X-PUBLIC-API-TOKEN`",
        "",
    ]

    for tag in sorted(groups):
        lines.extend([f"## {tag}", ""])
        for path, method, operation in sorted(groups[tag], key=lambda item: (item[0], item[1])):
            lines.extend([f"### `{method} {path}`", ""])
            if operation.get("summary"):
                lines.append(f"- Summary: {operation['summary']}")
            if operation.get("description"):
                desc = operation["description"].replace("<br><br>", " ").replace("<br>", " ")
                lines.append(f"- Notes: {desc}")

            params = operation.get("parameters", [])
            if params:
                lines.extend(["- Parameters:", ""])
                lines.extend([render_param(resolve_ref(spec, param)) for param in params])

            request_body = operation.get("requestBody")
            if request_body:
                lines.extend(["", "- Request body:", ""])
                for content_type, content in request_body.get("content", {}).items():
                    lines.append(f"- Content-Type: `{content_type}`")
                    lines.extend(render_request_body(content.get("schema", {})))

            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    REF_DIR.mkdir(parents=True, exist_ok=True)
    try:
        spec = fetch_spec()
    except SyncError as exc:
        print(f"sync_openapi: {exc}", file=sys.stderr)
        raise SystemExit(1)

    if not spec.get("paths"):
        print("sync_openapi: the spec has no `paths` — refusing to overwrite the references.", file=sys.stderr)
        raise SystemExit(1)

    OPENAPI_PATH.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    ENDPOINTS_PATH.write_text(build_markdown(spec), encoding="utf-8")
    print(f"Wrote {OPENAPI_PATH}")
    print(f"Wrote {ENDPOINTS_PATH}")


if __name__ == "__main__":
    main()

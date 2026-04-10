"""Per-language snippet renderers; register new modules here for SDK expansion."""

from solution_planning_api.infrastructure.snippets.formats.curl import render_curl_bundle
from solution_planning_api.infrastructure.snippets.formats.javascript import render_javascript_bundle
from solution_planning_api.infrastructure.snippets.formats.python import render_python_bundle

FORMAT_RENDERERS = {
    "curl": render_curl_bundle,
    "javascript": render_javascript_bundle,
    "python": render_python_bundle,
}

__all__ = ["FORMAT_RENDERERS", "render_curl_bundle", "render_javascript_bundle", "render_python_bundle"]

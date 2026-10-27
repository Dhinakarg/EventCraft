"""Tests for frontend assets, accessibility markup, and security rules."""

from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


def test_index_html_accessibility_and_seo() -> None:
    """Verify index.html has skip links, unique IDs, single h1, and SEO tags."""
    index_path = STATIC_DIR / "index.html"
    assert index_path.exists()
    content = index_path.read_text(encoding="utf-8")

    assert "<!DOCTYPE html>" in content
    assert "<title>" in content
    assert '<meta name="description"' in content
    assert '<a href="#main-content" class="skip-link">' in content
    assert content.count("<h1") == 1
    assert 'role="tablist"' in content
    assert 'aria-live="polite"' in content


def test_no_inner_html_in_frontend_js() -> None:
    """Strictly verify JavaScript does not use innerHTML to insert content."""
    js_files = list((STATIC_DIR / "js").glob("*.js"))
    assert len(js_files) >= 3
    for js_file in js_files:
        code = js_file.read_text(encoding="utf-8")
        assert ".innerHTML" not in code, f"Forbidden innerHTML found in {js_file.name}"
        assert "insertAdjacentHTML" not in code, f"Forbidden insertAdjacentHTML in {js_file.name}"


def test_serve_frontend_via_fastapi() -> None:
    """Verify root and static asset HTTP serving."""
    res_root = client.get("/")
    assert res_root.status_code == 200
    assert "EventCraft AI" in res_root.text

    res_css = client.get("/static/css/style.css")
    assert res_css.status_code == 200

    res_js = client.get("/static/js/app.js")
    assert res_js.status_code == 200

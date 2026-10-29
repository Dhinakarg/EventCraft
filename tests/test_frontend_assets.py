"""Tests for frontend assets, accessibility markup, and security rules."""

from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


def test_index_html_accessibility_and_seo() -> None:
    """Verify index.html has skip links, fieldsets, single h1, and live regions."""
    index_path = STATIC_DIR / "index.html"
    assert index_path.exists()
    content = index_path.read_text(encoding="utf-8")

    assert "<!DOCTYPE html>" in content
    assert "<title>" in content
    assert '<meta name="description"' in content
    assert '<a href="#main-content" class="skip-link">' in content
    assert content.count("<h1") == 1
    assert "<fieldset>" in content
    assert "<legend>" in content
    assert 'role="tablist"' in content
    assert 'aria-live="polite"' in content
    assert 'autocomplete="address-level2"' in content
    base_css = (STATIC_DIR / "css" / "base.css").read_text(encoding="utf-8")
    assert "@media (forced-colors: active)" in base_css


def test_no_inner_html_in_frontend_js() -> None:
    """Strictly verify all frontend JavaScript avoids forbidden innerHTML."""
    js_files = list(STATIC_DIR.glob("**/*.js"))
    assert len(js_files) >= 2
    for js_file in js_files:
        code = js_file.read_text(encoding="utf-8")
        assert ".innerHTML" not in code, f"Forbidden innerHTML found in {js_file.name}"
        assert "insertAdjacentHTML" not in code, f"Forbidden insertAdjacentHTML in {js_file.name}"


def test_serve_frontend_via_fastapi() -> None:
    """Verify root and static asset HTTP serving."""
    res_root = client.get("/")
    assert res_root.status_code == 200
    assert "EventCraft AI" in res_root.text

    res_styles = client.get("/static/styles.css")
    assert res_styles.status_code == 200
    assert "@media print" in res_styles.text

    res_app = client.get("/static/app.js")
    assert res_app.status_code == 200

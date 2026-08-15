"""
Automated Test Suite for ProductIQ AI Web URL Ingestion & SSRF Security Validation.
Tests public HTTP/HTTPS URL parsing, BeautifulSoup extraction, SSRF security guards, and timeout error handling.
"""

import sys
import os
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath("."))

from backend.ingestion import IngestionError, validate_public_url, WebSourceAdapter, ingest_url


def test_url_ingestion_suite():
    print("==================================================")
    print("PRODUCTIQ AI -- URL INGESTION & SSRF SECURITY TEST SUITE")
    print("==================================================")

    # 1. Test SSRF Protection against Localhost and Loopback IPs
    print("\n--- 1. Testing SSRF Security Guards ---")
    ssrf_blocked_urls = [
        "http://localhost",
        "http://localhost:8000",
        "http://127.0.0.1",
        "http://127.0.0.1:7860/admin",
        "http://0.0.0.0",
        "ftp://example.com/datasheet.pdf",
        "file:///C:/Windows/System32/drivers/etc/hosts"
    ]

    for bad_url in ssrf_blocked_urls:
        try:
            validate_public_url(bad_url)
            assert False, f"SSRF Guard failed to block malicious URL: {bad_url}"
        except IngestionError as e:
            print(f"[PASS] Correctly blocked '{bad_url}': {e}")

    # 2. Test Public URL Validation
    print("\n--- 2. Testing Valid Public HTTP/HTTPS URLs ---")
    valid_url = "https://example.com/products/valve-100"
    try:
        clean = validate_public_url(valid_url)
        assert clean.startswith("https://"), "Cleaned URL scheme mismatch"
        print(f"[PASS] Valid public URL accepted: '{clean}'")
    except IngestionError as e:
        assert False, f"Valid URL raised unexpected error: {e}"

    # 3. Test WebSourceAdapter Content Scraping (Mocked HTTP Response)
    print("\n--- 3. Testing Web Page Text & Table Scraping ---")
    html_fixture = """
    <!DOCTYPE html>
    <html>
    <head><title>Acme High-Pressure Pneumatic Valve PV-50</title></head>
    <body>
        <nav><a href="/home">Home</a></nav>
        <h1>Acme High-Pressure Pneumatic Valve PV-50</h1>
        <p>Industrial solenoid control valve for pneumatic automation applications.</p>
        <h2>Technical Specifications</h2>
        <table>
            <tr><th>Attribute</th><th>Value</th></tr>
            <tr><td>Bore Size</td><td>25 mm</td></tr>
            <tr><td>Operating Pressure</td><td>1 to 10 bar</td></tr>
        </table>
        <footer>Copyright 2026 Acme Corp</footer>
    </body>
    </html>
    """

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = html_fixture.encode("utf-8")
    mock_response.text = html_fixture
    mock_response.headers = {"content-type": "text/html; charset=utf-8"}
    mock_response.url = "https://example.com/products/valve-50"

    adapter = WebSourceAdapter()
    with patch("httpx.Client.get", return_value=mock_response):
        source_doc = adapter.ingest("https://example.com/products/valve-50")
        assert source_doc.source_type == "url", f"Expected type 'url', got '{source_doc.source_type}'"
        assert "Acme High-Pressure" in source_doc.content, "Page title/header missing"
        assert "25 mm" in source_doc.content, "Table data missing"
        assert "<nav>" not in source_doc.content, "Nav tag was not stripped"
        assert "<footer>" not in source_doc.content, "Footer tag was not stripped"
        print(f"[PASS] Web page content parsed successfully ({len(source_doc.content)} chars extracted).")

    # 4. Test Web Timeout Handling
    print("\n--- 4. Testing Web Timeout Error Handling ---")
    import httpx
    with patch("httpx.Client.get", side_effect=httpx.TimeoutException("Request timed out")):
        try:
            adapter.ingest("https://example.com/slow-page")
            assert False, "Should have raised IngestionError on timeout"
        except IngestionError as e:
            assert "timed out" in str(e).lower(), f"Unexpected error message: {e}"
            print("[PASS] Web timeout handled gracefully with user alert.")

    print("\n==================================================")
    print("ALL URL INGESTION & SSRF SECURITY TESTS PASSED CLEANLY!")
    print("==================================================")
    return True


if __name__ == "__main__":
    success = test_url_ingestion_suite()
    sys.exit(0 if success else 1)

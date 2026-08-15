"""
Web Source Adapter with strict SSRF protection and HTML content parsing using BeautifulSoup & httpx.
"""

import socket
import ipaddress
import uuid
from urllib.parse import urlparse
import httpx
from bs4 import BeautifulSoup

from backend.config import URL_TIMEOUT, MAX_WEB_CONTENT_SIZE
from backend.ingestion.base import BaseSourceAdapter, IngestionError
from backend.ingestion.models import SourceDocument


def validate_public_url(url: str) -> str:
    """Validates URL for HTTP/HTTPS scheme and guards against SSRF attacks."""
    if not url or not isinstance(url, str):
        raise IngestionError("A valid URL string is required.")

    clean_url = url.strip()
    parsed = urlparse(clean_url)

    if parsed.scheme not in {"http", "https"}:
        raise IngestionError("Only HTTP and HTTPS URLs are allowed.")

    hostname = parsed.hostname
    if not hostname:
        raise IngestionError("Invalid URL hostname.")

    # Guard against localhost and special strings
    if hostname.lower() in {"localhost", "loopback", "127.0.0.1", "0.0.0.0", "::1"}:
        raise IngestionError("Requests to localhost or internal network addresses are strictly forbidden.")

    # Resolve IP address to check against private/reserved ranges (SSRF protection)
    try:
        addresses = socket.getaddrinfo(hostname, None)
        for addr_info in addresses:
            ip_str = addr_info[4][0]
            ip_obj = ipaddress.ip_address(ip_str)
            if not ip_obj.is_global:
                raise IngestionError("Requests to private or internal IP ranges are forbidden.")
    except socket.gaierror as e:
        raise IngestionError(f"Unable to resolve host '{hostname}'.") from e
    except ValueError as e:
        raise IngestionError(f"Invalid IP address format for host '{hostname}'.") from e

    return parsed.geturl()


class WebSourceAdapter(BaseSourceAdapter):
    """Adapter for ingesting public web pages and product URLs."""

    def ingest(self, url: str) -> SourceDocument:
        validated_url = validate_public_url(url)
        source_id = f"web_{uuid.uuid4().hex[:12]}"

        try:
            with httpx.Client(
                timeout=URL_TIMEOUT,
                follow_redirects=True,
                max_redirects=3,
                headers={"User-Agent": "ProductIQ-AI/1.0 (Industrial Product Intelligence; local-inference)"}
            ) as client:
                response = client.get(validated_url)
                response.raise_for_status()

                if len(response.content) > MAX_WEB_CONTENT_SIZE:
                    raise IngestionError(f"Web page content exceeds maximum allowed size ({MAX_WEB_CONTENT_SIZE // 1024 // 1024} MB).")

                content_type = response.headers.get("content-type", "").lower()
                if "html" not in content_type and "text" not in content_type:
                    raise IngestionError("URL did not return an HTML product document.")

                html_text = response.text

        except httpx.TimeoutException as e:
            raise IngestionError(f"Website request timed out after {URL_TIMEOUT} seconds.") from e
        except httpx.HTTPStatusError as e:
            raise IngestionError(f"Website returned HTTP error {e.response.status_code}.") from e
        except httpx.HTTPError as e:
            raise IngestionError(f"Failed to connect to website: {str(e)}") from e

        soup = BeautifulSoup(html_text, "html.parser")

        # Decompose non-content elements
        for element in soup(["script", "style", "noscript", "nav", "footer", "header", "svg", "form", "iframe"]):
            element.decompose()

        title = soup.title.get_text(" ", strip=True) if soup.title else "Web Product Datasheet"

        # Structured extraction from headings, lists, tables, and paragraphs
        extracted_sections = []
        if title:
            extracted_sections.append(f"PAGE TITLE: {title}")

        for h in soup.find_all(["h1", "h2", "h3", "h4"]):
            h_text = h.get_text(strip=True)
            if h_text:
                extracted_sections.append(f"\nSECTION: {h_text}")

        for table in soup.find_all("table"):
            rows = []
            for tr in table.find_all("tr"):
                cells = [td.get_text(" ", strip=True) for td in tr.find_all(["td", "th"])]
                if any(cells):
                    rows.append(" | ".join(cells))
            if rows:
                extracted_sections.append("\nTABLE DATA:\n" + "\n".join(rows))

        full_body_text = soup.get_text("\n", strip=True)
        if not full_body_text:
            raise IngestionError("Web page contained no readable product text (page may rely on client-side JavaScript rendering).")

        combined_text = f"URL SOURCE: {validated_url}\nTITLE: {title}\n\n" + "\n".join(extracted_sections) + f"\n\nFULL TEXT:\n{full_body_text}"

        return SourceDocument(
            source_id=source_id,
            source_type="url",
            source_name=title or validated_url,
            content=combined_text,
            source_uri=validated_url,
            metadata={
                "title": title,
                "url": validated_url,
                "content_length": len(combined_text)
            },
            mime_type="text/html"
        )

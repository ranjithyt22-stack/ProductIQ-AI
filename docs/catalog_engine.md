# ProductIQ AI — Scalable Product Catalog Engine

> **Architecture & Processing Specification for Multi-Product Catalog Ingestion**

---

## Executive Summary

The **ProductIQ AI Scalable Catalog Engine** extends ProductIQ AI from a single-datasheet analyzer into a batch catalog intelligence platform capable of processing multi-product industrial datasets from CSV files and multi-PDF document archives.

---

## Architecture & Data Flow

```
                      +-----------------------------+
                      | Catalog CSV / Multi-PDFs    |
                      +--------------+--------------+
                                     |
                                     v
                      +-----------------------------+
                      |   Catalog Ingestion Layer   |
                      |  (parse_catalog_csv)        |
                      +--------------+--------------+
                                     |
                                     v
                      +-----------------------------+
                      |    Catalog Orchestration    |
                      |   (process_catalog_batch)   |
                      +--------------+--------------+
                                     |
              +----------------------+----------------------+
              |                      |                      |
              v                      v                      v
      +---------------+      +---------------+      +---------------+
      |   Product 1   |      |   Product 2   |      |   Product 3   |
      | (Single-Prod  |      | (Single-Prod  |      | (Single-Prod  |
      |   Pipeline)   |      |   Pipeline)   |      |   Pipeline)   |
      +-------+-------+      +-------+-------+      +-------+-------+
              |                      |                      |
              +----------------------+----------------------+
                                     |
                                     v
                      +-----------------------------+
                      |     Catalog Aggregation     |
                      | (aggregate_catalog_metrics) |
                      +--------------+--------------+
                                     |
                                     v
                      +-----------------------------+
                      | Catalog Dashboard & Exports |
                      |    (JSON & Commerce CSV)    |
                      +-----------------------------+
```

---

## Input Formats

### 1. Catalog CSV Ingestion
Accepts CSV files with column headers matching:
- `product_name` (or `name`, `title`)
- `manufacturer` (or `brand`, `vendor`)
- `product_code` (or `part_number`, `sku`)
- `description` (or `details`)
- `product_url` (or `url`)
- `source_file` (or `pdf`)

*Missing columns are handled gracefully without raising exceptions.*

### 2. Multi-PDF Document Ingestion
Accepts multiple uploaded PDF datasheets simultaneously. Filenames are automatically mapped to catalog items or processed as individual source candidates.

---

## Fault-Tolerant Batch Processing

The batch processor operates sequentially (`Product 1 → Product 2 → Product 3`). 

If processing fails for a specific product (e.g. malformed input or unreadable document):
1. The failed product records `status = FAILED` and captures the exact `error_message`.
2. The batch processor **continues processing all remaining catalog products**.
3. The catalog summary calculates the `failed_products` count and sets the overall processing status to `PARTIAL`.

---

## Catalog Data Models

### `CatalogProduct`
```python
@dataclass
class CatalogProduct:
    product_id: str              # Unique dynamic ID (e.g. PIQ-000001)
    source_id: str               # Original source reference (e.g. csv_row_001)
    product_name: str
    manufacturer: str
    product_code: str
    category: str
    status: str                  # QUEUED, PROCESSING, COMPLETED, PARTIAL, FAILED
    quality_score: int           # 0 - 100 score
    readiness_status: str        # READY FOR COMMERCE, REVIEW RECOMMENDED, REQUIRES MANUAL REVIEW
    validation_status: str       # PASS, WARNING, FAIL
    evidence_coverage: int       # % of specs with verbatim evidence
    confidence: float            # Extraction confidence %
    error_message: str
    record: Optional[ProductIntelligenceRecord]
```

### `CatalogResult`
```python
@dataclass
class CatalogResult:
    catalog_id: str              # Unique catalog batch ID (e.g. CATALOG-A1B2C3)
    total_products: int
    processed_products: int
    failed_products: int
    review_required_products: int
    ready_products: int
    average_quality_score: float
    average_evidence_coverage: float
    validation_pass_rate: float
    products: List[CatalogProduct]
    processing_status: str
```

---

## Catalog Exports

- **Commerce CSV Export**: Flat tabular summary containing `product_id`, `product_name`, `manufacturer`, `product_code`, `category`, `description`, `quality_score`, `readiness_status`, `validation_status`, `evidence_coverage`, `processing_status`, and `error_message`.
- **Full Intelligence JSON Export**: Complete nested intelligence record preserving all specifications, validation results, evidence snippets, confidence scores, and AI enrichment taxonomy for every catalog item.

---

## Future Scalability Roadmap

For enterprise production deployment:
1. **Asynchronous Worker Queue**: Replace sequential batch processing with Celery / Redis worker pools.
2. **Multimodal OCR Service**: Integrate Tesseract or PaddleOCR sidecars for scanned paper catalog pages.
3. **Cross-Catalog RAG Indexing**: Index extracted catalog specifications into a vector database for similarity search and duplicate detection.

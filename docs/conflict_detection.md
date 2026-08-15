# Cross-Source Conflict Detection Architecture

## Overview
ProductIQ AI implements deterministic, multi-source conflict detection to eliminate discrepancies across fragmented industrial product sources (datasheets, websites, ERP systems, distributor catalogs).

---

## 1. Normalized Equivalence Comparison
Traditional systems rely on string matching, generating false-positive conflicts when equivalent units or formatting differences are present. ProductIQ AI normalizes physical quantities prior to comparison:

- **Pressure Equivalence**: `1 MPa == 10 bar == 1000 kPa`
- **Length / Dimensions**: `1000 mm == 1 m == 100 cm`
- **Mass / Weight**: `1000 g == 1 kg`
- **Power**: `1 kW == 1000 W`
- **Temperature Ranges**: `-20 to 80 °C == -20-80 °C`
- **Casing / Formatting**: `10 BAR == 10 bar == 10Bar`

---

## 2. Conflict Classification Taxonomy
The platform classifies multi-source discrepancies into 6 distinct categories:

| Conflict Type | Description |
|---|---|
| `VALUE_MISMATCH` | Distinct numerical or textual values reported across sources (e.g. 10 bar vs 16 bar). |
| `UNIT_MISMATCH` | Conflicting dimensional units that cannot be converted to equal physical quantities. |
| `MISSING_VALUE` | Critical attribute present in one source but absent from an authoritative counterpart. |
| `DUPLICATE_ATTRIBUTE` | Multiple conflicting values cited within the same document source. |
| `IDENTITY_CONFLICT` | Manufacturer, Part Number (SKU), or Product Name discrepancy. |
| `CATEGORY_CONFLICT` | Conflicting industrial equipment categorization. |

---

## 3. Deterministic Severity Assignment
Severity is assigned deterministically based on engineering domain semantics:

- **`CRITICAL`**: Product identity (SKU, Part #, Manufacturer), safety-critical specifications (Operating Pressure, Rated Voltage, Max Temperature, Explosive / Hazardous Rating).
- **`HIGH`**: Core functional engineering specifications (Bore Diameter, Stroke Length, Dynamic Load Rating, Speed, Flow Rate).
- **`MEDIUM`**: Secondary technical specifications (Port Size, Mounting Style, Fluid Compatibility, IP Rating).
- **`LOW`**: Cosmetic or non-essential descriptive details (Finish, Color, Packaging).

---

## 4. Calculated Conflict Confidence
Conflict confidence (0–100%) evaluates source reliability weights and evidence citation status:

$$\text{Confidence} = \frac{(W_A \cdot M_A \cdot E_A) + (W_B \cdot M_B \cdot E_B)}{2} \times 100$$

Where $W$ is the Source Reliability Weight, $M$ is the Evidence Match Status multiplier ($1.0$ for `VERIFIED`, $0.8$ for `PARTIALLY_VERIFIED`), and $E$ is the Evidence Confidence Score.

---

## 5. Commerce Readiness Gating
Any unresolved `CRITICAL` or `HIGH` conflict strictly forces the product status to `REVIEW_REQUIRED`, blocking publication to downstream commerce catalogs until a human engineer resolves the discrepancy.

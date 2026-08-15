"""
Validation engine for ProductIQ AI.
Executes deterministic Python validation rules across 8 categories.
"""

import re
from typing import List, Dict, Any, Optional
from backend.models import ValidationResult, ProductInfo, SpecificationAttribute


STANDARD_UNITS = {
    "mm", "cm", "m", "kg", "g", "bar", "psi", "Pa", "kPa", "MPa",
    "V", "A", "W", "kW", "°C", "°F", "m/s", "rpm"
}

RECOMMENDED_CYLINDER_SPECS = [
    "Bore Diameter",
    "Stroke Length",
    "Operating Pressure",
    "Operating Temperature",
    "Body Material",
    "Port Size",
    "Mounting",
    "Weight"
]


def validate_product_data(
    product: ProductInfo,
    specifications: List[SpecificationAttribute],
    user_metadata: Optional[Dict[str, Any]] = None
) -> List[ValidationResult]:
    """Runs all 8 validation check categories and returns structured validation results."""
    results: List[ValidationResult] = []

    # Category 1: Required Field Validation
    required_fields = {
        "product_name": product.product_name,
        "manufacturer": product.manufacturer,
        "product_code": product.product_code,
        "category": product.category,
        "description": product.description
    }

    for field_name, value in required_fields.items():
        pretty_name = field_name.replace("_", " ").title()
        if not value or str(value).strip().lower() in ["null", "none", "not found", ""]:
            results.append(ValidationResult(
                rule="Required Field Check",
                status="WARNING",
                severity="MEDIUM",
                message=f"{pretty_name} was not found in the source document.",
                field=field_name
            ))
        else:
            results.append(ValidationResult(
                rule="Required Field Check",
                status="PASS",
                severity="INFO",
                message=f"{pretty_name} identified: '{value}'",
                field=field_name
            ))

    # Convert specs to dict map for easy lookup
    spec_map: Dict[str, SpecificationAttribute] = {}
    spec_names_lower: Dict[str, List[SpecificationAttribute]] = {}

    for spec in specifications:
        low_name = spec.name.strip().lower()
        if low_name not in spec_names_lower:
            spec_names_lower[low_name] = []
        spec_names_lower[low_name].append(spec)
        spec_map[spec.name] = spec

    # Category 2: Unit Validation & Category 3: Numeric Validation
    for spec in specifications:
        # Unit Check
        if spec.unit:
            if spec.unit not in STANDARD_UNITS:
                results.append(ValidationResult(
                    rule="Unit Validation",
                    status="WARNING",
                    severity="LOW",
                    message=f"Unrecognized unit: '{spec.unit}' for attribute '{spec.name}'",
                    field=spec.name
                ))
            else:
                results.append(ValidationResult(
                    rule="Unit Validation",
                    status="PASS",
                    severity="INFO",
                    message=f"Unit '{spec.unit}' for '{spec.name}' is standard.",
                    field=spec.name
                ))

        # Numeric Format Check
        val_str = str(spec.value).strip()
        if val_str and val_str.lower() not in ["null", "none", "not found"]:
            # Check if range vs single number vs string
            is_range = bool(re.search(r"\b(to|-)\b", val_str, re.IGNORECASE))
            if is_range:
                results.append(ValidationResult(
                    rule="Numeric Validation",
                    status="PASS",
                    severity="INFO",
                    message=f"Valid numeric range format '{val_str}' for '{spec.name}'",
                    field=spec.name
                ))
            else:
                # Check single number conversion
                clean_num = re.sub(r"[^\d.-]", "", val_str)
                if clean_num:
                    results.append(ValidationResult(
                        rule="Numeric Validation",
                        status="PASS",
                        severity="INFO",
                        message=f"Valid numeric value '{val_str}' for '{spec.name}'",
                        field=spec.name
                    ))
                elif len(val_str) > 0 and not spec.unit:
                    # Pure text specification (e.g. Material="Aluminium Alloy")
                    results.append(ValidationResult(
                        rule="Text Specification",
                        status="PASS",
                        severity="INFO",
                        message=f"Text specification '{val_str}' for '{spec.name}'",
                        field=spec.name
                    ))

    # Category 4: Range & Sanity Check (Non-negative checks)
    non_negative_keywords = ["bore", "stroke", "weight", "length", "diameter", "height", "width", "speed", "power", "current", "pressure"]

    for spec in specifications:
        val_str = str(spec.value).strip()
        low_name = spec.name.lower()
        if any(kw in low_name for kw in non_negative_keywords):
            try:
                num_val = float(re.sub(r"[^\d.-]", "", val_str))
                if num_val < 0:
                    results.append(ValidationResult(
                        rule="Sanity Range Check",
                        status="FAIL",
                        severity="HIGH",
                        message=f"Negative value ({num_val}) detected for physical attribute '{spec.name}'",
                        field=spec.name
                    ))
            except ValueError:
                pass

    # Category 5: Duplicate Attribute Detection
    for low_name, spec_list in spec_names_lower.items():
        if len(spec_list) > 1:
            values = list(set(s.value for s in spec_list))
            msg = f"Duplicate attribute '{spec_list[0].name}' specified {len(spec_list)} times (Values: {values})."
            results.append(ValidationResult(
                rule="Duplicate Attribute Check",
                status="WARNING",
                severity="LOW",
                message=msg,
                field=spec_list[0].name
            ))


    # Category 6: Missing Attribute Detection (Recommended industrial specs)
    cat_lower = (product.category or "").lower()
    name_lower = (product.product_name or "").lower()
    if "cylinder" in cat_lower or "cylinder" in name_lower or "actuator" in cat_lower:
        for rec_spec in RECOMMENDED_CYLINDER_SPECS:
            found = any(rec_spec.lower() in s.name.lower() for s in specifications)
            if not found:
                results.append(ValidationResult(
                    rule="Missing Data Detection",
                    status="WARNING",
                    severity="LOW",
                    message=f"Recommended field '{rec_spec}' was not found in the source. Status: REQUIRES REVIEW",
                    field=rec_spec
                ))

    # Category 7: Logical Consistency Checks (e.g. Electrical Power P = V * I)
    voltage_spec = next((s for s in specifications if "voltage" in s.name.lower()), None)
    current_spec = next((s for s in specifications if "current" in s.name.lower()), None)
    power_spec = next((s for s in specifications if "power" in s.name.lower()), None)

    if voltage_spec and current_spec and power_spec:
        try:
            v_val = float(re.sub(r"[^\d.-]", "", str(voltage_spec.value)))
            i_val = float(re.sub(r"[^\d.-]", "", str(current_spec.value)))
            p_val = float(re.sub(r"[^\d.-]", "", str(power_spec.value)))

            expected_p = v_val * i_val
            # Allow 15% tolerance
            if abs(p_val - expected_p) > (0.15 * expected_p):
                results.append(ValidationResult(
                    rule="Logical Consistency",
                    status="WARNING",
                    severity="MEDIUM",
                    message=f"Potential inconsistency detected: Reported power ({p_val} W) does not match Voltage × Current ({v_val} V × {i_val} A = {expected_p} W).",
                    field=power_spec.name
                ))
            else:
                results.append(ValidationResult(
                    rule="Logical Consistency",
                    status="PASS",
                    severity="INFO",
                    message=f"Electrical parameters are logically consistent ({v_val} V × {i_val} A ≈ {p_val} W).",
                    field="Electrical Power"
                ))
        except ValueError:
            pass

    # Category 8: Cross-Source Conflict Detection
    if user_metadata:
        for key in ["manufacturer", "product_name", "product_code"]:
            user_val = user_metadata.get(key)
            doc_val = getattr(product, key, None)
            if user_val and doc_val and str(user_val).strip() and str(doc_val).strip():
                if str(user_val).strip().lower() not in str(doc_val).strip().lower() and str(doc_val).strip().lower() not in str(user_val).strip().lower():
                    results.append(ValidationResult(
                        rule="Cross-Source Conflict",
                        status="WARNING",
                        severity="MEDIUM",
                        message=f"User-provided {key.replace('_', ' ')} ('{user_val}') differs from document ('{doc_val}').",
                        field=key
                    ))

    return results

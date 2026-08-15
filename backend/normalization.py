"""
Normalization Layer for ProductIQ AI.
Provides deterministic unit standardization, numeric value extraction, unit conversion,
and normalization rule tracking for transparent data lineage.
"""

import re
from typing import Tuple, Optional, Dict, Any

# Canonical unit mappings
UNIT_MAPPINGS: Dict[str, str] = {
    # Length
    "millimeter": "mm",
    "millimeters": "mm",
    "millimetre": "mm",
    "millimetres": "mm",
    "mm": "mm",
    "centimeter": "cm",
    "centimeters": "cm",
    "centimetre": "cm",
    "centimetres": "cm",
    "cm": "cm",
    "meter": "m",
    "meters": "m",
    "metre": "m",
    "metres": "m",
    "m": "m",
    "inch": "inch",
    "inches": "inch",
    "in": "inch",
    # Weight / Mass
    "kilogram": "kg",
    "kilograms": "kg",
    "kilograms.": "kg",
    "kg": "kg",
    "gram": "g",
    "grams": "g",
    "g": "g",
    # Pressure
    "bar": "bar",
    "bars": "bar",
    "psi": "psi",
    "pascal": "Pa",
    "pascals": "Pa",
    "pa": "Pa",
    "kpa": "kPa",
    "mpa": "MPa",
    # Temperature
    "degrees celsius": "°C",
    "degree celsius": "°C",
    "deg c": "°C",
    "degc": "°C",
    "celsius": "°C",
    "°c": "°C",
    "c": "°C",
    "degrees fahrenheit": "°F",
    "degree fahrenheit": "°F",
    "deg f": "°F",
    "degf": "°F",
    "fahrenheit": "°F",
    "°f": "°F",
    "f": "°F",
    # Electrical
    "volt": "V",
    "volts": "V",
    "v": "V",
    "v dc": "V DC",
    "vdc": "V DC",
    "v ac": "V AC",
    "vac": "V AC",
    "amp": "A",
    "amps": "A",
    "ampere": "A",
    "amperes": "A",
    "a": "A",
    "watt": "W",
    "watts": "W",
    "w": "W",
    "kilowatt": "kW",
    "kilowatts": "kW",
    "kw": "kW",
    # Velocity / Speed
    "meters per second": "m/s",
    "metres per second": "m/s",
    "m/s": "m/s",
    "m/sec": "m/s",
    "revolutions per minute": "rpm",
    "rpm": "rpm",
    "rev/min": "rpm",
}


def normalize_unit(raw_unit: Optional[str]) -> Optional[str]:
    """Standardizes unit strings based on dictionary mappings."""
    if not raw_unit:
        return None
    cleaned = raw_unit.strip().lower()
    cleaned = re.sub(r"[^\w°/.-]", "", cleaned)
    return UNIT_MAPPINGS.get(cleaned, raw_unit.strip())


def separate_value_and_unit(value_str: Any, unit_str: Optional[str] = None) -> Tuple[str, Optional[str], bool, Optional[str]]:
    """
    Separates numbers/ranges from trailing units if combined in value_str,
    and detects applied normalization rules.
    Returns: (normalized_value, normalized_unit, normalization_applied, rule_name)
    """
    if value_str is None:
        return "", unit_str, False, None

    val = str(value_str).strip()
    raw_val_orig = str(value_str).strip()
    applied = False
    rule = None

    # If unit is already provided and valid, keep value as clean as possible
    if unit_str and unit_str.strip():
        norm_unit = normalize_unit(unit_str)
        if norm_unit != unit_str.strip():
            applied = True
            rule = f"unit_standardization ({unit_str} -> {norm_unit})"

        # Check if value end repeats unit (e.g. value="50 mm", unit="mm")
        if val.lower().endswith(unit_str.strip().lower()):
            val = val[:-len(unit_str.strip())].strip()
            applied = True
            rule = rule or "trim_redundant_unit"
        elif norm_unit and val.lower().endswith(norm_unit.lower()):
            val = val[:-len(norm_unit)].strip()
            applied = True
            rule = rule or "trim_redundant_unit"

        return val, norm_unit, applied, rule

    # Attempt regex separation for embedded unit
    # Range pattern: e.g., "1 to 10 bar", "-10 to 60 °C", "-20 to 80 deg c", "0.5 - 2.5 kg"
    range_match = re.match(r"^([+-]?\d+(?:\.\d+)?\s*(?:to|-)\s*[+-]?\d+(?:\.\d+)?)\s*([a-zA-Z°/.\s-]+)$", val, re.IGNORECASE)
    if range_match:
        cand_val = range_match.group(1).strip()
        cand_unit = range_match.group(2).strip()
        norm_unit = normalize_unit(cand_unit)
        # Check that extracted unit is recognized or reasonable
        if norm_unit or len(cand_unit.split()) <= 3:
            return cand_val, norm_unit or cand_unit, True, f"extract_range_unit ({cand_unit} -> {norm_unit or cand_unit})"

    # Single number pattern: e.g. "50 mm", "1.8 kg", "24V", "10 bar", "10 deg c"
    single_match = re.match(r"^([+-]?\d+(?:\.\d+)?)\s*([a-zA-Z°/.\s-]+)$", val, re.IGNORECASE)
    if single_match:
        cand_val = single_match.group(1).strip()
        cand_unit = single_match.group(2).strip()
        norm_unit = normalize_unit(cand_unit)
        if norm_unit or len(cand_unit.split()) <= 3:
            return cand_val, norm_unit or cand_unit, True, f"extract_value_unit ({cand_unit} -> {norm_unit or cand_unit})"


    norm_u = normalize_unit(unit_str)
    if norm_u != unit_str:
        applied = True
        rule = f"unit_standardization ({unit_str} -> {norm_u})"

    return val, norm_u, applied, rule


def convert_unit_equivalences(value: str, unit: Optional[str]) -> Tuple[str, Optional[str], bool, Optional[str]]:
    """
    Applies standard unit conversions for common industrial pressure/length units where applicable.
    E.g. MPa to bar (1 MPa = 10 bar).
    """
    if not unit or not value:
        return value, unit, False, None

    # MPa -> bar conversion (e.g. 1 MPa = 10 bar)
    if unit == "MPa":
        try:
            # Single numeric value
            num = float(value)
            bar_val = num * 10.0
            return f"{bar_val:g}", "bar", True, "MPa_to_bar (1 MPa = 10 bar)"
        except ValueError:
            # Range e.g. "0.1 to 1"
            m = re.match(r"^([+-]?\d+(?:\.\d+)?)\s*(to|-)\s*([+-]?\d+(?:\.\d+)?)$", value)
            if m:
                v1 = float(m.group(1)) * 10.0
                v2 = float(m.group(3)) * 10.0
                sep = m.group(2)
                return f"{v1:g} {sep} {v2:g}", "bar", True, "MPa_to_bar (1 MPa = 10 bar)"

    return value, unit, False, None


def normalize_specification(spec_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizes a single specification dictionary in-place and records transparent lineage metadata.
    """
    raw_name = spec_dict.get("name", "")
    raw_val = spec_dict.get("value", "")
    raw_unit = spec_dict.get("unit", None)

    orig_str = f"{raw_val} {raw_unit}".strip() if raw_unit else str(raw_val)

    val, norm_unit, applied, rule = separate_value_and_unit(raw_val, raw_unit)

    # Optional conversion
    conv_val, conv_unit, conv_applied, conv_rule = convert_unit_equivalences(val, norm_unit)
    if conv_applied:
        val = conv_val
        norm_unit = conv_unit
        applied = True
        rule = f"{rule}; {conv_rule}" if rule else conv_rule

    spec_dict["raw_value"] = str(raw_val)
    spec_dict["original_value"] = orig_str
    spec_dict["normalized_value"] = val
    spec_dict["value"] = val
    spec_dict["unit"] = norm_unit
    spec_dict["normalization_applied"] = applied
    spec_dict["normalization_rule"] = rule
    return spec_dict

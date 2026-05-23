import re


def parse_rs_amount(text: str) -> int:
    """Extract integer amount from strings like 'Rs. 500' or 'Rs. 1,500'."""
    match = re.search(r"Rs\.?\s*([\d,]+)", text)
    if not match:
        raise ValueError(f"No Rs. amount found in: {text!r}")
    return int(match.group(1).replace(",", ""))

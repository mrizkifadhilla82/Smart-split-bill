# libs/validator.py
def validate_totals(bill: dict, tolerance: float = 0.05) -> dict:
    if not bill:
        return {"valid": False, "error": "No data"}

    # Ambil sum item
    items_sum = sum(item.get("total", 0) or 0 for item in bill.get("items", []))
    
    # Ambil sum extras (Tax, Service, dll)
    extras_sum = sum(extra.get("amount", 0) or 0 for extra in bill.get("extras", []) if extra)
    
    expected = bill.get("total", 0) or 0
    computed = items_sum + extras_sum
    
    diff = abs(computed - expected)
    # Gunakan toleransi karena pembulatan desimal sering terjadi di struk
    valid = diff <= (expected * tolerance) if expected > 0 else True

    return {
        "valid": valid,
        "items_sum": items_sum,
        "extras_sum": extras_sum,
        "expected": expected,
        "diff": diff
    }
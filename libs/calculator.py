# libs/calculator.py
def calculate_fair_split(bill_data, assignments, participants):
    """
    assignments: { item_index: [list_nama_orang] }
    """
    personal_subtotals = {name: 0.0 for name in participants}
    
    # 1. Hitung belanja pokok per orang
    for idx, item in enumerate(bill_data['items']):
        payers = assignments.get(idx, [])
        if payers:
            share = (item.get('total') or 0) / len(payers)
            for p in payers:
                personal_subtotals[p] += share

    # 2. Hitung total extras (Pajak + Service)
    total_extras = sum(extra.get("amount", 0) or 0 for extra in bill_data.get("extras", []) if extra)
    total_subtotal_items = sum(item.get("total", 0) or 0 for item in bill_data.get("items", []))

    # 3. Bagi Extras secara proporsional
    final_results = []
    for name in participants:
        my_sub = personal_subtotals[name]
        # Rasio belanjaan orang tsb dibanding total belanjaan seluruhnya
        ratio = my_sub / total_subtotal_items if total_subtotal_items > 0 else 0
        
        my_extra_share = ratio * total_extras
        
        final_results.append({
            "name": name,
            "base_amount": round(my_sub, 2),
            "extra_amount": round(my_extra_share, 2),
            "grand_total": round(my_sub + my_extra_share, 2)
        })
        
    return final_results
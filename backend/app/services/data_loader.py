import pandas as pd
import re
from typing import Dict, List, Tuple

# Fuzzy matching rules for headers
COLUMN_SYNONYMS = {
    "order_id": ["order id", "order_id", "id", "order", "transaction id", "transaction_id", "orderid"],
    "order_date": ["order date", "order_date", "date", "transaction date", "transaction_date", "timestamp", "orderdate"],
    "customer_id": ["customer id", "customer_id", "cust id", "cust_id", "customer", "client id", "client_id", "customerid"],
    "customer_name": ["customer name", "customer_name", "cust name", "cust_name", "client name", "client_name", "customername"],
    "product_id": ["product id", "product_id", "prod id", "prod_id", "product", "item id", "item_id", "productid"],
    "product_name": ["product name", "product_name", "prod name", "prod_name", "item name", "item_name", "productname"],
    "category": ["category", "dept", "department", "product category", "prod_category", "type"],
    "region": ["region", "state", "city", "country", "location", "zone"],
    "quantity": ["quantity", "qty", "units", "count", "quantity_ordered"],
    "unit_price": ["unit price", "unit_price", "price", "rate", "unitprice"],
    "discount": ["discount", "disc", "rebate", "discount_rate"],
    "sales": ["sales", "revenue", "turnover", "amount", "total amount", "sales_amount"],
    "cost": ["cost", "expense", "cogs", "product_cost"],
    "profit": ["profit", "margin", "earnings", "net_profit"]
}

REQUIRED_GROUPS = {
    "sales_analysis": ["order_date", "sales", "quantity"],
    "customer_rfm": ["customer_id", "order_date", "sales"],
    "product_analysis": ["product_name", "sales"]
}

def clean_column_name(col: str) -> str:
    """Normalize a header string for comparison."""
    return re.sub(r'[^a-z0-9_]', '', str(col).strip().lower())

def suggest_column_mappings(headers: List[str]) -> Tuple[Dict[str, str], Dict[str, List[str]]]:
    """
    Fuzzy match CSV headers to standard dataset keys.
    Returns:
        (mappings, debug_info)
    """
    mappings = {}
    normalized_headers = {clean_column_name(h): h for h in headers}
    
    for std_col, synonyms in COLUMN_SYNONYMS.items():
        matched = False
        # Phase 1: Direct match with synonyms
        for syn in synonyms:
            syn_norm = clean_column_name(syn)
            if syn_norm in normalized_headers:
                mappings[std_col] = normalized_headers[syn_norm]
                matched = True
                break
        
        # Phase 2: Substring matches
        if not matched:
            for syn in synonyms:
                syn_norm = clean_column_name(syn)
                for norm_h, original_h in normalized_headers.items():
                    if syn_norm in norm_h or norm_h in syn_norm:
                        # Avoid double mapping a header
                        if original_h not in mappings.values():
                            mappings[std_col] = original_h
                            matched = True
                            break
                if matched:
                    break
                    
    # Validate features/capabilities
    missing_required = []
    # Identify which analytics suites can be enabled
    enabled_features = {}
    for feature, reqs in REQUIRED_GROUPS.items():
        missing_for_feat = [r for r in reqs if r not in mappings]
        enabled_features[feature] = len(missing_for_feat) == 0
        
    return mappings, enabled_features

def load_file_metadata(file_path: str) -> Dict[str, any]:
    """Read first few lines of CSV or Excel file to get headers and shape."""
    # Determine format
    if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
        df = pd.read_excel(file_path, nrows=5)
        # Get shape via full sheet read of dimensions (very fast)
        full_df = pd.read_excel(file_path)
        rows, cols = full_df.shape
    else:
        # CSV default
        df = pd.read_csv(file_path, nrows=5)
        # Count rows without loading entire file in memory
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            rows = sum(1 for _ in f) - 1 # discount header
        cols = len(df.columns)
        
    headers = list(df.columns)
    suggested, features = suggest_column_mappings(headers)
    
    return {
        "headers": headers,
        "row_count": max(0, rows),
        "col_count": cols,
        "suggested_mappings": suggested,
        "enabled_features": features
    }

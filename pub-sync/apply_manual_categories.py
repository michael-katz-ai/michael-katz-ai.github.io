#!/usr/bin/env python3
"""
Apply manual category assignments to unified JSONL.
"""

import json
import sys
from typing import Dict, List, Any

def load_jsonl(filepath: str) -> List[Dict[str, Any]]:
    """Load JSONL file."""
    publications = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                publications.append(json.loads(line))
    return publications

def load_manual_categories(filepath: str) -> Dict[str, Dict[str, str]]:
    """Load manual category mappings."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Convert list to dict keyed by ID
    mappings = {}
    for mapping in data.get('mappings', []):
        pub_id = mapping['id']
        mappings[pub_id] = {
            'category': mapping['category'],
            'subcategory': mapping.get('subcategory', None)
        }
    
    return mappings

def apply_manual_categories(publications: List[Dict[str, Any]], 
                           manual_cats: Dict[str, Dict[str, str]]) -> tuple:
    """Apply manual categories to publications."""
    applied_count = 0
    
    for pub in publications:
        pub_id = pub.get('id') or pub.get('bibtex_key')
        if pub_id in manual_cats:
            # Only apply if currently uncategorized
            if pub.get('category') is None:
                pub['category'] = manual_cats[pub_id]['category']
                pub['subcategory'] = manual_cats[pub_id].get('subcategory')
                applied_count += 1
    
    return publications, applied_count

def save_jsonl(publications: List[Dict[str, Any]], filepath: str):
    """Save publications to JSONL."""
    with open(filepath, 'w', encoding='utf-8') as f:
        for pub in publications:
            json.dump(pub, f, ensure_ascii=False)
            f.write('\n')

def main():
    if len(sys.argv) < 4:
        print("Usage: python apply_manual_categories.py <input_jsonl> <manual_categories.json> <output_jsonl>")
        print("\nApplies manual category assignments to uncategorized publications.")
        sys.exit(1)
    
    input_file = sys.argv[1]
    manual_file = sys.argv[2]
    output_file = sys.argv[3]
    
    # Load data
    print(f"Loading publications from: {input_file}")
    publications = load_jsonl(input_file)
    print(f"  Loaded {len(publications)} publications")
    
    print(f"\nLoading manual categories from: {manual_file}")
    manual_cats = load_manual_categories(manual_file)
    print(f"  Loaded {len(manual_cats)} manual category assignments")
    
    # Count uncategorized before
    uncategorized_before = sum(1 for p in publications if p.get('category') is None)
    print(f"\nUncategorized publications before: {uncategorized_before}")
    
    # Apply manual categories
    print("\nApplying manual categories...")
    publications, applied_count = apply_manual_categories(publications, manual_cats)
    
    # Count uncategorized after
    uncategorized_after = sum(1 for p in publications if p.get('category') is None)
    
    # Save output
    print(f"\nWriting to: {output_file}")
    save_jsonl(publications, output_file)
    
    # Print summary
    print("\nSummary:")
    print(f"  Manual categories applied: {applied_count}")
    print(f"  Uncategorized before: {uncategorized_before}")
    print(f"  Uncategorized after: {uncategorized_after}")
    print(f"  Reduction: {uncategorized_before - uncategorized_after}")
    
    # Show category distribution
    from collections import defaultdict
    by_category = defaultdict(int)
    for pub in publications:
        category = pub.get('category', 'Uncategorized')
        by_category[category] += 1
    
    print("\nPublications by category:")
    # Sort categories, putting None/Uncategorized last
    sorted_cats = sorted(
        by_category.keys(),
        key=lambda x: (x is None or x == 'Uncategorized', x or 'Uncategorized')
    )
    for category in sorted_cats:
        cat_name = category if category else 'Uncategorized'
        print(f"  {cat_name}: {by_category[category]}")
    
    print(f"\n✅ Successfully applied manual categories")

if __name__ == '__main__':
    main()

# Made with Bob

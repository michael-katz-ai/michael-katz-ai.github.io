#!/usr/bin/env python3
"""
Apply Uncategorized Resolution
Reads uncategorized_resolution.json and updates publications with categories.
"""

import json
import sys
from pathlib import Path


def load_jsonl(filepath):
    """Load JSONL file into list of dictionaries."""
    publications = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                publications.append(json.loads(line))
    return publications


def save_jsonl(publications, filepath):
    """Save list of dictionaries to JSONL file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        for pub in publications:
            json.dump(pub, f, ensure_ascii=False)
            f.write('\n')


def apply_resolution(publications, resolution):
    """Apply categorization from resolution config."""
    
    # Build lookup of paper IDs to categories
    categorization = {}
    
    # Add papers from add_to_cv
    for category, subcategories in resolution['add_to_cv'].items():
        for subcategory, paper_ids in subcategories.items():
            for paper_id in paper_ids:
                categorization[paper_id] = {
                    'category': category,
                    'subcategory': subcategory
                }
    
    # Build exclusion list
    exclude_ids = {item['id'] for item in resolution['exclude']['papers']}
    
    # Apply categorization
    updated_count = 0
    excluded_count = 0
    
    filtered_publications = []
    for pub in publications:
        pub_id = pub.get('id') or pub.get('bibtex_key')
        
        # Skip excluded papers
        if pub_id in exclude_ids:
            excluded_count += 1
            print(f"Excluding: {pub_id}")
            continue
        
        # Apply categorization if found
        if pub_id in categorization:
            cat_info = categorization[pub_id]
            pub['category'] = cat_info['category']
            pub['subcategory'] = cat_info['subcategory']
            updated_count += 1
            print(f"Categorized: {pub_id} -> {cat_info['category']} / {cat_info['subcategory']}")
        
        filtered_publications.append(pub)
    
    return filtered_publications, updated_count, excluded_count


def main():
    if len(sys.argv) != 4:
        print("Usage: python3 apply_uncategorized_resolution.py <input.jsonl> <resolution.json> <output.jsonl>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    resolution_file = sys.argv[2]
    output_file = sys.argv[3]
    
    print(f"Loading publications from: {input_file}")
    publications = load_jsonl(input_file)
    print(f"  Loaded {len(publications)} publications")
    
    print(f"\nLoading resolution config from: {resolution_file}")
    with open(resolution_file, 'r', encoding='utf-8') as f:
        resolution = json.load(f)
    
    print("\nApplying categorization...")
    filtered_pubs, updated, excluded = apply_resolution(publications, resolution)
    
    print(f"\nSaving to: {output_file}")
    save_jsonl(filtered_pubs, output_file)
    
    print(f"\n✅ Summary:")
    print(f"  Original: {len(publications)} publications")
    print(f"  Updated: {updated} publications")
    print(f"  Excluded: {excluded} publications")
    print(f"  Final: {len(filtered_pubs)} publications")


if __name__ == '__main__':
    main()

# Made with Bob

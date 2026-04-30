#!/usr/bin/env python3
"""
Generate paper_order.json from current publications.
This file can be edited to manually specify paper order within each subtopic.
"""

import json
import sys
from collections import defaultdict
from pathlib import Path


def load_topic_order(topic_order_file: str = 'topic_order.json'):
    """Load topic order from configuration file."""
    try:
        with open(topic_order_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # Extract category names in order
            category_order = [topic['name'] for topic in config['topics']]
            # Extract subcategory order for each category
            subcategory_order = {}
            for topic in config['topics']:
                subcategory_order[topic['name']] = topic.get('subtopics', [])
            return category_order, subcategory_order
    except FileNotFoundError:
        print(f"Warning: {topic_order_file} not found, using alphabetical order")
        return None, None


def generate_paper_order(input_file: str, output_file: str):
    """Generate paper order configuration from unified JSONL."""
    
    # Load topic order configuration
    category_order, subcategory_order = load_topic_order()
    
    print(f"Loading publications from: {input_file}")
    publications = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                publications.append(json.loads(line))
    
    print(f"  Loaded {len(publications)} publications")
    
    # Organize by category and subcategory
    by_category = defaultdict(lambda: defaultdict(list))
    
    for pub in publications:
        category = pub.get('category')
        subcategory = pub.get('subcategory') or 'Other'
        if category and category != 'Uncategorized':
            bibtex_key = pub.get('bibtex_key', pub.get('id', ''))
            year = pub.get('year', 0)
            title = pub.get('title', '')
            by_category[category][subcategory].append({
                'key': bibtex_key,
                'year': int(year) if str(year).isdigit() else 0,
                'title': title
            })
    
    # Sort by year (chronological) within each subcategory
    for category in by_category:
        for subcategory in by_category[category]:
            by_category[category][subcategory].sort(key=lambda x: x['year'])
    
    # Create paper order structure using topic_order.json order
    paper_order = {}
    
    # Use category order from topic_order.json if available
    categories_to_process = category_order if category_order else sorted(by_category.keys())
    
    for category in categories_to_process:
        if category not in by_category:
            continue
            
        paper_order[category] = {}
        
        # Use subcategory order from topic_order.json if available
        if subcategory_order and category in subcategory_order and subcategory_order[category]:
            subcats_to_process = subcategory_order[category]
            # Add any subcategories not in the order list at the end
            for subcat in by_category[category]:
                if subcat not in subcats_to_process:
                    subcats_to_process.append(subcat)
        else:
            subcats_to_process = sorted(by_category[category].keys())
        
        for subcategory in subcats_to_process:
            if subcategory in by_category[category]:
                papers = by_category[category][subcategory]
                # Store just the keys in order
                paper_order[category][subcategory] = [p['key'] for p in papers]
    
    # Write to file
    print(f"\nWriting paper order to: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'paper_order': paper_order,
            'notes': [
                "This file controls the order of papers within each subtopic.",
                "Papers are listed by their BibTeX keys.",
                "Reorder the keys in each array to change the display order.",
                "Papers not listed will appear at the end in chronological order.",
                "After editing, run: python3 format_website_json_v2.py katz_unified_deduplicated.jsonl publications_final.json"
            ]
        }, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\nSummary:")
    for category, subcats in paper_order.items():
        total = sum(len(keys) for keys in subcats.values())
        print(f"  {category}: {total} papers in {len(subcats)} subtopics")
    
    print(f"\n✅ Successfully generated paper order configuration")
    print(f"\nTo reorder papers:")
    print(f"  1. Edit {output_file}")
    print(f"  2. Reorder the BibTeX keys in each subtopic array")
    print(f"  3. Run: python3 format_website_json_v2.py katz_unified_deduplicated.jsonl publications_final.json")


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_paper_order.py <input_jsonl> <output_json>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    generate_paper_order(input_file, output_file)


if __name__ == '__main__':
    main()

# Made with Bob

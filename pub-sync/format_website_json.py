#!/usr/bin/env python3
"""
Convert unified JSONL to website-ready JSON format.
Organizes publications by category with proper structure for the website.
"""

import json
import sys
from collections import defaultdict
from typing import Dict, List, Any

def load_jsonl(filepath: str) -> List[Dict[str, Any]]:
    """Load JSONL file."""
    publications = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                publications.append(json.loads(line))
    return publications

def get_venue_info(pub: Dict[str, Any]) -> Dict[str, str]:
    """Extract venue information from publication."""
    venue_info = {}
    
    # Get venue name from crossref or booktitle/journal
    if 'crossref' in pub:
        venue_info['venue'] = pub['crossref']
    elif 'booktitle' in pub:
        venue_info['venue'] = pub['booktitle']
    elif 'journal' in pub:
        venue_info['venue'] = pub['journal']
    else:
        venue_info['venue'] = 'Unknown'
    
    # Get year
    if 'year' in pub:
        venue_info['year'] = str(pub['year'])
    
    # Get pages if available
    if 'pages' in pub:
        venue_info['pages'] = pub['pages']
    
    # Get volume/number for journals
    if 'volume' in pub:
        venue_info['volume'] = pub['volume']
    if 'number' in pub:
        venue_info['number'] = pub['number']
    
    return venue_info

def format_for_website(pub: Dict[str, Any]) -> Dict[str, Any]:
    """Format a publication for website JSON."""
    formatted = {
        'id': pub.get('bibtex_key', pub.get('id', '')),
        'title': pub.get('title', ''),
        'authors': pub.get('authors', []),
        'year': str(pub.get('year', '')),
        'type': pub.get('type', 'inproceedings'),
    }
    
    # Add venue information
    venue_info = get_venue_info(pub)
    formatted.update(venue_info)
    
    # Add PDF link if we can infer it from the ID
    bibtex_key = pub.get('bibtex_key', pub.get('id', ''))
    if bibtex_key:
        formatted['pdf'] = f'papers/{bibtex_key}.pdf'
    
    # Add category and subcategory if available
    if pub.get('category'):
        formatted['category'] = pub['category']
    if pub.get('subcategory'):
        formatted['subcategory'] = pub['subcategory']
    
    return formatted

def organize_by_category(publications: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Organize publications by category."""
    by_category = defaultdict(list)
    
    for pub in publications:
        category = pub.get('category', 'Uncategorized')
        by_category[category].append(pub)
    
    # Sort publications within each category by year (descending)
    for category in by_category:
        by_category[category].sort(
            key=lambda x: int(x.get('year', 0)) if str(x.get('year', '')).isdigit() else 0,
            reverse=True
        )
    
    return dict(by_category)

def main():
    if len(sys.argv) < 3:
        print("Usage: python format_website_json.py <input_jsonl> <output_json>")
        print("\nConverts unified JSONL to website-ready JSON format.")
        print("Organizes publications by category with proper structure.")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    # Load publications
    print(f"Loading publications from: {input_file}")
    publications = load_jsonl(input_file)
    print(f"  Loaded {len(publications)} publications")
    
    # Format for website
    print("\nFormatting publications for website...")
    formatted_pubs = [format_for_website(pub) for pub in publications]
    
    # Organize by category
    print("Organizing by category...")
    by_category = organize_by_category(formatted_pubs)
    
    # Create final structure matching the expected format
    website_data = {
        'thesis': {
            'title': 'Structural Patterns Heuristics via Fork Decomposition',
            'year': '2012',
            'university': 'Technion - Israel Institute of Technology',
            'advisor': 'Prof. Carmel Domshlak',
            'award': 'ICAPS 2013 Best Dissertation Award',
            'links': {
                'pdf': 'PHD/MichaelKatzPhD.pdf',
                'slides': 'PHD/PhDAwardICAPS-talk.pdf'
            }
        },
        'topics': {},
        'total_publications': len(formatted_pubs),
        'last_updated': '2026-04-29'
    }
    
    # Add each category as a topic
    for category, pubs in sorted(by_category.items()):
        # Skip uncategorized
        if category == 'Uncategorized':
            continue
        website_data['topics'][category] = {
            'count': len(pubs),
            'publications': pubs
        }
    
    # Write output
    print(f"\nWriting to: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(website_data, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\nCategory summary:")
    for category in sorted(by_category.keys()):
        count = len(by_category[category])
        print(f"  {category}: {count} publications")
    
    print(f"\n✅ Successfully created website JSON with {len(formatted_pubs)} publications")

if __name__ == '__main__':
    main()

# Made with Bob

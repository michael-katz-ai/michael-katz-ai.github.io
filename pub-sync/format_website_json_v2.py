#!/usr/bin/env python3
"""
Convert unified JSONL to website-ready JSON format.
Matches the structure expected by publications.js
Uses topic_order.json to control the order of topics and subtopics.
"""

import json
import sys
from pathlib import Path
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

# Venue name mapping for common crossrefs
VENUE_NAMES = {
    'aaai2024': 'AAAI 2024',
    'aaai2025': 'AAAI 2025',
    'icaps2024': 'ICAPS 2024',
    'icaps2026': 'ICAPS 2026',
    'ijcai2023': 'IJCAI 2023',
    'neurips2023': 'NeurIPS 2023',
    'neurips2024': 'NeurIPS 2024',
    'icaps2023': 'ICAPS 2023',
    'icaps2022': 'ICAPS 2022',
    'icaps2020': 'ICAPS 2020',
    'icaps2019': 'ICAPS 2019',
    'icaps2018': 'ICAPS 2018',
    'icaps2017': 'ICAPS 2017',
    'aaai2022': 'AAAI 2022',
    'aaai2021': 'AAAI 2021',
    'aaai2020': 'AAAI 2020',
    'aaai2019': 'AAAI 2019',
    'aaai2018': 'AAAI 2018',
    'ijcai2021': 'IJCAI 2021',
    'ijcai2019': 'IJCAI 2019',
    'ijcai2016': 'IJCAI 2016',
    'ijcai2015': 'IJCAI 2015',
}

def format_for_website(pub: Dict[str, Any]) -> Dict[str, Any]:
    """Format a publication for website JSON."""
    # Get venue - prefer booktitle/journal, then howpublished (for arXiv), then crossref
    venue = pub.get('booktitle') or pub.get('journal')
    
    # For @misc entries (like arXiv), use howpublished
    if not venue and pub.get('type', '').lower() == 'misc':
        venue = pub.get('howpublished', '')
    
    # Fall back to crossref if still no venue
    if not venue:
        crossref = pub.get('crossref', '')
        venue = VENUE_NAMES.get(crossref, crossref)
    
    bibtex_key = pub.get('bibtex_key', pub.get('id', ''))
    
    formatted = {
        'bibtex_key': bibtex_key,  # Add BibTeX key for mapping
        'title': pub.get('title', ''),
        'authors': pub.get('authors', []),
        'year': str(pub.get('year', '')),
        'venue': venue,
        'pdf': f"papers/{bibtex_key}.pdf",
        'type': pub.get('type', 'inproceedings'),
    }
    
    # Add optional fields
    if 'award' in pub:
        formatted['award'] = pub['award']
    if 'doi' in pub:
        formatted['doi'] = pub['doi']
    if 'url' in pub:
        formatted['url'] = pub['url']
    
    return formatted

def load_topic_order(config_path='topic_order.json'):
    """Load topic order configuration from JSON file."""
    config_file = Path(__file__).parent / config_path
    if not config_file.exists():
        print(f"Warning: {config_path} not found, using default order")
        return None
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    return config['topics']


def load_paper_order(config_path='paper_order.json'):
    """Load paper order configuration from JSON file."""
    config_file = Path(__file__).parent / config_path
    if not config_file.exists():
        print(f"Warning: {config_path} not found, using chronological order")
        return None
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    return config.get('paper_order', {})

def organize_by_category_and_subcategory(publications: List[Dict[str, Any]]) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
    """Organize publications by category and subcategory."""
    by_category = defaultdict(lambda: defaultdict(list))
    
    for pub in publications:
        category = pub.get('category')
        subcategory = pub.get('subcategory') or 'Other'
        if category and category != 'Uncategorized':
            by_category[category][subcategory].append(pub)
    
    # Sort publications within each subcategory by year (ascending - chronological order)
    for category in by_category:
        for subcategory in by_category[category]:
            by_category[category][subcategory].sort(
                key=lambda x: int(x.get('year', 0)) if str(x.get('year', '')).isdigit() else 0,
                reverse=False  # Changed to False for chronological order (oldest to newest)
            )
    
    # Convert defaultdict to regular dict
    return {cat: dict(subcat_dict) for cat, subcat_dict in by_category.items()}

def main():
    if len(sys.argv) < 3:
        print("Usage: python format_website_json_v2.py <input_jsonl> <output_json>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    # Load publications
    print(f"Loading publications from: {input_file}")
    publications = load_jsonl(input_file)
    print(f"  Loaded {len(publications)} publications")
    
    # Load topic order configuration
    print("Loading topic order configuration...")
    topic_order_config = load_topic_order()
    
    # Load paper order configuration
    print("Loading paper order configuration...")
    paper_order_config = load_paper_order()
    
    # Organize by category and subcategory
    print("Organizing by category and subcategory...")
    by_category = organize_by_category_and_subcategory(publications)
    
    # Create a lookup for publications by bibtex_key
    pub_by_key = {pub.get('bibtex_key', pub.get('id', '')): pub for pub in publications}
    
    # Create topics array using the order from config
    topics = []
    if topic_order_config:
        # Use configured order
        for topic_config in topic_order_config:
            category_name = topic_config['name']
            if category_name in by_category:
                subcategories = by_category[category_name]
                
                # Create subtopics array
                subtopics = []
                
                # Get subtopic order from config
                subtopic_order = topic_config.get('subtopics', [])
                
                if subtopic_order:
                    # Use configured order for subtopics
                    for subcat_name in subtopic_order:
                        if subcat_name in subcategories:
                            pubs = subcategories[subcat_name]
                            
                            # Check if we have a paper order for this subtopic
                            if paper_order_config and category_name in paper_order_config:
                                if subcat_name in paper_order_config[category_name]:
                                    # Use paper order from config
                                    paper_keys = paper_order_config[category_name][subcat_name]
                                    ordered_pubs = []
                                    remaining_pubs = list(pubs)
                                    
                                    # Add papers in specified order
                                    for key in paper_keys:
                                        for pub in remaining_pubs:
                                            if pub.get('bibtex_key', pub.get('id', '')) == key:
                                                ordered_pubs.append(pub)
                                                remaining_pubs.remove(pub)
                                                break
                                    
                                    # Add any remaining papers at the end (chronological)
                                    ordered_pubs.extend(remaining_pubs)
                                    pubs = ordered_pubs
                            
                            formatted_pubs = [format_for_website(p) for p in pubs]
                            subtopics.append({
                                'title': subcat_name,
                                'papers': formatted_pubs
                            })
                    
                    # Add any subtopics not in config (alphabetically at the end)
                    remaining = set(subcategories.keys()) - set(subtopic_order)
                    for subcat_name in sorted(remaining):
                        pubs = subcategories[subcat_name]
                        formatted_pubs = [format_for_website(p) for p in pubs]
                        subtopics.append({
                            'title': subcat_name,
                            'papers': formatted_pubs
                        })
                else:
                    # No subtopic order specified, sort alphabetically (Other last)
                    sorted_subcats = sorted(subcategories.items(), key=lambda x: (x[0] == 'Other', x[0] or ''))
                    for subcategory_name, pubs in sorted_subcats:
                        # Check if we have a paper order for this subtopic
                        if paper_order_config and category_name in paper_order_config:
                            if subcategory_name in paper_order_config[category_name]:
                                # Use paper order from config
                                paper_keys = paper_order_config[category_name][subcategory_name]
                                ordered_pubs = []
                                remaining_pubs = list(pubs)
                                
                                # Add papers in specified order
                                for key in paper_keys:
                                    for pub in remaining_pubs:
                                        if pub.get('bibtex_key', pub.get('id', '')) == key:
                                            ordered_pubs.append(pub)
                                            remaining_pubs.remove(pub)
                                            break
                                
                                # Add any remaining papers at the end (chronological)
                                ordered_pubs.extend(remaining_pubs)
                                pubs = ordered_pubs
                        
                        formatted_pubs = [format_for_website(p) for p in pubs]
                        subtopics.append({
                            'title': subcategory_name,
                            'papers': formatted_pubs
                        })
                
                topic = {
                    'id': topic_config['id'],
                    'title': category_name,
                    'description': topic_config['description'],
                    'subtopics': subtopics
                }
                topics.append(topic)
    else:
        # Fallback to alphabetical order if no config
        for category_name in sorted(by_category.keys()):
            subcategories = by_category[category_name]
            
            subtopics = []
            sorted_subcats = sorted(subcategories.items(), key=lambda x: (x[0] == 'Other', x[0] or ''))
            for subcategory_name, pubs in sorted_subcats:
                formatted_pubs = [format_for_website(p) for p in pubs]
                subtopics.append({
                    'title': subcategory_name,
                    'papers': formatted_pubs
                })
            
            topic = {
                'id': category_name.lower().replace(' ', '-'),
                'title': category_name,
                'description': '',
                'subtopics': subtopics
            }
            topics.append(topic)
    
    # Create final structure
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
        'topics': topics,
        'total_publications': sum(len(pubs) for cat in by_category.values() for pubs in cat.values()),
        'last_updated': '2026-04-29'
    }
    
    # Write output
    print(f"\nWriting to: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(website_data, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\nTopic summary:")
    for topic in topics:
        total_papers = sum(len(st['papers']) for st in topic['subtopics'])
        print(f"  {topic['title']}: {total_papers} publications")
    
    print(f"\n✅ Successfully created website JSON with {website_data['total_publications']} publications")

if __name__ == '__main__':
    main()

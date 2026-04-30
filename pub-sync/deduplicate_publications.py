#!/usr/bin/env python3
"""
Deduplicate publications by title, preferring higher-quality venues.

Priority order (highest to lowest):
1. Journal articles (article)
2. Conference papers (inproceedings) - main conference
3. Workshop papers (inproceedings) - workshop
4. Technical reports (techreport)
5. Other types
"""

import json
import sys
from collections import defaultdict
from typing import List, Dict, Any


def get_venue_priority(pub: Dict[str, Any]) -> int:
    """
    Determine venue priority for deduplication.
    Lower number = higher priority (keep this one).
    """
    entry_type = pub.get('type', '').lower()
    venue = (pub.get('booktitle') or pub.get('journal') or pub.get('crossref', '')).lower()
    bibtex_key = pub.get('bibtex_key', pub.get('id', '')).lower()
    
    # Journal articles - highest priority
    if entry_type == 'article':
        return 1
    
    # Technical reports - lowest priority
    if entry_type == 'techreport':
        return 4
    
    # Conference papers
    if entry_type == 'inproceedings':
        # Workshop papers - lower priority
        if any(ws in venue or ws in bibtex_key for ws in ['workshop', 'ws', 'demo', 'exhibit']):
            return 3
        # Main conference papers - high priority
        else:
            return 2
    
    # Other types
    return 5


def deduplicate_publications(input_file: str, output_file: str):
    """Deduplicate publications by title, keeping highest priority version."""
    
    print(f"Loading publications from: {input_file}")
    publications = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                publications.append(json.loads(line))
    
    print(f"  Loaded {len(publications)} publications")
    
    # Group by normalized title
    by_title = defaultdict(list)
    for pub in publications:
        title = pub.get('title', '').lower().strip()
        if title:
            by_title[title].append(pub)
    
    # Find duplicates
    duplicates = {title: entries for title, entries in by_title.items() if len(entries) > 1}
    
    print(f"\nFound {len(duplicates)} duplicate titles")
    
    # Deduplicate: keep highest priority version
    kept_publications = []
    removed_count = 0
    
    for title, entries in by_title.items():
        if len(entries) == 1:
            # No duplicates, keep it
            kept_publications.append(entries[0])
        else:
            # Duplicates found - sort by priority and keep the best one
            sorted_entries = sorted(entries, key=get_venue_priority)
            best_entry = sorted_entries[0]
            kept_publications.append(best_entry)
            removed_count += len(entries) - 1
            
            # Report what was kept and removed
            print(f"\nTitle: {title[:80]}...")
            print(f"  KEPT: {best_entry.get('year')} | {best_entry.get('type'):15} | {best_entry.get('bibtex_key', best_entry.get('id'))}")
            for removed in sorted_entries[1:]:
                print(f"  REMOVED: {removed.get('year')} | {removed.get('type'):15} | {removed.get('bibtex_key', removed.get('id'))}")
    
    # Write deduplicated publications
    print(f"\nWriting deduplicated publications to: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        for pub in kept_publications:
            json.dump(pub, f, ensure_ascii=False)
            f.write('\n')
    
    print(f"\nSummary:")
    print(f"  Original: {len(publications)} publications")
    print(f"  Removed: {removed_count} duplicates")
    print(f"  Final: {len(kept_publications)} publications")
    print(f"\n✅ Successfully deduplicated publications")


def main():
    if len(sys.argv) < 3:
        print("Usage: python deduplicate_publications.py <input_jsonl> <output_jsonl>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    deduplicate_publications(input_file, output_file)


if __name__ == '__main__':
    main()

# Made with Bob

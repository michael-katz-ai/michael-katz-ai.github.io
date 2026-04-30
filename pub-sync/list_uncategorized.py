#!/usr/bin/env python3
"""List publications without categories."""

import json
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python list_uncategorized.py <unified_jsonl>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    uncategorized = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                pub = json.loads(line)
                if pub.get('category') is None:
                    uncategorized.append(pub)
    
    # Sort by year (descending), then title
    uncategorized.sort(
        key=lambda x: (
            -int(x.get('year', 0)) if str(x.get('year', '')).isdigit() else 0,
            x.get('title', '')
        )
    )
    
    print(f"Found {len(uncategorized)} uncategorized publications:\n")
    
    for pub in uncategorized:
        year = pub.get('year', 'N/A')
        title = pub.get('title', 'No title')
        pub_id = pub.get('id', 'no-id')
        pub_type = pub.get('type', 'unknown')
        
        print(f"{year} [{pub_type}] {title}")
        print(f"  ID: {pub_id}")
        
        # Show authors
        authors = pub.get('authors', [])
        if authors:
            author_str = ', '.join(authors[:3])
            if len(authors) > 3:
                author_str += f', ... ({len(authors)} total)'
            print(f"  Authors: {author_str}")
        
        print()

if __name__ == '__main__':
    main()

# Made with Bob

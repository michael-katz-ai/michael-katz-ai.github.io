#!/usr/bin/env python3
"""
Extract publications from old HTML and organize them into JSON format
according to the CV structure.
"""

import json
import re
from pathlib import Path

# Read the old publications HTML
html_path = Path("../publications.html")
with open(html_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

# Initialize the publications structure
publications_data = {
    "metadata": {
        "lastUpdated": "2025-01-15",
        "totalPapers": 0
    },
    "thesis": {
        "title": "Implicit Abstraction Heuristics for Cost-Optimal Planning",
        "university": "Technion - Israel Institute of Technology",
        "year": 2010,
        "award": "ICAPS Best Dissertation Award 2011",
        "links": {
            "pdf": "PHD/MichaelKatzPhD.pdf",
            "slides": "PHD/PhDAwardICAPS-talk.pdf"
        }
    },
    "topics": []
}

# Define the topic structure based on CV
topics_structure = {
    "llms-planning": {
        "id": "llms-planning",
        "title": "LLMs for Planning and Neuro-Symbolic Reasoning",
        "description": "Fundamental contributions to formalizing planning with large language models through principled frameworks, benchmarks, and methods that ensure efficiency, soundness, and completeness.",
        "subtopics": {
            "position": {"id": "position", "title": "Position Papers", "papers": []},
            "thought-of-search": {"id": "thought-of-search", "title": "Thought of Search", "papers": []},
            "nl2pddl": {"id": "nl2pddl", "title": "NL2PDDL - Domain Generation", "papers": []},
            "nl2policy": {"id": "nl2policy", "title": "NL2Policy - Generalized Planning", "papers": []},
            "benchmarking": {"id": "benchmarking", "title": "Benchmarking and Fine-tuning", "papers": []}
        }
    },
    "multiple-solutions": {
        "id": "multiple-solutions",
        "title": "Multiple Solutions for Classical Planning",
        "description": "Pioneering work on top-k, top-quality, and diverse planning, introducing novel algorithms and certification techniques.",
        "subtopics": {
            "top-k": {"id": "top-k", "title": "Top-k/Top-quality Planning", "papers": []},
            "diverse": {"id": "diverse", "title": "Diverse Planning", "papers": []}
        }
    },
    "theory-practice": {
        "id": "theory-practice",
        "title": "Theory and Practice of Classical Planning",
        "description": "Foundational advances in planning as heuristic search, including test-of-time award-winning contributions.",
        "subtopics": {
            "abstractions": {"id": "abstractions", "title": "Abstractions", "papers": []},
            "cost-partitioning": {"id": "cost-partitioning", "title": "Cost Partitioning", "papers": []},
            "psp": {"id": "psp", "title": "Partial Satisfaction Planning", "papers": []},
            "red-black": {"id": "red-black", "title": "Red-Black Planning", "papers": []},
            "planner-selection": {"id": "planner-selection", "title": "Planner Selection", "papers": []},
            "symmetry-por": {"id": "symmetry-por", "title": "State Pruning (Symmetry & POR) & Relevance", "papers": []},
            "novelty": {"id": "novelty", "title": "Novelty", "papers": []}
        }
    },
    "planning-rl": {
        "id": "planning-rl",
        "title": "Planning and Reinforcement Learning",
        "description": "Key contributions to neuro-symbolic planning-learning integration for interpretable and sample-efficient decision-making.",
        "subtopics": {
            "parl": {"id": "parl", "title": "Planning Annotated RL (PaRL)", "papers": []},
            "action-models": {"id": "action-models", "title": "Action Models & Rewards", "papers": []}
        }
    },
    "applications": {
        "id": "applications",
        "title": "Applications, Data, and AI Planning Solutions",
        "description": "Leadership in translating planning research into enterprise-scale AI systems and deployed solutions.",
        "subtopics": {
            "ibm-spa": {"id": "ibm-spa", "title": "IBM Scenario Planning Advisor", "papers": []},
            "data": {"id": "data", "title": "Data and Benchmarks", "papers": []},
            "other-apps": {"id": "other-apps", "title": "Other Applications", "papers": []}
        }
    }
}

# Paper mapping based on CV - mapping paper identifiers to topic/subtopic
# Format: "identifier": ("topic_id", "subtopic_id")
paper_mapping = {
    # LLMs for Planning
    "Planning in the LLM Era": ("llms-planning", "position"),
    "Make Planning Research Rigorous Again": ("llms-planning", "position"),
    "Automating Thought of Search": ("llms-planning", "thought-of-search"),
    "Thought of Search: Planning with Language Models": ("llms-planning", "thought-of-search"),
    "Transition Function Prediction": ("llms-planning", "thought-of-search"),
    "Model Space Reasoning as Search": ("llms-planning", "nl2pddl"),
    "Large Language Models as Planning Domain Generators": ("llms-planning", "nl2pddl"),
    "Can LLMs Fix Issues with Reasoning Models": ("llms-planning", "nl2pddl"),
    "Improved Generalized Planning with LLMs": ("llms-planning", "nl2policy"),
    "Generalized Planning in PDDL Domains": ("llms-planning", "nl2policy"),
    "ACPBench: Reasoning about Action": ("llms-planning", "benchmarking"),
    "ACPBench Hard": ("llms-planning", "benchmarking"),
    "Seemingly Simple Planning Problems": ("llms-planning", "benchmarking"),
    "Less is More: Learning Graph Tasks": ("llms-planning", "benchmarking"),
    
    # Multiple Solutions
    "Some Orders Are Important": ("multiple-solutions", "top-k"),
    "Unifying and Certifying Top-Quality": ("multiple-solutions", "top-k"),
    "K* Search Over Orbit Space": ("multiple-solutions", "top-k"),
    "On K* Search for Top-K Planning": ("multiple-solutions", "top-k"),
    "K* and Partial Order Reduction": ("multiple-solutions", "top-k"),
    "Who Needs These Operators Anyway": ("multiple-solutions", "top-k"),
    "Top-Quality Planning: Finding Practically": ("multiple-solutions", "top-k"),
    "A Novel Iterative Approach to Top-k": ("multiple-solutions", "top-k"),
    "Conflict-Directed Diverse Planning": ("multiple-solutions", "diverse"),
    "Bounding Quality in Diverse Planning": ("multiple-solutions", "diverse"),
    "Reshaping Diverse Planning": ("multiple-solutions", "diverse"),
    
    # Theory and Practice - Abstractions
    "Landmark-Enhanced Abstraction Heuristics": ("theory-practice", "abstractions"),
    "Implicit Abstraction Heuristics for Cost-Optimal": ("theory-practice", "abstractions"),
    "Implicit Abstraction Heuristics": ("theory-practice", "abstractions"),
    "New Islands of Tractability": ("theory-practice", "abstractions"),
    "Structural Patterns Beyond Forks": ("theory-practice", "abstractions"),
    "How to Relax a Bisimulation": ("theory-practice", "abstractions"),
    "When Abstractions Met Landmarks": ("theory-practice", "abstractions"),
    "Structural-Pattern Databases": ("theory-practice", "abstractions"),
    "Structural Pattern Heuristics via Fork": ("theory-practice", "abstractions"),
    "Structural patterns of tractable": ("theory-practice", "abstractions"),
    "Catching Label Subsets": ("theory-practice", "abstractions"),
    "On Satisficing Planning with Admissible": ("theory-practice", "abstractions"),
    
    # Cost Partitioning
    "Optimal Admissible Composition": ("theory-practice", "cost-partitioning"),
    "When Optimal is Just Not Good Enough": ("theory-practice", "cost-partitioning"),
    "Optimal Additive Composition": ("theory-practice", "cost-partitioning"),
    
    # PSP
    "On Partial Satisfaction Planning": ("theory-practice", "psp"),
    "On Producing Shortest Cost-Optimal": ("theory-practice", "psp"),
    "A* Search and Bound-Sensitive": ("theory-practice", "psp"),
    "Symbolic Search for Oversubscription": ("theory-practice", "psp"),
    "Oversubscription Planning as Classical": ("theory-practice", "psp"),
    "In Search of Tractability for Partial": ("theory-practice", "psp"),
    
    # Red-Black
    "Red-black planning: a new systematic": ("theory-practice", "red-black"),
    "Custom-Design of FDR Encodings": ("theory-practice", "red-black"),
    "Red-Black Heuristics for Planning Tasks": ("theory-practice", "red-black"),
    "Red-Black Relaxed Plan Heuristics Reloaded": ("theory-practice", "red-black"),
    "Red-Black Relaxed Plan Heuristics": ("theory-practice", "red-black"),
    "Who Said we Need to Relax All Variables": ("theory-practice", "red-black"),
    "Pushing the Limits of Partial Delete": ("theory-practice", "red-black"),
    
    # Planner Selection
    "Beyond Message Passing": ("theory-practice", "planner-selection"),
    "Online Planner Selection with Graph": ("theory-practice", "planner-selection"),
    "Deep learning for cost-optimal planning": ("theory-practice", "planner-selection"),
    
    # Symmetry & POR
    "Simplifying Planning Tasks with Fact-Level": ("theory-practice", "symmetry-por"),
    "Theoretical foundations for structural": ("theory-practice", "symmetry-por"),
    "A Symmetry-based Task Reduction": ("theory-practice", "symmetry-por"),
    "Strengthening Canonical Pattern Databases": ("theory-practice", "symmetry-por"),
    "Stubborn Sets for Fully Observable": ("theory-practice", "symmetry-por"),
    "Structural Symmetries for Fully Observable": ("theory-practice", "symmetry-por"),
    "Heuristics and Symmetries in Classical": ("theory-practice", "symmetry-por"),
    "Factored symmetries for merge-and-shrink": ("theory-practice", "symmetry-por"),
    "An Empirical Case Study on Symmetry": ("theory-practice", "symmetry-por"),
    "Integrating Partial Order Reduction": ("theory-practice", "symmetry-por"),
    "Symmetry Breaking: Satisficing Planning": ("theory-practice", "symmetry-por"),
    "Enhanced Symmetry Breaking in Cost-Optimal": ("theory-practice", "symmetry-por"),
    
    # Novelty
    "The Fewer the Merrier": ("theory-practice", "novelty"),
    "Adapting Novelty to Classical Planning": ("theory-practice", "novelty"),
    
    # Planning and RL
    "Learning Parameterized Policies": ("planning-rl", "parl"),
    "AI Planning Annotation in Reinforcement": ("planning-rl", "parl"),
    "Guiding Hierarchical Reinforcement Learning": ("planning-rl", "parl"),
    "Optimistic Exploration in Reinforcement": ("planning-rl", "action-models"),
    "Efficient Black-Box Planning Using Macro": ("planning-rl", "action-models"),
    "On Reducing Action Labels": ("planning-rl", "action-models"),
    "Reinforcement Learning for Classical Planning": ("planning-rl", "action-models"),
    
    # Applications
    "IBM Scenario Planning Advisor: Plan recognition": ("applications", "ibm-spa"),
    "An AI Planning Solution to Scenario": ("applications", "ibm-spa"),
    "Scenario Planning In The Wild": ("applications", "ibm-spa"),
    "IBM Scenario Planning Advisor: A Neuro-Symbolic": ("applications", "ibm-spa"),
    "Answering binary causal questions": ("applications", "ibm-spa"),
    "Generating SAS+ Planning Tasks": ("applications", "data"),
    "IPC: A Benchmark Data Set": ("applications", "data"),
    "Democratizing Usage of Planning Systems": ("applications", "data"),
    "The Role of IPC in Setting Standards": ("applications", "data"),
    "QueryGym: Step-by-Step Interaction": ("applications", "other-apps"),
    "PARIS: Planning Algorithms for Reconfiguring": ("applications", "other-apps"),
    "Exploring Context-Free Languages": ("applications", "other-apps"),
    "A Conflict-driven Interface between Symbolic": ("applications", "other-apps"),
    "Towards Automated Planning for Enterprise": ("applications", "other-apps"),
    "Semi-Black Box: Rapid Development": ("applications", "other-apps"),
}

def extract_paper_info(li_content):
    """Extract paper information from an <li> element content."""
    # Extract title (usually in <b> tags)
    title_match = re.search(r'<b>(.*?)</b>', li_content, re.DOTALL)
    if not title_match:
        return None
    
    title = title_match.group(1).strip()
    title = re.sub(r'<[^>]+>', '', title)  # Remove any HTML tags
    
    # Extract authors (before the title usually)
    authors_text = li_content[:title_match.start()].strip()
    authors_text = re.sub(r'<[^>]+>', '', authors_text)
    authors_text = re.sub(r'\s+', ' ', authors_text).strip()
    
    # Split authors by comma, "and", or other separators
    if authors_text:
        authors = [a.strip() for a in re.split(r',|\sand\s', authors_text) if a.strip()]
    else:
        authors = []
    
    # Extract venue and year
    venue_match = re.search(r'<i>(.*?)</i>', li_content)
    venue = venue_match.group(1).strip() if venue_match else ""
    
    year_match = re.search(r'\b(19|20)\d{2}\b', li_content)
    year = int(year_match.group(0)) if year_match else 0
    
    # Extract PDF link
    pdf_match = re.search(r'href=["\']([^"\']*\.pdf)["\']', li_content)
    pdf_link = pdf_match.group(1) if pdf_match else ""
    
    # Determine type based on venue
    paper_type = "conference"
    if "Journal" in venue or "AIJ" in venue or "JAIR" in venue:
        paper_type = "journal"
    elif "Workshop" in venue or "workshop" in venue.lower():
        paper_type = "workshop"
    
    # Check for awards
    award = None
    if "ICAPS Influential Paper" in li_content or "test-of-time" in li_content:
        award = "ICAPS Influential Paper Award 2023"
    elif "Best" in li_content and "Award" in li_content:
        award_match = re.search(r'(Best[^<.]*Award[^<.]*)', li_content)
        if award_match:
            award = award_match.group(1).strip()
    
    return {
        "title": title,
        "authors": authors,
        "venue": venue,
        "year": year,
        "type": paper_type,
        "links": {"pdf": pdf_link} if pdf_link else {},
        "award": award
    }

def find_topic_subtopic(title):
    """Find the topic and subtopic for a paper based on its title."""
    for key, (topic_id, subtopic_id) in paper_mapping.items():
        if key.lower() in title.lower():
            return topic_id, subtopic_id
    return None, None

# Extract all papers from HTML
papers_by_year = {}
year_sections = re.findall(r'<font size="\+1"><b>(\d{4})</b></font>(.*?)(?=<font size="\+1"><b>|$)', html_content, re.DOTALL)

for year, section_content in year_sections:
    year = int(year)
    # Find all <li> elements in this section
    li_items = re.findall(r'<li>(.*?)</li>', section_content, re.DOTALL)
    
    for li_content in li_items:
        paper_info = extract_paper_info(li_content)
        if paper_info and paper_info['title']:
            if year not in papers_by_year:
                papers_by_year[year] = []
            papers_by_year[year].append(paper_info)

# Organize papers into topics
for year in sorted(papers_by_year.keys(), reverse=True):
    for paper in papers_by_year[year]:
        topic_id, subtopic_id = find_topic_subtopic(paper['title'])
        if topic_id and subtopic_id:
            # Add paper to the appropriate subtopic
            if topic_id in topics_structure:
                if subtopic_id in topics_structure[topic_id]['subtopics']:
                    paper_id = f"{topic_id}-{subtopic_id}-{len(topics_structure[topic_id]['subtopics'][subtopic_id]['papers']) + 1}"
                    paper['id'] = paper_id
                    topics_structure[topic_id]['subtopics'][subtopic_id]['papers'].append(paper)

# Build final structure
for topic_id, topic_data in topics_structure.items():
    topic_entry = {
        "id": topic_data["id"],
        "title": topic_data["title"],
        "description": topic_data["description"],
        "subtopics": []
    }
    
    for subtopic_id, subtopic_data in topic_data["subtopics"].items():
        if subtopic_data["papers"]:  # Only include subtopics with papers
            topic_entry["subtopics"].append({
                "id": subtopic_data["id"],
                "title": subtopic_data["title"],
                "papers": subtopic_data["papers"]
            })
    
    if topic_entry["subtopics"]:  # Only include topics with subtopics
        publications_data["topics"].append(topic_entry)

# Count total papers
total_papers = sum(
    len(paper) 
    for topic in publications_data["topics"] 
    for subtopic in topic["subtopics"] 
    for paper in subtopic["papers"]
)
publications_data["metadata"]["totalPapers"] = total_papers

# Write to JSON file
output_path = Path("data/publications.json")
output_path.parent.mkdir(exist_ok=True)
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(publications_data, f, indent=2, ensure_ascii=False)

print(f"Extracted {total_papers} papers")
print(f"Output written to {output_path}")

# Print summary by topic
for topic in publications_data["topics"]:
    topic_total = sum(len(st["papers"]) for st in topic["subtopics"])
    print(f"\n{topic['title']}: {topic_total} papers")
    for subtopic in topic["subtopics"]:
        print(f"  - {subtopic['title']}: {len(subtopic['papers'])} papers")

# Made with Bob

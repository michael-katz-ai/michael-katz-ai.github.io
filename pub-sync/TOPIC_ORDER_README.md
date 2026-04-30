# Topic Order Configuration

## Overview

The `topic_order.json` file controls the display order of research topics and their subtopics on your website.

## File Location

`new-site/pub-sync/topic_order.json`

## How It Works

The `format_website_json_v2.py` script reads this configuration file to determine:
1. The order in which topics appear on the website
2. The order of subtopics within each topic
3. Topic metadata (ID, description)

## File Structure

```json
{
  "topics": [
    {
      "name": "Topic Name",
      "id": "topic-id",
      "description": "Topic description",
      "subtopics": ["Subtopic 1", "Subtopic 2", ...]
    }
  ]
}
```

### Fields

- **name**: The full topic name (must match category name from CV)
- **id**: URL-friendly identifier for the topic
- **description**: Brief description shown on the website
- **subtopics**: Array of subtopic names in desired display order
  - If empty `[]`, subtopics will be sorted alphabetically
  - If specified, subtopics appear in the given order
  - Any subtopics not listed will appear alphabetically at the end

## How to Reorder

### Reorder Topics

Simply move topic objects in the `topics` array:

```json
{
  "topics": [
    { "name": "Topic A", ... },  // Will appear first
    { "name": "Topic B", ... },  // Will appear second
    { "name": "Topic C", ... }   // Will appear third
  ]
}
```

### Reorder Subtopics

Edit the `subtopics` array for a topic:

```json
{
  "name": "LLMs for Planning and Neuro-Symbolic Reasoning",
  "subtopics": [
    "Position",              // Will appear first
    "Thought of Search",     // Will appear second
    "NL2PDDL",              // Will appear third
    "NL2Policy",            // Will appear fourth
    "Benchmarking and fine-tuning"  // Will appear fifth
  ]
}
```

### Leave Subtopics Unordered

To use alphabetical ordering for subtopics, use an empty array:

```json
{
  "name": "Theory and Practice of Classical Planning",
  "subtopics": []  // Subtopics will be sorted alphabetically
}
```

## After Making Changes

After editing `topic_order.json`, regenerate the website JSON:

```bash
cd new-site/pub-sync
python3 format_website_json_v2.py katz_unified_with_manual.jsonl publications_final.json
cp publications_final.json ../data/publications.json
```

## Example: Changing Order

**Before:**
```json
{
  "topics": [
    { "name": "LLMs for Planning", ... },
    { "name": "Multiple Solutions", ... }
  ]
}
```

**After (swapped order):**
```json
{
  "topics": [
    { "name": "Multiple Solutions", ... },
    { "name": "LLMs for Planning", ... }
  ]
}
```

## Notes

- Topic names must exactly match the category names from your CV
- Subtopic names must exactly match the subcategory names extracted from your CV
- The file uses standard JSON format (no comments allowed in the actual file)
- Invalid JSON will cause the script to fall back to alphabetical ordering

## Current Topics

As of the last update, the configured topics are:

1. LLMs for Planning and Neuro-Symbolic Reasoning
2. Multiple Solutions for Classical Planning
3. Theory and Practice of Classical Planning
4. Planning and Reinforcement Learning
5. Applications, Data, and AI Planning based solutions
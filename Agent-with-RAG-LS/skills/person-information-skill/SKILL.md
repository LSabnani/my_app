---
name: person_search_tool
description: Queries internal registry database to find person details including full name, city, country, job title, and department.
---

# Person Information Skill

## Description
Queries internal registry database to find person details including full name, city, country, job title, and department.

## Metadata
- **Name**: person_search_tool
- **Function**: `person_search.query_person_registry`
- **Trigger Queries**:
  - Who is Lucas Dubois?
  - Find employees living in Paris or Working as Data Engineers.
  - Search for job title of Sophia Martinez.

## Parameters
- `keyword` (string): Search term or person name/job title to search for.
- `field` (string, optional): Specific field to filter by (`name`, `city`, `country`, `job_title`). Default: `all`.

# Data Processing Scripts

This folder documents the expected Python scripts for processing publication
data and generating collaboration matches. The scripts are not included in this
public repository.

## Scripts

### `build_collab_hub_from_scratch.py`
Processes raw publication CSV data and creates aggregated researcher profiles.

**Input**: `filtered_publications.csv` (raw publication data)
**Output**: `Researcher_Profiles_For_PowerBI.csv` (aggregated researcher data)

**What it does**:
- Aggregates multiple publications per researcher
- Identifies primary SDG focus
- Infers research methods from keywords/abstracts
- Calculates career stages
- Extracts top keywords

### `generate_ccs_demo_data.py`
Generates collaboration matches and calculates Collaboration Compatibility Scores.

**Input**: `Researcher_Profiles_For_PowerBI.csv`
**Output**: `data/CCS_Demo_Data.csv` (collaboration matches with scores)

**What it does**:
- Creates simulated user searches
- Matches researchers based on compatibility
- Calculates CCS scores (Topic Match, Method Match, Career Fit)
- Generates explainable recommendations

## Usage

If you have access to the scripts, place them in this folder and run them
locally against the raw publication data. This repo only includes the demo
output (`data/CCS_Demo_Data.csv`).

## Data Flow

```
filtered_publications.csv
    ↓
build_collab_hub_from_scratch.py
    ↓
Researcher_Profiles_For_PowerBI.csv
    ↓
generate_ccs_demo_data.py
    ↓
data/CCS_Demo_Data.csv
```

For detailed documentation, see:
- [CCS_DEMO_DATA_EXPLANATION.md](../docs/methodology/CCS_DEMO_DATA_EXPLANATION.md)
- [SDG_MATCHING_EXPLANATION.md](../docs/methodology/SDG_MATCHING_EXPLANATION.md)

## Note on availability
This README documents expected inputs and outputs so reviewers can understand
the pipeline even without the scripts.

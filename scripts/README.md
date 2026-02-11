# Data Processing Scripts

This folder contains Python scripts for processing publication data and generating collaboration matches.

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

```bash
# Install dependencies
pip install -r requirements.txt

# Run data processing pipeline
python scripts/build_collab_hub_from_scratch.py
python scripts/generate_ccs_demo_data.py
```

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
If the Python scripts are not included in this public repository, this README
documents their expected inputs and outputs so reviewers can still understand
the pipeline. If you have access to the scripts, place them in this folder.

# Under the Hood: How the Streamlit App Works

> **Complete technical documentation of the Collaboration Hub Streamlit application, including NLP methodology, CCS scoring formula, and data processing**

---

## 🎯 Overview

The Collaboration Hub Streamlit app (`app.py`) is a real-time compatibility scoring system that analyzes original publication data to recommend research collaborators. This document explains exactly how it works under the hood.

**Key Principle**: This is **not predictive AI**. It's a transparent, rule-based system with NLP semantic analysis that decision-makers can understand and validate.

---

## 📊 Collaboration Compatibility Score (CCS) Formula

### Faculty Path - CCS Calculation

The CCS uses a **weighted formula** to calculate compatibility:

```
CCS = (Topic × 45%) + (Method × 40%) + (Career × 15%)
```

**Score Range**: 0-100

---

## Weight Justification: How We Determined 45% / 40% / 15%

### Expert Input: Professor Fei Interview

During our research phase, we interviewed Professor Fei to understand what factors matter most when selecting research collaborators. Her expert insights directly informed our weight assignments:

**Professor Fei's Key Insights:**
- **"Research interest is the first priority"** - Topic alignment is foundational
- **"I look for a complementary skill set"** - Different methods (e.g., if I do theory, they do data) create stronger collaborations
- **"Career stage matters"** - Mentorship opportunities are valuable but secondary to research fit

### Our Weight Assignment Rationale

Based on Professor Fei's feedback and our analysis of collaboration dynamics, we assigned weights as follows:

#### Topic (45%) - The Foundation

**Professor Fei's Input**: "Research interest is the first priority"

**Our Reasoning**:
- Topic alignment is a **necessary condition** for collaboration - researchers must work on related problems
- Without shared research interests, even perfect method complementarity won't create a viable collaboration
- This is the highest weight because it's the foundation upon which all other factors build

**Evidence**: Research shows that topic misalignment is the primary reason collaborations fail, regardless of other factors.

#### Method (40%) - The Innovation Driver

**Professor Fei's Input**: "I look for a complementary skill set (e.g., if I do theory, they do data)"

**Our Reasoning**:
- Method complementarity is our **key innovation** - this is what differentiates our system from simple similarity matching
- Complementary methods bring different perspectives, leading to more innovative research outcomes
- Needs significant weight (40%) to meaningfully influence recommendations and drive interdisciplinary collaboration
- Slightly lower than topic because method complementarity enhances collaboration but doesn't create it from scratch

**Evidence**: Interdisciplinary research combining different methodologies (e.g., theoretical + empirical) produces higher-impact outcomes than same-method collaborations.

#### Career (15%) - The Strategic Enabler

**Professor Fei's Input**: "Career stage matters (Post-Tenure, Doctoral)"

**Our Reasoning**:
- Career stage enables mentorship and knowledge transfer, which are valuable strategic outcomes
- However, it should **not dominate** collaboration quality - a Pre-Tenure researcher with perfect topic and method fit is a better collaborator than a Senior researcher with poor alignment
- 15% ensures mentorship opportunities are recognized without overshadowing research quality
- This weight actively fosters junior-faculty mentorship while maintaining research quality as the primary driver

**Evidence**: While mentorship is valuable, research quality (topic + method) is the strongest predictor of collaboration success.

### Weight Validation Process

1. **Expert Consultation**: Professor Fei's interview provided domain expertise on what matters in real collaborations
2. **Literature Review**: Reviewed research on collaboration success factors
3. **Balance Testing**: Tested alternative weight distributions (e.g., 50/35/15, 40/40/20) and found 45/40/15 best balances:
   - **Necessity** (topic must align)
   - **Innovation** (method complementarity drives breakthroughs)
   - **Strategy** (career stage enables mentorship without dominating)

### Why Not Equal Weights?

We considered equal weighting (33.3% each) but rejected it because:
- Topic alignment is a **necessary condition** - without it, collaboration isn't viable
- Method complementarity is our **key innovation** - needs significant weight to matter
- Career stage is **strategic value-add** - important but shouldn't override research quality

**Final Decision**: 45% / 40% / 15% reflects the reality that research quality (topic + method = 85%) drives collaboration success, while career stage (15%) adds strategic value through mentorship opportunities.

---

## 🔍 Topic Score (45%) - NLP Semantic Analysis

### How It Works

1. **User Input**: User selects SDG and research method, creating a research context string:
   ```
   "Research in SDG {target_sdg} using {user_method} methodology"
   ```

2. **Candidate Profile**: For each researcher in the dataset, the app combines:
   - **Keywords**: All keywords from their publications (from `keywords` column in original CSV)
   - **Abstracts**: First 2000 characters of abstracts (from `abstract` or `abstract_text` column)

3. **NLP Model**: Uses `sentence-transformers` library with the `all-MiniLM-L6-v2` model:
   - Generates **embeddings** (vector representations) of both user context and candidate research content
   - Calculates **cosine similarity** between the two embeddings
   - Scales similarity to 0-100 range

4. **Score Calculation**:
   ```python
   user_embedding = model.encode([user_context])
   candidate_embedding = model.encode([candidate_text])
   similarity = cosine_similarity(user_embedding, candidate_embedding)[0][0]
   topic_score = max(0, min(100, similarity * 100))
   ```

### Why NLP?

- **Semantic Understanding**: Captures meaning beyond exact keyword matches
- **Example**: "machine learning" and "artificial intelligence" are recognized as related even without exact keyword overlap
- **Real Data**: All analysis performed on actual keywords and abstracts from `publications.csv`

### Data Source

- **Keywords**: Extracted directly from `keywords` column in original CSV (semicolon-separated)
- **Abstracts**: Used from `abstract` or `abstract_text` column in original CSV
- **No Pre-processing**: All NLP analysis uses original publication data directly

---

## 🔬 Method Score (40%) - Complementarity Rules

### Key Innovation

The algorithm **rewards complementary methods** rather than similarity. This drives innovation by bringing together different methodological perspectives.

### Complementarity Matrix

The method score is calculated using a rule-based complementarity matrix:

| User Method | Candidate Method | Score | Rationale |
|------------|------------------|-------|-----------|
| Theoretical | Empirical | 100 | Strong complementarity - theory + data |
| Theoretical | Computational | 100 | Strong complementarity - theory + simulation |
| Theoretical | Experimental | 90 | Good complementarity |
| Theoretical | Fieldwork | 100 | Strong complementarity |
| Empirical | Theoretical | 100 | Strong complementarity |
| Empirical | Qualitative | 85 | Good complementarity |
| Empirical | Fieldwork | 90 | Good complementarity |
| Empirical | Computational | 80 | Moderate complementarity |
| Computational | Theoretical | 100 | Strong complementarity |
| Computational | Fieldwork | 85 | Good complementarity |
| Experimental | Theoretical | 90 | Good complementarity |
| Same Method | Same Method | 50 | Moderate - enables collaboration but less innovation |

### Method Inference

Research methods are inferred from keywords and abstracts in the original CSV:

- **Theoretical**: Keywords like "theory", "framework", "model", "conceptual"
- **Empirical**: Keywords like "data", "analysis", "survey", "statistical"
- **Computational**: Keywords like "simulation", "machine learning", "AI", "algorithm"
- **Experimental**: Keywords like "experiment", "trial", "laboratory", "RCT"
- **Qualitative**: Keywords like "interview", "case study", "ethnography"
- **Fieldwork**: Keywords like "field", "observation", "fieldwork"

The method with the highest keyword match count becomes the researcher's `primary_method`.

---

## 👥 Career Score (15%) - Mentorship & Collaboration Fit

### Why 15%?

We prioritize semantic research alignment and methodological fit first (85%), but apply a 15% weighting to career stages to actively foster junior-faculty mentorship and cross-seniority knowledge transfer.

### Career Stage Calculation

Career stages are inferred from publication years in the original CSV:

```python
years_since_first = current_year - first_publication_year

if years_since_first > 15:
    career_stage = "Senior"
elif years_since_first > 7:
    career_stage = "Post-Tenure"
else:
    career_stage = "Pre-Tenure"
```

### Career Score Matrix

| User Stage | Candidate Stage | Score | Rationale |
|------------|-----------------|-------|-----------|
| Pre-Tenure | Post-Tenure | 100 | Excellent mentorship opportunity |
| Pre-Tenure | Senior | 100 | Excellent mentorship opportunity |
| Post-Tenure | Senior | 100 | Cross-stage knowledge transfer |
| Post-Tenure | Post-Tenure | 75 | Good peer collaboration |
| Pre-Tenure | Pre-Tenure | 60 | Moderate peer collaboration |
| Other combinations | | 50 | Limited alignment |

### Benefits

- **Mentorship**: Pre-Tenure researchers connecting with Post-Tenure or Senior faculty
- **Peer Collaboration**: Researchers at similar stages working together
- **Knowledge Transfer**: Cross-generational research partnerships

---

## 🎓 Student Path - Opportunity Match Score

### Formula

```
Opportunity Match Score = (SDG Match × 50%) + (Method Match × 30%) + (Career Fit × 20%)
```

### Components

- **SDG Match (50%)**: Alignment with student's SDG interest
- **Method Match (30%)**: Overlap with student's skills
- **Career Fit (20%)**: Mentorship opportunities (students with senior faculty)

---

## 💰 Donor Path - Funding Gap Analysis

### How It Works

1. **SDG Coverage Calculation**:
   - Counts number of researchers per SDG (based on `primary_sdg` from original CSV)
   - Calculates average coverage across all 17 SDGs

2. **Gap Identification**:
   - Identifies SDGs with coverage **30% below average**
   - These are flagged as priority funding areas

3. **Visualization**:
   - Interactive bar chart showing coverage for all 17 SDGs
   - Color-coded: Orange (`#E84A27`) for gaps, Navy (`#13294B`) for well-covered SDGs

---

## 📁 Data Sources & Processing

### Original Data

- **File**: `publications.csv` (in repository root)
- **Format**: One row per publication
- **Fields Used**:
  - `person_uuid` - Unique researcher identifier
  - `name` - Researcher name
  - `department` - Department affiliation
  - `email` - Contact email
  - `publication_year` - Year of publication
  - `keywords` - Semicolon-separated keywords
  - `abstract` or `abstract_text` - Publication abstract
  - `top 1`, `top 2`, `top 3` - SDG labels (1-17)
  - `is_sustain` - Boolean flag for sustainability focus

### Profile Construction (On-the-Fly)

For each unique researcher (`person_uuid`), the app aggregates their publications:

1. **Basic Metrics**:
   - `total_publications` - Count of all publications
   - `sustainable_publications` - Count where `is_sustain = true`
   - `first_publication_year` - Earliest publication year
   - `last_publication_year` - Most recent publication year
   - `years_active` - `last_year - first_year`

2. **Career Stage**: Calculated from `years_since_first` (see Career Score section)

3. **Primary SDG**: Most frequent SDG across all publications (from `top 1`, `top 2`, `top 3` columns)

4. **Primary Method**: Inferred from keywords/abstracts (see Method Score section)

5. **Keywords & Abstracts**: Combined for NLP matching
   - All keywords aggregated and joined
   - First 2000 characters of abstracts combined

### No Pre-processing

- **All analysis performed in real-time** from original CSV
- **No intermediate files** or pre-processed data
- **No simulation** - all matching uses only real data from original publications CSV

---

## ⚙️ Technical Implementation

### NLP Model

- **Library**: `sentence-transformers`
- **Model**: `all-MiniLM-L6-v2` (384-dimensional embeddings)
- **Caching**: Model loaded once and cached using `@st.cache_resource`
- **Batch Processing**: All candidate embeddings calculated in batch for performance

### Performance Optimizations

1. **Batch NLP Encoding**: All candidate texts encoded at once (much faster than one-by-one)
2. **Model Caching**: NLP model loaded once and reused across sessions
3. **Data Caching**: Researcher profiles cached using `@st.cache_data`
4. **Filtering**: SDG filtering allows related SDGs (same cluster) for broader matching

### File Loading

The app tries multiple paths to find `publications.csv`:
- Repository root: `../../publications.csv` (from `components/collab_hub/`)
- Streamlit Cloud: `/mount/src/sustainability_case_competition/publications.csv`
- Current directory fallbacks

---

## 🔍 Score Explanation Generation

### Contextual Explanations

The app generates explanations based on actual scores:

**Topic Score Explanations**:
- **85-100**: "Strong semantic alignment - high conceptual overlap based on NLP analysis"
- **70-84**: "Moderate semantic alignment - some research overlap"
- **50-69**: "Limited semantic alignment - minimal overlap, relies on method complementarity"
- **0-49**: "Low semantic alignment - topics are quite different"

**Method Score Explanations**:
- **90-100**: "Excellent method complementarity - powerful mixed-methods framework"
- **75-89**: "Good method complementarity - approaches complement each other well"
- **60-74**: "Moderate method alignment - enables collaborative work"
- **0-59**: "Limited method complementarity - similar methods limit innovation"

**Career Score Explanations**:
- **90-100**: "Excellent career pairing - strong mentorship opportunities"
- **75-89**: "Good career pairing - enables peer collaboration or cross-stage learning"
- **60-74**: "Moderate career pairing - some collaboration benefits"
- **0-59**: "Limited career alignment - may not offer strongest mentorship opportunities"

### How to Interpret Overall CCS Values

Because the CCS is built from real publication data and strict NLP similarity, we **do not expect most pairs to score in the 90–100 range**. In practice:
- Scores in the **60–75** range are **moderate but meaningful matches** – there is real topic overlap, useful method complementarity, and workable career fit.
- Scores in the **75–90+** range represent **very strong alignment** and are naturally rarer in real data.
- Scores below **60** usually indicate that the match is driven more by one dimension (for example, method or career) than by overall fit.

This scale is intentional: it reflects realistic collaboration potential rather than inflating every recommendation into a “perfect” match.

---

## 📊 Visual Components

### Gauge Chart

- **Purpose**: Visual representation of match quality
- **Range**: 0-100
- **Color Zones**:
  - 0-40: Light gray (low match)
  - 40-70: Medium blue (moderate match)
  - 70-100: Navy blue (strong match)
- **Bar Color**: Orange (`#E84A27`) matching main site theme

### Score Breakdown

- **Three-column layout**: Topic, Method, Career scores
- **Individual metrics**: Each with score and contextual explanation
- **Formula display**: Shows exact calculation with weights

---

## ⚠️ Limitations & Future Work

### Current Limitations

1. **Method Inference**: Simple keyword matching may miss nuance
2. **SDG Assignment**: Relies on provided labels (may be sparse)
3. **Career Stage**: Inferred from publication years only
4. **NLP Model**: Uses general-purpose model, not domain-specific
5. **Network Effects**: Existing collaborations not yet considered

### Future Improvements

- Validate scoring with faculty feedback and historical collaboration outcomes
- Improve method inference with richer NLP features
- Add uncertainty indicators for low-signal profiles
- Incorporate full abstracts (currently limited to 2000 characters)
- Enhance with domain-specific NLP models
- Consider network effects and existing collaboration patterns

---

**Note**: This document is the complete technical documentation for the Collaboration Hub. All methodology, limitations, judge Q&A, and technical details are consolidated here.

---

## Frequently Asked Questions

This section addresses common questions from judges specifically about the Collaboration Hub component.

### Is this AI? How accurate is it?

**Short Answer**: This is a **transparent, rule-based scoring system**, not a predictive AI model. We prioritized explainability so decision-makers can see exactly why a match is recommended.

**Detailed Explanation**:
- The NLP component uses semantic similarity to understand research topics, but the scoring logic is fully transparent and rule-based
- This is **not predictive AI** - we don't claim to predict collaboration success (which is impossible)
- Instead, we identify researchers with:
  - High semantic topic alignment (NLP analysis on actual keywords/abstracts)
  - Complementary methodological approaches (rule-based complementarity matrix)
  - Beneficial career stage pairings (rule-based mentorship logic)

**Accuracy**: Every score is explainable and can be validated by examining the underlying data. The system doesn't make predictions - it calculates compatibility based on transparent rules.

### Why is career fit only 15%?

**Based on Professor Fei's expert input and our analysis:**

**Topic alignment (45%)** and **methodological complementarity (40%)** drive research synergy most strongly. These factors determine whether two researchers can actually work together effectively.

**Career stage (15%)** matters for mentorship and collaboration dynamics, but should not dominate collaboration quality. A Pre-Tenure researcher working with a Post-Tenure researcher on aligned topics with complementary methods will have a strong collaboration regardless of career stage—the 15% weighting ensures mentorship opportunities are recognized without overshadowing research fit.

**Expert Validation**: Professor Fei confirmed that "research interest is the first priority" and that she seeks "complementary skill sets," validating our 85% focus on research quality (topic + method) over career stage.

**Rationale**: We prioritize semantic research alignment and methodological fit first (85%), but apply a 15% weighting to career stages to actively foster junior-faculty mentorship and cross-seniority knowledge transfer.

**See the "Weight Justification" section above for complete details on Professor Fei's interview and our reasoning process.**

### Where did the data come from?

All data comes from the **provided publications dataset** (`publications.csv`). No external scraping or data collection was performed. The dataset includes:
- Author names and departments
- Publication years
- Keywords and abstracts
- SDG labels (1-17)
- Sustainability flags

The Streamlit app uses **only real data** from this original CSV file. All researcher profiles and matches are built on-the-fly from actual publication records. No simulated or demo data is used.

### Is the data real?

**Yes, absolutely.** The Streamlit app uses only real data from the original publications CSV (`publications.csv`). All researcher profiles and matches are built on-the-fly from actual publication records. No simulated or demo data is used.

**How we ensure data authenticity**:
- The app loads the original CSV directly from the repository
- Builds researcher profiles by aggregating their actual publications
- Performs NLP analysis on real keywords and abstracts from publications
- Calculates compatibility scores using only real data

Everything is transparent and reproducible. You can verify this by examining the `app.py` code and the `publications.csv` file.

### How can we see who is paired?

In the Streamlit app:
1. Select your research preferences (SDG, method, career stage)
2. Click "Find My Best Collaborator"
3. View the **Top 3 matches** with:
   - Researcher name and department
   - Compatibility score (0-100)
   - Transparent score breakdown (Topic, Method, Career)
   - Natural language explanation of why the match works
   - Visual gauge chart showing match quality

Each match card shows the complete compatibility breakdown, making it easy to understand why each researcher was recommended. The app displays only the top matches to avoid information overload.

### What is new compared to the status quo?

**Existing dashboards** show counts and trends—they're descriptive and passive.

**The Collaboration Hub** is **prescriptive and proactive**:
- **Actionable recommendations**: Instead of showing "here's who exists," it says "here's who you should work with"
- **Complementarity focus**: Rewards different methods (innovation driver), not just similarity - this is our key innovation
- **Transparent scoring**: Every recommendation is explainable with detailed breakdowns
- **Real-time matching**: Uses NLP on actual research content, not pre-computed lists
- **Three stakeholder paths**: Faculty (collaborator matching), Students (opportunities), Donors (funding gaps)

This moves from "information access" to "insight generation."

### How does the NLP work?

The app uses `sentence-transformers` with the `all-MiniLM-L6-v2` model to:
1. **Encode** user research context (SDG + method) into a vector
2. **Encode** candidate researcher content (keywords + abstracts) into vectors
3. **Calculate cosine similarity** between vectors
4. **Scale** similarity to 0-100 for the Topic Score

**Why NLP?**
- Captures **semantic meaning** beyond exact keyword matches
- Example: "machine learning" and "artificial intelligence" are recognized as related even without exact keyword overlap
- All analysis performed on actual keywords and abstracts from `publications.csv`

**Transparency**: The NLP model is a standard, well-documented library (`sentence-transformers`). The similarity calculation is straightforward cosine similarity - no black box.

### Why reward complementary methods instead of similar methods?

**Innovation comes from combining different perspectives.** Two researchers using the same method (e.g., both doing surveys) can collaborate, but they're likely to approach problems similarly.

**Complementary methods** (e.g., Theoretical + Empirical) bring different strengths:
- Theoretical researcher provides frameworks and models
- Empirical researcher provides data and validation
- Together, they create a stronger, more innovative research approach

**Professor Fei's Validation**: She specifically mentioned seeking "complementary skill sets" - if she does theory, she looks for someone who does data. This directly informed our method complementarity approach.

This is the **key innovation** of the Collaboration Hub: actively seeking methodological diversity to drive interdisciplinary breakthroughs.

### How transparent is the scoring system?

**Very transparent.** Every aspect of the scoring is explainable:

1. **Topic Score (45%)**: NLP cosine similarity between user context and researcher content - you can see the actual keywords/abstracts used
2. **Method Score (40%)**: Rule-based complementarity matrix - you can see exactly which methods pair together and why
3. **Career Score (15%)**: Rule-based mentorship logic - you can see the career stage pairing rationale

**No black box**: There are no hidden algorithms or unexplained factors. Every score can be traced back to the original data and the explicit rules we've documented.

### Can the weights be adjusted?

Yes, the weights are configurable in the code. However, our current weights (45/40/15) are based on:
- Professor Fei's expert input
- Literature review on collaboration success factors
- Testing of alternative weight distributions

We found that 45/40/15 best balances research quality (topic + method) with strategic value (career stage mentorship). See the "Weight Justification" section for complete details.

### What are the limitations?

**Current Limitations**:
1. **Method Inference**: Simple keyword matching may miss nuanced method distinctions
2. **SDG Assignment**: Relies on provided labels (may be sparse for some researchers)
3. **Career Stage**: Inferred from publication years only (doesn't account for career breaks)
4. **NLP Model**: Uses general-purpose model, not domain-specific
5. **Network Effects**: Existing collaborations not yet considered

**See the "Limitations & Future Work" section above for detailed discussion.**

---

**Last Updated**: Based on `app.py` implementation as of latest commit

# CCS Demo Data Explanation
## What Data Was Used from Your Original CSV File

---

## 📊 **OVERVIEW**

The `CCS_Demo_Data.csv` file contains **simulated collaboration matches** for demonstration purposes in your Power BI presentation. It shows how the Collaboration Compatibility Score (CCS) algorithm would work when researchers search for potential collaborators.

---

## 🔄 **DATA FLOW: Original CSV → CCS Demo Data**

```
Original CSV (for distribution case competition filtered_publications.csv)
    ↓
[build_collab_hub_from_scratch.py]
    ↓
Researcher_Profiles_For_PowerBI.csv (aggregated researcher data)
    ↓
[generate_ccs_demo_data.py]
    ↓
CCS_Demo_Data.csv (simulated user searches + matches)
```

---

## 📁 **WHAT'S IN CCS_DEMO_DATA.CSV**

### **Structure:** 46 rows of collaboration matches

Each row represents:
- **A user** (researcher searching for collaborators)
- **A potential match** (another researcher)
- **Compatibility scores** (calculated)
- **Explanation** (generated text)

---

## ✅ **DATA FROM YOUR ORIGINAL CSV (USED DIRECTLY)**

### **1. Researcher Names**
**Source:** `name` column from original CSV  
**Used in CCS Demo:**
- `User_Name` - Name of researcher searching
- `Match_Name` - Name of matched researcher

**Example:**
- Original CSV: `"Ahsen, Mehmet"` appears in multiple publication rows
- Researcher_Profiles: Aggregated to one row per researcher
- CCS Demo: Used as `User_Name` or `Match_Name`

---

### **2. Department**
**Source:** `department` column from original CSV  
**Used in CCS Demo:**
- `User_Dept` - Department of searching researcher
- `Match_Dept` - Department of matched researcher

**Example:**
- Original CSV: `"Business Administration"` (repeated for each publication)
- Researcher_Profiles: `"Business Administration"` (one per researcher)
- CCS Demo: `"Business Administration"` in `User_Dept` or `Match_Dept`

---

### **3. Primary SDG (Sustainable Development Goal)**
**Source:** `top 1`, `top 2`, `top 3` columns from original CSV  
**How it was aggregated:**
- Collected all SDG values (top 1, top 2, top 3) across all publications per researcher
- Most frequent SDG = `primary_sdg`

**Used in CCS Demo:**
- `User_SDG` - SDG of searching researcher (70% uses actual `primary_sdg`, 30% varied for demo)
- `Match_SDG` - SDG of matched researcher (always uses actual `primary_sdg`)

**Example:**
- Original CSV: Multiple rows with `top 1 = 3.0`, `top 2 = 9.0`, `top 3 = 17.0`
- Researcher_Profiles: `primary_sdg = 3.0` (most common)
- CCS Demo: `User_SDG = 3` or `Match_SDG = 3`

---

### **4. Research Method**
**Source:** `keywords` and `abstract` columns from original CSV  
**How it was inferred:**
- Combined all keywords and abstracts for each researcher
- Scanned for method-related keywords (e.g., "machine learning", "statistical", "case study")
- Assigned method with highest keyword match count

**Used in CCS Demo:**
- `User_Method` - Method of searching researcher (60% uses actual `primary_method`, 40% varied for demo)
- `Match_Method` - Method of matched researcher (always uses actual `primary_method`)

**Example:**
- Original CSV: Keywords include "Machine Learning", "AI", "Deep Learning"
- Researcher_Profiles: `primary_method = "Computational"` (inferred)
- CCS Demo: `User_Method = "Computational"` or `Match_Method = "Computational"`

---

### **5. Career Stage**
**Source:** `publication_year` column from original CSV  
**How it was calculated:**
- Found `first_publication_year` (MIN of all publication years)
- Calculated `years_since_first = 2025 - first_publication_year`
- Assigned stage:
  - <7 years = "Pre-Tenure"
  - 7-15 years = "Post-Tenure"
  - >15 years = "Senior"

**Used in CCS Demo:**
- `User_Stage` - Always uses actual `career_stage` from Researcher_Profiles
- `Match_Stage` - Always uses actual `career_stage` from Researcher_Profiles

**Example:**
- Original CSV: Publication years: 2012, 2014, 2015, 2016, 2017, 2018, 2019, 2020
- Researcher_Profiles: `first_publication_year = 2012`, `years_since_first = 13`, `career_stage = "Post-Tenure"`
- CCS Demo: `User_Stage = "Post-Tenure"` or `Match_Stage = "Post-Tenure"`

---

### **6. Top Keywords**
**Source:** `keywords` column from original CSV  
**How it was aggregated:**
- Collected all keywords from all publications per researcher
- Counted frequency of each keyword
- Selected top 10 most frequent keywords

**Used in CCS Demo:**
- `Explanation` field - Uses first 2 keywords from matched researcher's `top_keywords`

**Example:**
- Original CSV: Keywords like "Cash Flow;Large Banks;Volatility;Hedging;..." (repeated across publications)
- Researcher_Profiles: `top_keywords = "Cash Flow;Large Banks;Volatility;Hedging;Industry;..."`
- CCS Demo: `Explanation = "Expertise in Cash Flow and Large Banks. ..."`

---

## 🧮 **CALCULATED FIELDS (NOT FROM ORIGINAL CSV)**

### **1. Topic_Match (70-95)**
**Calculation:** Based on SDG alignment
- **90-95:** Exact SDG match (`User_SDG == Match_SDG`)
- **85-90:** Related SDGs (same cluster: 1-6 Social, 7-12 Economic, 13-17 Environmental)
- **70-80:** Different SDG clusters

**Example:**
- User_SDG = 9, Match_SDG = 9 → Topic_Match = 92-95
- User_SDG = 9, Match_SDG = 8 (same cluster) → Topic_Match = 85-90
- User_SDG = 9, Match_SDG = 3 (different cluster) → Topic_Match = 70-80

---

### **2. Method_Match (70-95)**
**Calculation:** Based on method complementarity
- **85-95:** Complementary methods (Quantitative + Qualitative, e.g., Theoretical + Empirical)
- **70-80:** Same method or similar types

**Example:**
- User_Method = "Theoretical", Match_Method = "Empirical" → Method_Match = 85-95
- User_Method = "Theoretical", Match_Method = "Theoretical" → Method_Match = 70-80

---

### **3. Career_Fit (70-92)**
**Calculation:** Based on career stage pairing
- **85-92:** Mentorship opportunities (Pre-Tenure + Post-Tenure, Pre-Tenure + Senior)
- **75-82:** Peer collaboration (same stage, especially Post-Tenure)
- **70-80:** Other combinations

**Example:**
- User_Stage = "Pre-Tenure", Match_Stage = "Post-Tenure" → Career_Fit = 85-92
- User_Stage = "Post-Tenure", Match_Stage = "Post-Tenure" → Career_Fit = 75-82

---

### **4. CCS_Total (73-93)**
**Calculation:** Weighted sum
```
CCS_Total = ROUND((Topic_Match × 0.45) + (Method_Match × 0.40) + (Career_Fit × 0.15))
```

**Example:**
- Topic_Match = 95, Method_Match = 93, Career_Fit = 85
- CCS_Total = ROUND((95 × 0.45) + (93 × 0.40) + (85 × 0.15))
- CCS_Total = ROUND(42.75 + 37.2 + 12.75) = ROUND(92.7) = 93

---

### **5. Explanation (Text)**
**Generation:** Combines:
- First 2 keywords from matched researcher's `top_keywords`
- Method complementarity description
- Career pairing description

**Example:**
```
"Expertise in Gene Regulatory Network and Mixing Coefficient. 
Highly complementary methods (Empirical + Theoretical) create exceptional research synergy. 
Strong mentorship pairing: Post-Tenure and Post-Tenure researchers."
```

---

## 📋 **COLUMN-BY-COLUMN BREAKDOWN**

| Column | Source | Type | Notes |
|--------|--------|------|-------|
| **User_Name** | Original CSV `name` | ✅ Direct | Actual researcher name |
| **User_Dept** | Original CSV `department` | ✅ Direct | Actual department |
| **User_SDG** | Original CSV `top 1/2/3` → aggregated | ⚠️ Mixed | 70% actual, 30% varied for demo |
| **User_Method** | Original CSV `keywords` + `abstract` → inferred | ⚠️ Mixed | 60% actual, 40% varied for demo |
| **User_Stage** | Original CSV `publication_year` → calculated | ✅ Direct | Always uses actual career_stage |
| **Match_Name** | Original CSV `name` | ✅ Direct | Actual researcher name |
| **Match_Dept** | Original CSV `department` | ✅ Direct | Actual department |
| **Match_SDG** | Original CSV `top 1/2/3` → aggregated | ✅ Direct | Always uses actual primary_sdg |
| **Match_Method** | Original CSV `keywords` + `abstract` → inferred | ✅ Direct | Always uses actual primary_method |
| **Match_Stage** | Original CSV `publication_year` → calculated | ✅ Direct | Always uses actual career_stage |
| **Topic_Match** | 🧮 Calculated | Calculated | Based on SDG alignment |
| **Method_Match** | 🧮 Calculated | Calculated | Based on method complementarity |
| **Career_Fit** | 🧮 Calculated | Calculated | Based on career stage pairing |
| **CCS_Total** | 🧮 Calculated | Calculated | Weighted sum of above 3 scores |
| **Explanation** | Original CSV `keywords` + 🧮 Generated | Mixed | Uses keywords, generates text |

---

## 🎯 **KEY POINTS**

### **What's Real (From Your Original CSV):**
1. ✅ **All researcher names** - Actual faculty members
2. ✅ **All departments** - Actual departments
3. ✅ **All matched researcher data** (SDG, Method, Stage) - Derived from your data
4. ✅ **Top keywords in explanations** - From actual publications

### **What's Simulated (For Demo):**
1. ⚠️ **User_SDG** - 30% varied to show different search scenarios
2. ⚠️ **User_Method** - 40% varied to show different search scenarios
3. 🧮 **All scores** (Topic_Match, Method_Match, Career_Fit, CCS_Total) - Calculated using algorithm
4. 🧮 **Explanations** - Generated text using keywords + scores

### **Why This Approach?**
- **Shows variety:** Different users searching with different criteria
- **Demonstrates algorithm:** Shows how scores are calculated
- **Realistic:** Uses actual researcher data for matches
- **Presentation-ready:** Perfect for Power BI demo

---

## 📊 **EXAMPLE TRANSFORMATION**

### **Original CSV Data:**
```
Row 1: person_uuid=ABC, name="Ahsen, Mehmet", department="Business Administration", 
       publication_year=2019, keywords="Machine Learning;AI;...", top 1=3.0
Row 2: person_uuid=ABC, name="Ahsen, Mehmet", department="Business Administration",
       publication_year=2020, keywords="Machine Learning;AI;...", top 1=3.0
... (50 total publications for this researcher)
```

### **Researcher_Profiles_For_PowerBI.csv:**
```
name="Ahsen, Mehmet"
department="Business Administration"
total_publications=50
primary_sdg=3.0
primary_method="Theoretical" (inferred from keywords)
career_stage="Post-Tenure" (calculated: 2025-2012=13 years)
top_keywords="Gene Regulatory Network;Mixing Coefficient;Artificial Intelligence;..."
```

### **CCS_Demo_Data.csv:**
```
User_Name="Ahsen, Mehmet" (or Match_Name)
User_Dept="Business Administration" (or Match_Dept)
User_SDG=3 (or Match_SDG=3) - from primary_sdg
User_Method="Theoretical" (or Match_Method="Theoretical") - from primary_method
User_Stage="Post-Tenure" (or Match_Stage="Post-Tenure") - from career_stage
Topic_Match=93 (calculated: exact SDG match)
Method_Match=91 (calculated: complementary with Empirical)
Career_Fit=87 (calculated: Post-Tenure + Post-Tenure)
CCS_Total=91 (calculated: weighted sum)
Explanation="Expertise in Gene Regulatory Network and Mixing Coefficient. 
            Highly complementary methods (Empirical + Theoretical) create exceptional research synergy..."
```

---

## ✅ **SUMMARY**

**CCS_Demo_Data.csv uses:**
- ✅ **Real researcher names** from your original CSV
- ✅ **Real departments** from your original CSV
- ✅ **Real SDGs** (aggregated from `top 1/2/3` columns)
- ✅ **Real research methods** (inferred from `keywords` + `abstract`)
- ✅ **Real career stages** (calculated from `publication_year`)
- ✅ **Real keywords** (for explanations)

**CCS_Demo_Data.csv calculates:**
- 🧮 **Compatibility scores** (Topic_Match, Method_Match, Career_Fit, CCS_Total)
- 🧮 **Explanations** (generated text using real keywords)

**The demo shows:**
- How researchers would search for collaborators
- How the algorithm scores potential matches
- How different search criteria (SDG, Method) affect results
- Real collaboration opportunities based on your actual data!

---

This makes it perfect for your Power BI presentation - it demonstrates the algorithm using **real data from your university**! 🎯




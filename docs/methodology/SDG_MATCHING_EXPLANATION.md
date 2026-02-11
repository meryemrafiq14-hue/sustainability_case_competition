# How SDG Matching Works in the Collaboration Algorithm

## **Overview**

The `Topic_Match` score (which feeds into the CCS calculation at 45% weight) is based on how well two researchers' Sustainable Development Goal (SDG) alignments overlap. The algorithm uses a hierarchical matching system that checks multiple levels of SDG alignment.

---

## **Step 1: Building Each Researcher's SDG Profile**

For each researcher, the algorithm:

1. **Extracts SDGs from all publications:**
   - Looks at the `top 1`, `top 2`, and `top 3` columns for each publication
   - Collects all non-zero SDG values (SDGs range from 1-17)
   - Example: If a researcher has publications with SDGs [9, 9, 8, 9, 13], it collects all of them

2. **Determines Primary SDG:**
   - Finds the most frequently occurring SDG across all publications
   - Example: From [9, 9, 8, 9, 13], the primary SDG = 9 (appears 3 times)

3. **Creates SDG List:**
   - All unique SDGs the researcher has worked on
   - Example: From [9, 9, 8, 9, 13], the SDG list = [8, 9, 13]

**In your CSV:**
- `UserSDG` = Primary SDG (single integer, 1-17)
- `MatchSDG` = Primary SDG of the match
- The full SDG lists are stored internally but not shown in the CSV

---

## **Step 2: Matching Logic (Hierarchical)**

When comparing two researchers, the algorithm checks in this order:

### **Level 1: Identical Primary SDGs** → Score: 90-95
- **Condition:** `UserSDG == MatchSDG`
- **Example:** Both researchers have SDG 9 as their primary
- **Score:** `random.randint(90, 95)`
- **Why:** Strongest match - both focus on the same primary sustainability goal

### **Level 2: Primary SDG in Other's List** → Score: 85-89
- **Condition:** User's primary SDG appears in Match's SDG list, OR Match's primary SDG appears in User's SDG list
- **Example:** User's primary = 9, Match's SDG list = [8, 9, 13]
- **Score:** `random.randint(85, 89)`
- **Why:** One researcher's primary focus overlaps with the other's broader work

### **Level 3: Any SDG Overlap** → Score: 80-84
- **Condition:** Any SDG from User's list matches any SDG from Match's list
- **Example:** User's list = [8, 9], Match's list = [9, 13] → overlap on 9
- **Score:** `random.randint(80, 84)`
- **Why:** Shared interest in at least one sustainability area

### **Level 4: Adjacent SDGs** → Score: 75-79
- **Condition:** Primary SDGs are next to each other (e.g., 8 and 9, or 12 and 13)
- **Example:** User's primary = 8, Match's primary = 9
- **Score:** `random.randint(75, 79)`
- **Why:** Related sustainability goals often have overlapping themes

### **Level 5: Same SDG Category** → Score: 72-76
- **Condition:** Both primary SDGs are in the same thematic cluster:
  - **Environment Cluster:** SDGs 7, 11, 12, 13, 14, 15
  - **Social Cluster:** SDGs 1, 2, 3, 4, 5, 10, 16, 17
  - **Economic Cluster:** SDGs 8, 9
- **Example:** User's primary = 7 (Environment), Match's primary = 13 (Environment)
- **Score:** `random.randint(72, 76)`
- **Why:** Thematically related even if not identical

### **Level 6: Default (No Match)** → Score: 70-74
- **Condition:** None of the above conditions are met
- **Example:** User's primary = 1 (No Poverty), Match's primary = 15 (Life on Land)
- **Score:** `random.randint(70, 74)`
- **Why:** Still a potential match, but weaker topic alignment

---

## **Real Examples from Your CSV**

### **Example 1: Strong Match (SDG 9 = SDG 9)**
- **Carrasco Kind, Matias** (UserSDG: 9) → **Mendoza, Kim** (MatchSDG: 9)
- **Topic_Match: 92**
- **Logic:** Identical primary SDGs → Level 1 match → Score 90-95

### **Example 2: Good Match (SDG Overlap)**
- **Lough, Benjamin** (UserSDG: 17) → **Zhou, Dan** (MatchSDG: 16)
- **Topic_Match: 89**
- **Logic:** Likely Level 2 or 3 match (primary in other's list, or list overlap)

### **Example 3: Moderate Match (Same Category)**
- **Rios, Kimberly** (UserSDG: 10) → **Zhou, Dan** (MatchSDG: 16)
- **Topic_Match: 85**
- **Logic:** Both in Social Cluster (10 and 16) → Level 5 match → Score 72-76, but might have additional overlap

---

## **Why This Approach?**

1. **Captures Research Breadth:** Uses all SDGs a researcher has worked on, not just the primary
2. **Hierarchical Matching:** Stronger matches get higher scores, but all matches are considered
3. **Thematic Clustering:** Recognizes that related SDGs (like 8 and 9, or 12 and 13) often have synergies
4. **Realistic Scoring:** Uses random ranges to add natural variation (no two identical matches get exactly the same score)

---

## **How to See Full SDG Lists**

The full SDG lists for each researcher are stored in `Researcher_Profiles.csv` in the `sdg_list` column (comma-separated values).

**Example from Researcher_Profiles.csv:**
- Researcher: "Ahsen, Mehmet"
- `primary_sdg`: 3
- `sdg_list`: "3,5,7,9,10,17" (has worked on 6 different SDGs)

This means when matching, the algorithm checks if any of these 6 SDGs overlap with potential matches.

---

## **Key Points for Your Presentation**

1. **Data-Driven:** Uses actual SDG classifications from publications (top 1, top 2, top 3)
2. **Multi-Level Matching:** Not just "same SDG or different" - recognizes degrees of alignment
3. **45% Weight:** Topic alignment is the most important factor (as Professor Du specified)
4. **Transparent:** The matching logic is explainable and defensible

---

## **Visual Representation**

```
SDG Matching Hierarchy:
┌─────────────────────────────────────┐
│ Level 1: Identical Primary (90-95)  │ ← Strongest
├─────────────────────────────────────┤
│ Level 2: Primary in List (85-89)   │
├─────────────────────────────────────┤
│ Level 3: Any Overlap (80-84)       │
├─────────────────────────────────────┤
│ Level 4: Adjacent SDGs (75-79)     │
├─────────────────────────────────────┤
│ Level 5: Same Category (72-76)     │
├─────────────────────────────────────┤
│ Level 6: Default (70-74)           │ ← Weakest
└─────────────────────────────────────┘
```





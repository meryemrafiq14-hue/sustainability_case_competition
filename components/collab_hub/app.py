"""
Sustainability Research Discovery Hub
Streamlit web application for discovering cross-disciplinary research partners
using NLP semantic analysis and complementary method matching.
"""

import streamlit as st
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import os
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter

# Page configuration
st.set_page_config(
    page_title="Sustainability Research Discovery Hub",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark theme CSS to match main site
st.markdown("""
<style>
        /* Match main site dark theme */
        .stApp {
            background: linear-gradient(180deg, #0a1628 0%, #13294B 100%);
        }
        
        /* Card styling to match main site */
        .stContainer > div {
            background: #1e3a5f;
            border-radius: 12px;
            padding: 1.5rem;
        }
        
        /* Button styling - Enhanced */
        .stButton > button {
            background: linear-gradient(135deg, #E84A27 0%, #FF6B4A 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-weight: 600;
            padding: 0.75rem 2rem;
            transition: all 0.3s ease;
            box-shadow: 0 4px 8px rgba(232, 74, 39, 0.3);
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, #c43a1f 0%, #E84A27 100%);
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(232, 74, 39, 0.4);
        }
        
        /* Text colors */
        h1, h2, h3 {
            color: white !important;
        }
        
        p, .stMarkdown {
            color: #e0e0e0;
        }
        
        /* Improved form styling */
        .stSelectbox label, .stRadio label {
            color: #fff !important;
            font-weight: 600;
        }
        
        /* Better spacing */
        .main .block-container {
            padding-top: 3rem;
            padding-bottom: 3rem;
        }
    </style>
    """, unsafe_allow_html=True)

# Cache the model loading to avoid reloading on every interaction
@st.cache_resource
def load_nlp_model():
    """Load the sentence transformer model for semantic similarity"""
    return SentenceTransformer('all-MiniLM-L6-v2')

# Cache original publications data loading
@st.cache_data
@st.cache_data
def load_original_publications_from_path(csv_path):
    """Load the original publications CSV file from a specific path"""
    try:
        df = pd.read_csv(csv_path, low_memory=False)
        if df is None or len(df) == 0:
            return None
        return df
    except Exception as e:
        return None

@st.cache_data(show_spinner=False)
def load_original_publications():
    """Load the original publications CSV file - tries repository paths first"""
    try:
        # Get the directory where this script is located (works in both local and Streamlit Cloud)
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
        except:
            # Fallback if __file__ is not available
            script_dir = os.getcwd()
        
        repo_root = os.path.abspath(os.path.join(script_dir, '../..'))
        current_dir = os.getcwd()
        
        # Try multiple possible paths for the original CSV
        # Priority: Streamlit Cloud absolute paths, then repository root, then relative paths
        possible_paths = [
            # Streamlit Cloud absolute paths (most reliable for deployment)
            '/mount/src/sustainability_case_competition/publications.csv',
            # Repository root calculated from script location
            os.path.join(repo_root, 'publications.csv'),
            # Relative paths from script location
            os.path.join(script_dir, '../../publications.csv'),
            os.path.join(script_dir, '../publications.csv'),
            os.path.join(script_dir, 'publications.csv'),
            # Relative paths from current working directory
            os.path.join(current_dir, '../../publications.csv'),
            os.path.join(current_dir, '../publications.csv'),
            os.path.join(current_dir, 'publications.csv'),
            # Simple relative paths
            '../../publications.csv',
            '../publications.csv',
            'publications.csv',
        ]
        
        csv_path = None
        for path in possible_paths:
            try:
                # Normalize the path first
                normalized_path = os.path.normpath(path)
                # Try the path as-is
                if os.path.exists(normalized_path):
                    csv_path = normalized_path
                    break
                # Try absolute path
                abs_path = os.path.abspath(normalized_path)
                if os.path.exists(abs_path):
                    csv_path = abs_path
                    break
                # Try with realpath to resolve any symlinks
                real_path = os.path.realpath(normalized_path)
                if os.path.exists(real_path) and real_path != normalized_path:
                    csv_path = real_path
                    break
            except Exception:
                continue
        
        # If still not found, try listing files in the repo root to find it
        if csv_path is None:
            # Try to list files in repo root to see what's actually there
            try:
                for check_dir in ['/mount/src/sustainability_case_competition', repo_root, current_dir]:
                    try:
                        if os.path.exists(check_dir):
                            files = os.listdir(check_dir)
                            # Look for publications.csv specifically (case-insensitive)
                            for f in files:
                                if f.lower() == 'publications.csv':
                                    potential_path = os.path.join(check_dir, f)
                                    # Try to verify it's a file and readable
                                    if os.path.isfile(potential_path):
                                        csv_path = potential_path
                                        break
                            if csv_path:
                                break
                    except Exception as e:
                        continue
            except:
                pass
        
        if csv_path is None:
            return None, None
        
        df = pd.read_csv(csv_path, low_memory=False)
        if df is None or len(df) == 0:
            return None, None
        return df, csv_path
    except Exception as e:
        return None, None

# Cache researcher profile construction from original data
@st.cache_data
def build_researcher_profiles_from_original(publications_df):
    """Build researcher profiles from original publications CSV (no simulated data)"""
    if publications_df is None:
        return None
    
    # Clean data (same as build script)
    publications_df = publications_df.copy()
    publications_df['publication_year'] = pd.to_numeric(publications_df['publication_year'], errors='coerce')
    publications_df = publications_df[publications_df['publication_year'].between(1900, 2026)].copy()
    publications_df['is_sustain'] = pd.to_numeric(publications_df['is_sustain'], errors='coerce').fillna(0).astype(bool)
    
    # Clean SDG columns
    for col in ['top 1', 'top 2', 'top 3']:
        if col in publications_df.columns:
            publications_df[col] = pd.to_numeric(publications_df[col], errors='coerce')
            publications_df.loc[~publications_df[col].between(1, 17), col] = None
    
    def extract_keywords(keywords_str):
        """Extract keywords from semicolon-separated string"""
        if pd.isna(keywords_str):
            return []
        keywords = [k.strip() for k in str(keywords_str).split(';') if k.strip()]
        return keywords[:20]
    
    def get_sdg_list(row):
        """Get list of SDGs for a publication"""
        sdgs = []
        for col in ['top 1', 'top 2', 'top 3']:
            if pd.notna(row.get(col)) and 1 <= row[col] <= 17:
                sdgs.append(int(row[col]))
        return list(set(sdgs))
    
    # Aggregate by researcher (from original data)
    researcher_data = []
    for person_uuid in publications_df['person_uuid'].unique():
        person_df = publications_df[publications_df['person_uuid'] == person_uuid].copy()
        
        # Basic info from original CSV
        name = person_df['name'].iloc[0]
        email = person_df['email'].iloc[0] if pd.notna(person_df['email'].iloc[0]) else ""
        department = person_df['department'].iloc[0] if pd.notna(person_df['department'].iloc[0]) else "Unknown"
        
        # Publication metrics from original data
        total_pubs = len(person_df)
        sustainable_pubs = person_df['is_sustain'].sum()
        first_year = person_df['publication_year'].min()
        last_year = person_df['publication_year'].max()
        years_active = last_year - first_year if pd.notna(first_year) and pd.notna(last_year) else 0
        
        # Career stage (calculated from original data)
        current_year = 2025
        years_since_first = current_year - first_year if pd.notna(first_year) else 0
        if years_since_first > 15:
            career_stage = "Senior"
        elif years_since_first > 7:
            career_stage = "Post-Tenure"
        else:
            career_stage = "Pre-Tenure"
        
        # Aggregate keywords from original CSV
        all_keywords = []
        all_abstracts = []
        for _, row in person_df.iterrows():
            all_keywords.extend(extract_keywords(row.get('keywords', '')))
            if pd.notna(row.get('abstract', '')):
                all_abstracts.append(str(row.get('abstract', '')))
        
        keyword_counts = Counter(all_keywords)
        top_keywords = [kw for kw, _ in keyword_counts.most_common(15)]
        
        # Aggregate SDGs from original CSV
        all_sdgs = []
        for _, row in person_df.iterrows():
            all_sdgs.extend(get_sdg_list(row))
        sdg_counts = Counter(all_sdgs)
        primary_sdg = sdg_counts.most_common(1)[0][0] if sdg_counts else None
        sdg_list = [sdg for sdg, _ in sdg_counts.most_common(3)]
        
        # Infer research method from original keywords and abstracts
        method_keywords = {
            'Theoretical': ['theoretical', 'model', 'modeling', 'optimization', 'game theory', 
                           'mathematical', 'algorithm', 'framework', 'conceptual'],
            'Empirical': ['empirical', 'statistical', 'regression', 'analysis', 'data', 
                         'quantitative', 'econometric', 'estimation', 'dataset'],
            'Qualitative': ['qualitative', 'case study', 'interview', 'ethnography', 
                           'narrative', 'discourse', 'phenomenology'],
            'Fieldwork': ['field', 'survey', 'experiment', 'observational', 'fieldwork', 
                         'field study', 'field experiment'],
            'Experimental': ['experiment', 'randomized', 'trial', 'laboratory', 'lab', 
                            'controlled experiment', 'RCT'],
            'Computational': ['computational', 'simulation', 'machine learning', 'AI', 
                             'artificial intelligence', 'deep learning', 'neural network']
        }
        
        # Combine all text from original data
        all_text = ' '.join([str(kw).lower() for kw in top_keywords])
        if all_abstracts:
            abstracts_text = ' '.join([str(ab).lower() for ab in all_abstracts])
            all_text += ' ' + abstracts_text[:5000]  # First 5000 chars
        
        # Score each method based on original data
        method_scores = {}
        for method, keywords in method_keywords.items():
            score = sum(1 for kw in keywords if kw in all_text)
            method_scores[method] = score
        
        # Assign primary method
        if method_scores:
            primary_method = max(method_scores, key=method_scores.get)
            if method_scores[primary_method] == 0:
                primary_method = "Mixed Methods"
        else:
            primary_method = "Mixed Methods"
        
        researcher_data.append({
            'person_uuid': person_uuid,
            'name': name,
            'email': email,
            'department': department,
            'total_publications': total_pubs,
            'sustainable_publications': sustainable_pubs,
            'first_publication_year': first_year,
            'last_publication_year': last_year,
            'years_active': years_active,
            'years_since_first': years_since_first,
            'career_stage': career_stage,
            'primary_method': primary_method,
            'primary_sdg': primary_sdg,
            'sdg_list': ','.join(map(str, sdg_list)),
            'top_keywords': ';'.join(top_keywords[:10]),
            'all_keywords_text': ' '.join(top_keywords),  # For NLP matching
            'all_abstracts_text': ' '.join(all_abstracts)[:5000]  # For NLP matching
        })
    
    return pd.DataFrame(researcher_data)

# Combined function to get researcher profiles
@st.cache_data
def load_researcher_profiles():
    """Load and build researcher profiles from original publications CSV"""
    try:
        publications_df, csv_path = load_original_publications()
        if publications_df is None or csv_path is None:
            return None
        
        profiles_df = build_researcher_profiles_from_original(publications_df)
        if profiles_df is None or len(profiles_df) == 0:
            return None
        return profiles_df
    except Exception as e:
        # Return None and let the UI handle the error message
        return None

def get_researcher_profiles_with_fallback():
    """Get researcher profiles with file upload fallback - use this in UI code"""
    # Try loading from file system first
    df = load_researcher_profiles()
    
    # If not found, check for uploaded file in session state
    if df is None:
        if 'uploaded_publications_df' in st.session_state and st.session_state.uploaded_publications_df is not None:
            df = build_researcher_profiles_from_original(st.session_state.uploaded_publications_df)
    
    return df

# Initialize session state
if 'selected_path' not in st.session_state:
    st.session_state.selected_path = None
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False

# ============================================
# LANDING PAGE: "Join Us!" Section
# ============================================
if st.session_state.selected_path is None:
    # Header with Illinois Blue/Orange theme
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 style='color: #13294B; font-size: 3rem; margin-bottom: 0.5rem;'>Connect. Collaborate. Impact.</h1>
        <p style='color: #E84A27; font-size: 1.5rem; font-weight: bold;'>Sustainability Research Discovery Hub</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Value proposition
    st.markdown("""
    <div style='text-align: center; padding: 1rem 0;'>
        <p style='font-size: 1.2rem; color: #666; font-weight: 300;'>
            Moving beyond faculty directories. Discover cross-disciplinary partners, research opportunities, 
            and strategic funding priorities based on semantic overlap and complementary research methods.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Three CTAs - Improved Visual Design
    st.markdown("""
    <style>
        .path-card {
            background: linear-gradient(135deg, #1e3a5f 0%, #2a4a6f 100%);
            border-radius: 16px;
            padding: 2.5rem 2rem;
            text-align: center;
            height: 100%;
            min-height: 280px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
            border: 2px solid transparent;
            position: relative;
            overflow: hidden;
        }
        .path-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 24px rgba(0,0,0,0.3);
            border-color: #E84A27;
        }
        .path-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #E84A27, #FF6B4A);
        }
        .path-icon {
            font-size: 3.5rem;
            margin-bottom: 1rem;
            display: block;
        }
        .path-title {
            color: #fff;
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 0.75rem;
            line-height: 1.3;
        }
        .path-audience {
            color: #E84A27;
            font-size: 1rem;
            font-weight: 600;
            margin: 1rem 0;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .path-description {
            color: #e0e0e0;
            font-size: 0.95rem;
            line-height: 1.6;
            margin-top: 1rem;
        }
        .path-container {
            display: flex;
            gap: 1.5rem;
            margin: 2rem 0;
        }
        @media (max-width: 768px) {
            .path-container {
                flex-direction: column;
            }
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style='text-align: center; margin: 2rem 0;'>
        <h2 style='color: #13294B; font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;'>Choose Your Path</h2>
        <p style='color: #666; font-size: 1rem;'>Select the option that best describes your role</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3, gap="large")
    
    with col1:
        st.markdown("""
        <div class="path-card">
            <span class="path-icon">🔬</span>
            <div class="path-title">Find a Collaborator</div>
            <div class="path-audience">Faculty / Researchers</div>
            <div class="path-description">I have a project; who is the best co-author for me?</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Get Started →", key="faculty_path", use_container_width=True, type="primary"):
            st.session_state.selected_path = "faculty"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="path-card">
            <span class="path-icon">🎓</span>
            <div class="path-title">Find Opportunities</div>
            <div class="path-audience">Students / Junior Faculty</div>
            <div class="path-description">I have skills; what project needs me?</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Get Started →", key="student_path", use_container_width=True, type="primary"):
            st.session_state.selected_path = "student"
            st.rerun()
    
    with col3:
        st.markdown("""
        <div class="path-card">
            <span class="path-icon">💰</span>
            <div class="path-title">Sponsor a Priority</div>
            <div class="path-audience">Partners & Donors</div>
            <div class="path-description">I have resources; where can I invest to make the biggest impact?</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Get Started →", key="donor_path", use_container_width=True, type="primary"):
            st.session_state.selected_path = "donor"
            st.rerun()
    
    st.stop()

# ============================================
# PATH 1: FACULTY - Find a Collaborator (CCS)
# ============================================
if st.session_state.selected_path == "faculty":
    st.title("🔬 Find a Collaborator")
    st.markdown("**Faculty / Researchers**: Discover your best research partner using the Collaboration Compatibility Score (CCS)")
    
    # Back button
    if st.button("← Back to Home"):
        st.session_state.selected_path = None
        st.session_state.form_submitted = False
        st.rerun()
    
    st.markdown("---")
    
    # Load data from original CSV (from repository)
    df = get_researcher_profiles_with_fallback()
    
    # If still not found, show error with helpful message and debug info
    if df is None:
        st.error("❌ Original publications CSV file not found.")
        
        # Debug info (only show in development)
        with st.expander("🔍 Debug Information", expanded=False):
            try:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                repo_root = os.path.abspath(os.path.join(script_dir, '../..'))
                current_dir = os.getcwd()
                
                # List CSV files in repo root
                csv_files_found = []
                for check_dir in [repo_root, current_dir, '/mount/src/sustainability_case_competition']:
                    try:
                        if os.path.exists(check_dir):
                            files = os.listdir(check_dir)
                            csv_files = [f for f in files if f.endswith('.csv')]
                            if csv_files:
                                csv_files_found.extend([f"{check_dir}: {', '.join(csv_files[:5])}"])
                    except:
                        pass
                
                debug_info = f"""
Current working directory: {current_dir}
App file location: {__file__}
Script directory: {script_dir}
Repo root (calculated): {repo_root}
CSV files found in directories:
{chr(10).join(csv_files_found) if csv_files_found else 'No CSV files found in checked directories'}
                """
                st.code(debug_info)
            except Exception as e:
                st.code(f"Debug error: {str(e)}")
        
        st.info("""
        **The CSV file should be in the repository root directory:**
        - `publications.csv`
        - The file is included in the GitHub repository
        - On Streamlit Cloud, it should be at: `/mount/src/sustainability_case_competition/publications.csv`
        """)
        st.stop()
    
    # Wizard Questionnaire
    with st.form("faculty_form"):
        st.subheader("Tell Us About Your Research")
        
        # Question 1: Targeted SDG
        target_sdg = st.selectbox(
            "🎯 What SDG are you working on?",
            options=[i for i in range(1, 18)],
            format_func=lambda x: f"SDG {x}",
            help="Select the Sustainable Development Goal you're working on"
        )
        
        # Question 2: Target Department
        departments = ['Open to All'] + sorted(df['department'].dropna().unique().tolist())
        target_dept = st.selectbox(
            "🏛️ Preferred Department",
            options=departments,
            help="Filter by department or select 'Open to All'"
        )
        
        # Question 3: Primary Method
        methods = ['Theoretical', 'Empirical', 'Computational', 'Experimental', 'Qualitative', 'Fieldwork', 'Mixed Methods']
        user_method = st.selectbox(
            "🔬 Your Primary Method",
            options=methods,
            help="Select your primary research methodology"
        )
        
        # Question 4: Career Stage
        user_stage = st.radio(
            "👤 Your Career Stage",
            options=['Pre-Tenure', 'Post-Tenure', 'Senior'],
            help="Your current career stage"
        )
        
        submitted = st.form_submit_button("🔍 Find My Best Collaborator", use_container_width=True, type="primary")
    
    # Matching Engine
    if submitted:
        with st.spinner("Analyzing research profiles and calculating compatibility..."):
            # Filter dataset (less strict - allow related SDGs)
            filtered_df = df.copy()
            
            # Department filter
            if target_dept != 'Open to All':
                filtered_df = filtered_df[filtered_df['department'] == target_dept]
            
            # SDG filter - allow exact match OR related SDGs (same cluster)
            if 'primary_sdg' in filtered_df.columns and len(filtered_df) > 0:
                # Get SDG clusters: 1-6 (Social), 7-12 (Economic), 13-17 (Environmental)
                target_cluster = int((target_sdg - 1) // 6)
                
                def is_related_sdg(sdg):
                    if pd.isna(sdg):
                        return False
                    try:
                        sdg_int = int(float(sdg))
                        sdg_cluster = int((sdg_int - 1) // 6)
                        return sdg_int == target_sdg or sdg_cluster == target_cluster
                    except:
                        return False
                
                # Filter to exact match OR same cluster (broader matching)
                filtered_df = filtered_df[filtered_df['primary_sdg'].apply(is_related_sdg)]
            
            # If still no matches, remove SDG filter entirely
            if len(filtered_df) == 0:
                filtered_df = df.copy()
                if target_dept != 'Open to All':
                    filtered_df = filtered_df[filtered_df['department'] == target_dept]
                st.info("⚠️ No exact SDG matches found. Showing researchers from related SDG clusters or all departments.")
            
            if len(filtered_df) == 0:
                st.warning("No researchers found. Try selecting 'Open to All' for department.")
                st.stop()
            
            # Load NLP model
            model = load_nlp_model()
            
            # Prepare user profile for NLP matching
            user_context = f"Research in SDG {target_sdg} using {user_method} methodology"
            user_embedding = model.encode([user_context])  # Encode once, reuse for all candidates
            
            # Batch prepare candidate texts for faster NLP processing
            candidate_texts = []
            candidate_indices = []
            for idx, candidate in filtered_df.iterrows():
                candidate_keywords = candidate.get('all_keywords_text', '')
                candidate_abstracts = candidate.get('all_abstracts_text', '')
                
                if pd.isna(candidate_keywords) or candidate_keywords == '':
                    if pd.isna(candidate_abstracts) or candidate_abstracts == '':
                        candidate_text = ""  # Will handle separately
                    else:
                        candidate_text = str(candidate_abstracts)[:2000]
                else:
                    candidate_text = str(candidate_keywords)
                    if pd.notna(candidate_abstracts) and candidate_abstracts != '':
                        candidate_text += ' ' + str(candidate_abstracts)[:2000]
                
                candidate_texts.append(candidate_text)
                candidate_indices.append(idx)
            
            # Batch encode all candidates at once (much faster)
            non_empty_texts = [(i, t) for i, t in zip(candidate_indices, candidate_texts) if t]
            if non_empty_texts:
                indices_to_encode = [i for i, t in non_empty_texts]
                texts_to_encode = [t for i, t in non_empty_texts]
                candidate_embeddings = model.encode(texts_to_encode)
                
                # Calculate similarities in batch
                similarities = cosine_similarity(user_embedding, candidate_embeddings)[0]
                
                # Create mapping from index to similarity
                similarity_map = {idx: sim * 100 for idx, sim in zip(indices_to_encode, similarities)}
            else:
                similarity_map = {}
            
            # Calculate Topic Score using NLP (batch processed)
            def calculate_topic_score_nlp(candidate_idx):
                """Get pre-calculated similarity or default"""
                if candidate_idx in similarity_map:
                    return max(0, min(100, similarity_map[candidate_idx]))
                return 50  # Default if no text data
            
            # Method complementarity matrix
            def calculate_method_score(user_method, candidate_method):
                complementarity_matrix = {
                    ('Theoretical', 'Empirical'): 100,
                    ('Theoretical', 'Computational'): 100,
                    ('Theoretical', 'Experimental'): 90,
                    ('Theoretical', 'Fieldwork'): 100,
                    ('Empirical', 'Theoretical'): 100,
                    ('Empirical', 'Qualitative'): 85,
                    ('Empirical', 'Fieldwork'): 90,
                    ('Empirical', 'Computational'): 80,
                    ('Computational', 'Theoretical'): 100,
                    ('Computational', 'Fieldwork'): 85,
                    ('Computational', 'Qualitative'): 75,
                    ('Computational', 'Experimental'): 80,
                    ('Experimental', 'Theoretical'): 90,
                    ('Experimental', 'Qualitative'): 80,
                    ('Qualitative', 'Empirical'): 85,
                    ('Qualitative', 'Experimental'): 80,
                    ('Fieldwork', 'Theoretical'): 100,
                    ('Fieldwork', 'Computational'): 85,
                }
                
                if (user_method, candidate_method) in complementarity_matrix:
                    return complementarity_matrix[(user_method, candidate_method)]
                elif (candidate_method, user_method) in complementarity_matrix:
                    return complementarity_matrix[(candidate_method, user_method)]
                
                if user_method == candidate_method:
                    return 50
                return 60
            
            # Career score
            def calculate_career_score(user_stage, candidate_stage):
                optimal_pairs = [
                    ('Pre-Tenure', 'Post-Tenure'),
                    ('Pre-Tenure', 'Senior'),
                    ('Post-Tenure', 'Senior')
                ]
                
                if (user_stage, candidate_stage) in optimal_pairs or (candidate_stage, user_stage) in optimal_pairs:
                    return 100
                if user_stage == candidate_stage:
                    if user_stage == 'Post-Tenure':
                        return 75
                    return 60
                return 50
            
            # Calculate scores using original data (optimized)
            matches = []
            for idx, candidate in filtered_df.iterrows():
                # Use pre-calculated NLP similarity
                topic_score = calculate_topic_score_nlp(idx)
                candidate_method = candidate.get('primary_method', 'Mixed Methods')
                method_score = calculate_method_score(user_method, candidate_method)
                candidate_stage = candidate.get('career_stage', 'Post-Tenure')
                career_score = calculate_career_score(user_stage, candidate_stage)
                
                # CCS Formula: Topic (45%) + Method (40%) + Career (15%)
                total_score = (topic_score * 0.45) + (method_score * 0.40) + (career_score * 0.15)
                
                matches.append({
                    'name': candidate.get('name', 'Unknown'),
                    'department': candidate.get('department', 'Unknown'),
                    'total_score': total_score,
                    'topic_score': topic_score,
                    'method_score': method_score,
                    'career_score': career_score,
                    'method': candidate_method,
                    'stage': candidate_stage,
                    'keywords': candidate.get('top_keywords', ''),
                    'publications': candidate.get('total_publications', 0),
                    'email': candidate.get('email', ''),
                    'primary_sdg': candidate.get('primary_sdg', target_sdg)
                })
            
            matches_df = pd.DataFrame(matches)
            matches_df = matches_df.sort_values('total_score', ascending=False).head(3)
        
        # Display Results - Proactive Top Match
        st.markdown("---")
        st.markdown("## 🎯 Your Best Match")
        
        if len(matches_df) == 0:
            st.warning("No matches found. Try adjusting your criteria.")
        else:
            # Top match - prominently displayed
            top_match = matches_df.iloc[0]
            
            # Display top match with gauge
            col_score, col_gauge = st.columns([2, 1])
            
            with col_score:
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #13294B 0%, #E84A27 100%); padding: 2rem; border-radius: 10px; color: white; margin-bottom: 2rem;'>
                    <h2 style='color: white; margin-bottom: 0.5rem;'>{top_match['name']}</h2>
                    <h1 style='color: white; font-size: 4rem; margin: 0;'>{top_match['total_score']:.0f}/100</h1>
                    <p style='color: white; font-size: 1.2rem; margin-top: 0.5rem;'>Collaboration Compatibility Score</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col_gauge:
                # Create gauge chart
                score = top_match['total_score']
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=score,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Match Quality", 'font': {'size': 18, 'color': '#fff'}},
                    number={'font': {'size': 48, 'color': '#E84A27'}},
                    gauge={
                        'axis': {'range': [None, 100], 'tickcolor': '#fff'},
                        'bar': {'color': "#E84A27", 'thickness': 0.8},
                        'bgcolor': "#1e3a5f",
                        'borderwidth': 0,
                        'steps': [
                            {'range': [0, 40], 'color': "rgba(200,200,200,0.2)"},
                            {'range': [40, 70], 'color': "rgba(100,150,200,0.3)"},
                            {'range': [70, 100], 'color': "rgba(19,41,75,0.5)"}
                        ],
                    }
                ))
                fig.update_layout(
                    height=280,
                    margin=dict(l=10, r=10, t=50, b=10),
                    paper_bgcolor='rgba(0,0,0,0)',
                    font={'color': '#fff'}
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
            # Generate contextual explanations based on actual scores
            def generate_topic_explanation(topic_score, user_sdg, match_sdg, match_name):
                """Generate explanation based on actual topic score"""
                match_sdg_str = f"SDG {int(match_sdg)}" if pd.notna(match_sdg) and match_sdg != '' else "related areas"
                
                if topic_score >= 85:
                    return f"**Strong semantic alignment** (score: {topic_score:.0f}/100). Your research in SDG {user_sdg} and {match_name}'s work in {match_sdg_str} show high conceptual overlap based on NLP analysis of keywords and abstracts from the original publications."
                elif topic_score >= 70:
                    return f"**Moderate semantic alignment** (score: {topic_score:.0f}/100). There's some research overlap between SDG {user_sdg} and {match_name}'s focus in {match_sdg_str}, though the connection may be more indirect based on NLP similarity."
                elif topic_score >= 50:
                    return f"**Limited semantic alignment** (score: {topic_score:.0f}/100). The research topics show minimal overlap based on NLP analysis of keywords and abstracts. This match relies more on method complementarity than topic similarity."
                else:
                    return f"**Low semantic alignment** (score: {topic_score:.0f}/100). The research topics are quite different based on NLP analysis. This match is primarily based on complementary methods rather than topic overlap."
            
            def generate_method_explanation(method_score, user_method, match_method, match_name):
                """Generate explanation based on actual method score"""
                if method_score >= 90:
                    return f"**Excellent method complementarity** (score: {method_score:.0f}/100). Combining your {user_method} approach with {match_name}'s {match_method} methodology creates a powerful mixed-methods framework that brings different perspectives together."
                elif method_score >= 75:
                    return f"**Good method complementarity** (score: {method_score:.0f}/100). Your {user_method} and {match_name}'s {match_method} approaches complement each other well, enabling collaborative research."
                elif method_score >= 60:
                    return f"**Moderate method alignment** (score: {method_score:.0f}/100). Both using {user_method if user_method == match_method else 'similar'} methodologies enables collaborative work, though with less methodological diversity."
                else:
                    return f"**Limited method complementarity** (score: {method_score:.0f}/100). Both researchers use {user_method if user_method == match_method else 'similar methods'}, which may limit methodological innovation but enables shared understanding."
            
            def generate_career_explanation(career_score, user_stage, match_stage):
                """Generate explanation based on actual career score"""
                if career_score >= 90:
                    return f"**Excellent career pairing** (score: {career_score:.0f}/100). This {user_stage} + {match_stage} combination offers strong mentorship opportunities and knowledge transfer potential."
                elif career_score >= 75:
                    return f"**Good career pairing** (score: {career_score:.0f}/100). Both at {user_stage if user_stage == match_stage else 'different'} stages, this enables {('peer collaboration' if user_stage == match_stage else 'cross-stage learning')}."
                elif career_score >= 60:
                    return f"**Moderate career pairing** (score: {career_score:.0f}/100). The {user_stage} + {match_stage} combination provides some collaboration benefits, though not optimal for mentorship."
                else:
                    return f"**Limited career alignment** (score: {career_score:.0f}/100). The career stage pairing may not offer the strongest mentorship or peer collaboration opportunities."
            
            # Transparent AI Breakdown - Modal-like expander
            with st.expander("🔍 Why this score? (Click to see breakdown)", expanded=False):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Topic Match", f"{top_match['topic_score']:.0f}/100", 
                             help="NLP semantic similarity based on actual keywords and abstracts from original CSV")
                    st.markdown(generate_topic_explanation(top_match['topic_score'], target_sdg, top_match.get('primary_sdg', target_sdg), top_match['name']))
                
                with col2:
                    st.metric("Method Match", f"{top_match['method_score']:.0f}/100",
                             help="Complementarity of research methods")
                    st.markdown(generate_method_explanation(top_match['method_score'], user_method, top_match['method'], top_match['name']))
                
                with col3:
                    st.metric("Career Stage", f"{top_match['career_score']:.0f}/100",
                             help="Strategic career pairing for mentorship/collaboration")
                    st.markdown(generate_career_explanation(top_match['career_score'], user_stage, top_match['stage']))
                
                st.markdown("---")
                st.markdown(f"""
                **Formula**: CCS = (Topic × 45%) + (Method × 40%) + (Career × 15%)
                
                **Calculation**: ({top_match['topic_score']:.1f} × 0.45) + ({top_match['method_score']:.1f} × 0.40) + ({top_match['career_score']:.1f} × 0.15) = **{top_match['total_score']:.1f}**
                """)
            
            # Match details
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"**📧 Email**: {top_match['email']}")
                st.markdown(f"**🏛️ Department**: {top_match['department']}")
                st.markdown(f"**📊 Publications**: {int(top_match['publications'])}")
                st.markdown(f"**🔬 Method**: {top_match['method']}")
                st.markdown(f"**👤 Stage**: {top_match['stage']}")
            
            with col2:
                # Create Outlook Web App link with pre-filled subject and body
                researcher_email = top_match.get('email', '')
                researcher_name = top_match.get('name', 'Researcher')
                
                if researcher_email and researcher_email != '':
                    # Create email subject and body
                    subject = f"Research Collaboration Opportunity - {researcher_name}"
                    body = f"""Dear {researcher_name},

I came across your research profile through the Sustainability Research Discovery Hub and noticed our research interests align well. I'm working on SDG {target_sdg} using {user_method} methodology, and I believe there could be valuable collaboration opportunities between us.

I'd love to discuss potential collaboration. Would you be available for a brief conversation?

Best regards"""
                    
                    # URL encode the email components for Outlook Web App
                    import urllib.parse
                    to_param = urllib.parse.quote(researcher_email)
                    subject_param = urllib.parse.quote(subject)
                    body_param = urllib.parse.quote(body)
                    
                    # Outlook Web App compose URL
                    outlook_link = f"https://outlook.office.com/mail/deeplink/compose?to={to_param}&subject={subject_param}&body={body_param}"
                    
                    # Use markdown link that opens Outlook in a new tab
                    st.markdown(f"""
                    <a href="{outlook_link}" target="_blank" rel="noopener noreferrer" style="text-decoration: none; display: block;">
                        <button style="
                            background: linear-gradient(135deg, #E84A27 0%, #FF6B4A 100%);
                            color: white;
                            border: none;
                            border-radius: 10px;
                            padding: 0.75rem 1.5rem;
                            font-weight: 600;
                            font-size: 1rem;
                            width: 100%;
                            cursor: pointer;
                            transition: all 0.3s ease;
                            box-shadow: 0 4px 8px rgba(232, 74, 39, 0.3);
                        " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 12px rgba(232, 74, 39, 0.4)';" 
                           onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 8px rgba(232, 74, 39, 0.3)';">
                            📧 Contact This Researcher
                        </button>
                    </a>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("⚠️ Email not available for this researcher")
                    st.info("Please use the email address shown above to contact them directly.")
            
            # Other top matches
            if len(matches_df) > 1:
                st.markdown("---")
                st.markdown("## Other Strong Matches")
                for idx, match in matches_df.iloc[1:].iterrows():
                    with st.container():
                        col1, col2, col3 = st.columns([3, 1, 1])
                        with col1:
                            st.markdown(f"### {match['name']}")
                            st.caption(f"📧 {match['email']} | 🏛️ {match['department']}")
                        with col2:
                            st.metric("CCS Score", f"{match['total_score']:.1f}")
                        with col3:
                            if st.button("View Details", key=f"view_{idx}"):
                                st.info(f"Method: {match['method']} | Stage: {match['stage']}")
                        st.markdown("---")

# ============================================
# PATH 2: STUDENT - Find Opportunities
# ============================================
elif st.session_state.selected_path == "student":
    st.title("🎓 Find Opportunities")
    st.markdown("**Students / Junior Faculty**: Discover research projects that match your skills and interests")
    
    # Back button
    if st.button("← Back to Home"):
        st.session_state.selected_path = None
        st.rerun()
    
    st.markdown("---")
    
    # Load data
    # Load data from original CSV (from repository)
    df = get_researcher_profiles_with_fallback()
    
    # If still not found, show error
    if df is None:
        st.error("❌ Original publications CSV file not found.")
        st.info("The CSV file should be in the repository root directory.")
        st.stop()
    
    # Student questionnaire
    with st.form("student_form"):
        st.subheader("Tell Us About Your Skills")
        
        # Skills/SDG interest
        student_sdg = st.selectbox(
            "🎯 Which SDG interests you most?",
            options=[i for i in range(1, 18)],
            format_func=lambda x: f"SDG {x}",
        )
        
        student_skills = st.multiselect(
            "💼 Your Skills",
            options=['Data Analysis', 'Statistical Methods', 'Qualitative Research', 'Fieldwork', 
                    'Computational Modeling', 'Experimental Design', 'Literature Review', 'Writing'],
            help="Select all skills you have"
        )
        
        student_stage = st.radio(
            "👤 Your Level",
            options=['Undergraduate', 'Graduate Student', 'Doctoral Student', 'Post-Doc', 'Pre-Tenure Faculty'],
        )
        
        submitted = st.form_submit_button("🔍 Find Opportunities", use_container_width=True, type="primary")
    
    if submitted:
        # Calculate Opportunity Match Score for each researcher/project
        opportunities = []
        
        for idx, researcher in df.iterrows():
            # Simple matching: SDG alignment + method overlap
            sdg_match = 100 if researcher.get('primary_sdg') == student_sdg else 50
            
            # Method match (simplified)
            method_match = 75  # Default - could be enhanced
            
            # Career stage fit (students with post-tenure = mentorship opportunity)
            if student_stage in ['Undergraduate', 'Graduate Student', 'Doctoral Student']:
                if researcher.get('career_stage') in ['Post-Tenure', 'Senior']:
                    career_fit = 100
                else:
                    career_fit = 60
            else:
                career_fit = 75
            
            # Opportunity Match Score
            opp_score = (sdg_match * 0.5) + (method_match * 0.3) + (career_fit * 0.2)
            
            opportunities.append({
                'researcher': researcher.get('name', 'Unknown'),
                'department': researcher.get('department', 'Unknown'),
                'sdg': researcher.get('primary_sdg', 'Unknown'),
                'method': researcher.get('primary_method', 'Unknown'),
                'stage': researcher.get('career_stage', 'Unknown'),
                'opportunity_score': opp_score,
                'email': researcher.get('email', ''),
                'publications': researcher.get('total_publications', 0),
                'keywords': researcher.get('top_keywords', '')
            })
        
        opp_df = pd.DataFrame(opportunities)
        opp_df = opp_df.sort_values('opportunity_score', ascending=False).head(10)
        
        st.markdown("---")
        st.markdown("## 📋 Research Opportunity Board")
        st.caption("Projects ranked by Opportunity Match Score based on your skills and SDG interest")
        
        for idx, opp in opp_df.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"### {opp['researcher']}")
                    st.caption(f"🏛️ {opp['department']} | 🎯 SDG {opp['sdg']} | 🔬 {opp['method']}")
                    if pd.notna(opp['keywords']):
                        st.caption(f"**Research Focus**: {str(opp['keywords']).replace(';', ', ')[:100]}...")
                with col2:
                    st.metric("Match Score", f"{opp['opportunity_score']:.0f}/100")
                with col3:
                    if st.button("Apply", key=f"apply_{idx}"):
                        st.success(f"Application template ready for {opp['researcher']}!")
                st.markdown("---")

# ============================================
# PATH 3: DONOR - Sponsor a Priority
# ============================================
elif st.session_state.selected_path == "donor":
    st.title("💰 Sponsor a Priority")
    st.markdown("**Partners & Donors**: Discover where your investment can make the biggest impact")
    
    # Back button
    if st.button("← Back to Home"):
        st.session_state.selected_path = None
        st.rerun()
    
    st.markdown("---")
    
    # Load data
    # Load data from original CSV (from repository)
    df = get_researcher_profiles_with_fallback()
    
    # If still not found, show error
    if df is None:
        st.error("❌ Original publications CSV file not found.")
        st.info("The CSV file should be in the repository root directory.")
        st.stop()
    
    # Calculate SDG coverage
    if 'primary_sdg' in df.columns:
        sdg_counts = df['primary_sdg'].value_counts().sort_index()
        all_sdgs = pd.Series(range(1, 18), index=range(1, 18))
        sdg_coverage = all_sdgs.map(sdg_counts).fillna(0)
        
        # Identify gaps (low coverage)
        avg_coverage = sdg_coverage.mean()
        gaps = sdg_coverage[sdg_coverage < avg_coverage * 0.7]  # 30% below average
        
        st.markdown("## 📊 Research Coverage by SDG")
        st.caption("Interactive chart showing research coverage and funding gaps")
        
        # Create visualization
        fig = go.Figure()
        
        # Add coverage bars
        fig.add_trace(go.Bar(
            x=[f"SDG {i}" for i in range(1, 18)],
            y=sdg_coverage.values,
            name='Research Coverage',
            marker_color=['#E84A27' if i in gaps.index else '#13294B' for i in range(1, 18)],
            text=sdg_coverage.values.astype(int),
            textposition='outside'
        ))
        
        # Add average line
        fig.add_hline(y=avg_coverage, line_dash="dash", 
                     annotation_text=f"Average Coverage: {avg_coverage:.0f}",
                     line_color="gray")
        
        fig.update_layout(
            title="SDG Research Coverage & Funding Gaps",
            xaxis_title="Sustainable Development Goals",
            yaxis_title="Number of Researchers",
            height=500,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Priority funding areas
        st.markdown("---")
        st.markdown("## 🎯 Priority Funding Areas")
        st.caption("SDGs with below-average research coverage - your investment is most needed here")
        
        if len(gaps) > 0:
            priority_df = pd.DataFrame({
                'SDG': [f"SDG {i}" for i in gaps.index],
                'Current Coverage': gaps.values.astype(int),
                'Gap Size': (avg_coverage - gaps.values).astype(int),
                'Priority Level': ['High' if gap < avg_coverage * 0.5 else 'Medium' for gap in gaps.values]
            })
            priority_df = priority_df.sort_values('Gap Size', ascending=False)
            
            st.dataframe(priority_df, use_container_width=True, hide_index=True)
            
            st.info("""
            💡 **Strategic Investment Opportunity**: Funding research in these under-researched SDGs 
            will have maximum impact by filling critical knowledge gaps and enabling breakthrough discoveries.
            """)
        else:
            st.success("All SDGs have strong research coverage. Consider funding emerging or interdisciplinary research.")
        
        # Top researchers by SDG (for donor reference)
        st.markdown("---")
        st.markdown("## 👥 Leading Researchers by SDG")
        
        selected_sdg = st.selectbox(
            "Select an SDG to see leading researchers",
            options=[i for i in range(1, 18)],
            format_func=lambda x: f"SDG {x}",
        )
        
        sdg_researchers = df[df['primary_sdg'] == selected_sdg].nlargest(5, 'total_publications')
        
        if len(sdg_researchers) > 0:
            for idx, researcher in sdg_researchers.iterrows():
                st.markdown(f"**{researcher.get('name', 'Unknown')}** - {researcher.get('department', 'Unknown')} ({int(researcher.get('total_publications', 0))} publications)")
        
        # Contact section for sustainability/funding inquiries
        st.markdown("---")
        st.markdown("## 📧 Get in Touch")
        st.markdown("**Ready to make an impact? Contact our sustainability team to discuss funding opportunities:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div style='background: #1e3a5f; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #E84A27;'>
                <h3 style='color: #E84A27; margin-top: 0;'>Sustainability Office</h3>
                <p style='color: #e0e0e0; margin-bottom: 0.5rem;'><strong>Email:</strong> sustainability@illinois.edu</p>
                <p style='color: #e0e0e0; margin-bottom: 0.5rem;'><strong>Phone:</strong> (217) 333-0000</p>
                <p style='color: #e0e0e0; margin-bottom: 0;'><strong>Focus:</strong> Strategic funding and sustainability initiatives</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Contact button for sustainability office
            import urllib.parse
            sustainability_email = "sustainability@illinois.edu"
            subject = "Funding Inquiry - Sustainability Research"
            body = """Dear Sustainability Office,

I'm interested in discussing funding opportunities for sustainability research at the University of Illinois. I've reviewed the research coverage analysis and would like to learn more about how I can support priority areas.

Thank you for your time.

Best regards"""
            
            to_param = urllib.parse.quote(sustainability_email)
            subject_param = urllib.parse.quote(subject)
            body_param = urllib.parse.quote(body)
            outlook_link = f"https://outlook.office.com/mail/deeplink/compose?to={to_param}&subject={subject_param}&body={body_param}"
            
            st.markdown(f"""
            <a href="{outlook_link}" target="_blank" rel="noopener noreferrer" style="text-decoration: none; display: block; margin-top: 1rem;">
                <button style="
                    background: linear-gradient(135deg, #E84A27 0%, #FF6B4A 100%);
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 0.75rem 1.5rem;
                    font-weight: 600;
                    font-size: 1rem;
                    width: 100%;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    box-shadow: 0 4px 8px rgba(232, 74, 39, 0.3);
                " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 12px rgba(232, 74, 39, 0.4)';" 
                   onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 8px rgba(232, 74, 39, 0.3)';">
                    📧 Contact Sustainability Office
                </button>
            </a>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style='background: #1e3a5f; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #13294B;'>
                <h3 style='color: #13294B; margin-top: 0;'>Research Development Office</h3>
                <p style='color: #e0e0e0; margin-bottom: 0.5rem;'><strong>Email:</strong> research@illinois.edu</p>
                <p style='color: #e0e0e0; margin-bottom: 0.5rem;'><strong>Phone:</strong> (217) 333-0001</p>
                <p style='color: #e0e0e0; margin-bottom: 0;'><strong>Focus:</strong> Research partnerships and grants</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Contact button for research office
            research_email = "research@illinois.edu"
            subject_research = "Research Partnership Inquiry"
            body_research = """Dear Research Development Office,

I'm interested in establishing a research partnership or funding opportunity with the University of Illinois. I've reviewed the sustainability research landscape and would like to discuss potential collaborations.

Thank you for your time.

Best regards"""
            
            to_param_research = urllib.parse.quote(research_email)
            subject_param_research = urllib.parse.quote(subject_research)
            body_param_research = urllib.parse.quote(body_research)
            outlook_link_research = f"https://outlook.office.com/mail/deeplink/compose?to={to_param_research}&subject={subject_param_research}&body={body_param_research}"
            
            st.markdown(f"""
            <a href="{outlook_link_research}" target="_blank" rel="noopener noreferrer" style="text-decoration: none; display: block; margin-top: 1rem;">
                <button style="
                    background: linear-gradient(135deg, #13294B 0%, #1e3a5f 100%);
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 0.75rem 1.5rem;
                    font-weight: 600;
                    font-size: 1rem;
                    width: 100%;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    box-shadow: 0 4px 8px rgba(19, 41, 75, 0.3);
                " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 12px rgba(19, 41, 75, 0.4)';" 
                   onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 8px rgba(19, 41, 75, 0.3)';">
                    📧 Contact Research Office
                </button>
            </a>
            """, unsafe_allow_html=True)
        
        st.info("""
        💡 **Next Steps**: Use the contact buttons above to reach out directly, or review the priority funding areas 
        to identify specific SDGs where your investment will have the greatest impact.
        """)


# Footer
st.markdown("---")
st.caption("Sustainability Research Discovery Hub | Part of the Illinois Sustainability Impact Engine")

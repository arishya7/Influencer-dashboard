import streamlit as st
import pandas as pd
import requests
from api_client import fetch_influencers, login_user

st.set_page_config(page_title="Influencer Dashboard", layout="wide")

#LOGIN PART
def show_login():
    
    st.markdown("""
        <style>
        /* Remove all Streamlit headers / toolbars / margins */
        header, [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"] {
            display: none !important;
        }

        /* Make the whole viewport a flexbox container */
        [data-testid="stAppViewContainer"] {
            background-color: #0f1116 !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            height: 100vh !important;
            padding: 0 !important;
            margin: 0 !important;
        }

        /* Force all parent containers to take full height */
        section[data-testid="stAppViewBlockContainer"],
        main,
        [data-testid="block-container"] {
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            flex-direction: column !important;
            height: 100% !important;
            width: 100% !important;
            padding: 0 !important;
            margin: 0 auto !important;
        }

        /* Centered login card */
        .login-card {
            background-color: #1b1f2a;
            padding: 40px 35px;
            border-radius: 16px;
            box-shadow: 0px 6px 18px rgba(0,0,0,0.6);
            text-align: center;
            width: 350px;
        }
        /* Constrain input container width */
        .stTextInput {
            max-width: 100% !important;
        }
        
        .stTextInput > div > div > input {
            background-color: #2a2f3c !important;
            color: white !important;
            border-radius: 6px;
            border: none;
            padding: 0.6rem 1rem !important;
            width: 100% !important;
            max-width: 100% !important;
        }

        /* Title and subtitle */
        .login-title {
            font-size: 1.8rem;
            font-weight: 700;
            color: white;
            margin-bottom: 8px;
            text-align: center;
        }
        .login-subtitle {
            font-size: 0.9rem;
            color: #ccc;
            margin-bottom: 20px;
            text-align: center;
        }

        /* Inputs */
        .stTextInput > div > div > input {
            background-color: #2a2f3c !important;
            color: white !important;
            border-radius: 6px;
            border: none;
            padding: 0.6rem 1rem !important;
        }

        /* Button */
        .stButton > button {
            background-color: #C990B8 !important;
            color: white !important;
            border: none;
            border-radius: 25px;
            font-weight: 600;
            padding: 0.6rem 2rem;
            transition: all 0.2s ease;
        }
        .stButton > button:hover {
            transform: scale(1.03);
        }
        </style>
        """, unsafe_allow_html=True)

    
    # Remove the opening div tag and just use markdown for titles
    st.markdown('<div class="login-title">👩‍💻Influencer Dashboard Login</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-subtitle">Please enter your credentials to continue</div>', unsafe_allow_html=True)

    username = st.text_input("Username", placeholder="Enter username", key="login_username", label_visibility="collapsed")
    password = st.text_input("Password", placeholder="Enter password", key="login_password", type="password", label_visibility="collapsed")

    if st.button("Login", use_container_width=True):
        token = login_user(username, password)
        if token:
            st.session_state["access_token"] = token
            st.session_state["username"] = username
            st.rerun()
        else:
            st.error("Invalid username or password")

    st.stop()

if "access_token" not in st.session_state:
    show_login()

st.markdown("<style>section[data-testid='stSidebar'] {display: block;}</style>", unsafe_allow_html=True)

st.markdown(f"""
<div style='text-align:right; color:white;'>
👤 {st.session_state.get("username", "")}
</div>
""", unsafe_allow_html=True)


#ACTUAL DASHBOARD PAGE
#styles 
st.markdown('<div class="main-title">📁 Influencer Dashboard </div>', unsafe_allow_html=True)
st.markdown("""<style>
/* --- your CSS styles unchanged --- */
.stApp { background-color: #13192A; color: #FFFFFF; }
.main-title { text-align:center; font-size:2rem; font-weight:800; color:#fff; background-color:#1E2335; padding:12px 20px; border-radius:10px; margin-bottom:25px; }
section[data-testid="stSidebar"] { background-color:#1B2236 !important; color:white; }
.card { background-color:#1E2335; border:1px solid #4964C5; border-radius:12px; padding:16px; margin-bottom:20px; box-shadow:0px 4px 12px rgba(0,0,0,0.4);}
</style>""", unsafe_allow_html=True)


#primary category
PRIMARY_CATEGORIES = [
    "Parenting + Lifestyle",
    "General Audience Brands",
    "Parenting + Beauty & Fashion",
    "Core Parenting & Family",
    "Parenting + Travel",
    "Mompreneurs / Dadpreneurs",
    "Family-Focused Brands & Services",
    "Parenting + Food",
    "Parenting + Health & Wellness"
]

SECONDARY_CATEGORIES = [
    "Lifestyle Mom / Dad",
    "General Business",
    "Mom Style / Beauty",
    "Mom / Dad Blogger",
    "Home & Living Family Blogger",
    "Family Travel Blogger",
    "Parenting Expert",
    "Professional Services",
    "Baby / Kids’ Products",
    "Family Food Blogger",
    "Founder / Entrepreneur",
    "Family Fitness & Health",
    "General Lifestyle / Brand",
    "Baby / Kids' Products",
    "Family Vlog / Activities"
]

#filters 
with st.sidebar:
    st.title("🔍 Filters")
    DEFAULT_FILTERS = {
    "platform_filter": [],
    "country_filter": [],
    "primary_filter": [],
    "secondary_filter": [],
    "tier_filter": "All",
    "influencer_filter": False,
    "followers_filter": 0,
    "child_age_filter": 0,
    "child_num_filter": 0
}

    for k, v in DEFAULT_FILTERS.items():
        st.session_state.setdefault(k, v)


    if st.button("🔄 Reset Filters"):
        st.session_state.update(DEFAULT_FILTERS)
        st.toast("✨ Filters cleared!")
        st.rerun()

    platform = st.multiselect("Platform", ["Tiktok", "Rednote", "Instagram"],key="platform_filter")
    country = st.multiselect("Country", ["Singapore", "China", "Malaysia", "United States", "Others"],key="country_filter")
    primary_category = st.multiselect(
    "Category",
    list(PRIMARY_CATEGORIES),key="primary_filter")

    secondary_category = st.multiselect(
    "Sub-Category",
    list(SECONDARY_CATEGORIES),key="secondary_filter")
    tier = st.selectbox("Follower Tier", ["All", "Seeder", "Nano", "Micro", "Macro", "Celebrity"],key="tier_filter")
    is_influencer = st.checkbox("Is Influencer", value=False,key="influencer_filter")
    followers = st.number_input("Min Followers", min_value=0, value=0, step=100,key="followers_filter")
    child_age = st.number_input("Min Child Age", min_value=0, value=0, step=1,key="child_age_filter")
    child_num = st.number_input("Min Number of Children", min_value=0, value=0, step=1,key="child_num_filter")

    if st.button("Logout"):
        st.session_state.clear()
        st.toast("👋 Logged out successfully!")
        st.rerun()



    
SAVE_FILE = "saved_profiles.csv"


def save_profile(profile):
    try:
        df = pd.read_csv(SAVE_FILE)
    except FileNotFoundError:
        df = pd.DataFrame(columns=profile.keys())

    if profile["username"] not in df["username"].values:
        df.loc[len(df)] = profile
        df.to_csv(SAVE_FILE, index=False)
        st.success(f"Saved {profile['username']}!")
    else:
        st.info(f"ℹ {profile['username']} already saved.")


tab1, tab2 = st.tabs(["📊 Influencer Analytics", "📋 Saved Profiles"])


PAGE_SIZE = 50
if "page" not in st.session_state:
    st.session_state.page = 1
if "last_filters" not in st.session_state:
    st.session_state.last_filters = None

filter_key = (
    tuple(platform), tuple(country), tuple(primary_category), tuple(secondary_category),
    tier, is_influencer, followers, child_age, child_num
)
if st.session_state.last_filters != filter_key:
    st.session_state.page = 1
    st.session_state.last_filters = filter_key

# Prepare parameters for API call
from urllib.parse import quote



params = []

# --- Platform ---
if platform:
    for p in platform:
        params.append(("platform", p))

# --- Country ---
if country:
    for c in country:
        params.append(("country", c))

# --- Primary Category ---
if primary_category:
    for c in primary_category:
        params.append(("primary_category", c))

# --- Secondary Category ---
if secondary_category:
    for c in secondary_category:
        params.append(("secondary_category", c))


# --- Other filters ---
if tier and tier != "All":
    params.append(("tier", tier))

if is_influencer:
    params.append(("is_brand", "Influencer"))
if followers > 0:
    params.append(("followers_min", str(followers)))
if child_age > 0:
    params.append(("age_children_min", str(child_age)))
if child_num > 0:
    params.append(("num_children_min", str(child_num)))

# --- Pagination ---
offset = (st.session_state.page - 1) * PAGE_SIZE
params.append(("limit", str(PAGE_SIZE)))
params.append(("skip", str(offset)))



#TAB1 - INFLUENCER PROFILES
with tab1:
    st.markdown("### Influencer Profiles")


    data = fetch_influencers(params)
 

    if not data.empty:
        # Add Save column (unchecked by default)
        data["Save"] = False

        if "total_results" in st.session_state:
            total = st.session_state.total_results
            current_start = (st.session_state.page - 1) * PAGE_SIZE + 1
            current_end = min(total, current_start + len(data) - 1)
            st.markdown(f"**Showing {current_start}-{current_end} of {total} results**")

        # Use editable data table
        edited_data = st.data_editor(
            data,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Save": st.column_config.CheckboxColumn("Save", help="Tick to save this profile")
            },
            key=f"page_{st.session_state.page}"
        )

        # Get selected (checked) rows
        saved_rows = edited_data[edited_data["Save"] == True]

        if not saved_rows.empty:
            st.success(f"{len(saved_rows)} profile(s) marked for saving.")
            try:
                existing = pd.read_csv(SAVE_FILE)
            except FileNotFoundError:
                existing = pd.DataFrame(columns=data.columns)

            combined = pd.concat([existing, saved_rows]).drop_duplicates(subset=["username"], keep="last")
            combined.to_csv(SAVE_FILE, index=False)

        # Pagination buttons
        st.markdown("<br>", unsafe_allow_html=True)
        total = st.session_state.get("total_results", len(data))
        col1, col2, col3 = st.columns([2, 3, 2])

        with col1:
            st.empty()  # left padding

        with col2:
            # Center the entire group
            st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
            prev, mid, nxt = st.columns([3, 3, 3])
            with prev:
                if st.button("⏪ Previous", disabled=(st.session_state.page == 1)):
                    st.session_state.page = max(1, st.session_state.page - 1)
                    st.rerun()
            with mid:
                st.write(f"**Page Number {st.session_state.page}**")
            with nxt:
                last_page_count = (total+ PAGE_SIZE - 1) // PAGE_SIZE 
                if st.button("Next ⏩️", disabled=(st.session_state.page >= last_page_count)):
                    st.session_state.page += 1
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        with col3:
            st.empty()  

    else:
        st.info("No influencers found with the selected filters.")

# TAB 2 - SAVED PROFILES
with tab2:
    st.markdown("### Saved Profiles")
    try:
        saved_df = pd.read_csv(SAVE_FILE)
        
        # Add Remove column (unchecked by default)
        saved_df["Remove"] = False
        
        st.success(f"Total saved profiles: {len(saved_df)}")
        
        # Use editable data table
        edited_saved = st.data_editor(
            saved_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Remove": st.column_config.CheckboxColumn("Remove", help="Tick to remove this profile")
            },
            key="saved_profiles_editor"
        )
        
        # Get rows marked for removal
        rows_to_remove = edited_saved[edited_saved["Remove"] == True]
        
        if not rows_to_remove.empty:
            st.warning(f"{len(rows_to_remove)} profile(s) marked for removal.")
            if st.button("Confirm Removal"):
                # Keep only rows NOT marked for removal
                remaining = edited_saved[edited_saved["Remove"] == False].drop(columns=["Remove"])
                remaining.to_csv(SAVE_FILE, index=False)
                st.success(f"Removed {len(rows_to_remove)} profile(s)!")
                st.rerun()
        
        # Download button
        csv = saved_df.drop(columns=["Remove"]).to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name='saved_profiles.csv',
            mime='text/csv',
        )
    except FileNotFoundError:
        st.info("No saved profiles yet.")
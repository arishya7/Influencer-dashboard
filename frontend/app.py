import streamlit as st
import pandas as pd
import requests
from api_client import fetch_influencers, login_user, add_influencer_column, add_influencer_row, update_creator, save_added_columns, export_influencers_csv, update_mentions

st.set_page_config(page_title="Influencer Dashboard", layout="wide")


# Pre-initialize all widget keys that appear anywhere in the UI.

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

    if st.button("Login", key = "login_button", use_container_width=True):
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

# ---- Global reload handler ----
if st.session_state.get("trigger_reload", False):
    st.session_state.trigger_reload = False
    st.rerun()

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
    if k not in st.session_state:
        st.session_state[k] = v



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
    "Baby / Kids' Products",
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
    

    for k, v in DEFAULT_FILTERS.items():
        st.session_state.setdefault(k, v)


    if st.button("🔄 Reset Filters"):
        for k, v in DEFAULT_FILTERS.items():
            st.session_state[k] = v
        st.rerun()


    show_all = st.sidebar.checkbox("Show All Profiles", value=False)

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

def safe_int(value):
    """Convert to int, but handle None, '', NaN safely."""
    try:
        if value is None:
            return None
        if isinstance(value, float) and pd.isna(value):
            return None
        if value == "":
            return None
        return int(value)
    except:
        return None


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

if show_all:
    params = [p for p in params if p[0] not in ("limit", "skip")]
    params.append(("limit", str(10000)))
    params.append(("skip", "0"))
else:
    offset = (st.session_state.page - 1) * PAGE_SIZE
    params.append(("limit", str(PAGE_SIZE)))
    params.append(("skip", str(offset)))

if "custom_columns" not in st.session_state:
    st.session_state.custom_columns = []

if "added_rows" not in st.session_state:
    st.session_state.added_rows = {}   # keyed by page number

import ast

def safe_parse_list(value):
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            parsed = ast.literal_eval(value)
            if isinstance(parsed, list):
                return parsed
        except:
            return []
    return []


#TAB1 - INFLUENCER PROFILES
with tab1:
    st.markdown("### Influencer Profiles")

    # Fetch data outside fragment (only once per page load)
    data = fetch_influencers(params)

    if not data.empty:
        if "total_results" in st.session_state:
            total = st.session_state.total_results
            current_start = (st.session_state.page - 1) * PAGE_SIZE + 1
            current_end = min(total, current_start + len(data) - 1)
            st.markdown(f"**Showing {current_start}-{current_end} of {total} results**")

        # Prepare data
        data_display = data.copy()

        # Add custom columns FIRST (before Save column)
        for col in st.session_state.custom_columns:
            if col not in data_display.columns:
                data_display[col] = ""

        # Then add Save column
        if "Save" not in data_display.columns:
            data_display["Save"] = False

        data_display["Save"] = data_display["Save"].fillna(False).astype(bool)

        # Append any added rows for the current page
        page_rows = st.session_state.added_rows.get(st.session_state.page, [])
        if page_rows:
            # Make sure added rows have all columns
            for row in page_rows:
                for col in st.session_state.custom_columns:
                    if col not in row:
                        row[col] = ""
            extra_df = pd.DataFrame(page_rows)
            data_display = pd.concat([data_display, extra_df], ignore_index=True)

        edited_data = st.data_editor(
            data_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Save": st.column_config.CheckboxColumn("Save", help="Tick to save this profile")
            },
            key=f"page_{st.session_state.page}_editor"
        )

        # Sync edited new rows back into session state
        if st.session_state.added_rows.get(st.session_state.page):
            num_added = len(st.session_state.added_rows[st.session_state.page])
            edited_new_rows = edited_data.tail(num_added).to_dict('records')
            st.session_state.added_rows[st.session_state.page] = edited_new_rows

        # Get selected (checked) rows
        saved_rows = edited_data[edited_data["Save"] == True]

        if not saved_rows.empty:
            st.success(f"{len(saved_rows)} profile(s) marked for saving.")
            try:
                existing = pd.read_csv(SAVE_FILE)
            except FileNotFoundError:
                existing = pd.DataFrame(columns=data_display.columns)

            combined = pd.concat([existing, saved_rows]).drop_duplicates(subset=["username"], keep="last")
            combined.to_csv(SAVE_FILE, index=False)

        # Add rows/columns buttons
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2= st.columns([2,2])
        with col1:
            new_col_name = st.text_input("New Column", placeholder="Enter column name", key="new_col_input")
        with col2:
            st.write("")  # spacer
            st.write("")  # spacer
            co1, co2, co3= st.columns([1,1,1])
            with co1:
                if st.button("Add Column"):
                    if new_col_name.strip():
                        response = add_influencer_column(new_col_name.strip())
                        if response and response.get("status") == "success":
                            st.session_state.custom_columns.append(new_col_name.strip())
                            st.success(f"Added column: {new_col_name}")
                            st.rerun()
                        else:
                            st.warning("Failed to add column.")
            with co2:
                if st.button("Add Row"):
                    page = st.session_state.page
                    if page not in st.session_state.added_rows:
                        st.session_state.added_rows[page] = []
                    empty = {
                    "name": "",
                    "username": "",
                    "source": "",
                    "followers": 0,
                    "uniqueid": "",
                    "heart": 0,
                    "verified": 0,
                    "country": "",
                    "primary_category": "",
                    "secondary_category": "",
                    "email": "",
                    "tier": "",
                    "is_brand": 0,
                    "contact": "",
                    "bio": "",
                    "profile_url": "",
                    "age_children": None,
                    "num_children": None,
                    "Save": False
                }
                    st.session_state.added_rows[page].append(empty)
                    st.success("Added empty row! Fill it out and click 'Save New Rows'")
                    st.rerun()


            # --- Save New Rows to Database ---
            if st.session_state.added_rows.get(st.session_state.page):
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("💾 Save New Rows to Database", use_container_width=True):

                    page_rows = st.session_state.added_rows[st.session_state.page]
                    success_count = 0
                    errors = []

                    for idx, row in enumerate(page_rows):
                            row_data = {
                                "name": str(row.get("name") or ""),
                                "username": str(row.get("username") or ""),
                                "source": str(row.get("source", "")),
                                "followers": int(row.get("followers", 0)),
                                "uniqueid": str(row.get("uniqueid", "")),
                                "heart": int(row.get("heart", 0)),
                                "verified": int(row.get("verified", 0)),
                                "country": str(row.get("country", "")),
                                "primary_category": str(row.get("primary_category", "")),
                                "secondary_category": str(row.get("secondary_category", "")),
                                "email": str(row.get("email", "")),
                                "tier": str(row.get("tier", "")),
                                "is_brand": int(row.get("is_brand", 0)),
                                "contact": str(row.get("contact", "")),
                                "bio": str(row.get("bio", "")),
                                "profile_url": str(row.get("profile_url", "")),
                                "age_children": safe_int(row.get("age_children")),
                                "num_children": safe_int(row.get("num_children")),
                                "save": False
                            }

                            # Send to backend
                            response = add_influencer_row(row_data)

                            if response and response.get("status") == "success":
                                success_count += 1
                            else:
                                errors.append(f"Row {idx+1}: Backend rejected the row.")

                    # Results
                    if success_count > 0:
                        st.success(f"Saved {success_count} new row(s) to database!")
                        st.session_state.added_rows[st.session_state.page] = []
                        # Full page rerun to fetch fresh data from backend
                        st.rerun()

                    for error in errors:
                        st.warning(error)

            with co3:
                if st.button("Save All Changes"):
                    errors = []
                    updated_count = 0
                    extra_json_updates = []
                    mentions_updates = []
                    changes_detected = False

                    fixed_cols = {
                        "creator_id", "uniqueid", "name", "username", "source", "followers",
                        "heart", "verified", "country", "primary_category", "secondary_category",
                        "email", "tier", "is_brand", "contact", "bio", "profile_url",
                        "age_children", "num_children", "mentions", "Save"
                    }

                    # Build a mapping from creator_id to ORIGINAL row
                    original_map = {}
                    for _, row in data_display.iterrows():
                        cid = row.get("creator_id")
                        if not pd.isna(cid):
                            original_map[int(cid)] = row

                    # Process each edited row
                    for _, row in edited_data.iterrows():

                        cid = row.get("creator_id")
                        if pd.isna(cid):
                            continue  # Skip new rows

                        cid = int(cid)

                        if cid not in original_map:
                            continue

                        original_row = original_map[cid]

                        # Track if this row was edited
                        row_edited = False

                        # ---- FIXED FIELDS (normal DB fields) ----
                        update_payload = {}

                        for field in [
                            "name", "username", "source", "followers", "uniqueid",
                            "heart", "verified", "country", "primary_category",
                            "secondary_category", "email", "tier", "is_brand",
                            "contact", "bio", "profile_url", "age_children",
                            "num_children"
                        ]:
                            old = original_row.get(field)
                            new = row.get(field)

                            # Handle NaN comparison safely
                            if pd.isna(old) and pd.isna(new):
                                continue

                            if old != new:
                                update_payload[field] = new
                                row_edited = True
                                changes_detected = True

                        # Send update if needed
                        if update_payload:
                            resp = update_creator(cid, update_payload)
                            if not resp or resp.get("status") != "success":
                                errors.append(f"Creator {cid}: Failed to update fixed fields")
                            else:
                                updated_count += 1

                        # ---- DYNAMIC FIELDS (added columns) ----
                        dynamic_fields = {}

                        for col in edited_data.columns:
                            if col in fixed_cols:
                                continue

                            old = original_row.get(col) if col in original_row else ""
                            new = row.get(col)

                            # Normalize empty values for comparison
                            old_val = "" if pd.isna(old) else old
                            new_val = "" if pd.isna(new) else new

                            if old_val != new_val:
                                dynamic_fields[col] = new
                                row_edited = True
                                changes_detected = True

                        if dynamic_fields:
                            extra_json_updates.append({
                                "creator_id": cid,
                                **dynamic_fields
                            })

                        # ---- MENTIONS (special case) ----
                        if "mentions" in row:
                            new_mentions = safe_parse_list(row.get("mentions"))
                            old_mentions = safe_parse_list(original_row.get("mentions"))

                            if new_mentions != old_mentions:
                                mentions_updates.append((cid, new_mentions))
                                row_edited = True
                                changes_detected = True

                    # --- Save dynamic JSON updates ---
                    if extra_json_updates:
                        resp2 = save_added_columns(extra_json_updates)
                        if not resp2 or resp2.get("status") != "success":
                            errors.append("Failed to save dynamic columns")

                    # --- Save mentions updates ---
                    for cid, mlist in mentions_updates:
                        resp_m = update_mentions(cid, mlist)
                        if not resp_m or resp_m.get("status") != "success":
                            errors.append(f"Creator {cid}: Failed to update mentions")

                    # --- Final user messages ---
                    if errors:
                        for e in errors:
                            st.warning(e)

                    if not changes_detected:
                        st.info("ℹ️ No changes detected.")
                    else:
                        st.success("✅ All changes saved successfully!")
                        st.rerun()


                
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

        


with tab2:
    st.markdown("### Saved Profiles")

    # Hide download button only for Tab 2's data editor
    st.markdown("""
    <script>
    // Wait for page to load, then hide toolbar in this tab only
    setTimeout(function() {
        // Get the current tab panel (Tab 2)
        const tabPanels = document.querySelectorAll('[role="tabpanel"]');
        const tab2Panel = tabPanels[1]; // Tab 2 is the second panel

        if (tab2Panel) {
            // Hide all toolbars within Tab 2 only
            const toolbars = tab2Panel.querySelectorAll('[data-testid="stElementToolbar"]');
            toolbars.forEach(toolbar => {
                toolbar.style.display = 'none';
                toolbar.style.visibility = 'hidden';
            });
        }
    }, 500);
    </script>
    <style>
    /* Fallback CSS - hide toolbar buttons when Tab 2 is active */
    [data-baseweb="tab-panel"]:nth-child(2) [data-testid="stElementToolbar"],
    [data-baseweb="tab-panel"]:nth-child(2) button[kind="elementToolbar"],
    [data-baseweb="tab-panel"]:nth-child(2) button[aria-label="Download as CSV"] {
        display: none !important;
        visibility: hidden !important;
    }
    </style>
    """, unsafe_allow_html=True)

    try:
        if "saved_df" not in st.session_state:
            df = pd.read_csv(SAVE_FILE)
            if "Save" not in df.columns:
                df["Save"] = True
            st.session_state.saved_df = df

        saved_df = st.session_state.saved_df.copy()

        st.info("Uncheck Save to remove a profile. Then press Save Changes.")

        edited_saved = st.data_editor(
            saved_df,
            use_container_width=True,
            hide_index=True,
            key="saved_profiles_editor",
            disabled=False
        )

        c1, c2, c3 = st.columns([1, 1, 2])

        with c1:
            if st.button("💾 Save Changes"):
                cleaned = edited_saved[edited_saved["Save"] == True].copy()
                cleaned.to_csv(SAVE_FILE, index=False)
                st.session_state.saved_df = cleaned
                st.success("Saved! Unchecked rows removed.")
                st.rerun()

        with c2:
            allowed_user = "user1"
            if st.session_state.get("username") == allowed_user:
                if st.button("⬇️ Download CSV"):
                    backend_csv = export_influencers_csv(allowed_user)
                    if backend_csv:
                        st.download_button(
                            label="Download Export",
                            data=backend_csv,
                            file_name="export.csv",
                            mime="text/csv"
                        )
                    else:
                        st.error("Not authorised.")

        with c3:
            st.empty()

    except FileNotFoundError:
        st.info("No saved profiles yet. Tick Save in Tab 1 to add profiles.")

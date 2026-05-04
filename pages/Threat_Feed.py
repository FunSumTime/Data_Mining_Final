import streamlit as st
import pandas as pd
import sqlite3
import streamlit_authenticator as stauth

# --- 1. Database Helper Functions ---
def get_user_credentials():
    """Pulls all users from SQLite and formats them for the authenticator."""
    conn = sqlite3.connect('database/users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username, name, email, password_hash FROM users")
    users = cursor.fetchall()
    conn.close()
    
    credentials = {"usernames": {}}
    for user in users:
        username, name, email, password_hash = user
        credentials["usernames"][username] = {
            "name": name,
            "email": email,
            "password": password_hash
        }
    return credentials

def get_tracked_software(username):
    """Pulls the custom list of tracked software for the logged-in user."""
    conn = sqlite3.connect('database/users.db')
    df = pd.read_sql_query("SELECT software_name FROM tracked_software WHERE username = ?", conn, params=(username,))
    conn.close()
    return df['software_name'].tolist()

def add_tracked_software(username, software_name):
    """Inserts a new software into the user's tracking list."""
    conn = sqlite3.connect('database/users.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO tracked_software (username, software_name) VALUES (?, ?)", (username, software_name))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False # They were already tracking it
    finally:
        conn.close()

# --- 2. Load the CVE Data ---
@st.cache_data
def load_cve_data():
    try:
        return pd.read_csv("database/processed_cves.csv")
    except FileNotFoundError:
        return pd.DataFrame()

df = load_cve_data()

# --- 3. Authentication ---
credentials = get_user_credentials()

authenticator = stauth.Authenticate(
    credentials=credentials,
    cookie_name="nvd_dashboard_cookie",
    key="some_random_secret_string", # Change this in production
    cookie_expiry_days=30
)

# Render the login widget
authenticator.login()

# --- 4. The Secure Dashboard ---
if st.session_state["authentication_status"]:
    # Get the username of whoever just logged in
    current_user = st.session_state["username"]
    
    authenticator.logout('Logout', 'sidebar')
    st.sidebar.write(f'Welcome *{st.session_state["name"]}*')

    st.title("🛡️ Threat Intelligence Feed")
    
    if df.empty:
        st.warning("No CVE data found. Please run the Analytics Pull pipeline first.")
        st.stop()

    # -- Feature: Search & Track --
    st.subheader("Add to Tracking List")
    all_software = df['affected_technology'].dropna().unique().tolist()
    search_term = st.selectbox("Select software to monitor:", all_software)
    
    if st.button(f"Track {search_term}"):
        success = add_tracked_software(current_user, search_term)
        if success:
            st.success(f"Added {search_term} to your tracking list!")
            st.rerun() # Refresh the page to update their feed instantly
        else:
            st.info(f"You are already tracking {search_term}.")

    st.divider()

  # -- Feature: The Custom Feeds --
    user_tracked_list = get_tracked_software(current_user)
    
    # Let's build a custom search bar to filter the global feed!
    st.divider()
    search_query = st.text_input("🔍 Search the Global Alert Feed for specific keywords (e.g., 'buffer', 'bypass'):", "")

    col1, col2 = st.columns([1, 1]) # Keep them equal width
    
    with col1:
        st.subheader("📌 Your Tracked Stack")
        if user_tracked_list:
            tracked_feed = df[df['affected_technology'].isin(user_tracked_list)]
            
            if tracked_feed.empty:
                st.info("No current vulnerabilities found for your tracked software.")
            else:
                # Replace the Excel sheet with clicking sliding expanders
                for index, row in tracked_feed.iterrows():
                    # The title of the sliding bar
                    with st.expander(f"🔴 {row['affected_technology']} - {row['cve_id']}"):
                        st.markdown(f"**Severity:** `{row['official_severity']}`")
                        st.markdown(f"**Published:** {row['published_date']}")
                        st.markdown(f"**Requires Patch:** {'Yes 🛑' if row['requires_patch'] else 'No 🟢'}")
                        st.markdown("**Summary:**")
                        st.info(row['plain_english_summary'])
        else:
            st.info("You aren't tracking any software yet.")
            
    with col2:
        st.subheader("⚠️ Global Alerts Feed")
        
        # Apply our custom search filter to the data before we display it!
        global_feed = df.copy()
        if search_query:
            # Filters the dataframe if the search word is in the summary or the tech name
            global_feed = global_feed[
                global_feed['plain_english_summary'].str.contains(search_query, case=False, na=False) |
                global_feed['affected_technology'].str.contains(search_query, case=False, na=False)
            ]

        if global_feed.empty:
            st.success("No alerts match your search.")
        else:
            # Build the sliding bars for the global feed
            for index, row in global_feed.iterrows():
                with st.expander(f"⚠️ {row['cve_id']} ({row['affected_technology']})"):
                    st.markdown(f"**Severity:** `{row['official_severity']}`")
                    st.markdown(f"**Requires Patch:** {'Yes 🛑' if row['requires_patch'] else 'No 🟢'}")
                    st.markdown("**Summary:**")
                    st.warning(row['plain_english_summary'])

elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password to view the Threat Feed.')
import streamlit as st
import pandas as pd
import database as db
import time

# --- Page Configuration ---
st.set_page_config(
    page_title="Cricket Auction Scout",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS (Sport-Blue & Gold) ---
def apply_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Oswald:wght@400;600&family=Roboto:wght@300;400;700&display=swap');
        
        :root {
            --primary-color: #1E88E5; /* Sport Blue */
            --accent-color: #FFD700; /* Gold */
            --bg-dark: #0f1116;
            --card-bg: #1e212b;
            --text-white: #ffffff;
        }

        .stApp {
            background-color: var(--bg-dark);
            font-family: 'Roboto', sans-serif;
        }

        h1, h2, h3 {
            font-family: 'Oswald', sans-serif;
            color: var(--text-white);
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        h1 {
            color: var(--accent-color);
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 20px;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: var(--card-bg);
            border-radius: 5px;
            color: #b0b0b0;
            padding: 10px 20px;
        }
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background-color: var(--primary-color);
            color: white;
            border: 1px solid var(--accent-color);
        }

        /* Metric Cards */
        div[data-testid="stMetricValue"] {
            font-family: 'Oswald', sans-serif;
            color: var(--accent-color) !important;
        }
        
        /* Buttons */
        div.stButton > button {
            background: linear-gradient(135deg, var(--primary-color) 0%, #1565C0 100%);
            color: white;
            border: 1px solid var(--accent-color);
            font-weight: bold;
            text-transform: uppercase;
            padding: 0.6rem 1.2rem;
            transition: 0.3s;
        }
        div.stButton > button:hover {
            box-shadow: 0 0 15px rgba(255, 215, 0, 0.4);
            transform: scale(1.02);
            color: var(--accent-color);
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #13151c;
            border-right: 1px solid #333;
        }
        
        /* DataFrame */
        .stDataFrame {
            border: 1px solid #333;
        }
        </style>
    """, unsafe_allow_html=True)

# --- Helper Functions ---
def init_app_state():
    if 'db_initialized' not in st.session_state:
        db.init_db()
        st.session_state['db_initialized'] = True

# --- Main App ---
def main():
    apply_custom_css()
    init_app_state()

    st.title("🏆 PRO Cricket Auction Dashboard")
    st.markdown("**Scouting | Analytics | Simulation**")
    
    # --- Tabs ---
    tab1, tab2, tab3 = st.tabs(["🔍 Player Discovery", "📊 Analytics Hub", "🛠️ Admin & Import"])

    # ==========================
    # TAB 1: PLAYER DISCOVERY
    # ==========================
    with tab1:
        st.header("Player Scout Registry")
        
        # Filters in Expander (Main area to save Sidebar for Global controls or clean look)
        with st.expander("🔎 Advanced Filters", expanded=True):
            col_f1, col_f2, col_f3, col_f4 = st.columns(4)
            
            with col_f1:
                search_text = st.text_input("Search Name")
            with col_f2:
                role_opts = ["Batsman", "Bowler", "All-rounder", "Wicketkeeper"]
                roles = st.multiselect("Role", role_opts)
            with col_f3:
                nat_opts = ["India", "Australia", "England", "South Africa", "New Zealand", "West Indies", "Pakistan", "Afghanistan", "Sri Lanka"]
                nationalities = st.multiselect("Nationality", nat_opts)
            with col_f4:
                min_price, max_price = st.slider("Base Price (Lakhs)", 20, 200, (20, 200), step=10)
        
        # Fetch Data
        filters = {
            'search': search_text,
            'role': roles,
            'nationality': nationalities,
            'price_min': min_price,
            'price_max': max_price
        }
        df = db.fetch_players(filters)

        # Display Data
        if not df.empty:
            st.dataframe(
                df,
                use_container_width=True,
                column_config={
                    "name": "Player",
                    "nationality": "Nation",
                    "role": st.column_config.TextColumn("Role", help="Playing Role"),
                    "base_price": st.column_config.NumberColumn("Base (L)", format="₹%d L"),
                    "final_price": st.column_config.NumberColumn("Sold For", format="₹%d L"),
                    "skill_rating": st.column_config.ProgressColumn("Rating", min_value=1, max_value=10, format="%d/10"),
                    "auction_status": st.column_config.SelectboxColumn("Status", options=["Available", "Sold", "Unsold"], disabled=True),
                    "strike_rate": st.column_config.NumberColumn("SR", format="%.2f"),
                    "economy_rate": st.column_config.NumberColumn("Econ", format="%.2f"),
                    "id": None
                },
                hide_index=True,
                height=500
            )
            st.caption(f"Showing {len(df)} players")
        else:
            st.warning("No players found matching criteria.")

    # ==========================
    # TAB 2: ANALYTICS
    # ==========================
    with tab2:
        st.header("Auction Analytics")
        
        stats = db.get_stats()
        
        # Top Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Players", stats.get('total_players', 0))
        m2.metric("Avg Base Price", f"₹{stats.get('avg_price', 0):.1f} L")
        m3.metric("Highest Rating", f"{stats.get('max_rating', 'N/A')}/10")
        
        # Charts
        st.divider()
        col_c1, col_c2 = st.columns(2)
        
        with col_c1:
            st.subheader("Role Distribution")
            role_data = stats.get('role_dist', pd.DataFrame())
            if not role_data.empty:
                st.bar_chart(role_data.set_index('role'))
            else:
                st.info("No data for charts")

        with col_c2:
            st.subheader("Price vs Rating Scatter")
            # Fetch raw data for scatter
            all_df = db.fetch_players()
            if not all_df.empty:
                # Simple scatter using st.scatter_chart (new in recent Streamlit) or generic chart
                st.scatter_chart(all_df, x='skill_rating', y='base_price', color='role')
    
    # ==========================
    # TAB 3: ADMIN & IMPORT
    # ==========================
    with tab3:
        st.header("Admin Control Panel")
        
        col_admin1, col_admin2 = st.columns([1, 1], gap="large")
        
        # Manual Entry
        with col_admin1:
            st.subheader("📝 Manual Entry")
            with st.form("manual_add"):
                name = st.text_input("Name")
                nat = st.selectbox("Nationality", ["India", "Australia", "England", "South Africa", "New Zealand", "West Indies", "Other"])
                role = st.selectbox("Role", ["Batsman", "Bowler", "All-rounder", "Wicketkeeper"])
                age = st.number_input("Age", 18, 45, 25)
                
                c1, c2 = st.columns(2)
                matches = c1.number_input("Matches", 0, 500, 0)
                rating = c2.slider("Rating", 1, 10, 5)
                
                c3, c4 = st.columns(2)
                sr = c3.number_input("Strike Rate", 0.0, 300.0, 100.0)
                econ = c4.number_input("Economy", 0.0, 15.0, 8.0)
                
                base = st.number_input("Base Price (Lakhs)", 20, 200, 20, step=10)
                
                if st.form_submit_button("Add Player"):
                    player_data = {
                        "name": name, "nationality": nat, "role": role, "age": age,
                        "matches_played": matches, "strike_rate": sr, "economy_rate": econ,
                        "base_price": base, "skill_rating": rating
                    }
                    db.add_player(player_data)
                    st.success(f"Added {name}!")

        # Import & Simulate
        with col_admin2:
            st.subheader("📂 Bulk Import")
            uploaded_file = st.file_uploader("Upload CSV", type=['csv'])
            if uploaded_file:
                if st.button("Import Data"):
                    try:
                        csv_df = pd.read_csv(uploaded_file)
                        db.bulk_import(csv_df)
                        st.success("Data Imported Successfully!")
                    except Exception as e:
                        st.error(f"Import Failed: {e}")
            
            st.divider()
            
            st.subheader("⚡ Auction Simulator")
            st.markdown("Randomly assign Sold/Unsold status and Final Price to available players.")
            if st.button("RUN SIMULATION", type="primary"):
                with st.spinner("Simulating Auction..."):
                    time.sleep(1) # Dramatic pause
                    count = db.simulate_auction()
                st.success(f"Simulation Complete! Updated {count} players.")
                st.balloons()
            
            if st.button("🔄 Reset Auction"):
                db.reset_auction()
                st.warning("Auction Reset! All players are now Available.")

if __name__ == "__main__":
    main()

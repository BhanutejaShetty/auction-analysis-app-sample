import os
import sqlite3
import pandas as pd
import app

# Setup a test database
TEST_DB = "test_scout.db"
app.DB_NAME = TEST_DB

def setup_module():
    """Remove existing test db if any."""
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    app.init_db()

def teardown_module():
    """Remove test db after tests."""
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
        
def test_add_and_fetch_player():
    print("Testing add_player and fetch_players...")
    
    # 1. Add Player
    app.add_player("Dhoni", "Wicketkeeper", 200, 10)
    app.add_player("Kohli", "Batsman", 200, 10)
    app.add_player("Bumrah", "Bowler", 150, 9)
    
    # 2. Fetch All
    df = app.fetch_players()
    assert len(df) == 3
    print("✅ Added 3 players successfully.")
    
    # 3. Test Search
    df_search = app.fetch_players(search_query="Dhoni")
    assert len(df_search) == 1
    assert df_search.iloc[0]['name'] == "Dhoni"
    print("✅ Search functionality works.")
    
    # 4. Test Filter
    df_filter = app.fetch_players(role_filter=["Batsman"])
    assert len(df_filter) == 1
    assert df_filter.iloc[0]['name'] == "Kohli"
    print("✅ Filter functionality works.")
    
    # 5. Test Combined Search & Filter
    df_combined = app.fetch_players(search_query="Bumrah", role_filter=["Bowler"])
    assert len(df_combined) == 1
    assert df_combined.iloc[0]['name'] == "Bumrah"
    print("✅ Combined Search & Filter works.")

if __name__ == "__main__":
    try:
        setup_module()
        test_add_and_fetch_player()
        teardown_module()
        print("\n🎉 All backend tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test Failed: {e}")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")

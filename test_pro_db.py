import os
import database as db
import pandas as pd

# Setup test DB
TEST_DB = "test_pro_scout.db"
db.DB_NAME = TEST_DB

def test_database_logic():
    print("Testing Professional Database Logic...")
    
    # 1. Init
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    db.init_db()
    print("✅ Database initialized.")

    # 2. Add Player
    player = {
        "name": "Test Player", "nationality": "India", "role": "Batsman", 
        "age": 25, "matches_played": 10, "strike_rate": 120.5, 
        "economy_rate": 0.0, "base_price": 50, "skill_rating": 8
    }
    db.add_player(player)
    
    players = db.fetch_players()
    assert len(players) == 1
    assert players.iloc[0]['name'] == "Test Player"
    print("✅ Add Player works.")

    # 3. Bulk Import
    data = {
        "name": ["P1", "P2"],
        "role": ["Bowler", "All-rounder"],
        "base_price": [30, 40],
        "skill_rating": [9, 7],
        # Optional fields missing, should default
    }
    df = pd.DataFrame(data)
    db.bulk_import(df)
    
    players = db.fetch_players()
    assert len(players) == 3
    print("✅ Bulk Import works.")

    # 4. Filter
    filters = {'role': ['Bowler']}
    bowlers = db.fetch_players(filters)
    assert len(bowlers) == 1
    assert bowlers.iloc[0]['name'] == "P1"
    print("✅ Filtering works.")

    # 5. Simulation
    print("Running simulation...")
    # All 3 are available. P1 (rating 9) has high chance of sell.
    db.simulate_auction()
    
    # Check if status changed
    updated_players = db.fetch_players()
    sold_unsold = updated_players['auction_status'].isin(['Sold', 'Unsold'])
    assert sold_unsold.all()
    print("✅ Auction Simulation executed (Status updated).")
    
    # Cleanup
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

if __name__ == "__main__":
    try:
        test_database_logic()
        print("\n🎉 All Professional DB tests passed!")
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()

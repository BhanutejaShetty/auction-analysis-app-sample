import database as db
import pandas as pd

def verify_app_state():
    print("running verification...")
    
    # 1. Check Data Count
    df = db.fetch_players()
    print(f"Total Players in DB: {len(df)}")
    if len(df) == 0:
        print("⚠️ No players found. Import might have failed or DB was empty.")
    else:
        print("✅ Data exists.")
        
    # 2. Check Integrity (No Null Names)
    if df['name'].isnull().any():
        print("❌ Found Null names!")
    else:
        print("✅ No Null names.")
        
    # 3. Test Reset Logic
    print("Testing Reset Logic...")
    db.reset_auction()
    df_reset = db.fetch_players()
    available_count = df_reset[df_reset['auction_status'] == 'Available'].shape[0]
    
    if available_count == len(df_reset):
        print("✅ Reset Auction works. All players Available.")
    else:
        print(f"❌ Reset failed. {len(df_reset) - available_count} players not available.")

if __name__ == "__main__":
    verify_app_state()

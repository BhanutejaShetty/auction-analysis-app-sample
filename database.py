import sqlite3
import pandas as pd
import random

DB_NAME = "scout.db"

def connect_db():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = connect_db()
    c = conn.cursor()
    # Drop table to apply new schema (WARNING: Data loss)
    c.execute('DROP TABLE IF EXISTS players')
    c.execute('''
        CREATE TABLE players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            nationality TEXT,
            role TEXT NOT NULL,
            age INTEGER,
            matches_played INTEGER,
            strike_rate REAL,
            economy_rate REAL,
            base_price INTEGER NOT NULL,
            skill_rating INTEGER NOT NULL,
            auction_status TEXT DEFAULT 'Available',
            final_price INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def add_player(data):
    """
    Adds a single player. 
    data: dict containing player attributes
    """
    conn = connect_db()
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO players (name, nationality, role, age, matches_played, strike_rate, economy_rate, base_price, skill_rating, auction_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['name'], data['nationality'], data['role'], data['age'], 
            data['matches_played'], data['strike_rate'], data['economy_rate'], 
            data['base_price'], data['skill_rating'], 'Available'
        ))
        conn.commit()
    except Exception as e:
        print(f"Error adding player: {e}")
    finally:
        conn.close()

def bulk_import(df):
    """
    Imports players from a pandas DataFrame.
    Expects columns matching schema.
    """
    conn = connect_db()
    try:
        # Map DataFrame columns to DB columns if necessary, or ensure CSV matches
        # For simplicity, we assume CSV has correct headers or we map them here
        # We'll select only relevant columns and let database handle defaults
        
        required_cols = ['name', 'role', 'base_price', 'skill_rating']
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")
        
        # Add missing optional columns with defaults if not present
        optional_defaults = {
            'nationality': 'Unknown', 'age': 25, 'matches_played': 0, 
            'strike_rate': 0.0, 'economy_rate': 0.0, 'auction_status': 'Available', 'final_price': 0
        }
        
        for col, default in optional_defaults.items():
            if col not in df.columns:
                df[col] = default

        # Write to DB
        df.to_sql('players', conn, if_exists='append', index=False)
    except Exception as e:
        print(f"Error executing bulk import: {e}")
        raise e
    finally:
        conn.close()

def fetch_players(filters=None):
    conn = connect_db()
    query = "SELECT * FROM players WHERE 1=1"
    params = []
    
    if filters:
        if filters.get('search'):
            query += " AND name LIKE ?"
            params.append(f"%{filters['search']}%")
        
        if filters.get('role'):
            placeholders = ','.join('?' for _ in filters['role'])
            query += f" AND role IN ({placeholders})"
            params.extend(filters['role'])
            
        if filters.get('nationality'):
            placeholders = ','.join('?' for _ in filters['nationality'])
            query += f" AND nationality IN ({placeholders})"
            params.extend(filters['nationality'])
            
        if filters.get('price_min') is not None:
             query += " AND base_price >= ?"
             params.append(filters['price_min'])
             
        if filters.get('price_max') is not None:
             query += " AND base_price <= ?"
             params.append(filters['price_max'])
             
        if filters.get('rating_min') is not None:
             query += " AND skill_rating >= ?"
             params.append(filters['rating_min'])

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def simulate_auction():
    """
    Randomly assigns 'Sold' or 'Unsold' status and a Final Price.
    Sold price is between Base Price and 5x Base Price (weighted by rating).
    """
    conn = connect_db()
    c = conn.cursor()
    
    # Fetch all available players
    c.execute("SELECT id, base_price, skill_rating FROM players WHERE auction_status = 'Available'")
    players = c.fetchall()
    
    updates = []
    
    for pid, base, rating in players:
        # Logic: Higher rating = higher chance of being sold and higher multiplier
        luck = random.random()
        sold_threshold = 0.3 if rating > 7 else 0.6 # High rated players rarely go unsold
        
        if luck > sold_threshold:
            status = 'Sold'
            # Multiplier based on rating and randomness
            multiplier = 1 + (rating / 10) * random.uniform(1, 4) 
            final_price = int(base * multiplier)
            # Round to nearest 5
            final_price = 5 * round(final_price / 5)
        else:
            status = 'Unsold'
            final_price = 0
            
        updates.append((status, final_price, pid))
    
    c.executemany("UPDATE players SET auction_status = ?, final_price = ? WHERE id = ?", updates)
    conn.commit()
    conn.close()
    return len(updates)

def reset_auction():
    """
    Resets all players to 'Available' status and clears Final Price.
    """
    conn = connect_db()
    c = conn.cursor()
    c.execute("UPDATE players SET auction_status = 'Available', final_price = 0")
    conn.commit()
    conn.close()

def get_stats():
    conn = connect_db()
    stats = {}
    
    # Total Players
    stats['total_players'] = pd.read_sql("SELECT COUNT(*) FROM players", conn).iloc[0,0]
    
    # Avg Base Price
    avg_price = pd.read_sql("SELECT AVG(base_price) FROM players", conn).iloc[0,0]
    stats['avg_price'] = avg_price if avg_price is not None else 0.0
    
    # Highest Rated
    max_rating = pd.read_sql("SELECT MAX(skill_rating) FROM players", conn).iloc[0,0]
    stats['max_rating'] = max_rating if max_rating is not None else 0
    
    # Role Distribution
    stats['role_dist'] = pd.read_sql("SELECT role, COUNT(*) as count FROM players GROUP BY role", conn)
    
    conn.close()
    return stats

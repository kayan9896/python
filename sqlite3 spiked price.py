import sqlite3
import random
from datetime import datetime, timedelta

# Function to generate sample stock prices
def generate_stock_prices(num_days=15, base_price=50):
    prices = []
    current_price = base_price

    start_date = datetime(2023, 1, 1)  # Starting date

    for day in range(num_days):
        # Generate a random price change between -5 and 5
        price_change = random.uniform(-5, 5)
        current_price += price_change

        # Ensure price doesn't go below 1
        current_price = max(1, current_price)

        # Calculate the date
        date = (start_date + timedelta(days=day)).strftime('%Y-%m-%d')

        prices.append((date, round(current_price, 2)))

    return prices

# Create and populate the database
def create_stock_price_db(db_name='stock_prices.db'):
    # Connect to SQLite database (it will be created if it doesn't exist)
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Create table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_prices
        (date TEXT PRIMARY KEY,
         price REAL NOT NULL)
    ''')

    # Generate sample data
    prices = generate_stock_prices()

    # Insert data into the table
    cursor.executemany('INSERT INTO daily_prices (date, price) VALUES (?, ?)', prices)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    print(f"Database '{db_name}' created successfully with {len(prices)} days of price data.")

# Function to display the contents of the database
def display_db_contents(db_name='stock_prices.db'):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM daily_prices ORDER BY date')
    rows = cursor.fetchall()

    print("\nDatabase contents:")
    print("Date\t\tPrice")
    print("-" * 20)
    for row in rows:
        print(f"{row[0]}\t${row[1]:.2f}")

    conn.close()

def find_price_spikes(db_name='stock_prices.db'):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    query = '''
    SELECT 
        date, 
        prev_price, 
        price, 
        next_price
    FROM (
        SELECT 
            date, 
            price, 
            LAG(price) OVER (ORDER BY date) AS prev_price, 
            LEAD(price) OVER (ORDER BY date) AS next_price 
        FROM daily_prices
    )
    WHERE 
        price > prev_price 
        AND price > next_price 
    ORDER BY date
    '''


  '''
  window function got syntax error for sqlite3 version under 3.25, like in python 3.6.
  an alternative approach can be used
    SELECT 
        b.date AS spike_date, 
        a.price AS previous_price,
        b.price AS spike_price,
        c.price AS next_price
    FROM 
        daily_prices a,
        daily_prices b,
        daily_prices c
    WHERE 
        date(a.date) = date(b.date, '-1 day')  -- previous day
        AND date(c.date) = date(b.date, '+1 day')  -- next day
        AND b.price > a.price  -- price higher than previous day
        AND b.price > c.price  -- price higher than next day
    ORDER BY 
        b.date
    '''

    cursor.execute(query)
    spikes = cursor.fetchall()

    conn.close()

    return spikes

# Function to display spike results
def display_spikes(spikes):
    if not spikes:
        print("No price spikes found.")
        return

    print("Price Spikes:")
    print("Date\t\tPrev Price\tSpike Price\tNext Price")
    print("-" * 60)
    for spike in spikes:
        #print(spike)
        print(f"{spike[0]}\t${spike[1]:.2f}\t\t${spike[2]:.2f}\t\t${spike[3]:.2f}")

def check_sqlite_version():
    conn = sqlite3.connect(':memory:')  # Create a temporary database in memory
    cursor = conn.cursor()

    cursor.execute('SELECT sqlite_version()')
    version = cursor.fetchone()[0]

    print(f"SQLite version: {version}")

    conn.close()
    
# Main execution
if __name__ == '__main__':
    # First, create and populate the database (if you haven't already)
    #create_stock_price_db()

    # Display all data for reference
    print("All price data:")
    display_db_contents()

    print("\n" + "="*60 + "\n")

    # Find and display spikes
    spikes = find_price_spikes()
    display_spikes(spikes)
    check_sqlite_version()

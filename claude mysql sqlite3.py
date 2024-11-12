'''insert'''
import sqlite3

# Connect to the SQLite3 database
conn = sqlite3.connect('sample.db')
cursor = conn.cursor()

# Create the CITIES table
cursor.execute('''
CREATE TABLE CITIES (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL
)
''')

# Create the USERS table
cursor.execute('''
CREATE TABLE USERS (
    id TEXT PRIMARY KEY,
    city_id TEXT NOT NULL,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    FOREIGN KEY (city_id) REFERENCES CITIES (id)
)
''')

# Create the SESSIONS table
cursor.execute('''
CREATE TABLE SESSIONS (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    actions INTEGER NOT NULL,
    duration INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES USERS (id)
)
''')

# Insert sample data into CITIES table
cities = [
    ('1', 'New York'),
    ('2', 'Los Angeles'),
    ('3', 'Chicago')
]
cursor.executemany('INSERT INTO CITIES (id, name) VALUES (?, ?)', cities)

# Insert sample data into USERS table
users = [
    ('1', '1', 'Alice', 'alice@example.com'),
    ('2', '2', 'Bob', 'bob@example.com'),
    ('3', '3', 'Charlie', 'charlie@example.com')
]
cursor.executemany('INSERT INTO USERS (id, city_id, name, email) VALUES (?, ?, ?, ?)', users)

# Insert sample data into SESSIONS table
sessions = [
    ('1', '1', 10, 120),
    ('2', '2', 5, 60),
    ('3', '3', 7, 90)
]
cursor.executemany('INSERT INTO SESSIONS (id, user_id, actions, duration) VALUES (?, ?, ?, ?)', sessions)

# Commit the transaction and close the connection
conn.commit()
conn.close()




'''analyze from db'''
import sqlite3
from typing import List, Tuple
import pandas as pd

def connect_to_database(db_path: str) -> sqlite3.Connection:
    """Create a connection to the SQLite database."""
    try:
        conn = sqlite3.connect(db_path)
        return conn
    except sqlite3.Error as e:
        raise Exception(f"Error connecting to database: {e}")

def get_session_duration_by_city(conn: sqlite3.Connection, query_type: int = 1) -> List[Tuple]:
    """
    Execute the query to get session durations by city.

    Args:
        conn: SQLite database connection
        query_type: Integer specifying which query to use (1, 2, or 3)

    Returns:
        List of tuples containing (city_name, total_duration)
    """
    queries = {
        1: """
            SELECT 
                c.name AS city_name,
                COALESCE(SUM(s.duration), 0) AS total_duration
            FROM 
                CITIES c
            LEFT JOIN 
                USERS u ON c.id = u.city_id
            LEFT JOIN 
                SESSIONS s ON u.id = s.user_id
            GROUP BY 
                c.id, c.name
            ORDER BY 
                total_duration ASC;
        """,
        2: """
            SELECT 
                c.name AS city_name,
                COALESCE(SUM(s.duration), 0) AS total_duration
            FROM 
                USERS u
            INNER JOIN 
                CITIES c ON u.city_id = c.id
            LEFT JOIN 
                SESSIONS s ON u.id = s.user_id
            GROUP BY 
                c.id, c.name
            ORDER BY 
                total_duration ASC;
        """,
        3: """
            SELECT 
                c.name AS city_name,
                SUM(s.duration) AS total_duration
            FROM 
                SESSIONS s
            INNER JOIN 
                USERS u ON s.user_id = u.id
            INNER JOIN 
                CITIES c ON u.city_id = c.id
            GROUP BY 
                c.id, c.name
            ORDER BY 
                total_duration ASC;
        """
    }

    try:
        cursor = conn.cursor()
        cursor.execute(queries[query_type])
        results = cursor.fetchall()
        return results
    except sqlite3.Error as e:
        raise Exception(f"Error executing query: {e}")

def display_results(results: List[Tuple]) -> None:
    """Display the results in a formatted way using pandas DataFrame."""
    if not results:
        print("No results found.")
        return

    df = pd.DataFrame(results, columns=['City', 'Total Duration'])
    print("\nSession Duration by City:")
    print(df.to_string(index=False))

def main():
    # Specify your database path
    db_path = "sample.db"

    try:
        # Connect to the database
        conn = connect_to_database(db_path)

        # Get results using different queries
        print("\n=== Results using Query 1 (Starting from CITIES) ===")
        results1 = get_session_duration_by_city(conn, query_type=1)
        display_results(results1)

        print("\n=== Results using Query 2 (Starting from USERS) ===")
        results2 = get_session_duration_by_city(conn, query_type=2)
        display_results(results2)

        print("\n=== Results using Query 3 (Starting from SESSIONS) ===")
        results3 = get_session_duration_by_city(conn, query_type=3)
        display_results(results3)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
  



'''extract and save'''
import sqlite3
import pandas as pd

def connect_to_database(db_path: str) -> sqlite3.Connection:
    """Create a connection to the SQLite database."""
    try:
        conn = sqlite3.connect(db_path)
        return conn
    except sqlite3.Error as e:
        raise Exception(f"Error connecting to database: {e}")

def get_table_data(conn: sqlite3.Connection, table_name: str) -> pd.DataFrame:
    """
    Fetch all data from a specified table.

    Args:
        conn: SQLite database connection
        table_name: Name of the table to fetch data from

    Returns:
        pandas DataFrame containing the table data
    """
    query = f"SELECT * FROM {table_name}"
    try:
        df = pd.read_sql_query(query, conn)
        return df
    except sqlite3.Error as e:
        raise Exception(f"Error fetching data from {table_name}: {e}")

def save_to_csv(dataframes: dict, output_file: str) -> None:
    """
    Save multiple DataFrames to a single CSV file with multiple sheets.

    Args:
        dataframes: Dictionary with table names as keys and DataFrames as values
        output_file: Name of the output CSV file
    """
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        for table_name, df in dataframes.items():
            df.to_excel(writer, sheet_name=table_name, index=False)
    print(f"Data saved to {output_file}")

def main():
    # Specify your database path and output file name
    db_path = "sample.db"
    output_file = "database_tables.xlsx"

    try:
        # Connect to the database
        conn = connect_to_database(db_path)

        # Fetch data from each table
        tables = ['CITIES', 'USERS', 'SESSIONS']
        dataframes = {}

        for table in tables:
            df = get_table_data(conn, table)
            print(f"\nTable: {table}")
            print(df.head())
            print(f"Data types:\n{df.dtypes}\n")
            dataframes[table] = df

        # Save all tables to a single Excel file
        save_to_csv(dataframes, output_file)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()




'''analyze from xlsx'''
import pandas as pd
from typing import Dict

def load_excel_data(file_path: str) -> Dict[str, pd.DataFrame]:
    """
    Load data from Excel file into separate DataFrames.

    Args:
        file_path: Path to the Excel file

    Returns:
        Dictionary containing DataFrames for each sheet
    """
    try:
        # Read each sheet into a different DataFrame
        cities_df = pd.read_excel(file_path, sheet_name='CITIES')
        users_df = pd.read_excel(file_path, sheet_name='USERS')
        sessions_df = pd.read_excel(file_path, sheet_name='SESSIONS')

        return {
            'cities': cities_df,
            'users': users_df,
            'sessions': sessions_df
        }
    except Exception as e:
        raise Exception(f"Error loading Excel file: {e}")

def calculate_city_durations(dfs: Dict[str, pd.DataFrame], analysis_type: str = 'all_cities') -> pd.DataFrame:
    """
    Calculate total session duration for each city using different analysis approaches.

    Args:
        dfs: Dictionary containing DataFrames for cities, users, and sessions
        analysis_type: Type of analysis to perform ('all_cities', 'cities_with_users', or 'cities_with_sessions')

    Returns:
        DataFrame with city names and their total session durations
    """
    cities_df = dfs['cities']
    users_df = dfs['users']
    sessions_df = dfs['sessions']

    if analysis_type == 'all_cities':
        # Include all cities (equivalent to LEFT JOINs)
        merged_df = cities_df.merge(users_df, how='left', left_on='id', right_on='city_id')
        merged_df = merged_df.merge(sessions_df, how='left', left_on='id_y', right_on='user_id')

    elif analysis_type == 'cities_with_users':
        # Include only cities with users (equivalent to INNER JOIN with users, LEFT JOIN with sessions)
        merged_df = cities_df.merge(users_df, how='inner', left_on='id', right_on='city_id')
        merged_df = merged_df.merge(sessions_df, how='left', left_on='id_y', right_on='user_id')

    elif analysis_type == 'cities_with_sessions':
        # Include only cities with sessions (equivalent to INNER JOINs)
        merged_df = cities_df.merge(users_df, how='inner', left_on='id', right_on='city_id')
        merged_df = merged_df.merge(sessions_df, how='inner', left_on='id_y', right_on='user_id')

    else:
        raise ValueError("Invalid analysis_type. Must be 'all_cities', 'cities_with_users', or 'cities_with_sessions'")

    # Group by city name and calculate total duration
    result_df = merged_df.groupby('name_x')['duration'].sum().reset_index()
    result_df.columns = ['City', 'Total Duration']

    # Fill NaN values with 0 for cities without sessions
    result_df['Total Duration'] = result_df['Total Duration'].fillna(0)

    # Sort by duration in ascending order
    result_df = result_df.sort_values('Total Duration')

    return result_df

def display_results(df: pd.DataFrame, analysis_type: str) -> None:
    """
    Display the results in a formatted way.

    Args:
        df: DataFrame containing the results
        analysis_type: Type of analysis performed
    """
    print(f"\nResults for analysis type: {analysis_type}")
    print("=" * 50)
    if df.empty:
        print("No results found.")
    else:
        print(df.to_string(index=False))
        print(f"\nTotal cities: {len(df)}")
        print(f"Total duration across all cities: {df['Total Duration'].sum():,.0f}")

def main():
    # Specify the path to your Excel file
    excel_file = "database_tables.xlsx"

    try:
        # Load data from Excel file
        print("Loading data from Excel file...")
        dfs = load_excel_data(excel_file)

        # Perform different types of analysis
        analysis_types = ['all_cities', 'cities_with_users', 'cities_with_sessions']

        for analysis_type in analysis_types:
            # Calculate durations
            result_df = calculate_city_durations(dfs, analysis_type)

            # Display results
            display_results(result_df, analysis_type)

            # Export results to CSV if needed
            output_file = f"session_duration_{analysis_type}.csv"
            result_df.to_csv(output_file, index=False)
            print(f"Results saved to {output_file}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

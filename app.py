import psycopg
import os
from dotenv import load_dotenv
import pmfunctions

# Load environment variables from the .env file
load_dotenv()

# Get the database credentials from the environment variables
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
master_password = os.getenv("MASTER_PASSWORD")

# Check if all env variables are set correctly
if not all([db_host, db_port, db_user, db_password, master_password]):
    raise ValueError("Some environment variables are missing. Please check the .env file") 

# Create a PasswordManager object
pm = pmfunctions.PasswordManager(master_password)

try:
    # Connect to the default database
    conn = psycopg.connect(dbname='postgres', user=db_user, password=db_password, host=db_host, port=db_port)

    # Set the conn to autocommit
    conn.auto_commit = True

    # Create a cursor to execute queries
    cursor= conn.cursor()

    # Check if the database exists
    cursor.execute("SELECT * FROM pg_database WHERE datname='passwordmanager'")
    exists = cursor.fetchone()

    if not exists:
        # Connect to the default database
        conn = psycopg.connect(dbname='postgres', user=db_user, password=db_password, host=db_host, port=db_port)

        # Set the conn to autocommit
        conn.autocommit = True

        # Create a cursor to execute queries
        cursor = conn.cursor()

        # Create a new database
        cursor.execute("CREATE DATABASE passwordmanager")

        # Confirm the creation of the database
        print("Database created successfully")

        # Close the cursor and the connection to the default database
        cursor.close()
        conn.close()

    # Connect to the recently created database
    conn = psycopg.connect(dbname = 'passwordmanager', user=db_user, password=db_password, host=db_host, port=db_port)

    # Set the autocommit to True
    conn.autocommit = True
        
    # Create a cursor to execute queries
    cursor = conn.cursor()

    # Create a table to store the passwords
    cursor.execute('''CREATE TABLE IF NOT EXISTS passwords(
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(255) NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    site_name VARCHAR(255) NOT NULL
                        )''')
        
    # Confirm the creation of the table
    print("Table created")

    # Close the cursor and the connection to the database
    cursor.close()
    conn.close()

# Handle exceptions
except Exception as e:
    print(f"Error: {e}")

# Create a menu
while (True):
    print("What would you like to do?")
    print("================================\n")
    print("1. Add a new password\n")
    print("2. Retrieve a password\n")
    print("3. Delete a password\n")
    print("4. Exit\n")

    choice = input("Enter your choice: ")

    if choice == '1':
        # Get the site name, username and password
        site_name = input("Enter the site name:")
        username = input("Enter your site username: ")
        password = input("Enter your desired password: ")

        # Add the password
        pm.add_password(site_name, username, password)
    
    elif choice == '2':
        # Get the site name
        site_name = input("Enter the site name:")

        # Retrieve the password
        pm.retrieve_password(site_name)
    
    elif choice == '3':
        # Get the site name
        site_name = input("Enter the site name:")

        # Delete the password
        pm.delete_password(site_name)
    
    elif choice == '4':
        print("Exiting the program")
        break

    else:
        print("Invalid choice. Please try again")
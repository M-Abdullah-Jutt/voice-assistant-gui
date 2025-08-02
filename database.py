
import pyodbc

# SQL Server database configuration
driver_name = 'SQL Server'
server = 'DESKTOP-M85DRSC\SQLEXPRESS'  # e.g., 'localhost'
database = 'UserCommandsDB'  # e.g., 'UserCommandsDB'
# username = 'DESKTOP-M85DRSC\SQLEXPRESS'  # e.g., 'sa'
# password = 'PythonTkinter1!'  # e.g., 'your_password'

def setup_database():
    conn = pyodbc.connect(f'DRIVER={driver_name};SERVER={server};DATABASE={database}')
    cursor = conn.cursor()
    cursor.execute('''
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'interactions')
        BEGIN
            CREATE TABLE interactions (
                id INT PRIMARY KEY IDENTITY(1,1),
                command NVARCHAR(MAX),
                response NVARCHAR(MAX),
                timestamp DATETIME DEFAULT GETDATE()
            )
        END
    ''')
    
    conn.commit()
    conn.close()

def store_interaction(command, response):
    conn = pyodbc.connect(f'DRIVER={driver_name};SERVER={server};DATABASE={database}')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO interactions (command, response) VALUES (?, ?)", (command, response))
    conn.commit()
    conn.close()
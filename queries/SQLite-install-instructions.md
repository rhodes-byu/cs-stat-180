SQLite in Visual Studio Code: Detailed Installation & Usage Guide

## 1. Install the SQLite Extension in VS Code

a.  Open Visual Studio Code.  
b.  Click on the Extensions icon on the left sidebar (or press
    `Ctrl+Shift+X`).  
c.  In the search bar, type "SQLite" and look for the extension named
    **SQLite** by alexcvzz.  
d.  Click "Install" to add it to your VS Code environment.  

## 2. Create and Configure a SQL File

a.  Open a folder or workspace in VS Code where you want to work with
    SQLite.  
b.  Create a new file with a `.sql` extension (e.g., `myscript.sql`).  
c.  Write your SQL code inside this file.  

## Example SQL Code:

``` sql
CREATE TABLE horses (id INTEGER, breed TEXT);
INSERT INTO horses (id, breed) VALUES (1, 'Arabian');
INSERT INTO horses (id, breed) VALUES (2, 'Quarter Horse');
INSERT INTO horses (id, breed) VALUES (3, 'Thoroughbred');
INSERT INTO horses (id, breed) VALUES (4, 'Clysdale');
SELECT * FROM horses;

ALTER TABLE horses ADD COLUMN rating INTEGER;
UPDATE horses SET rating = 8 WHERE id=4;
SELECT * FROM horses;
```

## 3. Run SQL Queries in VS Code

a.  Right-click anywhere inside the `.sql` file.  
b.  From the context menu, select **"Run Query"**.  
c.  The results will appear in a tab called "SQLite" at the bottom or
    side of the editor.  

Note: If no database is connected yet, you'll be prompted to create or
open one.

## 4. Working with SQLite Databases

a.  Open the SQLite Explorer from the left sidebar.  
b.  Click on the "+" icon to open or create a new `.db` file.  
c.  Once connected, you can browse tables, run queries, and view
    results.  

## 5. Alternative: Running SQLite in Google Colab

If you prefer running SQL in a notebook format:

a.  Use the following Python code in Google Colab:  

``` python
import sqlite3
import pandas as pd

conn = sqlite3.connect(':memory:')
cursor = conn.cursor()

cursor.execute("CREATE TABLE horses (id INTEGER, breed TEXT);")
cursor.execute("INSERT INTO horses (id, breed) VALUES (1, 'Mustang');")
cursor.execute("INSERT INTO horses (id, breed) VALUES (4, 'Clysdale');")

df = pd.read_sql_query("SELECT * FROM horses;", conn)
print(df)
```

Note: - Use triple quotes (`'''`) to define multi-line SQL commands in
Colab. - Execute one command at a time to avoid errors.

## 6. Additional Resources

-   The SQLite extension for VS Code:  
    https://marketplace.visualstudio.com/items?itemName=alexcvzz.vscode-sqlite
-   SQLite documentation: https://www.sqlite.org/docs.html

Happy querying!

## 7. Optional: Install SQLite3 Editor by yy0931

Another useful extension for working with SQLite databases is **SQLite3
Editor** by yy0931.

## To install:

a.  Open the Extensions tab in VS Code (Ctrl+Shift+X).  
b.  Search for "SQLite3 Editor" by yy0931.  
c.  Click "Install".  

## Why Use SQLite3 Editor?

-   It provides an **interactive interface** for viewing and editing
    database tables.  
-   Allows you to browse databases without writing SQL.  
-   Lets you **add, edit, and delete** table contents via a
    spreadsheet-like interface.  
-   Especially helpful for beginners who want to **visualize data** or
    debug queries.  

## How to Use:

1.  Open or create an SQLite database file (`.db`) in your workspace.  
2.  Open the Command Palette (Ctrl+Shift+P) and type `SQLite3 Editor`.  
3.  Select `SQLite3 Editor: Open Database` and choose your `.db` file.  
4.  Click on a table to view or edit its contents.  

This is a great complement to the main SQLite extension for those who
prefer GUI interactions.

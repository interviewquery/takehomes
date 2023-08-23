import sqlite3






class driver:
    def __init__(self, db_connector):
        self._db_connector = db_connector
        self._conn = None

    @property
    def conn(self):
        if self._conn is None:
            self._conn = self._db_connector()
        return self._conn

    def execute(self, query, params=None):
        """Execute a query that does not return a result set."""
        cursor = self.conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        self.conn.commit()
        cursor.close()

    def fetch(self, query, params=None):
        """Execute a query that returns a result set and fetch rows as dictionaries."""
        cursor = self.conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        # Get column names from the cursor description
        columns = [column[0] for column in cursor.description]
        # Fetch all rows
        rows = cursor.fetchall()
        # Convert rows to a list of dictionaries
        result = [dict(zip(columns, row)) for row in rows]

        cursor.close()
        return result

    def get_connection(self):
        """Retrieve the connection instance from this wrapper class."""
        return self.conn

# Example usage:
if __name__ == "__main__":
    db = Driver()
    db.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT);")
    db.execute("INSERT INTO test (name) VALUES (?);", ("John Doe",))
    rows = db.fetch("SELECT * FROM test;")
    for row in rows:
        print(row["name"])

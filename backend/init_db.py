import sqlite3

def init_database():
    """Initialize the SQLite database for the blog app"""
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()

    # Create posts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            body TEXT NOT NULL,
            author TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create comments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    print("[SUCCESS] Database initialized successfully!")
    print("[INFO] Database file: blog.db")

    # Check if tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='posts'")
    posts_table = cursor.fetchone()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='comments'")
    comments_table = cursor.fetchone()

    if posts_table:
        print("[SUCCESS] Table 'posts' created successfully!")
        cursor.execute("PRAGMA table_info(posts)")
        columns = cursor.fetchall()
        print("\nPosts Table Structure:")
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")

    if comments_table:
        print("\n[SUCCESS] Table 'comments' created successfully!")
        cursor.execute("PRAGMA table_info(comments)")
        columns = cursor.fetchall()
        print("\nComments Table Structure:")
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")

    conn.close()

if __name__ == '__main__':
    init_database()

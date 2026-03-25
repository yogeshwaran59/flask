
from flask import Flask, render_template, request, redirect, url_for
import requests
import sqlite3
from datetime import datetime

app = Flask(__name__)

# ================== ✅ FIX: Initialize DB on startup ==================
def init_db():
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            body TEXT NOT NULL,
            author TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

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
    conn.close()

# ✅ THIS IS THE IMPORTANT PART (runs on Render)
with app.app_context():
    init_db()

# ================== DATABASE FUNCTIONS ==================

def get_db_posts():
    conn = sqlite3.connect('blog.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM posts ORDER BY created_at DESC')
    posts = cursor.fetchall()
    conn.close()
    return [dict(post) for post in posts]

def add_post(title, body, author):
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO posts (title, body, author) VALUES (?, ?, ?)',
                   (title, body, author))
    conn.commit()
    conn.close()

def get_post_by_id(post_id):
    conn = sqlite3.connect('blog.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM posts WHERE id = ?', (post_id,))
    post = cursor.fetchone()
    conn.close()
    return dict(post) if post else None

def update_post(post_id, title, body, author):
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE posts SET title = ?, body = ?, author = ? WHERE id = ?',
                   (title, body, author, post_id))
    conn.commit()
    conn.close()

def delete_post(post_id):
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM posts WHERE id = ?', (post_id,))
    conn.commit()
    conn.close()

# ================== COMMENT FUNCTIONS ==================

def get_comments_by_post_id(post_id):
    conn = sqlite3.connect('blog.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM comments WHERE post_id = ? ORDER BY created_at DESC', (post_id,))
    comments = cursor.fetchall()
    conn.close()
    return [dict(comment) for comment in comments]

def add_comment(post_id, content):
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO comments (post_id, content) VALUES (?, ?)',
                   (post_id, content))
    conn.commit()
    conn.close()

def get_comment_by_id(comment_id):
    conn = sqlite3.connect('blog.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM comments WHERE id = ?', (comment_id,))
    comment = cursor.fetchone()
    conn.close()
    return dict(comment) if comment else None

def update_comment(comment_id, content):
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE comments SET content = ? WHERE id = ?',
                   (content, comment_id))
    conn.commit()
    conn.close()

def delete_comment(comment_id):
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM comments WHERE id = ?', (comment_id,))
    conn.commit()
    conn.close()

# ================== ROUTES ==================

@app.route('/')
def index():
    db_posts = get_db_posts()
    try:
        response = requests.get('https://jsonplaceholder.typicode.com/posts')
        api_posts = response.json()
    except:
        api_posts = []

    return render_template('index.html', db_posts=db_posts, api_posts=api_posts)

@app.route('/create', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')
        author = request.form.get('author')

        if title and body and author:
            add_post(title, body, author)
            return redirect(url_for('index'))

    return render_template('create-post.html')

@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')
        author = request.form.get('author')

        if title and body and author:
            update_post(post_id, title, body, author)
            return redirect(url_for('index'))

    post = get_post_by_id(post_id)
    if post:
        return render_template('edit.html', post=post)
    else:
        return redirect(url_for('index'))

@app.route('/delete/<int:post_id>')
def delete_post_route(post_id):
    delete_post(post_id)
    return redirect(url_for('index'))

@app.route('/post/<int:post_id>')
def post_detail(post_id):
    try:
        response = requests.get(f'https://jsonplaceholder.typicode.com/posts/{post_id}')
        post = response.json()
        return render_template('post-detail.html', post=post)
    except:
        return render_template('post-detail.html', post=None)

@app.route('/my-post/<int:post_id>')
def view_post(post_id):
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
    post = cursor.fetchone()
    conn.close()

    comments = get_comments_by_post_id(post_id)
    return render_template("view_post.html", post=post, comments=comments)

@app.route('/add-comment/<int:post_id>', methods=['POST'])
def add_comment_route(post_id):
    content = request.form.get('content')
    if content:
        add_comment(post_id, content)
    return redirect(url_for('view_post', post_id=post_id))

@app.route('/edit-comment/<int:comment_id>', methods=['GET', 'POST'])
def edit_comment_route(comment_id):
    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            update_comment(comment_id, content)
            comment = get_comment_by_id(comment_id)
            if comment:
                return redirect(url_for('view_post', post_id=comment['post_id']))
        return redirect(url_for('index'))

    comment = get_comment_by_id(comment_id)
    if comment:
        return render_template('edit_comment.html', comment=comment)
    else:
        return redirect(url_for('index'))

@app.route('/delete-comment/<int:comment_id>')
def delete_comment_route(comment_id):
    comment = get_comment_by_id(comment_id)
    if comment:
        post_id = comment['post_id']
        delete_comment(comment_id)
        return redirect(url_for('view_post', post_id=post_id))
    return redirect(url_for('index'))

# ================== RUN ==================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)


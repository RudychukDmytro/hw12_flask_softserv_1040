import sqlite3
from datetime import datetime

from flask import Flask, flash, redirect, render_template, request, url_for
from werkzeug.exceptions import abort


def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

connection = sqlite3.connect("database.db")

with open("schema.sql") as f:
    connection.executescript(f.read())

    cur = connection.cursor()

    cur.execute("INSERT INTO posts (title, content) VALUES (?, ?)",
                        ("First Post", "Content for the first post")
                        )

    cur.execute("INSERT INTO posts (title, content) VALUES (?, ?)",
                        ("Second Post", "Content for the second post")
                        )

    connection.commit()
    connection.close()

def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post

def get_responses(post_id):
    conn = get_db_connection()
    responses = conn.execute("SELECT * FROM response WHERE post_id = ?", (post_id,)).fetchall()
    conn.close()
    return responses



app = Flask(__name__)
app.config['SECRET_KEY'] = "key"

@app.route('/')
def index():
    conn = get_db_connection()
    posts = conn.execute("SELECT * FROM posts").fetchall()
    conn.close()
    return render_template('index.html', posts=posts)


@app.route("/<int:post_id>")
def post(post_id):
    responses = get_responses(post_id)
    post = get_post(post_id)
    return render_template("post.html", post=post, responses=responses)


@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        current_datetime = datetime.now()
        updated = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE posts SET title = ?, content = ?, updated = ?'
                         ' WHERE id = ?',
                         (title, content, updated, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('edit.html', post=post)


@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    post = get_post(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index'))

@app.route('/<int:id>/created', methods=('GET', 'POST'))
def created(id):
    post = get_post(id)
    responses = get_responses(id)
    if request.method == 'POST':
        author = request.form['author']
        content_response = request.form['content_response']
        post_id = request.form['id']
        if not author:
            flash('Author is required!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO response (author, content_response, post_id) VALUES (?, ?, ?)',
                         (author, content_response, post_id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('created_response.html', post=post, responses=responses)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
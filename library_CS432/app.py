from flask import Flask
from flask import render_template, request, redirect, url_for, session, flash

from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL

import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# # Creating SQLAlchemy instance
# db = SQLAlchemy()

# Configure db
app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB

mysql = MySQL(app)


@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('home', username=session['username']))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT * FROM user WHERE username = %s', (username,)
        )
        user = cur.fetchone()
        if user:
            error = 'Account already exists !'

        if error is None:
            cur.execute('INSERT INTO user (username, password) VALUES (%s, %s)', (username, password,))
            mysql.connection.commit()

        flash(error)
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT * FROM user WHERE username = %s AND password = %s', (username, password)
        )
        users = cur.fetchone()
        if users is None:
            error = 'Incorrect username / password !'
        if error is None:
            session['username'] = username
            return redirect(url_for('home', username=username))
        flash(error)
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/home/<username>')
def home(username):
    if 'username' in session and session['username'] == username:
        return render_template('home.html', username=username)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask
from flask import render_template, request, redirect, url_for, session, abort, jsonify
import time

from flask_mysqldb import MySQL

import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# Configure db
app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB

mysql = MySQL(app)


# Aashmun Gupta
@app.route('/')
def index():
    if 'username' in session and 'role' in session:
        return redirect(url_for(session['role'].lower(), username=session['username']))
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

        cur.close()

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
            session['role'] = users[8]
            if users[8] == 'Admin':
                return redirect(url_for('admin', username=username))
            if users[8] == 'Student':
                return redirect(url_for('home', username=username))
            if users[8] == 'Faculty':
                return redirect(url_for('faculty', username=username))
        cur.close()
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/home/<username>')
def home(username):
    if 'username' in session and session['username'] == username and session['role'] == 'Student':
        return render_template('home.html', username=username)
    return redirect(url_for('login'))


@app.route('/admin/<username>')
def admin(username):
    if 'username' in session and session['username'] == username and session['role'] == 'Admin':
        library_data = get_library_data()
        return render_template('admin/index.html', username=username)
    return redirect(url_for('login'))


@app.route('/admin/<username>/external')
def ext_lib(username):
    if 'username' in session and session['username'] == username and session['role'] == 'Admin':
        library_data = get_library_data()
        return render_template('admin/external_library.html', username=username)
    return redirect(url_for('login'))


# Dhruv Sharma
def get_library_data():
    cur = mysql.connection.cursor()
    cur.execute("SELECT library_id, exchanges, amount FROM external_library")
    library_data = cur.fetchall()
    cur.close()
    return library_data


# Aashmun Gupta
@app.route('/faculty/<username>', methods=['GET', 'POST'])
def faculty(username):
    if 'username' in session and session['username'] == username and session['role'] == 'Faculty':
        if request.method == 'POST':
            return redirect(url_for('faculty_recommend', username=username))
        return render_template('faculty.html', username=username)
    return redirect(url_for('login'))


@app.route('/faculty/<username>/recommend', methods=['GET', 'POST'])
def faculty_recommend(username):
    if 'username' in session and session['username'] == username and session['role'] == 'Faculty':
        if request.method == 'POST':
            user_id = request.form['user_id']
            course = request.form['course']
            title = request.form['title']
            catalogue = catalogue_ref(title)
            if catalogue is None:
                error = "Catalogue not found for the given title."
                return jsonify({'error': error}), 400  # Return error as JSON with status code 400
            try:
                cur = mysql.connection.cursor()
                cur.execute(
                    'INSERT INTO recommendation (user_id, catalogue_id, course_id) VALUES (%s, %s, %s)',
                    (user_id, catalogue, course,)
                )
                mysql.connection.commit()
                cur.close()
                return jsonify({'success': True, 'message': ' Created successfully'})
            except Exception as e:
                return jsonify({'success': False, 'message': str(e)}), 500


def catalogue_ref(title):
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT catalogue_id FROM catalogue WHERE title = %s",
        (title,)
    )
    result = cur.fetchone()
    cur.close()
    return result


@app.route('/<username>/rooms', methods=['GET', 'POST'])
def rooms(username):
    if 'username' in session and session['username'] == username:
        if request.method == 'POST':
            start = request.form['start_time']
            end = request.form['end_time']
            cur = mysql.connection.cursor()
            cur.execute(
                'SELECT room_id FROM rooms WHERE leaving_time < %s OR entry_time > %s',
                (start, end,)
            )
            cur.close()
            return jsonify()
        return render_template('room_book.html')
    abort(403)  # forbidden


# Anmol Kumar
# Code to get all catalouge data
@app.route('/catalogues', methods=['GET'])
def get_catalogues():
    try:
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT c.catalogue_id, c.category_no, c.cost, c.title, c.catalogue_type, a.name AS author_name, p.name AS publisher_name, c.purchase_date, c.subscription_end, c.count FROM catalogue c JOIN author a ON c.author_id = a.author_id JOIN publisher p ON c.publisher_id = p.publisher_id ORDER BY c.catalogue_id DESC")
        results = cur.fetchall()
        cur.close()

        catalogue_list = []
        for row in results:
            catalogue = {
                'catalogue_id': row[0],
                'category_no': row[1],
                'cost': row[2],
                'title': row[3],
                'catalogue_type': row[4],
                'author_name': row[5],
                'publisher_name': row[6],
                'purchase_date': row[7],
                'subscription_end': row[8],
                'count': row[9]
            }
            catalogue_list.append(catalogue)

        return jsonify(catalogue_list)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/catalogue/search', methods=['POST'])
def search_catalogue():
    search_query = request.form['search_query']
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT title, author_id, catalogue_type, count FROM catalogue WHERE title LIKE %s",
        ('%' + search_query + '%',)
    )
    results = cur.fetchall()
    cur.close()
    catalogue_list = [{'title': result[0], 'catalogue_type': result[2]} for result in results]
    return jsonify(catalogue_list)


# Route to create a category
@app.route('/add_category', methods=['POST'])
def create_category():
    try:
        category_no = request.form['category_no']
        category_name = request.form['category_name']
        column_no = request.form['column_no']
        status = request.form['status']

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO shelf (category_no, category_name, column_no, status)
            VALUES (%s, %s, %s, %s)
        """, (category_no, category_name, column_no, status))
        mysql.connection.commit()
        cur.close()

        return jsonify({'success': True, 'message': 'Category created successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/add_catalogue', methods=['POST'])
def add_catalogue():
    title = request.form['title']
    author_name = request.form['authorName']
    publisher_name = request.form['publisherName']
    category_no = request.form['categoryNo']
    cost = request.form['cost']
    catalogue_type = request.form['catalogueType']
    purchase_date = request.form['purchaseDate']
    subscription_end = request.form['subscriptionEnd']
    count = request.form['count']

    try:
        # Insert author first
        cur = mysql.connection.cursor()
        cur.execute("SELECT author_id FROM author WHERE name = %s", (author_name,))
        author_id = cur.fetchone()
        if author_id is None:
            cur.execute("INSERT INTO author (name) VALUES (%s)", (author_name,))
            print("Author inserted")
            mysql.connection.commit()
            author_id = cur.lastrowid
            print("Author id fetched")
        else:
            author_id = author_id[0]
            print("Author already exists")

        # Insert publisher second
        cur.execute("SELECT publisher_id FROM publisher WHERE name = %s", (publisher_name,))
        publisher_id = cur.fetchone()
        if publisher_id is None:
            cur.execute("INSERT INTO publisher (name) VALUES (%s)", (publisher_name,))
            mysql.connection.commit()
            print("Publisher inserted")
            publisher_id = cur.lastrowid
            print("Publisher id fetched")
        else:
            publisher_id = publisher_id[0]
            print("Publisher already exists")

        # Now inserting in catalogue
        cur.execute(
            "INSERT INTO catalogue (title, author_id, publisher_id,category_no, cost, catalogue_type, purchase_date, subscription_end, count ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (
            title, author_id, publisher_id, category_no, cost, catalogue_type, purchase_date, subscription_end, count,))
        mysql.connection.commit()
        print("Catalogue inserted")
        cur.close()
        return jsonify({'success': True, 'message': 'Catalogue added successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# To Delete a catalogue

@app.route('/delete_catalogue/<int:catalogue_id>', methods=['DELETE'])
def delete_catalogue(catalogue_id):
    try:
        cur = mysql.connection.cursor()

        # Delete from recommendation table first
        cur.execute("DELETE FROM recommendation WHERE catalogue_id = %s", (catalogue_id,))
        # Commit the deletion
        mysql.connection.commit()

        # Now delete from the catalogue table
        cur.execute("DELETE FROM catalogue WHERE catalogue_id = %s", (catalogue_id,))
        # Commit the deletion
        mysql.connection.commit()

        cur.close()

        return jsonify({'success': True, 'message': f'Catalogue with ID {catalogue_id} deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# Route to add members
@app.route('/add_member', methods=['POST'])
def add_member():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    phone = request.form['phone']
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']
    dues = request.form['dues']
    department = request.form['department']
    member_type = request.form['member_type']
    subscription_fees = request.form['subscription_fees']
    user_img = request.form['user_img']
    try:
        app.logger.info(request.form)

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO user (first_name, last_name, phone, username, password, dues, department, member_type, subscription_fees, user_img)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
        first_name, last_name, phone, username, password, dues, department, member_type, subscription_fees, user_img))
        user_id = cur.lastrowid

        # Insert email into the user_mail table
        cur.execute("""
            INSERT INTO user_mail (user_ID, email)
            VALUES (%s, %s)
        """, (user_id, email))

        mysql.connection.commit()
        cur.close()

        return jsonify({'success': True, 'message': 'Member added successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/recommended', methods=['GET'])
def get_recomend():
    username = session.get('username')
    cur = mysql.connection.cursor()
    cur.execute("SELECT user_ID FROM user WHERE username = %s", (username,))
    user_id_row = cur.fetchone()
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * from recommendation where user_ID = %s", (user_id_row,))
        results = cur.fetchall()
        cur.close()

        courses = []
        for row in results:
            recommened = {
                'user_ID': row[0],
                'catalogue_id': row[1],
                'course_id': row[2],

            }
            courses.append(recommened)

        return jsonify(courses)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)

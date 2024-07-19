from flask import Flask
from flask import render_template, request, redirect, url_for, session, abort, jsonify, current_app, send_file
import time, random, string
from datetime import date, datetime, timedelta
import bleach
import csv
from authlib.integrations.flask_client import OAuth
from authlib.common.security import generate_token


from flask_mysqldb import MySQL

import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
oauth = OAuth(app)


# Configure db
app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB

mysql = MySQL(app)


# Anmol Kumar

@app.route('/google/')
def google():

    GOOGLE_CLIENT_ID = '881936870792-b6ffk3acq9rrbv5dk0ocdb4nqt0ag8kk.apps.googleusercontent.com'
    GOOGLE_CLIENT_SECRET = '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'

    CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
    oauth.register(
        name='google',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url=CONF_URL,
        client_kwargs={
            'scope': 'openid email profile'
        }
    )

    redirect_uri = url_for('google_auth', _external=True)
    # print(redirect_uri)
    session['nonce'] = generate_token()
    return oauth.google.authorize_redirect(redirect_uri, nonce=session['nonce'])

@app.route('/google/auth/')
def google_auth():
    token = oauth.google.authorize_access_token()
    user = oauth.google.parse_id_token(token, nonce=session['nonce'])
    
    if 'email' in user and user['email'].endswith('@iitgn.ac.in'):
        session['user'] = user
        # print("Google User ", user)
        email = user.get('email', '')
        print("Email ", email)
        cur = mysql.connection.cursor()
        cur.execute("SELECT user_ID FROM user_mail WHERE email=%s", (email,))
        user_id = cur.fetchone()
        print("Done fetcting User ID ", user_id)

        if user_id:
            user_id = user_id[0]
            print("User ID after If", user_id)
            cur.execute("SELECT * FROM user WHERE user_ID=%s", (user_id,))
            userdata = cur.fetchone()
            username= userdata[4]

            session['username'] = username
            session['role'] = userdata[8]
            if userdata[8] == 'Admin':
                return redirect(url_for('admin', username=username))
            if userdata[8] == 'Staff':
                return redirect(url_for('staff', username=username))
            if userdata[8] == 'InterLibrary':
                return redirect(url_for('external', username=username))
            if userdata[8] == 'Student':
                return redirect(url_for('home', username=username))
            if userdata[8] == 'Faculty':
                return redirect(url_for('faculty', username=username))



        return redirect('/')
    else:
        return "Unauthorized access. Only users iitgn.ac.in are allowed to login."
    




@app.route('/')
def index():
    return render_template('homepage/index.html')


@app.route('/unavailable')
def unavailable():
    return render_template('unavailable.html')


@app.route('/features')
def features():
    return render_template('homepage/features.html')


@app.route('/contact')
def contact():
    return render_template('homepage/contact.html')


@app.route('/subscribe')
def subscribe():
    return render_template('homepage/subscribe.html')


@app.route('/search-catalogue', methods=['GET', 'POST'])
def search_catalogue_page():
    search_query = request.form['search_query']
    cur = mysql.connection.cursor()
    cur.execute("SELECT c.catalogue_id, c.category_no, c.cost, c.title, c.catalogue_type, a.name AS author_name, p.name AS publisher_name, c.purchase_date, c.subscription_end, c.count FROM catalogue c JOIN author a ON c.author_id = a.author_id JOIN publisher p ON c.publisher_id = p.publisher_id WHERE c.title LIKE %s", ("%" + search_query + "%",))
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
    return render_template('homepage/search-catalogue-page.html', results=catalogue_list, search_query=search_query)


# Aashmun Gupta
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         error = None
#         cur = mysql.connection.cursor()
#         cur.execute(
#             'SELECT * FROM user WHERE username = %s AND password = %s', (username, password)
#         )
#         users = cur.fetchone()
#         if users is None:
#             error = 'Incorrect username / password !'
#         if error is None:
#             session['username'] = username
#             session['role'] = users[8]
#             if users[8] == 'Admin':
#                 return redirect(url_for('admin', username=username))
#             if users[8] == 'Staff':
#                 return redirect(url_for('staff', username=username))
#             if users[8] == 'InterLibrary':
#                 return redirect(url_for('external', username=username))
#             if users[8] == 'Student':
#                 return redirect(url_for('home', username=username))
#             if users[8] == 'Faculty':
#                 return redirect(url_for('faculty', username=username))
#         cur.close()

#     return render_template('login.html')

login_attempts = {}
MAX_LOGIN_ATTEMPTS = 5
LOGIN_WINDOW_SECONDS = 60

@app.route('/login', methods=['GET', 'POST'])
def login():
  
    if request.method == 'POST':
        ip_address = request.remote_addr
        print(ip_address)
        if ip_address in login_attempts:
            print("IP address found in login attempts")
            attempts, last_attempt_time = login_attempts[ip_address]
            if datetime.now() - last_attempt_time < timedelta(seconds=LOGIN_WINDOW_SECONDS):
                if attempts >= MAX_LOGIN_ATTEMPTS:
                    print("Too many login attempts")
                    return "<h1>Too many login attempts. Please try again later.</h1>"
            else:
                login_attempts.pop(ip_address)

        # Attempt login
        username = request.form['username']
        password = request.form['password']
        error = None
        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT * FROM user WHERE username = %s AND password = %s', (username, password)
        )
        user = cur.fetchone()
        if user is None:
            error = 'Incorrect username / password !'
        if error is None:
            session['username'] = username
            session['role'] = user[8]
            if user[8] == 'Admin':
                return redirect(url_for('admin', username=username))
            if user[8] == 'Staff':
                return redirect(url_for('staff', username=username))
            if user[8] == 'InterLibrary':
                return redirect(url_for('external', username=username))
            if user[8] == 'Student':
                return redirect(url_for('home', username=username))
            if user[8] == 'Faculty':
                return redirect(url_for('faculty', username=username))
        cur.close()
        
        if ip_address in login_attempts:
            attempts, _ = login_attempts[ip_address]
            login_attempts[ip_address] = (attempts + 1, datetime.now())
            print(login_attempts)
        else:
            login_attempts[ip_address] = (1, datetime.now())

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


@app.route('/external/<username>')
def external(username):
    if 'username' in session and session['username'] == username and session['role'] == 'InterLibrary':
        return render_template('external.html', username=username)
    return redirect(url_for('login'))


@app.route('/staff/<username>')
def staff(username):
    if 'username' in session and session['username'] == username and session['role'] == 'Staff':
        return render_template('staff.html', username=username)
    return redirect(url_for('login'))


@app.route('/admin/<username>')
def admin(username):
    if 'username' in session and session['username'] == username and session['role'] == 'Admin':
        return render_template('admin/index.html', username=username)
    return redirect(url_for('login'))


@app.route('/admin/<username>/external')
def ext_lib(username):
    if 'username' in session and session['username'] == username and session['role'] == 'Admin':
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

#get by id catalogue data

@app.route('/catalogues/<int:catalogue_id>', methods=['GET'])
def get_catalogue_by_id(catalogue_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT c.catalogue_id, c.category_no, c.cost, c.title, c.catalogue_type, a.name AS author_name, p.name AS publisher_name, c.purchase_date, c.subscription_end, c.count FROM catalogue c JOIN author a ON c.author_id = a.author_id JOIN publisher p ON c.publisher_id = p.publisher_id WHERE c.catalogue_id = %s", (catalogue_id,))
        result = cur.fetchone()
        cur.close()

        if result:
            catalogue = {
                'catalogue_id': result[0],
                'category_no': result[1],
                'cost': result[2],
                'title': result[3],
                'catalogue_type': result[4],
                'author_name': result[5],
                'publisher_name': result[6],
                'purchase_date': result[7],
                'subscription_end': result[8],
                'count': result[9]
            }
            return jsonify(catalogue)
        else:
            return jsonify({'message': 'Catalogue not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    
@app.route('/catalogue/search', methods=['POST'])
def search_catalogue():
    try:
        search_query = request.form['search_query']
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT c.catalogue_id, c.category_no, c.cost, c.title, c.catalogue_type, a.name AS author_name, p.name AS publisher_name, c.purchase_date, c.subscription_end, c.count FROM catalogue c JOIN author a ON c.author_id = a.author_id JOIN publisher p ON c.publisher_id = p.publisher_id WHERE c.title LIKE %s",
            ('%' + search_query + '%',)
        )
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


@app.route('/add_category', methods=['POST'])
def create_category():
    try:
        category_no = request.form['category_no']
        category_name = request.form['category_name']
        column_no = request.form['column_no']
        time_period = request.form['time_period']
        status = request.form['status']

        # Insert into shelf table
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO shelf (category_no, category_name, column_no, status)
            VALUES (%s, %s, %s, %s)
        """, (category_no, category_name, column_no, status))
        mysql.connection.commit()

        # Insert into policy table
        cur.execute("""
            INSERT INTO policy (policy_id, category, time_period)
            VALUES (%s, %s, %s)
        """, (category_no, category_name, time_period))
        mysql.connection.commit()

        cur.close()

        return jsonify({'success': True, 'message': 'Category created successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/add_catalogue', methods=['POST'])
def add_catalogue():
    title = bleach.clean(request.form['title']) 
    author_name = bleach.clean(request.form['authorName'])
    publisher_name = bleach.clean(request.form['publisherName'])
    category_no = bleach.clean(request.form['categoryNo'])
    cost = bleach.clean(request.form['cost'])
    catalogue_type = bleach.clean(request.form['catalogueType'])
    purchase_date = bleach.clean(request.form['purchaseDate'])
    subscription_end = bleach.clean(request.form['subscriptionEnd'])
    count = bleach.clean(request.form['count'])

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

@app.route('/rename')
def rename():
    return render_template('admin/rename.html')

@app.route('/rename-table', methods=['POST'])
def rename_table():
    new_table_name = request.json['table_name']
    if not new_table_name:
        return 'Table name cannot be empty', 400

    cur = mysql.connection.cursor()

    try:
        cur.execute(f"ALTER TABLE rooms RENAME TO {new_table_name}")
        mysql.connection.commit()
        return 'Table renamed successfully!', 200
    except Exception as e:
        return f'Error renaming table: {str(e)}', 500
    finally:
        cur.close()

# to update catalogue    
@app.route('/update_catalogue', methods=['POST'])
def update_catalogue():
    catalogue_id = bleach.clean(request.form['catalogueId'])
    title = bleach.clean(request.form['title'])
    author_name = bleach.clean(request.form['authorName'])
    publisher_name = bleach.clean(request.form['publisherName'])
    category_no = bleach.clean(request.form['categoryNo'])
    cost = bleach.clean(request.form['cost'])
    catalogue_type = bleach.clean(request.form['catalogueType'])
    purchase_date = bleach.clean(request.form['purchaseDate'])
    subscription_end = bleach.clean(request.form['subscriptionEnd'])
    count = bleach.clean(request.form['count'])

    try:
        # Update author
        cur = mysql.connection.cursor()
        
        cur.execute("SELECT author_id FROM author WHERE name = %s", (author_name,))
        author_id = cur.fetchone()
        if author_id is None:
            cur.execute("INSERT INTO author (name) VALUES (%s)", (author_name,))
            mysql.connection.commit()
            author_id = cur.lastrowid
        else:
            author_id = author_id[0]

        # Update publisher
        cur.execute("SELECT publisher_id FROM publisher WHERE name = %s", (publisher_name,))
        publisher_id = cur.fetchone()
        if publisher_id is None:
            cur.execute("INSERT INTO publisher (name) VALUES (%s)", (publisher_name,))
            mysql.connection.commit()
            publisher_id = cur.lastrowid
        else:
            publisher_id = publisher_id[0]

        # Update catalogue
        cur.execute("LOCK TABLES catalogue WRITE")
        cur.execute("UPDATE catalogue SET title = %s, author_id = %s, publisher_id = %s, category_no = %s, cost = %s, catalogue_type = %s, purchase_date = %s, subscription_end = %s, count = %s WHERE catalogue_id = %s",
                    (title, author_id, publisher_id, category_no, cost, catalogue_type, purchase_date, subscription_end, count, catalogue_id,))
        mysql.connection.commit()
        cur.execute("UNLOCK TABLES")
        
        cur.close()
        return jsonify({'success': True, 'message': 'Catalogue updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

    
# To Delete a catalogue

@app.route('/delete_catalogue/<int:catalogue_id>', methods=['DELETE'])
def delete_catalogue(catalogue_id):
    try:
        cur = mysql.connection.cursor()

        cur.execute("DELETE FROM recommendation WHERE catalogue_id = %s", (catalogue_id,))
        # Commit the deletion
        mysql.connection.commit()

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
    

@app.route('/external_library/exchanges', methods=['GET'])
def get_ext_lib():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT library_id, exchanges, amount, type FROM external_library")
        results = cur.fetchall()
        cur.close()

        ext_lib_data = []
        for row in results:
            ext_lib = {
                'library_id': row[0],
                'exchanges': row[1],
                'amount': row[2],
                'type': row[3],
            }
            ext_lib_data.append(ext_lib)

        return jsonify(ext_lib_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/home/<username>/issue')
def issue(username):
    if 'username' in session and session['username'] == username and session['role'] == 'Student':
        return render_template('issue.html', username=username)
    return redirect(url_for('login'))

def generate_issue_id():
    current_time_ms = int(time.time() * 1000)
    random_component = random.randint(10000, 99999)
    unique_number = int(str(current_time_ms)[-3:]+str(random_component)[-2:])
    return unique_number

def get_current_date():
    return date.today()


# Route for issuing items
@app.route('/issue_item', methods=['POST'])
def issue_item():
    try:
        catalogue_id = request.form['catalogue_id']


        username = session.get('username')
        cur = mysql.connection.cursor()

        cur.execute("SELECT user_ID FROM user WHERE username = %s", (username,))
        user_ID = cur.fetchone()

        cur.execute("""
            SELECT category_no
            FROM catalogue
            WHERE catalogue_id = %s
        """, (catalogue_id,))
        category_id = cur.fetchone()
        
        # Generate unique issue_id and current date
        issue_id = generate_issue_id()
        issue_date = get_current_date()

        cur.execute("SELECT time_period FROM policy WHERE policy_id = %s", (category_id,))
        time_period = cur.fetchone()
        print(time_period)
        return_date = issue_date + timedelta(days=time_period[0])
        print(return_date)

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO issue (issue_id, issue_date) VALUES (%s, %s)", (issue_id, issue_date))
        mysql.connection.commit()



        cur.execute("INSERT INTO issueing (catalogue_id, user_ID, issue_id) VALUES (%s, %s, %s)", (catalogue_id, user_ID, issue_id))
        mysql.connection.commit()



        cur.execute("INSERT INTO lending (catalogue_id, policy_id) VALUES (%s, %s)", (catalogue_id, category_id))
        mysql.connection.commit()


        cur.execute("INSERT INTO returnn (issue_id, return_date, remarks) VALUES (%s, %s, %s)", (issue_id, return_date, 'Due'))
        mysql.connection.commit()
        cur.close()

        return jsonify({'success': True, 'message': 'Item issued successfully', 'issue_id': issue_id}), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/issued', methods=['GET'])
def get_issued():
    username = session.get('username')
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT user_ID FROM user WHERE username = %s", (username,))
        user_id_row = cur.fetchone()
        app.logger.info(user_id_row)
        cur.close()

        if user_id_row:
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT i.catalogue_id, c.title AS catalogue_name, iss.issue_date
                FROM issueing AS i
                JOIN catalogue AS c ON i.catalogue_id = c.catalogue_id
                JOIN issue AS iss ON i.issue_id = iss.issue_id
                WHERE i.user_ID = %s
            """, (user_id_row,))
            issued_items = cur.fetchall()
            cur.close()

            # Format the fetched data
            issued = []
            for item in issued_items:
                issued.append({
                    'user_ID': user_id_row[0],
                    'catalogue_id': item[0],
                    'catalogue_name': item[1],
                    'issue_date': item[2]
                })

            return jsonify(issued)
        else:
            return jsonify({'error': 'User not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500


#get room data
@app.route('/get_rooms')
def get_room_availability():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM rooms")
        rooms_data = cur.fetchall()
        cur.close()
        data = []
        for item in rooms_data:
            data.append({
                'room_id': item[0],
                'occupied': item[1],
                'entry_time': item[2],
                'leaving_time': item[3]
            })
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/about')
def about():
    return render_template('homepage/about.html')

@app.route('/reports')
def catalogue():
    return render_template('admin/reports.html')

@app.route('/LMS')
def LMS():
    return render_template('LMS.html')

@app.route('/catalogue_report', methods=['GET'])
def generate_catalogue_report_csv():
    try:
        cur = mysql.connection.cursor()

        cur.execute("""
            SELECT c.catalogue_id, c.title, c.category_no, c.cost, c.catalogue_type, a.name AS author_name, p.name AS publisher_name, c.purchase_date, c.subscription_end, c.count 
            FROM catalogue c 
            JOIN author a ON c.author_id = a.author_id 
            JOIN publisher p ON c.publisher_id = p.publisher_id
        """)
        catalogue_report_data = cur.fetchall()

        csv_filename = 'catalogue_report.csv'
        with open(csv_filename, 'w', newline='') as csvfile:
            fieldnames = ['Catalogue ID', 'Title', 'Category No', 'Cost', 'Catalogue Type', 'Author Name', 'Publisher Name', 'Purchase Date', 'Subscription End', 'Count']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for catalogue in catalogue_report_data:
                writer.writerow({
                    'Catalogue ID': catalogue[0],
                    'Title': catalogue[1],
                    'Category No': catalogue[2],
                    'Cost': catalogue[3],
                    'Catalogue Type': catalogue[4],
                    'Author Name': catalogue[5],
                    'Publisher Name': catalogue[6],
                    'Purchase Date': catalogue[7],
                    'Subscription End': catalogue[8],
                    'Count': catalogue[9]
                })

        cur.close()

        return send_file(csv_filename, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/issued_books_report', methods=['GET'])
def generate_books_issued_report_csv():
    try:
        cur = mysql.connection.cursor()

        cur.execute("""
            SELECT i.catalogue_id, c.title AS catalogue_title, u.username AS issued_by, iss.issue_date AS issue_date
            FROM issueing i
            JOIN user u ON i.user_ID = u.user_ID
            JOIN issue iss ON i.issue_id = iss.issue_id
            JOIN catalogue c ON i.catalogue_id = c.catalogue_id
        """)
        books_issued_data = cur.fetchall()

        csv_filename = 'books_issued_report.csv'
        with open(csv_filename, 'w', newline='') as csvfile:
            fieldnames = ['Catalogue ID', 'Catalogue Title', 'Issued By', 'Issue Date']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for book in books_issued_data:
                writer.writerow({
                    'Catalogue ID': book[0],
                    'Catalogue Title': book[1],
                    'Issued By': book[2],
                    'Issue Date': book[3]
                })

        cur.close()

        return send_file(csv_filename, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)

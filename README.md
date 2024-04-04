<div style="text-align: center;">
    <h1>CS 432 : DATABASES</h1>
    <h2>LIBRARY MANAGEMENT SYSTEM</h2>
    <img src="Images/nmp_Image_1.png" width="250" height="250" alt="Library Management System Image">

**ASSIGNMENT 3**

**GROUP MEMBERS**
</div>
<table align="center" style="width: 70%;">
    <tr>
        <th>Name</th>
        <th>Roll Number</th>
    </tr>
    <tr>
        <td>Aashmun Gupta</td>
        <td>22110005</td>
    </tr>
    <tr>
        <td>Anmol Kumar</td>
        <td>22110028</td>
    </tr>
    <tr>
        <td>Anushri Sanodia</td>
        <td>22110030</td>
    </tr>
    <tr>
        <td>Deepanjali Kumari</td>
        <td>22110069</td>
    </tr>
    <tr>
        <td>Dhruv Sharma</td>
        <td>22110074</td>
    </tr>
    <tr>
        <td>Pavani Khale</td>
        <td>22110191</td>
    </tr>
    <tr>
        <td>Yash Patel</td>
        <td>21110243</td>
    </tr>
</table>

### Configuration Setup
In `config.py`, ensure to set up the following variables:

```python
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = '<password>'
MYSQL_DB = 'Library'

SECRET_KEY = '123456789'
```

### Dependencies
Make sure to install the required dependencies in your virtual environment using the following commands:

```bash
pip install Flask
pip install Flask-mysqldb
```

### Database Table
The application utilizes the 'users' table.

### Generating SECRET_KEY:
You can generate a secure secret key by running the following Python script:

```python
import secrets

secret_key = secrets.token_hex(16)
print("Generated Secret Key:", secret_key)
```

### Creating a Virtual Environment
If you haven't set up a virtual environment (`pyvenv`), you can do so using the following command:

```bash
python -m venv your_venv_name
```

Activate the virtual environment:

- On Windows:
```bash
your_venv_name\Scripts\activate
```
- On Unix or MacOS:
```bash
source your_venv_name/bin/activate
```

### Running the Application
To start the Flask application, execute `flask run` in your terminal.

### Cloning Repository
To get started with the project, clone the repository from the following URL:

```bash
git clone https://github.com/AshStorm17/CS432
```

### **3.1 Responsibilty of G1:**:
1. In this we worked on creating the corresponding routes for the features created in the frontend .
2. Integrated our Library System database with the Webapp.
3. Created a dynamic programme which can insert, modify and delete the information as per the need by the admin.


### **3.2 Responsibilty of G1:**:
1. We made the login interface and admin view, adding functions in the admin view like update, edit, and delete, i.e., modifications like these are shown.
2. Made faculty view where only faculty can view it for adding course recommendations.
3. Made student view along with catalog search, where student can see what books he/she has already issued previously.



### **3.3 Responsibility of G1 and G2:**

**FUNCTIONS :**

HOME PAGE :

![Enter image alt description](Images/ZE7_Image_2.png)

LOGIN PAGE :

![Enter image alt description](Images/aIP_Image_3.png)

1. **INSERT :**

Inserting a new catalogue:

![Enter image alt description](Images/NFF_Image_4.png)

![Enter image alt description](Images/zaX_Image_5.png)

BEFORE INSERTING NEW RECORD :

![Enter image alt description](Images/QGE_Image_6.png)

AFTER INSERTING NEW CATALOGUE :

![Enter image alt description](Images/XJB_Image_7.png)

2. **UPDATE  :**

Before Updating Count:

![Enter image alt description](Images/eXO_Image_8.png)

After Updating Count:

![Enter image alt description](Images/zEf_Image_9.png)

![Enter image alt description](Images/zHm_Image_10.png)

3. **DELETE :**

Deleting the catalogue Destiny.

![Enter image alt description](Images/Zqo_Image_11.png)

4. **RENAME :**

We added a button to demonstrate RENAME function on a table name.

![Enter image alt description](Images/eVN_Image_12.png)

After button click, We get

![Enter image alt description](Images/irj_Image_13.png)

![Enter image alt description](Images/K4y_Image_14.png)

5. **WHERE CLAUSE :**

WHERE clause is used in Updating/Inserting the Author name in the database.

![Enter image alt description](Images/jcY_Image_15.png)


**CONTRIBUTIONS:**

1. **Aashmun Gupta (G2)** -
Worked on Backend development.

2. **Anmol Kumar (G1 and G2)** -
Worked on both Frontend and Backend development.

3. **Anushri Sanodia (G1)** -
Worked on Frontend Development.

4. **Deepanjali Kumari (G1)-**.
Worked on Frontend Development.

5. **Dhruv Sharma (G2) -**
Worked on Backend development.

6. **Pavani Khale (G2) -**
Worked on Backend development.

7. **Yash Patel (G1) -**
Worked on Frontend Development.

### References
Template code flask + mySQL https://github.com/febin-george/flaskapp.
Template for homepage - https://html.design/
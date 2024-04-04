# CS432

## Configuration Setup
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

#### Database Table
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

Feel free to reach out if you have any questions or issues!

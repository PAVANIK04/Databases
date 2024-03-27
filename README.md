# CS432
In config.py:

    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = '<password>'
    MYSQL_DB = '<database>'

    SECRET_KEY = '<Enter the secret key>'


run the following commands in your venv:

    pip install Flask
    pip install Flask-mysqldb

#### The table 'users' has been used

### To generate SECRET_KEY:
    
    import secrets

    secret_key = secrets.token_hex(16)
    print("Generated Secret Key:", secret_key)

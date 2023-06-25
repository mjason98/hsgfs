import psycopg2
import os
import hashlib


SCHEMA = 'gfs'


def create_conn():
    db_host = os.environ.get('DB_HOST')
    db_port = os.environ.get('DB_PORT')
    db_name = os.environ.get('DB_NAME')
    db_user = os.environ.get('DB_USER')
    db_password = os.environ.get('DB_PASSWORD')

    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        database=db_name,
        user=db_user,
        password=db_password
    )

    return conn.cursor()


def hash_string_to_sha256(string):
    # Convert the string to bytes
    string_bytes = string.encode('utf-8')

    # Create a new SHA-256 hash object
    sha256_hash = hashlib.sha256()

    # Update the hash object with the string bytes
    sha256_hash.update(string_bytes)

    # Get the hexadecimal representation of the hashed value
    hashed_value = sha256_hash.hexdigest()

    return hashed_value

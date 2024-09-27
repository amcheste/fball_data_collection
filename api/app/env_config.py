import os

DB_HOST = os.getenv('DB_HOST', default='localhost')
DB_PORT = int(os.getenv('DB_PORT', default=5432))
DB_NAME = os.getenv('DB_NAME', default='nfl_data')
DB_USER = os.getenv('DB_USER', default='nfl_data')
# TODO better way to get this?
DB_PASSWORD = os.getenv('DB_PASSWORD', default='nfl_data')
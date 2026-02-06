import os
from dotenv import load_dotenv

def load_config():
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    env_path = os.path.join(base_path, '.env')

    if os.path.exists(env_path):
        load_dotenv(env_path)

    if os.getenv('DATABASE_URL'):
        return {
            'DEBUG': True,
            'DB_URL': os.getenv('DATABASE_URL'),
            'JWT_SECRET_KEY': os.getenv('JWT_SECRET_KEY', 'dev-secret-key')
        }
    else:
        return {
            'DEBUG': True,
            'DB_URL': 'postgresql://postgres:postgres@localhost:5432/trip_planner',
            'JWT_SECRET_KEY': 'dev-secret-key'
        }
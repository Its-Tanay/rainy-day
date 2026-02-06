from app.utils.factory import create_app
from flask import g
from app.utils.config import load_config

if __name__ == "__main__":
    try:
        app = create_app()
        app.config.update(load_config())

        with app.app_context():
            app.run(host='0.0.0.0', port=3000, use_reloader=False)
    except Exception as e:
        raise

else:
    gunicorn_app = create_app()
    gunicorn_app.config.update(load_config())
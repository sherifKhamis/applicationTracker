import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    # If Render Disk is mounted at /var/data, store SQLite there, else use local folder
    render_disk_path = '/var/data'
    if os.path.exists(render_disk_path):
        sqlite_path = os.path.join(render_disk_path, 'app_tracker.db')
    else:
        sqlite_path = os.path.join(basedir, 'app_tracker.db')
        
    SQLALCHEMY_DATABASE_URI = db_url or f'sqlite:///{sqlite_path}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


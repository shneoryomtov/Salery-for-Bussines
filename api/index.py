import os
from app import create_app, db

# For Vercel serverless, use in-memory database
if os.getenv('VERCEL'):
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
else:
    os.environ.setdefault('DATABASE_URL', 'sqlite:///site.db')

app = create_app()

# Initialize database on startup
with app.app_context():
    db.create_all()


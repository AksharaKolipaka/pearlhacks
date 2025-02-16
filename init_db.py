from app import app, db

# Drop all tables and create new ones
with app.app_context():
    db.drop_all()
    db.create_all()
    print("Database has been reset successfully!") 
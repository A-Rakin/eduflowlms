# reset_db.py
import os
from app import app, db
from add_sample_data import add_sample_data


def reset_database():
    with app.app_context():
        # Drop all tables
        db.drop_all()
        print("Dropped all existing tables.")

        # Create all tables
        db.create_all()
        print("Created all tables.")

        # Add sample data
        add_sample_data()

        print("Database reset and initialized with sample data successfully!")


if __name__ == '__main__':
    # Ask for confirmation
    response = input("This will delete all existing data. Are you sure? (yes/no): ")
    if response.lower() == 'yes':
        reset_database()
    else:
        print("Operation cancelled.")
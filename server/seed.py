import json
import os
from datetime import time
from app.database.models import Base, City, Category, Cuisine, Activity, ActivityAvailability, FoodOption, FoodOptionAvailability
from sqlalchemy.orm import Session
from app.database.db import engine
from app.utils.factory import create_app

def seed_data():
    app = create_app()
    with app.app_context():
        session = Session(engine)
        
        # Load data from JSON
        seeds_path = os.path.join(os.path.dirname(__file__), 'app', 'database', 'seeds.json')
        with open(seeds_path, 'r') as f:
            data = json.load(f)

        print("Seeding Cities...")
        for item in data['cities']:
            session.merge(City(**item))

        print("Seeding Categories...")
        for item in data['categories']:
            session.merge(Category(**item))

        print("Seeding Cuisines...")
        for item in data['cuisines']:
            session.merge(Cuisine(**item))

        print("Seeding Activities...")
        for item in data['activities']:
            session.merge(Activity(**item))

        print("Seeding Food Options...")
        for item in data['food_options']:
            session.merge(FoodOption(**item))

        print("Seeding Activity Availability...")
        activity_availability = []
        for activity_id in range(16, 46):
            for day in range(7):
                if activity_id in [17, 20, 28, 32, 37]:
                    open_time = time(8, 0)
                    close_time = time(17, 0)
                elif activity_id in [18, 23, 30, 34, 42]:
                    open_time = time(10, 0)
                    close_time = time(22, 0)
                else:
                    open_time = time(9, 0)
                    close_time = time(18, 0)
                
                activity_availability.append(
                    ActivityAvailability(
                        id=len(activity_availability) + 1 + 105,
                        activity_id=activity_id,
                        day_of_week=day,
                        open_time=open_time,
                        close_time=close_time
                    )
                )

        for avail in activity_availability:
            session.merge(avail)

        print("Seeding Food Option Availability...")
        food_option_availability = []
        for food_option_id in range(16, 46):
            for day in range(7):
                if food_option_id in [18, 23, 25, 33, 37, 40]:
                    open_time = time(11, 0)
                    close_time = time(23, 59)
                    has_breakfast = False
                    has_lunch = True
                    has_dinner = True
                elif food_option_id in [22, 24, 26, 29, 32, 34, 41]: 
                    open_time = time(12, 0)
                    close_time = time(23, 0)
                    has_breakfast = False
                    has_lunch = True
                    has_dinner = True
                elif food_option_id in [16, 19, 27, 35, 38, 43]:
                    open_time = time(8, 0)
                    close_time = time(22, 0)
                    has_breakfast = True
                    has_lunch = True
                    has_dinner = True
                else: 
                    open_time = time(11, 0)
                    close_time = time(22, 30)
                    has_breakfast = False
                    has_lunch = True
                    has_dinner = True
                
                food_option_availability.append(
                    FoodOptionAvailability(
                        id=len(food_option_availability) + 1 + 105,
                        food_option_id=food_option_id,
                        day_of_week=day,
                        open_time=open_time,
                        close_time=close_time,
                        has_breakfast=has_breakfast,
                        has_lunch=has_lunch,
                        has_dinner=has_dinner
                    )
                )

        for avail in food_option_availability:
            session.merge(avail)

        session.commit()
        
        # Verification
        city_count = session.query(City).count()
        activity_count = session.query(Activity).count()
        print(f"Database seeded successfully.")
        print(f"Stats: {city_count} Cities, {activity_count} Activities.")
        
        session.close()

if __name__ == "__main__":
    seed_data()

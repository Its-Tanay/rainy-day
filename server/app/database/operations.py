from datetime import datetime, timedelta
from .models import Activity, City, FoodOption
from sqlalchemy.orm import Session
from app.database.db import engine
from functools import cmp_to_key
from datetime import datetime, time, timedelta
from sqlalchemy import delete, desc, or_, case, insert, select
from app.database.models import Activity, ActivityAvailability, FoodOption, FoodOptionAvailability, Itinerary, ItineraryActivity, ItineraryFood
from sqlalchemy.orm import Session

def generate_itinerary(params, current_user):
     # Main function to generate an itinerary based on user preferences
    with Session(engine) as session:
        # Extract parameters from the input
        start_date, end_date, city, activity_budget, activity_categories, food_budget, food_cuisines, is_veg, accessibility_needed = extract_params(params)
        # Create a new itinerary in the database
        itinerary = create_new_itinerary(session, start_date, end_date, current_user, city)
        # Query food options based on user preferences
        food_options = query_food_options(session, city, food_budget, is_veg, accessibility_needed, food_cuisines)
        # Calculate the duration of the trip
        no_of_days = calculate_trip_duration(start_date, end_date)
        # Create meal plans for the entire trip
        meal_plans = create_meal_plans(food_options, start_date, no_of_days)
        # Query activity options based on user preferences
        activity_options = query_activity_options(session, city, activity_budget, accessibility_needed, activity_categories)
        # Assign activities to the itinerary
        full_itinerary = assign_activities(meal_plans, activity_options, start_date, no_of_days)
        # Calculate the total expense of the itinerary
        total_expense = calculate_total_expense(full_itinerary)
        # Save the generated itinerary to the database
        save_itinerary_to_db(engine, itinerary.id, full_itinerary)
        
        return {"itinerary": full_itinerary, "start_date": start_date, "end_date": end_date, "total_expense": total_expense}
    
def calculate_total_expense(full_itinerary):
    total_expense = 0
    for day in full_itinerary:
        for item in day:
            total_expense += item.get("expense")
    return total_expense

def extract_params(params):
    return (
        params.get("duration").get("startDate"),
        params.get("duration").get("endDate"),
        params.get("city"),
        params.get("activityPreferences").get("budget"),
        params.get("activityPreferences").get("categories"),
        params.get("foodPreferences").get("budget"),
        params.get("foodPreferences").get("cuisines"),
        params.get("foodPreferences").get("isVeg"),
        params.get("accessibility_need")
    )

def create_new_itinerary(session, start_date, end_date, current_user, city):
    itinerary = Itinerary(
        name="Itinerary", 
        created_at=datetime.now(), 
        start_date=datetime.strptime(start_date, "%Y-%m-%d"), 
        end_date=datetime.strptime(end_date, "%Y-%m-%d"), 
        user_id=current_user,
        city_id=city
    )
    session.add(itinerary)
    session.commit()
    return itinerary

def calculate_trip_duration(start_date, end_date):
    return (datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days + 1

def query_food_options(session, city, food_budget, is_veg, accessibility_needed, food_cuisines):
    # Query food options based on user preferences for each day of the week
    foodOptions = []
    for day in range(7):
        statement = select(
            FoodOption, FoodOptionAvailability
        ).join(
            FoodOption.availabilities
        ).where(
            # Apply filters based on user preferences and requirements
            (FoodOptionAvailability.day_of_week == day) & 
            (FoodOption.city_id == city) &
            (FoodOptionAvailability.close_time > FoodOptionAvailability.open_time) &
            (FoodOption.budget_category <= food_budget) &
            (or_(is_veg == False, FoodOption.is_vegetarian == True)) &
            (or_(accessibility_needed == False, FoodOption.wheelchair_accessibility == True))
        ).order_by(
            # Order by popularity, with bonus for preferred cuisines
            desc(
                case(
                    (FoodOption.cuisine_id.in_(food_cuisines), FoodOption.popularity + 3),
                    else_ = FoodOption.popularity
                )
            )
        )

        optThatDay = []
        for obj in session.execute(statement):
            opt = obj.FoodOption.to_dict()
            opt2 = obj.FoodOptionAvailability.to_dict()
            opt2.update(opt)
            optThatDay.append(opt2)
        
        foodOptions.append(optThatDay)
    return foodOptions

def create_meal_plans(food_options, start_date, no_of_days):
    # Create meal plans for the entire trip
    allForThisTripUnsorted = []
    foodSelectsId = {}
    for i in range(no_of_days):
        delta = timedelta(days=i)
        currDate = datetime.strptime(start_date, "%Y-%m-%d") + delta

        b, l, d = None, None, None
         # First pass: Try to find unique restaurants for breakfast, lunch, and dinner
        for option in food_options[int(currDate.strftime("%w"))]:
            if b and l and d:
                break
            # Check if the restaurant is open and serves the specific meal
            # Assign the restaurant to the corresponding meal if conditions are met
            if not foodSelectsId.get(option.get('id')):
                if not b and option.get('has_breakfast') and time.fromisoformat(option.get('open_time')).hour * 60 + time.fromisoformat(option.get('open_time')).minute <= 540 and time.fromisoformat(option.get('close_time')).hour * 60 + time.fromisoformat(option.get('open_time')).minute >= 600:
                    b = option
                    foodSelectsId[option.get('id')] = True
                elif not l and option.get('has_lunch') and time.fromisoformat(option.get('open_time')).hour * 60 + time.fromisoformat(option.get('open_time')).minute <= 780 and time.fromisoformat(option.get('close_time')).hour * 60 + time.fromisoformat(option.get('open_time')).minute >= 840:
                    l = option
                    foodSelectsId[option.get('id')] = True
                elif not d and option.get('has_dinner') and time.fromisoformat(option.get('open_time')).hour * 60 + time.fromisoformat(option.get('open_time')).minute <= 1260 and time.fromisoformat(option.get('close_time')).hour * 60 + time.fromisoformat(option.get('open_time')).minute >= 1320:
                    d = option
                    foodSelectsId[option.get('id')] = True
        
        if not b or not l or not d:
            foodSelectsId.clear()
            for option in food_options[int(currDate.strftime("%w"))]:
                if b and l and d:
                    break
                if not foodSelectsId.get(option.get('id')):
                    if not b and option.get('has_breakfast') and time.fromisoformat(option.get('open_time')).hour * 60 + time.fromisoformat(option.get('open_time')).minute <= 540 and time.fromisoformat(option.get('close_time')).hour * 60 + time.fromisoformat(option.get('open_time')).minute >= 600:
                        b = option
                        foodSelectsId[option.get('id')] = True
                    elif not l and option.get('has_lunch') and time.fromisoformat(option.get('open_time')).hour * 60 + time.fromisoformat(option.get('open_time')).minute <= 780 and time.fromisoformat(option.get('close_time')).hour * 60 + time.fromisoformat(option.get('open_time')).minute >= 840:
                        l = option
                        foodSelectsId[option.get('id')] = True
                    elif not d and option.get('has_dinner') and time.fromisoformat(option.get('open_time')).hour * 60 + time.fromisoformat(option.get('open_time')).minute <= 1260 and time.fromisoformat(option.get('close_time')).hour * 60 + time.fromisoformat(option.get('open_time')).minute >= 1320:
                        d = option
                        foodSelectsId[option.get('id')] = True

        day_meals = []
        if b:
            day_meals.append({**b, "startTime": time(hour=9).strftime("%H:%M"), "endTime": time(hour=10).strftime("%H:%M"), "expense": b.get("average_price"), "type": "food"})
        if l:
            day_meals.append({**l, "startTime": time(hour=13).strftime("%H:%M"), "endTime": time(hour=14).strftime("%H:%M"), "expense": l.get("average_price"), "type": "food"})
        if d:
            day_meals.append({**d, "startTime": time(hour=21).strftime("%H:%M"), "endTime": time(hour=22).strftime("%H:%M"), "expense": d.get("average_price"), "type": "food"})
        
        allForThisTripUnsorted.append(day_meals)

    return allForThisTripUnsorted

def query_activity_options(session, city, activity_budget, accessibility_needed, activity_categories):
    # Query activity options based on user preferences for each day of the week
    activityOptions = []
    for day in range(7):
        statement = select(
            Activity, ActivityAvailability
        ).join(
            Activity.availabilities
        ).join(
            Activity.city
        ).where(
            # Apply filters based on user preferences and requirements
            (ActivityAvailability.day_of_week == day) & 
            (Activity.city_id == city) &
            (ActivityAvailability.close_time > ActivityAvailability.open_time) &
            (Activity.budget_category <= activity_budget) &
            (or_(accessibility_needed == False, Activity.wheelchair_accessibility == True))
        ).order_by(
            # Order by popularity, with bonus for preferred categories
            desc(
                case(
                    (Activity.category_id.in_(activity_categories), Activity.popularity + 3),
                    else_ = Activity.popularity
                )
            )
        )

        optThatDay = [] 
        for obj in session.execute(statement):
            opt = obj.Activity.to_dict()
            opt2 = obj.ActivityAvailability.to_dict()
            opt2.update(opt)
            optThatDay.append(opt2)
        
        activityOptions.append(optThatDay)
    return activityOptions

def assign_activities(meal_plans, activity_options, start_date, no_of_days):
     # Assign activities to the itinerary, fitting them between meals
    allForThisTrip = []
    activitySelectsId = {}

    for i in range(no_of_days):
        delta = timedelta(days=i)
        currDate = datetime.strptime(start_date, "%Y-%m-%d") + delta

        currEnd = 600  # Start after breakfast

        # Assign morning activities (between breakfast and lunch)
        for option in activity_options[int(currDate.strftime("%w"))]:
            if not activitySelectsId.get(option.get('id')):
                # Check if the activity fits in the available time slot
                if time.fromisoformat(option.get('open_time')).hour * 60 + time.fromisoformat(option.get('open_time')).minute <= currEnd and min(time.fromisoformat(option.get('close_time')).hour * 60 + time.fromisoformat(option.get('open_time')).minute, 780) >= currEnd + option.get("average_duration"):
                    # Add the activity to the day's plan
                    meal_plans[i].append({
                        **option,
                        "startTime": time(hour=int(currEnd/60), minute=int(currEnd%60)).strftime("%H:%M"),
                        "endTime": time(hour=int((currEnd+option.get("average_duration"))/60), minute=int((currEnd+option.get("average_duration"))%60)).strftime("%H:%M"),
                        "expense": option.get("average_price"),
                        "type": "activity"
                    })
                    currEnd += option.get("average_duration")
                    activitySelectsId[option.get('id')] = True

        currEnd = 840  # Start after lunch 

        # Assign afternoon activities (between lunch and dinner)
        for option in activity_options[int(currDate.strftime("%w"))]:
             # ... (similar logic as morning activities)
            if not activitySelectsId.get(option.get('id')):
                if time.fromisoformat(option.get('open_time')).hour * 60 + time.fromisoformat(option.get('open_time')).minute <= currEnd and min(time.fromisoformat(option.get('close_time')).hour * 60 + time.fromisoformat(option.get('open_time')).minute, 1260) >= currEnd + option.get("average_duration"):
                    meal_plans[i].append({
                        **option,
                        "startTime": time(hour=int(currEnd/60), minute=int(currEnd%60)).strftime("%H:%M"),
                        "endTime": time(hour=int((currEnd+option.get("average_duration"))/60), minute=int((currEnd+option.get("average_duration"))%60)).strftime("%H:%M"),
                        "expense": option.get("average_price"),
                        "type": "activity"
                    })
                    currEnd += option.get("average_duration")
                    activitySelectsId[option.get('id')] = True

        # Sort the day's activities and meals by start time
        allForThisTrip.append(sorted(meal_plans[i], key=cmp_to_key(lambda item1, item2: 
            (datetime.strptime(item1.get('startTime'), "%H:%M") - datetime.strptime(item2.get('startTime'), "%H:%M")).total_seconds()
        )))

    return allForThisTrip

def save_itinerary_to_db(engine, itinerary_id, full_itinerary):
    # Save the generated itinerary to the database
    with engine.connect() as conn:
        for i, day_itinerary in enumerate(full_itinerary):
            for obj in day_itinerary:
                if obj.get('type') == 'activity':
                    # Insert activity into ItineraryActivity table
                    statement = insert(ItineraryActivity).values(
                        itinerary_id=itinerary_id,
                        activity_id=obj.get('id'),
                        day=i,
                        start_time=datetime.strptime(obj.get('startTime'), "%H:%M"),
                        duration=obj.get('average_duration')
                    )
                    conn.execute(statement)
                elif obj.get('type') == 'food':
                    # Insert food option into ItineraryFood table
                    statement = insert(ItineraryFood).values(
                        itinerary_id=itinerary_id,
                        food_option_id=obj.get('id'),
                        day=i,
                        start_time=datetime.strptime(obj.get('startTime'), "%H:%M"),
                        duration=60
                    )
                    conn.execute(statement)
            conn.commit()

def get_itineraries_by_user(current_user):
    # Retrieve all itineraries for a given user
    with Session(engine) as session:
        statement = select(Itinerary, City).join(Itinerary.city).where(Itinerary.user_id == current_user)

        results = []

        for obj in session.execute(statement):
            results.append({
                **obj.Itinerary.to_dict(),
                "city": obj.City.name,
                "start_date": obj.Itinerary.start_date.strftime("%Y-%m-%d"),
                "end_date": obj.Itinerary.end_date.strftime("%Y-%m-%d")
            })

        return results
    
def get_itinerary_by_id(current_user, itinerary_id):
    # Retrieve a specific itinerary by its ID for a given user
    statement = select(Itinerary, City).join(Itinerary.city).where(Itinerary.id == itinerary_id)

    itinerary = {}

    with Session(engine) as session:
        res = session.execute(statement)
        for obj in res:
            print(obj.Itinerary.user_id)
            if obj.Itinerary.user_id != current_user:
                return None
            itinerary = {**obj.Itinerary.to_dict(), "city": obj.City.name}

    no_of_days = (itinerary.get('end_date') - itinerary.get('start_date')).days + 1
    allForThisTrip = []

    for i in range(no_of_days):
        allForToday = []
        # Retrieve food options for this day
        stmt = select(ItineraryFood, FoodOption).join(FoodOption).where(
            (ItineraryFood.c.itinerary_id == itinerary_id) &
            (ItineraryFood.c.day == i)
        )

        with engine.connect() as conn:
            for row in conn.execute(stmt):
                allForToday.append({
                    **row._asdict(),
                    "startTime": row._asdict().get('start_time').strftime("%H:%M"),
                    "endTime": row._asdict().get('start_time') + timedelta(
                        hours=int(row._asdict().get('duration')/60),
                        minutes=int(row._asdict().get('duration')%60)
                    ),
                    "expense": row._asdict().get('average_price'),
                    "type": "food"
                })

        # Retrieve activities for this day
        stmt = select(ItineraryActivity, Activity).join(Activity).where(
            (ItineraryActivity.c.itinerary_id == itinerary_id) &
            (ItineraryActivity.c.day == i)
        )

        with engine.connect() as conn:
            for row in conn.execute(stmt):
                allForToday.append({
                    **row._asdict(),
                    "startTime": row._asdict().get('start_time').strftime("%H:%M"),
                    "endTime": row._asdict().get('start_time') + timedelta(
                        hours=int(row._asdict().get('duration')/60),
                        minutes=int(row._asdict().get('duration')%60)
                    ),
                    "expense": row._asdict().get('average_price'),
                    "type": "activity"
                })

        # Sort the day's activities and meals by start time
        allForThisTrip.append(sorted(allForToday, key=cmp_to_key(lambda item1, item2:
            (item1.get('start_time') - item2.get('start_time')).total_seconds()
        )))

    return {
        **itinerary,
        "itinerary": allForThisTrip,
        "start_date": itinerary.get('start_date').strftime("%Y-%m-%d"),
        "end_date": itinerary.get('end_date').strftime("%Y-%m-%d")
    }

def delete_itinerary_by_id(current_user, itinerary_id):
    # Delete a specific itinerary by its ID for a given user
    with Session(engine) as session:
        itinerary = session.query(Itinerary).filter(Itinerary.id == itinerary_id, Itinerary.user_id == current_user).first()
        if not itinerary:
            return False  
        try:
            # Delete related entries in ItineraryActivity and ItineraryFood tables
            session.execute(delete(ItineraryActivity).where(ItineraryActivity.c.itinerary_id == itinerary_id))
            session.execute(delete(ItineraryFood).where(ItineraryFood.c.itinerary_id == itinerary_id))
            # Delete the itinerary itself
            session.delete(itinerary)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error deleting itinerary: {str(e)}")
            return False  
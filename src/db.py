"""
file: db.py
written by: Johan Solbakken, Morten Tobias Rinde Sunde
date: 10.10.2023

    Contains all the database functions used in the project.
    
"""

import dbconnection
import log
import performance
import datetime

"""
Singleton database connection
"""

initiated: bool = False
connector: dbconnection.DbConnector = None
client = None
db = None


def init():
    global initiated, connector, client, db
    _ = performance.Timer("(Database) Database init")
    try:
        connector = dbconnection.DbConnector()
    except Exception as e:
        log.error(f"(Database) Failed to connect to database. {e}")

    client = connector.client
    db = connector.db

    initiated = True


def shutdown():
    check_initiated()
    global initiated, connector
    _ = performance.Timer("(Database) Database shutdown")
    connector.close_connection()
    initiated = False


def check_initiated():
    global initiated
    if initiated == False:
        log.error("(Database) Not initiated. Call db.init() first.")
        raise Exception("(Database) Not initiated. Call db.init() first.")
    
def create_indexes():
    _ = performance.Timer("(Database) Creating indexes")
    if "activity" in db.list_collection_names():
        db["activity"].create_index([("altitude", 1)])  
    if "trackpoint" in db.list_collection_names():
        db["trackpoint"].create_index([("user_id", 1)])
        db["trackpoint"].create_index([("activity_id", 1)])


def nuke_database():
    global db
    check_initiated()
    _ = performance.Timer("(Database) Nuking database")
    db.drop_collection("user")
    db.drop_collection("activity")
    db.drop_collection("trackpoint")


def tables_exist():
    global db
    check_initiated()
    _ = performance.Timer("(Database) Checking if tables exist")
    users_exist = "user" in db.list_collection_names()
    activities_exist = "activity" in db.list_collection_names()
    trackpoints_exist = "trackpoint" in db.list_collection_names()
    return users_exist and activities_exist and trackpoints_exist

# -------------- Part 2 --------------

# 1.1 - users


def get_number_of_users():
    global db
    check_initiated()
    with performance.Timer("(Database) Getting number of users"):
        users_collection = db["user"]
        number_of_users = users_collection.count_documents({})
    return number_of_users

# 1.2 - activities


def get_number_of_activities():
    global db
    check_initiated()
    with performance.Timer("(Database) Getting number of activities"):
        activities_collection = db["activity"]
        number_of_activities = activities_collection.count_documents({})
    return number_of_activities

# 1.3


def get_number_of_trackpoints():
    global db
    check_initiated()
    with performance.Timer("(Database) Getting number of trackpoints"):
        trackpoints_collection = db["trackpoint"]
        number_of_trackpoints = trackpoints_collection.count_documents({})
    return number_of_trackpoints

# 2


def get_average_activities_per_user():
    global db
    check_initiated()
    with performance.Timer("(Database) Getting average activities per user"):
        activity_collection = db["activity"]
        number_of_activities = activity_collection.count_documents({})
        user_collection = db["user"]
        number_of_users = user_collection.count_documents({})
        average_activities_per_user = number_of_activities / number_of_users
    return average_activities_per_user

# 3


def get_top_users_most_activites(n: int):
    global db
    check_initiated()
    with performance.Timer(f"(Database) Getting top {n} users with most activities"):
        top_n_users_most_activities = db["activity"].aggregate([
            {"$group": {"_id": "$user_id", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": n}
        ])
    top_n_users_most_activities = [
        [user["_id"], user["count"]] for user in top_n_users_most_activities]
    return top_n_users_most_activities


# 4
def get_all_users_that_used(transportation_mode: str):
    global db
    check_initiated()
    with performance.Timer(f"(Database) Getting all users that have taken the {transportation_mode}"):
        users = db["activity"].aggregate([
            {"$match": {"transportation_mode": transportation_mode}},
            {"$group": {"_id": "$user_id"}}
        ])
    users = [[user["_id"]] for user in users]
    return users

# 5


def get_transportation_modes_count():
    """Find all types of transportation modes and count how many activities that are 
    tagged with these transportation mode labels. Do not count the rows where 
    the mode is null.

    Result ("taxi", 20), (transportation_mode, count)
    """
    global db
    check_initiated()
    with performance.Timer("(Database) Getting transportation modes count"):
        activities = db["activity"].aggregate([
            {"$group": {"_id": "$transportation_mode", "count": {"$sum": 1}}},
            {"$match": {"_id": {"$ne": ""}}},
            {"$sort": {"count": -1}}
        ])
    activities = [[activity["_id"], activity["count"]]
                  for activity in activities]
    return activities


# 6 - old
def get_all_duplicate_activities():
    assert False, "Todo: not implemented"
    global cursor
    check_initiated()
    _ = performance.Timer("(Database) Getting all duplicate activities")
    cursor.execute(Queries.duplicate_activities)
    return cursor.fetchall()
# 6.a


def get_year_with_most_activities():
    global db
    check_initiated()
    with performance.Timer("(Database) Getting year with most activities"):
        activities = db["activity"].aggregate([
            {"$group": {"_id": {"$year": "$start_date_time"}, "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 1}
        ])
    activities = [[activity["_id"], activity["count"]]
                  for activity in activities]
    return activities[0]

# 6.b


def get_year_with_most_recorded_hours():
    global db
    check_initiated()
    with performance.Timer("(Database) Getting year with most recorded hours"):
        activity_duration = db["activity"].aggregate([
            {"$group": {"_id": {"$year": "$start_date_time"}, "duration": {
                "$sum": {"$subtract": ["$end_date_time", "$start_date_time"]}}}},
            {"$sort": {"count": -1}},
            {"$limit": 1}
        ])
    activity_duration = [[activity["_id"], activity["duration"]]
                         for activity in activity_duration]
    return activity_duration[0]

 # 7
 # TODO NB VERY IMPORTANTE -> KILOMETROS!!!!!!!!!!!!
def get_activities_transportation_by_user_in_year(transportation_mode: str, user_id: int, year: int):
    global db
    check_initiated()
    with performance.Timer("(Database) Getting total distance walked by user in year"):
        activities = db["activity"].find({
            "$and": [
                {"user_id": str(user_id)},
                {"transportation_mode": transportation_mode},
                {"$expr": {"$eq": [{"$year": "$start_date_time"}, year]}}
            ]
        })
    return activities

def get_user_transportation_activity_hours_lasting_to_next_day(limit: bool = False):
    assert False, "Todo: not implemented"
    global cursor
    check_initiated()
    _ = performance.Timer(
        "(Database) Getting users with activities lasting to next day")
    if limit:
        cursor.execute(
            Queries.user_transportation_mode_activity_hours + " LIMIT 15")
    else:
        cursor.execute(Queries.user_transportation_mode_activity_hours)
    return cursor.fetchall()


def get_all_users():
    global db
    check_initiated()
    _ = performance.Timer("(Database) Getting all users")
    user = db["user"]
    return user.find({})


def get_all_activities():
    global db
    check_initiated()
    _ = performance.Timer("(Database) Getting all activities")
    activity = db["activity"]
    return activity.find({})


def get_all_trackpoints():
    global db
    check_initiated()
    _ = performance.Timer("(Database) Getting all trackpoints")
    trackpoint = db["trackpoint"]
    return trackpoint.find({})




def user_exists(user_id: str):
    global db
    check_initiated()
    _ = performance.Timer("(Database) Checking if user exists")
    user = db["user"]
    return user.find_one({"_id": user_id}) != None


def get_all_activities_for_user(user_id: str):
    global db
    check_initiated()
    _ = performance.Timer("(Database) Getting all activities for user")
    activity = db["activity"]
    return activity.find({"user_id": user_id})


def get_all_trackpoints_for_activity(activity_id: str):
    global db
    check_initiated()
    _ = performance.Timer("(Database) Getting all trackpoints for activity")
    trackpoint = db["trackpoint"]
    return trackpoint.find({"activity_id": activity_id})

def get_all_trackpoints_for_user(user_id: str):
    global db
    check_initiated()
    _ = performance.Timer("(Database) Getting all trackpoints for user")
    trackpoint = db["trackpoint"]
    return trackpoint.find({"user_id": user_id})

# 8 
def get_all_valid_trackpoints(activity_id: str):
    global db
    check_initiated()
    _ = performance.Timer("(Database) Getting all valid trackpoints")
    trackpoint = db["trackpoint"]
    return trackpoint.find({"$and": [{"activity_id": activity_id}, {"altitude": {"$ne": "-777"}}]})

# 9 All users with invalid activities



def insert_user(user_id: str, has_labels: bool):
    global db
    check_initiated()
    _ = performance.Timer("(Database) Inserting user")
    user = db["user"]
    user.insert_one({"_id": user_id, "has_labels": has_labels})


def insert_activity(id: str, user_id: str, transportation_mode: str, start_date_time: datetime.datetime, end_date_time: datetime.datetime):
    global db
    check_initiated()
    _ = performance.Timer("(Database) Inserting activity")
    activity = db["activity"]
    activity.insert_one({"_id": id, "user_id": user_id, "transportation_mode": transportation_mode,
                        "start_date_time": start_date_time, "end_date_time": end_date_time})


def insert_trackpoint(activity_id: str, lat: str, lon: str, altitude: str, date_days: str, date_time: datetime.datetime, user_id: str):
    global db
    check_initiated()
    _ = performance.Timer("(Database) Inserting trackpoint")
    trackpoint = db["trackpoint"]
    trackpoint.insert_one({"activity_id": activity_id, "lat": lat, "lon": lon,
                          "altitude": altitude, "date_days": date_days, "date_time": date_time, "user_id": user_id})


def get_distinct_transportation_modes():
    global db
    check_initiated()
    _ = performance.Timer("(Database) Getting distinct transportation modes")
    activity = db["activity"]
    return activity.distinct("transportation_mode")


def get_users_longest_distance_one_day_per_trasnsportation_mode():
    assert False, "Todo: not implemented"
    global cursor
    check_initiated()
    _ = performance.Timer(
        "(Database) Getting users longest distance one day per trasnportation mode")
    cursor.execute(
        Queries.get_users_longest_distance_one_day_per_trasnportation_mode)
    return cursor.fetchall()


def count_activities_where_user_transportation_mode(user_id: str, transportation_mode: str):
    """return count of activities for user with transportation mode"""
    global db
    check_initiated()
    _ = performance.Timer(
        "(Database) Count user activity transportation mode")
    activity = db["activity"]
    return activity.count_documents({"$and": [{"user_id": user_id}, {"transportation_mode": transportation_mode}]})


def find_user_id_from_activity_id(activity_id: str):
    assert False, "Todo: not implemented"
    global cursor
    check_initiated()
    _ = performance.Timer("(Database) Find user id from activity id")
    cursor.execute(Queries.find_user_from_activity, [activity_id])
    return cursor.fetchone()[0]

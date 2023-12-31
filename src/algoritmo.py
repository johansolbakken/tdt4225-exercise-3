"""
file: algoritmo.py
written by: Johan Solbakken, Morten Tobias Rinde Sunde
date: 10.10.2023

    Contains all the algorithms used in the project.
    
"""

import log as Log
import performance as Performance
import haversine
import model as Model
import db as Database
import random

def feet_to_meters(feet: float) -> float:
    return feet * 0.3048

def create_clusters_based_on_distance(trackpoints, min_radius_meter, min_time_sec):
    clusters = []  # Initialize an empty list to store clusters
    
    for point in trackpoints:
        # Check if the point can be added to an existing cluster
        added_to_existing = False
        for cluster in clusters:
            # Check if the point is within the minimum radius and time difference
            if all(
                haversine.haversine((point.lat, point.lon), (p.lat, p.lon)) <= min_radius_meter
                and abs((point.date_time - p.date_time).total_seconds()) <= min_time_sec
                and point.activity_id != p.activity_id
                for p in cluster
            ):
                cluster.append(point)
                added_to_existing = True
                break
        
        # If the point wasn't added to an existing cluster, create a new cluster
        if not added_to_existing:
            clusters.append([point])
    
    return clusters


def find_the_number_of_users_which_have_been_close_to_each_other_in_time_and_space(min_radius_meter: float=50, min_time_sec: float=30) -> int:
    _ = Performance.Timer("(Algoritmo) find_the_number_of_users_which_have_been_close_to_each_other_in_time_and_space")

    Log.enabled(False)

    trackpoints = Model.get_all_trackpoints()
    random.shuffle(trackpoints) # Because the dataset is really big, and we are dealing with subset, we randomize to make it interesting
    trackpoints = trackpoints[:10000] # Because this algorithm is very slow, we only use a subset of the data

    clusters = create_clusters_based_on_distance(trackpoints, min_radius_meter, min_time_sec)   

    activity_ids = set()
    for cluster in clusters:
        if len(cluster) > 1:
            for trackpoint in cluster:
                activity_ids.add(trackpoint.activity_id)

    user_ids = set()
    for activity_id in activity_ids:
        user_ids.add(Database.find_user_id_from_activity_id(activity_id))

    Log.enabled(True)

    return len(user_ids)

def calculate_activity_elevation(activity: Model.Activity) -> float:
    s = 0
    trackpoints = Model.get_all_valid_trackpoints(activity.id)
    for i in range(len(trackpoints) - 1):
        tn = trackpoints[i]
        tn1 = trackpoints[i + 1]
        if tn.altitude > tn1.altitude:
            s += tn.altitude - tn1.altitude
    return s

def find_highest_elevation(user: Model.User) -> float:
    highest = 0
    activities = Model.get_all_activities_for_user(user.id)
    progress = Performance.ProgressEstimator(len(activities), enabled=False)
    for activity in activities:
        activity_elevation = calculate_activity_elevation(activity)
        if activity_elevation > highest:
            highest = activity_elevation
        progress.increment()
        Log.enabled(True)
        progress.print()
        Log.enabled(False)
    return highest

def top_n_users_gained_most_elevation(n: int=20):
    _ = Performance.Timer("(Algoritmo) top_n_users_gained_most_elevation")
    Log.enabled(False)
    
    elevators = []
    users = Model.get_all_users()

    progress = Performance.ProgressEstimator(len(users), enabled=False)
    for user in users:
        highest_elevation = find_highest_elevation(user)
        elevators.append((user.id, feet_to_meters(highest_elevation)))
        progress.increment()
        Log.enabled(True)
        progress.print()
        Log.enabled(False)

    Log.enabled(True)

    elevators.sort(key=lambda x: x[1], reverse=True)

    return elevators[:min(n, len(elevators))]

def top_users_a_day(transportation_mode:str, limit:int=10):
    _ = Performance.Timer("(Algoritmo) top_users_a_day")
    longest = Database.get_users_longest_distance_one_day_per_trasnsportation_mode()
    longest = [l for l in longest if l[1] == transportation_mode]
    total_per_user = {}
    for user_id, _, distance in longest:
        if user_id not in total_per_user:
            total_per_user[user_id] = 0
        total_per_user[user_id] += distance
    total_per_user = [(k, v) for k, v in total_per_user.items()]
    total_per_user.sort(key=lambda x: x[1], reverse=True)
    return total_per_user[:min(limit, len(total_per_user))]

def check_invalid_activity(activity: Model.Activity) -> bool:
    delta = 5 * 60 # seconds (5 minutes)
    trackpoints = Model.get_all_trackpoints_for_activity(activity.id)
    trackpoints.sort(key=lambda x: x.date_time)
    for i in range(len(trackpoints) - 1):
        tn = trackpoints[i].date_time
        tn1 = trackpoints[i + 1].date_time
        if (tn1 - tn).total_seconds() > delta:
            return True
    return False

def users_count_invalid_activities():
    _ = Performance.Timer("(Algoritmo) users_count_invalid_activities")

    users = Model.get_all_users()
    user_invalid_map = {}

    Log.enabled(False)
    progress = Performance.ProgressEstimator(len(users), enabled=False)
    for user in users:
        count = 0
        activities = Model.get_all_activities_for_user(user.id)
        for activity in activities:
            if check_invalid_activity(activity):
                count += 1
        user_invalid_map[user.id] = count
        progress.increment()
        Log.enabled(True)
        progress.print()
        Log.enabled(False)
    Log.enabled(True)

    table = [(k, v) for k,v in user_invalid_map.items()]
    table.sort(key=lambda x: x[1], reverse=True)
    return table

def users_favorite_transportation_mode():
    _ = Performance.Timer("(Algoritmo) users_favorite_transportation_mode")

    Log.enabled(False)
    transportation_modes = Model.get_transportation_modes()
    users = Model.get_all_users()
    user_favorite_transportation_mode_hash = {}
    # should return a list of tuples (user_id, transportation_mode)
    for user in users:
        count = 0
        fav = ""
        for mode in transportation_modes:
            mode_count = Database.count_activities_where_user_transportation_mode(user.id, mode)
            if mode_count > count:
                count = mode_count
                fav = mode
        if count > 0:
            user_favorite_transportation_mode_hash[user.id] = fav
    Log.enabled(True)

    table = [(k, v) for k,v in user_favorite_transportation_mode_hash.items()]
    table.sort(key=lambda x: x[0])
    return table

def trackpoints_distance_km(trackpoints: list[Model.Trackpoint]) -> float:
    distance = 0
    for i in range(len(trackpoints) - 1):
        tn = trackpoints[i]
        tn1 = trackpoints[i + 1]
        distance += haversine.haversine((tn.lat, tn.lon), (tn1.lat, tn1.lon), unit=haversine.Unit.KILOMETERS)
    return distance

def distance_km_travedled_by_user_in_year(user_id, transportation_mode, year):
    _ = Performance.Timer("(Algoritmo) distance_km_travedled_by_user_in_year")
    Log.enabled(False)
    activities = Model.get_all_activities_for_user_for_transportation_mode_year(user_id=user_id, transportation_mode=transportation_mode, year=year)
    total_distance = 0
    for activity in activities:
        trackpoints = Model.get_all_trackpoints_for_activity(activity.id)
        total_distance += trackpoints_distance_km(trackpoints)
    Log.enabled(True)
    return total_distance

def user_has_been_within_radius_km(user_id, position, radius):
    lat, lon = position
    trackpoints = Model.get_all_trackpoints_for_user(user_id)
    for trackpoint in trackpoints:
        if haversine.haversine((trackpoint.lat, trackpoint.lon), (lat, lon), unit=haversine.Unit.KILOMETERS) <= radius:
            return True
    return False

def fetch_users_within_radius_km(position, radius):
    lat, lon = position

    users = Model.get_all_users()
    users_within_radius = []
    Log.enabled(False)
    progress = Performance.ProgressEstimator(len(users), enabled=False)
    for user in users:
        if user_has_been_within_radius_km(user.id, position, radius):
            users_within_radius.append((user.id,))
        progress.increment()
        Log.enabled(True)
        progress.print()
        Log.enabled(False)
    Log.enabled(True)
    return users_within_radius

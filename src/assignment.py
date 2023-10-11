"""
file: assignment.py
written by: Johan Solbakken, Morten Tobias Rinde Sunde
date: 10.10.2023

    Contains the assignment class which solves all the tasks.

"""

import db as Database
import log
import tabulate
import algoritmo as Algoritmo


class Assignment:
    def task_2_1(self):
        number_of_users = Database.get_number_of_users()
        log.info(f"Number of users: {number_of_users}")

        number_of_activities = Database.get_number_of_activities()
        log.info(f"Number of activities: {number_of_activities}")

        number_of_trackpoints = Database.get_number_of_trackpoints()
        log.info(f"Number of trackpoints: {number_of_trackpoints}")

    def task_2_2(self):
        average_activities_per_user = Database.get_average_activities_per_user()
        log.info(f"Average activities per user: {average_activities_per_user}")

    def task_2_3(self):
        top_20_users_activities = Database.get_top_users_most_activites(20)
        log.info("Top 20 users with most activities:")
        print(tabulate.tabulate(top_20_users_activities,
              headers=["User ID", "Number of activities"]))

    def task_2_4(self):
        users_that_have_taken_taxi = Database.get_all_users_that_used("taxi")
        log.info("Users that have taken the taxi:")
        print(tabulate.tabulate(
            users_that_have_taken_taxi, headers=["User ID"]))

    def task_2_5(self):
        top_transportation_modes = Database.get_transportation_modes_count()
        log.info("Top transportation modes:")
        print(tabulate.tabulate(top_transportation_modes,
              headers=["Transportation mode", "Count"]))

    def task_2_6_a(self):
        year_with_most_activities = Database.get_year_with_most_activities()[0]
        log.info(f"Year with most activities: {year_with_most_activities}")

    def task_2_6_b(self):
        year_with_most_recorded_hours = Database.get_year_with_most_recorded_hours()[
            0]
        log.info(
            f"Year with most recorded hours: {year_with_most_recorded_hours}")
        year_with_most_activities = Database.get_year_with_most_activities()[0]
        log.info("Is the answer from 2_6_a the year with most recorded hours the same as the year with most activities? " +
                 ("yes" if year_with_most_activities == year_with_most_recorded_hours else "no"))

    def task_2_7(self):
        total_distance_walked_by_112_in_2008 = Algoritmo.distance_km_travedled_by_user_in_year(
            112, "walk", 2008)
        log.info(
            f"Total distance walked by user 112 in 2008: {total_distance_walked_by_112_in_2008} km")

    def task_2_8(self):
        top_users_gained_most_elevation = Algoritmo.top_n_users_gained_most_elevation(
            20)
        log.info("Top 20 users gained most elevation:")
        print(tabulate.tabulate(top_users_gained_most_elevation,
              headers=["User ID", "Elevation gained (meters)"]))
    
    def task_2_9(self):
        user_invalid_count = Algoritmo.users_count_invalid_activities()
        log.info("Users with invalid activities:")
        print(tabulate.tabulate(user_invalid_count, headers=[
                "User ID", "Number of invalid activities"]))
        
    def task_2_10(self):
        users_within_rad = Algoritmo.fetch_users_within_radius_km((39.916, 116.397), 10)
        log.info("Users within radius of 10 km from lat: 39.916, lon: 116.397:")
        print(tabulate.tabulate(users_within_rad, headers=["User ID"]))

    def task_2_11(self):
        user_favorite_transportation_mode = Algoritmo.users_favorite_transportation_mode()
        log.info("Users favorite transportation mode:")
        print(tabulate.tabulate(user_favorite_transportation_mode,
              headers=["User ID", "Transportation mode"]))

    def comp(x):
        parts = x.split("_")
        num1 = int(parts[1])
        num2 = int(parts[2])

        return num1 * 100 + num2

    def methods(self):
        methods = [method for method in dir(self) if callable(
            getattr(self, method)) and method.startswith("task")]
        methods.sort(key=Assignment.comp)
        return methods

    def format_title(self, title: str) -> str:
        tokens = title.split("_")

        tokens[0] = "Task"

        # insert "." between every pair of numbers
        for i in range(1, len(tokens)):
            if tokens[i].isdigit() and tokens[i - 1].isdigit():
                tokens[i] = f".{tokens[i]}"

        out = " ".join(tokens)
        out = out.replace(" .", ".")

        return out

"""
file: performance.py
written by: Johan Solbakken, Morten Tobias Rinde Sunde
date: 10.10.2023

    Contains a timer class that can be used to time functions.

"""

import datetime

import config
import log

def print_timer(timer):
    end = datetime.datetime.now()
    duration = end - timer.start

    if duration.total_seconds() < 1:
        duration = duration.total_seconds() * 1000
        log.timer("{} took {:.2f}ms".format(timer.name,duration))
    elif duration.total_seconds() < 60:
        duration = duration.total_seconds()
        log.timer("{} took {:.2f}s".format(timer.name,duration))
    elif duration.total_seconds() < 60 * 60:
        duration = duration.total_seconds() / 60
        log.timer("{} took {:.2f}m".format(timer.name,duration))
    else:
        duration = duration.total_seconds() / 60 / 60
        log.timer("{} took {:.2f}h".format(timer.name,duration))

class Timer:
    def __init__(self, name:str, func=lambda timer: print_timer(timer)) -> None:
        self.name = name
        self.start = datetime.datetime.now()
        self.__func = func

    def __del__(self):
        if config.PERFORMANCE_TESTING:
            self.__func(self)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return

class ProgressEstimator:
    def __init__(self, total, enabled=True) -> None:
        self.__start = datetime.datetime.now()
        self.__last = self.__start
        self.__count = 0
        self.__total = total
        self.__times = []
        self.__enabled = enabled

    def increment(self):
        self.__count += 1

    def estimate(self):
        now = datetime.datetime.now()
        delta = now - self.__last
        self.__last = now
        self.__times.append(delta.total_seconds())
        mean = sum(self.__times) / len(self.__times)
        return (self.__total - self.__count) * mean
    
    def print(self):
        if not self.__enabled:
            return
        seconds = self.estimate()
        time_string =""
        if seconds < 1:
            duration = seconds * 1000
            time_string = "{:.2f}ms".format(duration)
        elif seconds < 60:
            duration = seconds
            time_string = "{:.2f}s".format(duration)
        elif seconds < 60 * 60:
            duration = seconds / 60
            time_string = "{:.2f}m".format(duration)
        else:
            duration = seconds / 60 / 60
            time_string = "{:.2f}h".format(duration)

        log.progress("Progress: {:.2f}% (estimated: {})".format(self.__count / self.__total * 100, time_string))
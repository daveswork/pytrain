
from datetime import datetime, timedelta

def time_difference(first_time, second_time):
    """
    Returns the difference between two epoch times in seconds.
    Where:
    first_time = type(int) 
    second_time = type(int)
    Returns the number of seconds difference:
    time_delta = type(int)
    """
    time_delta = second_time - first_time
    return time_delta

def convert_seconds(seconds):
    """
    Takes number of seconds, as integers.
    Returns formatted time.
    Input: int (number of seconds)
    Sample output:
    >>> mta_output_formatting.convert_seconds(600)
    datetime.timedelta(seconds=600)
    >>> print(mta_output_formatting.convert_seconds(600))
    0:10:00
    >>> 

    """
    return timedelta(seconds=seconds)

if __name__ == "__main__":
    pass
    # print(convert_seconds(time_difference(1725639005, 1725639245)))

import time
from datetime import datetime
import pytz
import secrets

def getTimeNow(timezone='Asia/Bangkok', format="%Y-%m-%d %H:%M:%S"):

    # Get the current UTC timestamp using time.time()
    timestamp_utc = time.time()

    # Convert the UTC timestamp to a datetime object in the UTC timezone
    dt_utc = datetime.utcfromtimestamp(timestamp_utc).replace(tzinfo=pytz.UTC)

    # Define the GMT+7 timezone
    gmt_plus_7 = pytz.timezone(timezone)  # Adjust 'Asia/Bangkok' based on your specific GMT+7 location

    # Convert the UTC datetime to GMT+7
    dt_gmt_plus_7 = dt_utc.astimezone(gmt_plus_7)

    # Format the datetime object as a string in the desired format
    formatted_datetime = dt_gmt_plus_7.strftime(format)

    return formatted_datetime

def generateRandomString(length):
    return ''.join(secrets.choice('0123456789') for _ in range(length))

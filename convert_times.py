from datetime import date, datetime

from dateutil import parser, tz
from dateutil.relativedelta import WE, relativedelta

mt = tz.gettz('US/Mountain')
ct = tz.gettz('US/Central')
et = tz.gettz('US/Eastern')

def get_next_wednesday():
    """
    Utility function to help generate a weekday in the future.
    Wednesdays were chosen because they are rarely holidays 
    with special schedules.
    """
    today = date.today()
    delta = relativedelta(days=1, weekday=WE(1))
    next_wednesday = today + delta
    return next_wednesday


def create_timestamp(str_time, tz=None):
    """
    Args:
        str_time (str): Time to convert. 
            Expects hours and minutes to be specified. Seconds are optional.
            If AM/PM is not specified, a 24-hour clock is assumed.
            If tz is not given, a 3-letter time zone (e.g., EDT, CDT, MDT) 
            must be specified after the time.

        tz (str, optional): 3-character timezone string.
    Returns:
        int: a POSIX timestamp (seconds from January 1, 1970 UTC)
             representing str_time next Wednesday.
    """

    tzinfo = {'EDT': et,
              'CDT': ct,
              'MDT': mt}
    if tz:
        str_time = str_time + ' ' + tz
    n = get_next_wednesday()
    full_dt = str(n) + ' ' + str_time
    timestamp = datetime.timestamp(parser.parse(full_dt, tzinfos=tzinfo))
    return int(timestamp)


def test_functions():
    """
    To test conversions, modify the code here, then run the function.
    Expected result is 07:30:00-06:00 for the next Wednesday 
    from when function is run.
    """
    conversion_1 = create_timestamp('7:30:00 MDT')
    conversion_2 = create_timestamp('7:30', 'MDT')
    print(datetime.fromtimestamp(conversion_1, tz=mt))
    print(datetime.fromtimestamp(conversion_2, tz=mt))

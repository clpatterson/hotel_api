from datetime import timedelta, date
from calendar import monthrange
from dateutil.relativedelta import relativedelta

def daterange(start_date, end_date):
    """Generate a date for each day in a date range."""
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

# Cribbed from https://stackoverflow.com/questions/1060279
# Daterange usage:
#
# start_date =  date.today() #date(2013, 1, 1)
# end_date = date(2021, 6, 2)
# for single_date in daterange(start_date, end_date):
#     print(single_date.strftime("%Y-%m-%d"))
#     print(type(single_date))

def month_end(date_object):
    """Round a date up to end of the month."""
    last_of_month = monthrange(date_object.year, date_object.month)[1]
    month_end = date(date_object.year, date_object.month, last_of_month)
    return month_end

# # Test month_end()
# print(month_end(date(2020, 12, 18)))

def months_out(start_date, months):
    """Calculate months out rounded to the end of the month."""
    months_out = month_end(start_date + relativedelta(months=+months))
    return months_out

# # Test months_out()
# print(months_out(date.today(), 8))
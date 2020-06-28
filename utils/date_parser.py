import datetime
import pytz
date_pattern = ['%Y-%m-%d', 
                    '%a, %d %b %Y %H:%M:%S %z', 
                    '%a, %d %b %Y %H:%M:%S %Z', 
                    '%Y-%m-%dT%H:%M:%S%z',
                    '%a,%d %b %y %H:%M:%S %z',
                    '%a, %d %b %y %H:%M:%S %z',
                    '%a %b %d %H:%M:%S %z %Y']

def get_date_from_str(datestr):
    date = None
    if datestr:
        try:
            date = datetime.datetime.fromisoformat(datestr)
        except:
            for pattern in date_pattern:
                try:
                    date = datetime.datetime.strptime(datestr, pattern)
                    break
                except:
                    continue
    if date and date.tzinfo is None:
        tz = "Africa/Abidjan"
        if "IST" in datestr:
            tz = "Asia/Kolkata"

        date = date.replace(tzinfo=pytz.timezone(tz))
    return date

if __name__=="__main__":
    date_str = "Thu Feb 06 16:02:31 +0000 2020"
    print(get_date_from_str(date_str))
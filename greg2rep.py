from datetime import datetime, timedelta
import pandas as pd


rural_day_names = pd.read_csv('ruralDayNames.csv', header=None, squeeze=True)
french_rep_months = pd.read_csv('frenchRepublicanMonths.csv', header=None, squeeze=True)


def greg2rep(gregDate):
    """
    Convert a Gregorian date to a French Republican date.

    Usage:
        outString = greg2rep(gregDate)

    Input:
        gregDate: A date in the Gregorian calendar, given as a datetime object

    Output:
        outString: A string representing the given date in the French
                   Republican calendar, in the format:
                   <day of month> <month> <year>; <rural day name>

    The rural day name is given in English, following the translation
    in Wikipedia, https://en.wikipedia.org/wiki/French_Republican_calendar#Rural_calendar
    as it appeared on 19 Thermidor 230 (August 6, 2022).
    The month name is given in French, with a translation to English on
    the 1st of each month.
    The complementary days are given in French with an English translation.

    Conversion from Gregorian to Republican dates is done according to the
    Equinox method for the years 1-15 of the Republic (1792-1805). From year
    15 on, the Romme method is used. For further explanation, see
    https://en.wikipedia.org/wiki/French_Republican_calendar#Converting_from_the_Gregorian_Calendar
    (accessed 19 Thermidor 230 (August 6, 2022)).

    Dates before initiation of the calendar (22-09-1792) return NaN.
    """

    # Calculate the difference between the input day and first day of Republican calendar
    rep_calendar_first_day = datetime(1792, 9, 22)
    days_since_first_day = (gregDate - rep_calendar_first_day).days

    if days_since_first_day < 0:
        return float('nan')

    # Leap year calculation. 
    # Follows the equinox method during the years of the Republic, 
    # and the Romme method afterwards
    is_rep_leap_year = lambda year: (year in [3, 7, 11]) or (year > 14 and year % 4 == 0 and (year % 100 != 0 or year % 400 == 0))
    days_in_rep_year = lambda year: 365 + is_rep_leap_year(year)

    # Find the Republican year of the given date 
    day_count = 0
    rep_year = 1  # Republican year at the given date
    first_day_of_year = rep_calendar_first_day

    while day_count + days_in_rep_year(rep_year) <= days_since_first_day:
        day_count += days_in_rep_year(rep_year)
        first_day_of_year += timedelta(days=days_in_rep_year(rep_year))
        rep_year += 1

    # Find the Republican date
    rep_day_of_year = (gregDate - first_day_of_year).days + 1  # Republican day of year
    rep_month = (rep_day_of_year - 1) // 30 + 1                # Republican month
    rep_day_of_month = (rep_day_of_year - 1) % 30 + 1          # Republican day of month

    # Load the rural day name 
    rural_day_name = rural_day_names.iloc[0][rep_day_of_year - 1]

    # Create output string
    if rep_month < 13:
        rep_month_name = french_rep_months.iloc[0][rep_month - 1]
        if rep_day_of_month == 1:
            new_month = f' ({french_rep_months.iloc[1][rep_month - 1]})'
        else:
            new_month = ''
        outString = f'{rep_day_of_month} {rep_month_name}{new_month} {rep_year}; {rural_day_name}'
    else:
        outString = f'{rural_day_name} {rep_year}'

    return outString


def create_french_republican_ical_calendar(start_date=None, end_date=None, output_file=None):
    """
    Create an iCalendar (.ics) file with French Republican dates.

    Usage:
    createFrenchRepublicaniCalendar(startDate, endDate, outputFile)
    Inputs:
    startDate       Date where iCalendar starts (in dd-mm-yyyy format)
                    If no argument is given, '01-01-2023' is used
    endDate         Date where iCalendar end (in dd-mm-yyyy format)
                    If no argument is given, '31-12-2023' is used
    outputFile      File name for the created iCal file.
                    If no argument is given, the name
                    FrenchRepublicanCalendar_<startDate>-<endDate>.ics
                    will be used.
                    The function will not allow overwriting, so if
                    outputFile already exists, an error will be thrown.
    
    The funcion creates an iCalendar (.ics) file that has for each day within the range, 
    an event with the following properties:
    Status: free
    Reminder: none
    Duration: all day
    Name: <day of month> <month> <year>; <rural day name>
        with day of month, month, year, and rural day name 
        according to the French Republican calendar.
        The rural day name is given in English, following the translation
        in Wikipedia, https://en.wikipedia.org/wiki/French_Republican_calendar#Rural_calendar
        as it appeared on 19 Thermidor 230 (August 6, 2022).
        The month name is given in French, with a translation to English on
        the 1st of each month.
        The complementary days are given in French with an English
        translation.
    Conversion from Greogrian to Republican dates is done according to the
    Equinox method for the years 1-15 of the Republic (1792-1805). From year
    15 on, the Romme method is used. Dates before initiation of
    the calendar (22-09-1792) will appear as NaN.
    """
    # Set default parameters
    if start_date is None or start_date == '':
        start_date = '01-01-2023'
    if end_date is None or end_date == '':
        end_date = '31-12-2023'
    if output_file is None or output_file == '':
        output_file = f'FrenchRepublicanCalendar_{start_date.replace("-", "")}-{end_date.replace("-", "")}.ics'

    if not output_file.endswith('.ics'):
        output_file += '.ics'

    start_date = datetime.strptime(start_date, '%d-%m-%Y')
    end_date = datetime.strptime(end_date, '%d-%m-%Y')

    # Create output file
    with open(output_file, 'w') as file_id:
        cal_start = start_date.strftime('%Y%m%dT000000')
        cal_end = end_date.strftime('%Y%m%dT000000')
        cal_name = 'French Republican'

        file_id.write(f'BEGIN:VCALENDAR\n'
                     f'PRODID:-//Microsoft Corporation//Outlook 16.0 MIMEDIR//EN\n'
                     f'VERSION:2.0\n'
                     f'METHOD:PUBLISH\n'
                     f'X-CALSTART:{cal_start}\n'
                     f'X-CALEND:{cal_end}\n'
                     f'X-WR-CALNAME:{cal_name}\n')

        for day in (start_date + timedelta(n) for n in range((end_date - start_date).days + 1)):
            file_id.write(f'BEGIN:VEVENT\n'
                         f'CLASS:PUBLIC\n'
                         f'DTEND;VALUE=DATE:{(day + timedelta(days=1)).strftime("%Y%m%d")}\n'
                         f'DTSTART;VALUE=DATE:{day.strftime("%Y%m%d")}\n'
                         f'PRIORITY:5\n'
                         f'SEQUENCE:0\n'
                         f'SUMMARY;LANGUAGE=en-gb:{greg2rep(day)}\n'
                         f'TRANSP:TRANSPARENT\n'
                         f'X-MICROSOFT-CDO-BUSYSTATUS:FREE\n'
                         f'X-MICROSOFT-CDO-IMPORTANCE:1\n'
                         f'X-MICROSOFT-DISALLOW-COUNTER:FALSE\n'
                         f'X-MS-OLK-CONFTYPE:0\n'
                         f'END:VEVENT\n')

        file_id.write('END:VCALENDAR')
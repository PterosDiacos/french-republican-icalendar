from greg2rep import create_french_republican_ical_calendar

if __name__ == '__main__':
    for year in range(2024, 2028):
        create_french_republican_ical_calendar(f'01-01-{year}', f'31-12-{year}')

#!/usr/bin/env python
# coding: utf-8

def build_url(**kwargs):
    """Format URL using event, gender and year
    Return all electronic-timed results with any wind reading
    """

    try:

        url = 'https://worldathletics.org/records/toplists/'
        url += kwargs.get('category') + '/'
        url += kwargs.get('event') + '/outdoor/' 
        url += kwargs.get('gender') + '/senior/' 
        url += str(kwargs.get('year'))
        url += '?regionType=world&timing=electronic&windReading=all&page='
        url += str(kwargs.get('page')) + '&bestResultsOnly=false'
        return url

    except Exception as e:

        print ('build_url', e)
        return None


def find_category(**kwargs):
    """Find category for event
    """
    
    categories = {'sprints': ['100-metres', '200-metres', '400-metres'],
                  'middle-long': ['800-metres', '1500-metres', '5000-metres', '10000-metres',
                                  '3000-metres-steeplechase'],
                  'hurdles': ['100-metres-hurdles' ,'110-metres-hurdles', '400-metres-hurdles'],
                  'road-running': ['marathon'],
                  'jumps': ['high-jump', 'pole-vault', 'long-jump', 'triple-jump'],
                  'throws': ['shot-put', 'javelin-throw', 'discus-throw', 'hammer-throw']}

    event = kwargs.get('event')
    
    for category, events in categories.items():
        if event in events:
            return category


def get_page(**kwargs):
    """Retrieve Table from World Athletics and format columns
    """

    import pandas as pd
    from datetime import datetime
    import re

    try:

        dfs = pd.read_html(kwargs.get('url'))
        df = dfs[0].dropna(how='all', axis=1)
        df = df.drop(columns=['Rank'])
        
        df.rename(columns={'WIND': 'Wind'}, errors='raise')

        df['DOB'] = df['DOB'].apply(lambda x: pd.to_datetime(x) if len(str(x))>4 else None)
        df['Date'] = pd.to_datetime(df['Date'])

        pattern = re.compile(r'(?P<place>\d*)(?P<stage>[a-zA-Z]*)(?P<section>\d*)')
        df['Place'] = df['Pos'].apply(lambda x: pattern.match(str(x)).groupdict()['place'])
        df['Stage'] = df['Pos'].apply(lambda x: pattern.match(str(x)).groupdict()['stage'])
        df['Section'] = df['Pos'].apply(lambda x: pattern.match(str(x)).groupdict()['section'])

        return df

    except Exception as e:

        return None


def get_event(**kwargs):
    """Continue to retrieve pages from World Athletics until end of pages reached
    """

    import pandas as pd
    import time

    data = pd.DataFrame()

    page = 1
    valid = True

    while valid:

        try:

            event = kwargs.get('event')
            gender = kwargs.get('gender')
            year = kwargs.get('year')
            category = find_category(event=event)

            url = build_url(event=event, category=category, gender=gender, year=year, page=page)
            df = get_page(url=url)
            df['Event'] = event
            df['Gender'] = gender

            data = pd.concat([data, df], axis=0)

            page += 1
            time.sleep(1)

        except Exception as e:
            
            #print ('get_event', e)
            valid = False

    return data


def save_performances(**kwargs):
    """Save event results to csv
    Encode as UTF-16 to accept international characters in competitor and venue names
    """

    try:

        event = kwargs.get('event')
        gender = kwargs.get('gender')
        year = kwargs.get('year')
        
        df = get_event(event=event, gender=gender, year=year)

        if df.shape[0] > 0:
            df.to_csv(f'{year}-{event}-{gender}.csv', index=False, encoding='utf-16')
        
    except Exception as e:
        
        print ('save_performances', e)


# # Main Program

events = ['100-metres', '200-metres'
          '400-metres', '800-metres', '1500-metres', 
          '100-metres-hurdles' ,'110-metres-hurdles', 
          '400-metres-hurdles', '3000-metres-steeplechase', 'marathon',
          '5000-metres', '10000-metres', 'high-jump', 'pole-vault', 'long-jump',
          'triple-jump', 'shot-put', 'javelin-throw', 'discus-throw', 'hammer-throw'
         ]

for event in events:

    for gender in ['men', 'women']:

        for year in range(2023, 2022, -1):

            print (f"{year} {gender}'s {event.replace('-', ' ')}")

            save_performances(event=event, gender=gender, year=year)

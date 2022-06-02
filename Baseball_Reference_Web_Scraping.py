# Import Libraries
from bs4 import BeautifulSoup
import datetime as dt
import pandas as pd
import numpy as np

# Access URL for MLB schedule
url = 'https://www.baseball-reference.com/leagues/MLB-schedule.shtml'
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# Get the appropriate section of the HTML code that contains the schedule
# Note that the following div id may change so you may have to check the HTML on the site
games = soup.find(id="div_2105697004")

# Initialize variables
main = games.find_all("div")
date = ''
time = ''
home = ''
away = ''
schedule_list = [['Day Of Week', 'Date', 'Time', 'Home', 'Away','Spring Flag']]
weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
springflag = 0

# For each game we want to know Day of Week, Date, Time (7:00 pm if game already happened), Home team, Away team
# Loop over every day
for day in main:
    # Scrape date
    date = str(day.find("h3"))
    date = date[date.find('>')+1:date.rfind('<')]
    # Format date and pull out day of week
    # If bringing into Tableau or something we may not even need to format date and can just leave it as long string
    # Special case: For today's date, we need to manually get the date and day of week
    if date == '<span id="today">Today\'s Games</span>':
        dayofweek = weekdays[dt.datetime.today().weekday()]
        date = dt.datetime.today().date()   
    else:
        dayofweek = date[:date.find(',')]
        date = dt.datetime.strptime(date, '%A, %B %d, %Y').date()
    # Loop over every game within the given day
    for game in day.find_all('p', class_ = 'game'):
        # Scrape time
        # We need to make an if-else statement to deal with time because games that have already been played don't have gametimes listed on the website
        if game.find("span", {"tz": "E"}):
            time = str(game.find("strong"))
            time = time[time.find('>')+1:time.rfind('<')]
        else:
            time = '7:00 pm'
        # Flag spring training games
        if 'Spring' in game.text:
            springflag = 1
        else:
            springflag = 0
        # Scrape both home and away before formatting them
        away = game.find("a")
        home = away.find_next("a")
        away = str(away)
        away = away[away.find('>')+1:away.rfind('<')]
        home = str(home)
        home = home[home.find('>')+1:home.rfind('<')]
        # Append each game to the MLB Schedule List
        schedule_list.append([dayofweek, date, time, home, away, springflag])
        
# Convert MLB Schedule list to DataFrame
schedule = pd.DataFrame(schedule_list)
new_header = schedule.iloc[0] #grab the first row for the header
schedule = schedule[1:] #take the data less the header row
schedule.columns = new_header #set the header row as the df header

# Assign 7pm as default time when gametime isn't provided
schedule['Time'].loc[schedule['Time']=='PPD'] = '7:00 pm'
schedule['Time'].loc[schedule['Time']=='TBD'] = '7:00 pm'

# add in datetime for calcs
schedule['Date'] = schedule['Date'].apply(lambda x: dt.datetime.strftime(x,'%Y-%m-%d'))
schedule["Datetime"] = pd.to_datetime(schedule["Date"]+' '+schedule["Time"])
schedule['Date'] = pd.to_datetime(schedule['Date']).dt.date

# Add flag for games occurring at alternate sites (i.e., Japan series, London series)
schedule['Special Flag'] = int(0)
# # Japan series
# schedule.loc[np.logical_and(schedule.Home == 'Oakland Athletics',schedule.Date == dt.datetime(2019,3,20).date()), 'Special Flag'] = int(1)
# schedule.loc[np.logical_and(schedule.Home == 'Oakland Athletics',schedule.Date == dt.datetime(2019,3,21).date()), 'Special Flag'] = int(1)
# # London series
# schedule.loc[np.logical_and(schedule.Home == 'Boston Red Sox',schedule.Date == dt.datetime(2019,6,29).date()), 'Special Flag'] = int(1)
# schedule.loc[np.logical_and(schedule.Home == 'Boston Red Sox',schedule.Date == dt.datetime(2019,6,30).date()), 'Special Flag'] = int(1)

# Add flag for last game of homestead
schedule['Last Game of Homestead Flag'] = int(0)
teams = stadium_df['Team'].tolist()

# Loop through each team's schedule flagging the last game of a homestead
for team in teams:
    team_sched = schedule.loc[np.logical_or(schedule.loc[:,'Home'] == team,schedule.loc[:,'Away']==team)]
    temp = '' # MLB doesn't do one-game series so a team's first game won't be the last of the homestead
    for i, row in team_sched.iterrows():
        if row['Home'] != team and temp == team:
            schedule.at[prev_game,'Last Game of Homestead Flag'] = int(1)
        temp = row['Home']
        prev_game = i
        
# Add flag for stadiums that are domes
schedule['Dome Flag'] = int(0)
schedule.loc[schedule.Home == 'Toronto Blue Jays', 'Dome Flag'] = int(1)
schedule.loc[schedule.Home == 'Arizona Diamondbacks', 'Dome Flag'] = int(1)
schedule.loc[schedule.Home == 'Seattle Mariners', 'Dome Flag'] = int(1)
schedule.loc[schedule.Home == 'Milwaukee Brewers', 'Dome Flag'] = int(1)
schedule.loc[schedule.Home == 'Houston Astros', 'Dome Flag'] = int(1)
schedule.loc[schedule.Home == 'Miami Marlins', 'Dome Flag'] = int(1)
schedule.loc[schedule.Home == 'Tampa Bay Rays', 'Dome Flag'] = int(1)

# Remove games that are not going to be considered with algorithm
# indexNames = schedule[(schedule['Spring Flag'] == int(1)) | (schedule['Special Flag'] == int(1)) | ((schedule['Last Game of Homestead Flag'] == int(1)) & (schedule['Dome Flag'] == int(0)))].index
indexNames = schedule[(schedule['Spring Flag'] == int(1)) | (schedule['Special Flag'] == int(1))].index
schedule.drop(indexNames, inplace=True)

# Remove games that have already happened
schedule = schedule[schedule['Date'] >= dt.datetime.today().date()]

schedule['Date'] = pd.to_datetime(schedule['Date']).dt.normalize()

# sort schedule dataframe by datetime column
schedule = schedule.sort_values(by=["Datetime","Park"])
schedule = schedule.reset_index(drop=True)

# Write MLB Schedule DataFrame to a CSV
export_csv = schedule.to_csv('C:\\Users\\npage\\Downloads\\MLB_Schedule_2022.csv')
print(export_csv)
# ALL FUNCTIONS FOR MLB TOUR NOTEBOOK

# Import the appropriate libraries
import requests
import datetime as dt
import pandas as pd
import numpy as np
import seaborn as sns
import os
import time
import config

pd.options.display.max_columns = 100


#==================================================================================
        
# original distance formula from https://github.com/dabillox/pyprojects/blob/master/citydistance.py
# edited to work with my list

# get_distance() takes in the latitude and longitude for two different locations and returns the distance in miles between these two locations.
# This will be used to calculate the distances between each park as well as the distances between each park and each weather station, so that we can choose the closest weather station to a given park to estimate rain probabilities.
def get_distance(lat_A,lng_A,lat_B,lng_B):
    
#     (lat_A,lng_A) = locA
#     (lat_B,lng_B) = locB
     
    #use haversine forumla
    earth_rad = 6371.0                 # in kilometers
    dlat = np.deg2rad(lat_B - lat_A)
    dlon = np.deg2rad(lng_B - lng_A)
   
    a = np.sin(dlat/2) * np.sin(dlat/2) + \
        np.cos(np.deg2rad(lat_A)) * np.cos(np.deg2rad(lat_B)) * \
        np.sin(dlon/2) * np.sin(dlon/2) 
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
                                           
    distance = earth_rad * c 
    #convert to miles
    distance = distance *  0.621371192 
     
    return distance

#=====================================================================================

# convert_weather_dates() is a very specific function that takes in a date value in string form and attempts to convert to a date datatype.
# This is used when cleaning the weather data because February 29 does not occur every year, so we need a function to account for this in our lambda function that we will use later in the weather DataFrame.
def convert_weather_dates(date_value):
    try:
        return dt.datetime.strptime(date_value, '%m-%d-%Y').date()
    except:
        return 'DELETE'
    
#==========================================================================================

# daterange() will be used to create a "date index" field.
# The function takes in two dates and returns an integer index for each date between those two dates.
# This will make it easier to identify when games are being played in each park without having to deal with date datatypes which can sometimes be difficult to work with.
def date_range(start_date, end_date):
    # We want to create a dataframe mapping dates to indexes for the hashset
    for n in range(int((end_date - start_date).days)):
        yield start_date + dt.timedelta(n)
        
#================================================================================

# order_available_parks() is one of the most important functions in the algorithm.
# It takes in the current park that we are at, the remaining parks on the schedule, and the remaining parks on the schedule that also fall in the same region as the current park.
# This function returns a DataFrame of possible next parks.
def order_available_parks(currentPark, remainingParks, remainingParksInRegion):
    # Only consider parks that are in the same region if any exist
    # If no more parks remain in region, move onto new region
    if len(remainingParksInRegion)==0:
        availableParks = config.stadium_df[config.stadium_df['Park'].isin(remainingParks)]
    else:
        availableParks = config.stadium_df[config.stadium_df['Park'].isin(remainingParksInRegion)]
    
    # filter anything out that is over the cutoff drive unless nothing remains
    column_header = 'd_' + currentPark.replace(' ','_').replace('-','_')
    cutoff = availableParks.loc[availableParks[column_header] <= config.cutoffDrive]
    if cutoff.empty==False:
        availableParks = cutoff
    
    # Order available parks by distance to current park
    bubble_sort(availableParks,column_header)
    
    return availableParks

#=================================================================================

# bubble_sort() takes in a DataFrame to be re-ordered and the column that will be used to determine the re-ordering.
# This will be used once we know the distances between parks so that we can order them from closest to furthest, making it easier to determine which park to choose next.
def bubble_sort(df,column):
    # We set swapped to True so the loop looks runs at least once
    swapped = True
    df = df.reset_index(drop=True)
    while swapped:
        swapped = False
        for i in range(len(df)-1):
            if df[column][i] > df[column][i + 1]:
                # Swap the elements
                temp = df.iloc[i].copy()
                df.iloc[i] = df.iloc[i+1]
                df.iloc[i+1] = temp
                # Set the flag to True so we'll loop again
                swapped = True
    df = df.reset_index(drop=True)

#====================================================================================

# time_on_road() takes in the distance in miles between two points and a parameter that we can set that represents the average speed for the car to go on the average drive.
def time_on_road(miles,avgSpeed):
    minutesToGo = (miles/avgSpeed)*60
    return minutesToGo

#======================================================================================

# short_long_drives calcules the shortest and longest drives (time and miles) depending on what we are asking the function to calculate
def short_long_drives(df, duration='short', dist_type='miles'):
    if duration == 'short':
        minDrive = df['Distance From Last Park'].loc[df['Distance From Last Park']>0].min()
        if dist_type == 'miles':
            return minDrive
        elif dist_type == 'minutes':
            minTimeOnRoad = time_on_road(minDrive,config.avgSpeed)
            return minTimeOnRoad
    elif duration == 'long':
        maxDrive = df['Distance From Last Park'].max()
        if dist_type == 'miles':
            return maxDrive
        elif dist_type == 'minutes':
            maxTimeOnRoad = time_on_road(maxDrive,config.avgSpeed)
            return maxTimeOnRoad

#===================================================================================

def find_route(baseball_df, park, date_index_start=0, date_index_end=1, hashset=[]):
    start_time = time.time()
    allRoutes = []
    for index in range(date_index_start,date_index_end):
        # Check if there is a game at the starting park on this particular index
        # If there is no game, go to next possible start date
        # If there is a game, initialize the final schedule list and append this game
        if park in hashset[index]:
            total_distance = 0
            total_days = pd.to_timedelta('0 days')
            firstGame = baseball_df.loc[(baseball_df["Park"]==park) & (baseball_df["Index"]==index)]
            finalScheduleR = [["Index","Date","Time","Datetime","Team","Park","Address","Latitude","Longitude","Region","Dome Flag","Last Game of Homestead Flag","Double Header Flag",'Rain Probability','Distance From Last Park','Total Distance','Days Since Last Park','Total Days']]
            finalScheduleR.append(firstGame.min().values.flatten().tolist() + [0,0,0,0])
            try:
                # Append games to final schedule list one by one until the schedule is complete
                while len(finalScheduleR) < 31:
                    # currDate is used as a starting point when looping through potential game options
                    currDateIndex = finalScheduleR[len(finalScheduleR)-1][0] + 1
                    # before moving onto a new region, we have to visit all parks in the current region first
                    # current region is the region of the current park
                    currentRegion = finalScheduleR[len(finalScheduleR)-1][9]
                    # the last park we chose is now the currentPark in the algorithm
                    currentPark = finalScheduleR[len(finalScheduleR)-1][5]
                    # list out remaining parks
                    chosenParks = [park[5] for park in finalScheduleR[1:]]
                    remainingParks = [park for park in config.stadium_df['Park'] if park not in chosenParks]
                    # list out remaining parks in currentRegion
                    zipped = zip(config.stadium_df['Park'],config.stadium_df['Region'])
                    parksInRegion = []
                    for (key, value) in dict(zipped).items():
                        if value == currentRegion:
                            parksInRegion.append(key)
                    remainingParksInRegion = [park for park in parksInRegion if park not in chosenParks]
                    # only consider parks in the current region
                    # if none, consider all available parks within the cutoff drive, and we will move to a new region
                    availableParks = order_available_parks(currentPark, remainingParks, remainingParksInRegion)
                    # Of the available parks, let's use the hashset to determine when games are occurring at these parks
                    tempHashset = hashset[currDateIndex:]
                    parkGames = [[[ i for i in range(len(tempHashset)) if j in tempHashset[i]][0] + currDateIndex,j] for j in list(availableParks['Park'])]
                    # Find earliest date with a game 
                    min_value = 999
                    for (key, value) in dict(parkGames).items():
                        if key < min_value:
                            min_value = key
                    # Loop through again and stop at first occurrence (aka closest park) on earliest date
                    # Choose this park!
                    for i in parkGames:
                        if i[0] == min_value:
                            choosePark = i[1]
                            # Calculate distances
                            dist_col_header = 'd_' + currentPark.replace(' ','_').replace('-','_')
                            distances_dict = dict(zip(config.stadium_df['Park'],config.stadium_df[dist_col_header]))
                            dist_last_park = distances_dict.get(choosePark)
                            total_distance += dist_last_park
                            # Calculate days on trip
                            days_since_last = baseball_df['Datetime'].loc[(baseball_df["Park"]==i[1]) & (baseball_df["Index"]==i[0])].min() - finalScheduleR[len(finalScheduleR)-1][3]
                            total_days = total_days + days_since_last
                            choosePark_df = pd.DataFrame(baseball_df.loc[(baseball_df["Park"]==i[1]) & (baseball_df["Index"]==i[0])].min())
                            finalScheduleR.append(choosePark_df.values.flatten().tolist() + [dist_last_park,total_distance,days_since_last,total_days])
                            break
                # Save all routes to list allRoutes
                allRoutes.append(finalScheduleR)
            except IndexError:
                break
    print("Processing Time: %s seconds" % (time.time() - start_time))
    return allRoutes

#====================================================================================================

def find_route_with_pop(baseball_df, park, date_index_start=0, date_index_end=1, hashset=[]):
    start_time = time.time()
    allRoutes = []
    for index in range(date_index_start,date_index_end):
        # Check if there is a game at the starting park on this particular index
        # If there is no game, go to next possible start date
        # If there is a game, initialize the final schedule list and append this game
        if park in hashset[index]:
            total_distance = 0
            total_days = pd.to_timedelta('0 days')
            remaining_parks = config.stadium_df['Park'].tolist()
            firstGame = baseball_df.loc[(baseball_df["Park"]==park) & (baseball_df["Index"]==index)]
            finalScheduleR = [["Index","Date","Time","Datetime","Team","Park","Address","Latitude","Longitude","Region","Dome Flag","Last Game of Homestead Flag","Double Header Flag",'Rain Probability','Distance From Last Park','Total Distance','Days Since Last Park','Total Days']]
            finalScheduleR.append(firstGame.min().values.flatten().tolist() + [0,0,0,0])
            try:
                # Append games to final schedule list one by one until the schedule is complete
                while len(finalScheduleR) < 31:
                    # currDate is used as a starting point when looping through potential game options
                    currDateIndex = finalScheduleR[len(finalScheduleR)-1][0] + 1
                    # before moving onto a new region, we have to visit all parks in the current region first
                    # current region is the region of the current park
                    currentRegion = finalScheduleR[len(finalScheduleR)-1][9]
                    # the last park we chose is now the currentPark in the algorithm
                    currentPark = finalScheduleR[len(finalScheduleR)-1][5]
                    # list out remaining parks
                    poppedPark = remaining_parks.pop(remaining_parks.index(currentPark))
                    remaining_parks_in_region = config.stadium_df['Park'].loc[config.stadium_df['Park'].isin(remaining_parks) & (config.stadium_df['Region']==currentRegion)].tolist()
                    # only consider parks in the current region
                    # if none, consider all available parks within the cutoff drive, and we will move to a new region
                    availableParks = order_available_parks(currentPark, remaining_parks, remaining_parks_in_region)
                    # Of the available parks, let's use the hashset to determine when games are occurring at these parks
                    tempHashset = hashset[currDateIndex:]
                    parkGames = [[[ i for i in range(len(tempHashset)) if j in tempHashset[i]][0] + currDateIndex,j] for j in list(availableParks['Park'])]
                    # Find earliest date with a game 
                    min_value = 999
                    for (key, value) in dict(parkGames).items():
                        if key < min_value:
                            min_value = key
                    # Loop through again and stop at first occurrence (aka closest park) on earliest date
                    # Choose this park!
                    for i in parkGames:
                        if i[0] == min_value:
                            choosePark = i[1]
                            # Calculate distances
                            dist_col_header = 'd_' + currentPark.replace(' ','_').replace('-','_')
                            distances_dict = dict(zip(config.stadium_df['Park'],config.stadium_df[dist_col_header]))
                            dist_last_park = distances_dict.get(choosePark)
                            total_distance += dist_last_park
                            # Calculate days on trip
                            days_since_last = baseball_df['Datetime'].loc[(baseball_df["Park"]==i[1]) & (baseball_df["Index"]==i[0])].min() - finalScheduleR[len(finalScheduleR)-1][3]
                            total_days = total_days + days_since_last
                            choosePark_df = pd.DataFrame(baseball_df.loc[(baseball_df["Park"]==i[1]) & (baseball_df["Index"]==i[0])].min())
                            finalScheduleR.append(choosePark_df.values.flatten().tolist() + [dist_last_park,total_distance,days_since_last,total_days])
                            break
                # Save all routes to list allRoutes
                allRoutes.append(finalScheduleR)
            except IndexError:
                break
    print("Processing Time: %s seconds" % (time.time() - start_time))
    return allRoutes
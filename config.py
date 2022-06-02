# Import libraries
import pandas as pd
import os

# Get the current working directory
cwd = os.getcwd()

# GLOBAL VARIABLES

startDate = '2022-04-15'
startPark = "Fenway Park"
gameLength = 5, #in hours
gameBuffer = 2, #in hours
avgSpeed = 40, #in mph
cutoffDrive = 1000 #in miles


# Stadium DataFrame
# Create DataFrame of stadium info
stadiums = [
    ["Los Angeles Angels","Angel Stadium of Anaheim","2000 Gene Autry Way, Anaheim, CA. 92806",33.799572,-117.889031,'Pacific'],
    ["Arizona D'Backs","Chase Field","P.O. Box 2095, Phoenix, AZ. 85001",33.452922,-112.038669,'Pacific'],
    ["Atlanta Braves","SunTrust Park","P.O. Box 4064, Atlanta, GA. 30302",33.74691,-84.391239,'Southeast'],
    ["Baltimore Orioles","Oriole Park at Camden Yards","333 W. Camden Street, Baltimore, MD. 21201",39.285243,-76.620103,'Northeast'],
    ["Boston Red Sox","Fenway Park","4 Yawkey Way, Boston, MA 02215",42.346613,-71.098817,'Northeast'],
    ["Chicago Cubs","Wrigley Field","1060 Addison Street, Chicago, IL 60616",41.947201,-87.656413,'Midwest'],
    ["Chicago White Sox","Guaranteed Rate Field","333 W. 35th Street, Chicago, IL 60616",41.830883,-87.635083,'Midwest'],
    ["Cincinnati Reds","Great American Ball Park","100 Cinergy Field, Cincinnati, OH 45202",39.107183,-84.507713,'Midwest'],
    ["Cleveland Guardians","Progressive Field","2401 Ontario Street, Cleveland, OH 44115",41.495149,-81.68709,'Midwest'],
    ["Colorado Rockies","Coors Field","2001 Blake Street, Denver, CO 80205-2000",39.75698,-104.965329,'Rocky Mountains'],
    ["Detroit Tigers","Comerica Park","2100 Woodward Ave., Detroit, MI 48201",42.346354,-83.059619,'Midwest'],
    ["Miami Marlins","Marlins Park","2269 NW 199th Street, Miami, FL 33056",25.954428,-80.238164,'Southeast'],
    ["Houston Astros","Minute Maid Park","P.O. Box 288, Houston, TX 77001-0288",29.76045,-95.369784,'Southwest'],
    ["Kansas City Royals","Kauffman Stadium","P.O. Boz 419969, Kansas City, MO 64141",39.10222,-94.583559,'Midwest'],
    ["Los Angeles Dodgers","Dodger Stadium","1000 Elysian Park Ave., Los Angeles, CA 90012",34.072437,-118.246879,'Pacific'],
    ["Milwaukee Brewers","Miller Park","P.O. Box 3099, Milwaukee, WI 53201-3099",43.04205,-87.905599,'Midwest'],
    ["Minnesota Twins","Target Field","501 Chicago Ave. S., Minneapolis, MN 55415",44.974346,-93.259616,'Midwest'],
    ["Washington Nationals","Nationals Park","1500 South Capitol Street SE, Washington, DC",38.87,-77.01,'Northeast'],
    ["New York Mets","Citi Field","Roosevelt Ave & 126th Street, New York, NY 11368",40.75535,-73.843219,'Northeast'],
    ["New York Yankees","Yankee Stadium","E. 161 Street & River Ave., New York, NY 10451",40.819782,-73.929939,'Northeast'],
    ["Oakland Athletics","Oakland Coliseum","700 Coliseum Way, Oakland, Ca 94621-1918",37.74923,-122.196487,'Pacific'],
    ["Philadelphia Phillies","Citizens Bank Park","P.O. Box 7575, Philadelphia, PA 19101",39.952313,-75.162392,'Northeast'],
    ["Pittsburgh Pirates","PNC Park","600 Stadium Circle, Pittsburgh, PA 15212",40.461503,-80.008924,'Northeast'],
    ["St. Louis Cardinals","Busch Stadium","250 Stadium Plaza, St. Louis, MO 63102",38.629683,-90.188247,'Midwest'],
    ["San Diego Padres","Petco Park","P.O. Box 2000, San Diego, CA 92112-2000",32.752148,-117.143635,'Pacific'],
    ["San Francisco Giants","Oracle Park","24 Willie Mays Plaza, San Francisco, CA 94107",37.77987,-122.389754,'Pacific'],
    ["Seattle Mariners","T-Mobile Park","P.O. Box 41000, 411 First Ave. S., Seattle, WA 98104",47.60174,-122.330829,'Pacific'],
    ["Tampa Bay Rays","Tropicana Field","1 Tropicana Drive, St. Petersburg, FL 33705",27.768487,-82.648191,'Southeast'],
    ["Texas Rangers","Globe Life Park in Arlington","1000 Ballpark Way, Arlington, TX 76011",32.750156,-97.081117,'Southwest'],
    ["Toronto Blue Jays","Rogers Centre","1 Blue Jay Way, Suite 3200, Toronto, ONT M5V 1J1",43.641653,-79.3917,'Midwest']
]
stadium_df = pd.DataFrame(stadiums, columns = ['Team', 'Park', 'Address', 'Latitude','Longitude', 'Region'])

# Weather DataFrame
# Read the weather CSV that has already been manipulated and fix any zip codes that lost their leading zeros
file_name = '/Source_Files/Daily_Rain_Probability_By_City.csv'
rainProb_df = pd.read_csv(cwd + file_name).drop(columns=['Unnamed: 0','STATION'])
rainProb_df["Zip Code"] = rainProb_df["Zip Code"].astype('str')
rainProb_df["Zip Code"] = rainProb_df["Zip Code"].apply(lambda x: '0'+ x if len(x)==4 else x)

# MLB Schedule DataFrame
# Read the CSV to get the main DataFrame
file_name = '/Source_Files/MLB_Schedule_2022.csv'
baseball_df = pd.read_csv(cwd + file_name).drop(columns=['Unnamed: 0'])
baseball_df['Date'] = pd.to_datetime(baseball_df['Date']).dt.normalize()



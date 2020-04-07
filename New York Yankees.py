import pandas as pd
import sqlite3

conn = sqlite3.connect('/Users/neilrawlins/Desktop/Baseball2016.sqlite')

NYY_query = '''select * from Teams where Teams.franchID == 'NYY';'''

NYY_list = conn.execute(NYY_query).fetchall()

NYY_df = pd.DataFrame(NYY_list)

cols = ['yearID','lgID','teamID','franchID','divID','Rank','G','Ghome','W','L','DivWin','WCWin',
        'LgWin','WSWin','R','AB','H','2B','3B','HR','BB','SO','SB','CS','HBP','SF','RA','ER','ERA',
        'CG','SHO','SV','IPouts','HA','HRA','BBA','SOA','E','DP','FP','name','park','attendance',
        'BPF','PPF','teamIDBR','teamIDlahman45','teamIDretro']

NYY_df.columns = cols

#This finds divID = 68, DivWin = 69, WCWin = 94, LgWin = 1, WSWin = 4, SO = 8, CS = 17, HBP = 99, SF = 99
print(NYY_df.isnull().sum().tolist())

import matplotlib.pyplot as plt

plt.plot(NYY_df['yearID'], NYY_df['W'],NYY_df['yearID'], NYY_df['G'])

plt.show()

##Here we will get the total wins per year and sum(teams) per year
all_teams_wins_query = '''select yearID, W, franchID from Teams'''

all_teams_wins_list = conn.execute(all_teams_wins_query).fetchall()

all_teams_wins_df = pd.DataFrame(all_teams_wins_list)

all_teams_wins_df.columns = ['year', 'wins', 'team']

total_wins_per_year = {}
total_teams_per_year = {}

for index, row in all_teams_wins_df.iterrows():
    year = row['year']
    wins = row['wins']
    team = row['team']
    if year in total_wins_per_year:
        total_wins_per_year[year] = total_wins_per_year[year] + wins
        total_teams_per_year[year] = total_teams_per_year[year] + 1
    else:
        total_wins_per_year[year] = wins
        total_teams_per_year[year] = 1

print(total_wins_per_year)
print(total_teams_per_year)

#Now we will find the average wins per year and compare that to the NYY each year with a graph

average_wins_per_year = {}

for key, value in total_teams_per_year.items():
    year = key
    teams = value
    wins = total_wins_per_year[year]
    average_wins_per_year[year] = wins/teams

print(average_wins_per_year)

list = sorted(average_wins_per_year.items())

df_average_wins = pd.DataFrame(list)

df_average_wins.columns = ['yearID','W']

plt.plot(NYY_df['yearID'], NYY_df['W'],NYY_df['yearID'], NYY_df['G'], df_average_wins['yearID'], df_average_wins['W'])
plt.legend(['NYY Wins', 'NYY Games Played', 'Average Wins by MLB Team'], loc = 2, prop = {'size': 6})

plt.show()
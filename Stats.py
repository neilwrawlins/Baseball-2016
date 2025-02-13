import pandas as pd
import sqlite3


#######DATA CLEANING

conn = sqlite3.connect('/Users/neilrawlins/Desktop/Baseball2016.sqlite')

Teams = conn.execute('''select * from Teams
inner join TeamsFranchises
on Teams.franchID == TeamsFranchises.franchID
where Teams.G >= 150 and TeamsFranchises.active == 'Y';
''').fetchall()

teams_df = pd.DataFrame(Teams)

cols = ['yearID','lgID','teamID','franchID','divID','Rank','G','Ghome','W','L','DivWin','WCWin',
        'LgWin','WSWin','R','AB','H','2B','3B','HR','BB','SO','SB','CS','HBP','SF','RA','ER','ERA',
        'CG','SHO','SV','IPouts','HA','HRA','BBA','SOA','E','DP','FP','name','park','attendance',
        'BPF','PPF','teamIDBR','teamIDlahman45','teamIDretro','franchID','franchName','active','NAassoc']

teams_df.columns = cols

#Drop unneeded columns
drop_cols = ['lgID','franchID','divID','Rank','Ghome','L','DivWin','WCWin','LgWin','WSWin','SF',
             'name','park','attendance','BPF','PPF','teamIDBR','teamIDlahman45','teamIDretro',
             'franchID','franchName','active','NAassoc']

df = teams_df.drop(drop_cols, axis=1)

#Checking total of nulls per column
df.isnull().sum(axis=0).tolist()

# Eliminating columns with null values - CS 419 and HBP 1777
df = df.drop(['CS','HBP'], axis=1)

# Filling null values - SO 110 DP 22
df['SO'] = df['SO'].fillna(df['SO'].median())
df['DP'] = df['DP'].fillna(df['DP'].median())

# Print out null values of all columns of `df`
print(df.isnull().sum(axis=0).tolist())

########EXPLORING AND VISUALIZING

import matplotlib.pyplot as plt

# Plotting distribution of wins
plt.hist(df['W'])
plt.xlabel('Wins')
plt.ylabel('Number of Teams')
plt.title('Distribution of Wins')

plt.show()


# Creating bins for the win column
def assign_win_bins(W):
    if W < 50:
        return 1
    if W >= 50 and W <= 69:
        return 2
    if W >= 70 and W <= 89:
        return 3
    if W >= 90 and W <= 109:
        return 4
    if W >= 110:
        return 5


df['win_bins'] = df['W'].apply(assign_win_bins)

# Plotting scatter graph of Year vs. Wins
plt.scatter(df['yearID'], df['W'], c=df['win_bins'])
plt.title('Wins Scatter Plot')
plt.xlabel('Year')
plt.ylabel('Wins')

plt.show()

#Very few seasons before 1900 as seen in above plot
df = df[df['yearID'] > 1900]

# Plotting scatter graph of Year vs. Wins for year > 1900
plt.scatter(df['yearID'], df['W'], c=df['win_bins'])
plt.title('Wins Scatter Plot')
plt.xlabel('Year')
plt.ylabel('Wins')

plt.show()

# Create runs per year and games per year dictionaries
runs_per_year = {}
games_per_year = {}

print(df)

#Will go to the else part of if/else until a year has been added to the dictionary
for index, row in df.iterrows():
    year = row['yearID']
    runs = row['R']
    games = row['G']
    if year in runs_per_year:
        runs_per_year[year] = runs_per_year[year] + runs
        games_per_year[year] = games_per_year[year] + games
    else:
        runs_per_year[year] = runs
        games_per_year[year] = games

print(runs_per_year)
print(games_per_year)

# Create MLB runs per game (per year) dictionary
mlb_runs_per_game = {}
for key, value in games_per_year.items():
    year = key
    games = value
    runs = runs_per_year[year]
    mlb_runs_per_game[year] = runs / games

print(mlb_runs_per_game)

lists = sorted(mlb_runs_per_game.items())

#Splits lists into two tuples, one with years and one with runs per game
x, y = zip(*lists)

plt.plot(x, y)
plt.title('MLB Runs Per Game by Year')
plt.xlabel('Year')
plt.ylabel('Runs Per Game')

plt.show()


# Creating "year_label" column, which will give your algorithm information about how certain years are related
# (Dead ball eras, Live ball/Steroid Eras)

def assign_label(year):
    if year < 1920:
        return 1
    elif year >= 1920 and year <= 1941:
        return 2
    elif year >= 1942 and year <= 1945:
        return 3
    elif year >= 1946 and year <= 1962:
        return 4
    elif year >= 1963 and year <= 1976:
        return 5
    elif year >= 1977 and year <= 1992:
        return 6
    elif year >= 1993 and year <= 2009:
        return 7
    elif year >= 2010:
        return 8


# Add `year_label` column to `df`
df['year_label'] = df['yearID'].apply(assign_label)

dummy_df = pd.get_dummies(df['year_label'], prefix='era')

# Concatenate `df` and `dummy_df`
df = pd.concat([df, dummy_df], axis=1)

print(df.head())

# Create column for MLB runs per game from the mlb_runs_per_game dictionary
def assign_mlb_rpg(year):
    return mlb_runs_per_game[year]

df['mlb_rpg'] = df['yearID'].apply(assign_mlb_rpg)

print(df.head())


# Convert years into decade bins and creating dummy variables
def assign_decade(year):
    if year < 1920:
        return 1910
    elif year >= 1920 and year <= 1929:
        return 1920
    elif year >= 1930 and year <= 1939:
        return 1930
    elif year >= 1940 and year <= 1949:
        return 1940
    elif year >= 1950 and year <= 1959:
        return 1950
    elif year >= 1960 and year <= 1969:
        return 1960
    elif year >= 1970 and year <= 1979:
        return 1970
    elif year >= 1980 and year <= 1989:
        return 1980
    elif year >= 1990 and year <= 1999:
        return 1990
    elif year >= 2000 and year <= 2009:
        return 2000
    elif year >= 2010:
        return 2010


df['decade_label'] = df['yearID'].apply(assign_decade)
decade_df = pd.get_dummies(df['decade_label'], prefix='decade')
df = pd.concat([df, decade_df], axis=1)

# Drop unnecessary columns
df = df.drop(['yearID', 'year_label', 'decade_label'], axis=1)

print(df.head())

# Create new features for Runs per Game and Runs Allowed per Game
df['R_per_game'] = df['R'] / df['G']
df['RA_per_game'] = df['RA'] / df['G']

# Create scatter plots for runs per game vs. wins and runs allowed per game vs. wins
fig = plt.figure(figsize=(12, 6))

ax1 = fig.add_subplot(1,2,1)
ax2 = fig.add_subplot(1,2,2)

ax1.scatter(df['R_per_game'], df['W'], c='blue')
ax1.set_title('Runs per Game vs. Wins')
ax1.set_ylabel('Wins')
ax1.set_xlabel('Runs per Game')

ax2.scatter(df['RA_per_game'], df['W'], c='red')
ax2.set_title('Runs Allowed per Game vs. Wins')
ax2.set_xlabel('Runs Allowed per Game')

plt.show()

#Shows how each varriable correlates to wins. 1 = perfect to -1 = lowest correlation
print df.corr()['W']

#Leaving out 'W' for K Means Clustering
attributes = ['G','R','AB','H','2B','3B','HR','BB','SO','SB','RA','ER','ERA','CG',
'SHO','SV','IPouts','HA','HRA','BBA','SOA','E','DP','FP','era_1','era_2','era_3',
              'era_4','era_5','era_6','era_7','era_8','decade_1910','decade_1920',
              'decade_1930','decade_1940','decade_1950','decade_1960','decade_1970','decade_1980',
              'decade_1990','decade_2000','decade_2010','R_per_game','RA_per_game','mlb_rpg']

data_attributes = df[attributes]

# Print the first rows of `df`
print(df.head())

# Import necessary modules from `sklearn`
from sklearn.cluster import KMeans
from sklearn import metrics

# Create silhouette score dictionary
s_score_dict = {}
for i in range(2,11):
    km = KMeans(n_clusters=i, random_state=1)
    l = km.fit_predict(data_attributes)
    s_s = metrics.silhouette_score(data_attributes, l)
    s_score_dict[i] = [s_s]

# Print out `s_score_dict`
print(s_score_dict)

# Create K-means model and determine euclidian distances for each data point
kmeans_model = KMeans(n_clusters=6, random_state=1)
distances = kmeans_model.fit_transform(data_attributes)

# Create scatter plot using labels from K-means model as color
labels = kmeans_model.labels_

plt.scatter(distances[:,0], distances[:,1], c=labels)
plt.title('Kmeans Clusters')

plt.show()

df['labels'] = labels
attributes.append('labels')

print(df.head())

# Create new DataFrame using only variables to be included in models
numeric_cols = ['G','R','AB','H','2B','3B','HR','BB','SO','SB','RA','ER','ERA',
                'CG','SHO','SV','IPouts','HA','HRA','BBA','SOA','E','DP','FP',
                'era_1','era_2','era_3','era_4','era_5','era_6','era_7','era_8','decade_1910',
                'decade_1920','decade_1930','decade_1940','decade_1950','decade_1960','decade_1970',
                'decade_1980','decade_1990','decade_2000','decade_2010','R_per_game','RA_per_game',
                'mlb_rpg','labels','W']

data = df[numeric_cols]
print(data.head())

# Split data DataFrame into train and test sets
train = data.sample(frac=0.75, random_state=1)
test = data.loc[~data.index.isin(train.index)]

x_train = train[attributes]
y_train = train['W']
x_test = test[attributes]
y_test = test['W']

# Import `LinearRegression` from `sklearn.linear_model`
from sklearn.linear_model import LinearRegression

# Import `mean_absolute_error` from `sklearn.metrics`
from sklearn.metrics import mean_absolute_error

# Create Linear Regression model, fit model, and make predictions
#Y=a+b*X + e, where a is intercept, b is slope of the line and e is error term.
lr = LinearRegression(normalize=True)
lr.fit(x_train, y_train)
predictions = lr.predict(x_test)

# Determine mean absolute error - MAE -- 1. Error = Actual values - Predicted values (individually),
# 2. Absolute Value of all Error (A1, A2, An) 3. MAE = (A1 + A2 + ... An)/n where n = total number of training set
mae = mean_absolute_error(y_test, predictions)

print(lr.coef_)

print(lr.intercept_)

# Print `mae`
print(mae)

# Import `RidgeCV` from `sklearn.linear_model`
from sklearn.linear_model import RidgeCV

# Create Ridge Linear Regression model, fit model, and make predictions
rrm = RidgeCV(alphas=(0.01, 0.1, 1.0, 10.0), normalize=True)
rrm.fit(x_train, y_train)
predictions_rrm = rrm.predict(x_test)

# Determine mean absolute error
mae_rrm = mean_absolute_error(y_test, predictions_rrm)
print(mae_rrm)
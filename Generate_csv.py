import requests
import pandas as pd

# This script fetches F1 race data from the Ergast API regarding the specified seasons and round numbers and saves it to a CSV file.
def get_race_results(season, round_number):
    url = f"https://ergast.com/api/f1/{season}/{round_number}/results.json"
    response = requests.get(url)
    if response.status_code == 200:
        races = response.json()['MRData']['RaceTable']['Races']
        if races:
            return races[0]['Results']
    return []

# Retrieves all race information for a specific season from the ergast API 
def get_all_races(season):
    url = f"https://ergast.com/api/f1/{season}.json"
    response = requests.get(url)
    if response.status_code == 200:
        races = response.json()['MRData']['RaceTable']['Races']
        return [(race['round'], race['Circuit']['circuitName']) for race in races]
    return []

# Builds a DataFrame containing race data such as drivers, teams, positions, and circuits for a given season.
def build_csv_data(season):
    all_data = []
    races = get_all_races(season)
    for round_number, circuit_name in races:
        results = get_race_results(season, round_number)
        for result in results:
            driver = result['Driver']
            position = int(result['position'])
            grid = int(result['grid'])
            constructor = result['Constructor']['name']
            all_data.append({
                'season': season,
                'round': int(round_number),
                'circuit': circuit_name,
                'driver': driver['familyName'],
                'grid': grid,
                'constructor': constructor,
                'won': 1 if position == 1 else 0,
                'weather': 'Sunny'  
            })
    return pd.DataFrame(all_data)

# Generates the CSV file and displays text if successful
df_all = pd.concat([build_csv_data(year) for year in range(2020, 2025)], ignore_index=True)
df_all.to_csv("F1 Race Data.csv")
print("CSV saved as F1 Race Data.csv")
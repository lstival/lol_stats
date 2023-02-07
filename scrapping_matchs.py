from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
from datetime import datetime
import time
from tqdm import tqdm

# df with columns of metrics of all matchs
df_match = pd.DataFrame(columns=['team_red', 'result_red', 'ban_0_red', 'ban_1_red', 'ban_2_red', 'ban_3_red', 'ban_4_red', 
                                'pick_0_red', 'pick_1_red', 'pick_2_red', 'pick_3_red', 'pick_4_red', 'kills_red', 'towers_red', 'dragons_red', 'barons_red',
                                'player_0_red', 'kda_0_red', 'csM_0_red', 'dpM_0_red', 'wpM_0_red', 'player_1_red', 'kda_1_red', 'csM_1_red', 'dpM_1_red',
                                'wpM_1_red', 'player_2_red', 'kda_2_red', 'csM_2_red', 'dpM_2_red', 'wpM_2_red', 'player_3_red', 'kda_3_red', 'csM_3_red',
                                'dpM_3_red', 'wpM_3_red', 'player_4_red', 'kda_4_red', 'csM_4_red', 'dpM_4_red', 'wpM_4_red', 'team_blue', 'result_blue',
                                'ban_0_blue', 'ban_1_blue', 'ban_2_blue', 'ban_3_blue', 'ban_4_blue', 'pick_0_blue', 'pick_1_blue', 'pick_2_blue',
                                'pick_3_blue', 'pick_4_blue', 'kills_blue', 'towers_blue', 'dragons_blue', 'barons_blue', 'player_0_blue', 
                                'kda_0_blue', 'csM_0_blue', 'dpM_0_blue', 'wpM_0_blue', 'player_1_blue', 'kda_1_blue', 'csM_1_blue', 'dpM_1_blue', 
                                'wpM_1_blue', 'player_2_blue', 'kda_2_blue', 'csM_2_blue', 'dpM_2_blue', 'wpM_2_blue', 'player_3_blue', 'kda_3_blue', 
                                'csM_3_blue', 'dpM_3_blue', 'wpM_3_blue', 'player_4_blue', 'kda_4_blue', 'csM_4_blue', 'dpM_4_blue', 'wpM_4_blue', 'match_duration'])

skiped_matchs = []
# 44693
pbar = tqdm(range(44431, 45200))
for match_idx in pbar:
    pbar.set_description(f"Processing match: {match_idx}")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"}
    html = requests.get(f"https://gol.gg/game/stats/{match_idx}/page-summary/", headers=headers).content
    soup = BeautifulSoup(html, 'html.parser')

    try:
        #Team blue side
        blue_team = soup.find("div", class_="row rowbreak fond-main-cadre p-4").find_all("div", class_="col-4 col-sm-5 text-center")[0].get_text()
        blue_result = soup.find("div", class_="row rowbreak fond-main-cadre p-4").find_all("div", class_="col-4 col-sm-5 text-center")[2].find("h1").get_text()

        #Team red side
        red_team = soup.find("div", class_="row rowbreak fond-main-cadre p-4").find_all("div", class_="col-4 col-sm-5 text-center")[1].get_text()
        red_result = soup.find("div", class_="row rowbreak fond-main-cadre p-4").find_all("div", class_="col-4 col-sm-5 text-center")[3].find("h1").get_text()


        # Match time
        try:
            match_time = datetime.strptime(soup.find("div", class_="col-4 col-sm-2 text-center align-middle right-side-win").find_all("h1")[0].get_text(), '%M:%S').time()
        except:
            match_time = datetime.strptime(soup.find("div", class_="col-4 col-sm-2 text-center align-middle left-side-win").find_all("h1")[0].get_text(), '%M:%S').time()

        #First 5 is the banned champions for blue side
        #Last 5 picke champions for blue side
        blue_champs = soup.find("div", class_="row rowbreak fond-main-cadre p-4").find_all("div", class_="col-4 col-sm-5 text-center")[2].find_all("img")

        #Same for the red side
        red_champs = soup.find("div", class_="row rowbreak fond-main-cadre p-4").find_all("div", class_="col-4 col-sm-5 text-center")[3].find_all("img")

        lst_blue_champs = []
        for champ in blue_champs:
            lst_blue_champs.append(champ["src"].split('/')[-1].split('.')[0])

        lst_red_champs = []
        for champ in red_champs:
            lst_red_champs.append(champ["src"].split('/')[-1].split('.')[0])


        # picks and bans of blue side
        blue_banned = lst_blue_champs[:5]
        blue_piked = lst_blue_champs[5:]


        #picks and bans of red side
        red_banned = lst_red_champs[:5]
        red_piked = lst_red_champs[5:]


        #Ordem of prints, Kills, Towers, Dragons, Barons

        #list of stats of each team
        blue_stats = []
        red_stats = []
        #For blue team

        for i in soup.find_all("div", class_="col-12 col-sm-6 pb-4")[0].find_all("span", class_="score-box"):
            #Keep only numbers in the string
            blue_stats.append(int(''.join(filter(str.isdigit, i.get_text()))))

        #For red team
        for i in soup.find_all("div", class_="col-12 col-sm-6 pb-4")[1].find_all("span", class_="score-box"):
            #Keep only numbers in the string
            red_stats.append(int(''.join(filter(str.isdigit, i.get_text()))))

        def get_team_stats(stats, team):
            dct_team = {}
            dct_team[f"kills_{team}"] = stats[0]
            dct_team[f"towers_{team}"] = stats[1]
            dct_team[f"dragons_{team}"] = stats[2]
            dct_team[f"barons_{team}"] = stats[3]

            return dct_team

        def player_kda(row):
            """
            row: line with data with kills, deaths and assists of each player

            return the KDA rounded to 2 decimals
            """
            kills, deaths, other = row.split('/')
            assists = other.split(' ')[0]
            if int(deaths) > 0:
                kda = (int(kills) + int(assists))/int(deaths)
            else:
                kda = (int(kills) + int(assists))
                
            return round(kda, 2)

        def get_team_kda(team):

            if team == "blue":
                idx = 0
            else:
                idx = 1
                

            #Get the KDA of each team
            table = soup.find_all("table", "table_list trhover")[int(idx)]
            row_marker = 0
            table_data = []

            #lopp for each row in the table
            for row in table.find_all('tr'):
                column_marker = 0
                column_data = []
                columns = row.find_all('td')

                #extract info for each collum and save in the list
                for column in columns:
                    column_data.append(column.get_text())
                table_data.append(column_data)

            table_data = table_data[1:]

            df_kda = pd.DataFrame(table_data,columns=['player', 'kda', 'csM', 'dpM','wpM'])
            df_kda.dropna(inplace=True)

            #Apply the function KDA and replace the single values for the metric
            df_kda['kda'] = df_kda.apply(lambda x: player_kda(x['kda']),axis=1)

            return df_kda

        # dict with blue team data
        blue_team_data = {}

        team = "blue"

        # team name
        blue_team_data[f"team_{team}"] = blue_team

        # info. if team win or lost
        blue_team_data[f"result_{team}"] = blue_result

        # bans of team
        for idx, ban in enumerate(blue_banned):
            blue_team_data[f"ban_{idx}_{team}"] = ban

        # picks of team
        for idx, pick in enumerate(blue_piked):
            blue_team_data[f"pick_{idx}_{team}"] = pick

        # kills, towers, drgans and barons
        blue_team_data.update(get_team_stats(blue_stats, team))

        # KDA of each player
        player_idx = 0
        dct_players = {}
        lst_player_kda_keys = ['player', 'kda', 'csM', 'dpM','wpM']

        def get_player_kda(row):
            global player_idx
            for idx, i in enumerate(row):
                dct_players[f"{lst_player_kda_keys[idx]}_{player_idx}_{team}"] = i
            player_idx += 1

        get_team_kda("blue").apply(lambda x: get_player_kda(x), axis=1)
        blue_team_data.update(dct_players)


        # dict with red team data
        red_team_data = {}

        team = "red"

        # team name
        red_team_data[f"team_{team}"] = red_team

        # info. if team win or lost
        red_team_data[f"result_{team}"] = red_result

        # bans of team
        for idx, ban in enumerate(red_banned):
            red_team_data[f"ban_{idx}_{team}"] = ban

        # picks of team
        for idx, pick in enumerate(red_piked):
            red_team_data[f"pick_{idx}_{team}"] = pick

        # kills, towers, drgans and barons
        red_team_data.update(get_team_stats(red_stats, team))

        # KDA of each player
        player_idx = 0
        dct_players = {}
        lst_player_kda_keys = ['player', 'kda', 'csM', 'dpM','wpM']

        def get_player_kda(row):
            global player_idx
            for idx, i in enumerate(row):
                dct_players[f"{lst_player_kda_keys[idx]}_{player_idx}_{team}"] = i
            player_idx += 1

        get_team_kda("red").apply(lambda x: get_player_kda(x), axis=1)
        red_team_data.update(dct_players)

        dct_teams = {**red_team_data, **blue_team_data}
        dct_teams["match_duration"] = match_time

        # Concat the match data to df with all data
        df_match = pd.concat([df_match, pd.DataFrame(dct_teams, index=[0])])

        # time.sleep(2)
    except AttributeError:
        skiped_matchs.append(match_idx)
    except IndexError:
        skiped_matchs.append(match_idx)

print(f" Matchs not finded: {skiped_matchs}")
        

# Save .csv with data of all match
df_match.to_csv("data/matchs_2023.csv")
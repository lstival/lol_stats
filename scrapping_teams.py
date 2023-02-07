from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np

#Read all champions info
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"}
html = requests.get("https://gol.gg/teams/list/season-S13/split-Spring/tournament-ALL/", headers=headers).content
soup = BeautifulSoup(html, 'html.parser')

#Get the main table of page (with all champions and statics)
table = soup.find_all("table", class_="table_list")[0]

#Get the name of collumns
table_columns = []
for i in table.find_all('th'):
    table_columns.append(i.getText())

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

df_teams = pd.DataFrame(table_data, columns=table_columns)
df_teams.to_csv("data/teams.csv")
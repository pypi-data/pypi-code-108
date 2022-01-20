import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import openpyxl
import sys

def main():
    base_url = 'https://understat.com/match/'
    match = str(input('Please enter the match id : '))
    url = base_url+ match

    res = requests.get(url)
    soup = BeautifulSoup(res.content, "lxml")

    scripts = soup.find_all('script')

    strings =  scripts[1].string

    ind_start = strings.index("('")+2
    ind_end = strings.index("')")

    json_data = strings[ind_start:ind_end]

    json_data = json_data.encode('utf8').decode('unicode_escape')
    data = json.loads(json_data)

    date = []
    minute = []
    team  =[]
    result = []
    x = []
    y = []
    xg = []
    result = []
    name = []
    situation = []
    shottype = []
    assist_player = []
    assist_action = []

    data_away = data['a']
    data_home = data['h']

    for index in range (len(data_away)):
        for key in data_away[index]:
            if key == 'date':
                date.append(data_away[index][key])
            if key == 'minute':
                minute.append(data_away[index][key])
            if key ==  "a_team":
                team.append(data_away[index][key])
            if key == 'result':
                result.append(data_away[index][key])
            if key == 'X':
                x.append(data_away[index][key])
            if key == 'Y':
                y.append(data_away[index][key])
            if key == 'player':
                name.append(data_away[index][key])
            if key == 'xG':
                xg.append(data_away[index][key])
            if key == 'situation':
                situation.append(data_away[index][key])
            if key == 'shotType':
                shottype.append(data_away[index][key])
            if key == 'player_assisted':
                assist_player.append(data_away[index][key])
            if key == 'lastAction':
                assist_action.append(data_away[index][key])

    for index in range (len(data_home)):
        for key in data_home[index]:
            if key == 'date':
                date.append(data_home[index][key])
            if key == 'minute':
                minute.append(data_home[index][key])
            if key ==  "h_team":
                team.append(data_home[index][key])
            if key == 'result':
                result.append(data_home[index][key])
            if key == 'X':
                x.append(data_home[index][key])
            if key == 'Y':
                y.append(data_home[index][key])
            if key == 'player':
                name.append(data_home[index][key])
            if key == 'xG':
                xg.append(data_home[index][key])
            if key == 'situation':
                situation.append(data_home[index][key])
            if key == 'shotType':
                shottype.append(data_home[index][key])
            if key == 'player_assisted':
                assist_player.append(data_home[index][key])
            if key == 'lastAction':
                assist_action.append(data_home[index][key])

    col_ = ['date','min','team',"b_x",'b_y','xg','name','result',"situation",'shottype','assist_player','assist_action']

    df = pd.DataFrame([date,minute,team,x,y,xg,name,result,shottype,situation,assist_player,assist_action],index = col_).T
    df=df.assign(x=df['b_x'].astype('float64')*120,y=df['b_y'].astype('float64')*80)
    df = df[['date','min','team','x','y','xg','name','result','situation','shottype','assist_player','assist_action']]

    print("scraped data")
    style = str(input('Which file do you want? csv or excel or sql? : '))

    if style == 'csv':
        filename = str(input("Please fill in the file name:"))
        df.to_csv(filename+".csv")
        print("created "+filename+".csv")
        sys.exit()

    elif style == 'excel':
        filename = str(input("Please fill in the file name:"))
        df.to_excel(filename+".xlsx")
        print("created "+filename+".xlsx")
        sys.exit()

    elif style == 'sql':
        shot_style = str(input("Which shot point type do you want? xy or point? : "))

        if shot_style == 'xy':
            filename = str(input("Please fill in the file name:"))
            DBname = str(input("Please fill in the Database table name:"))
            f = open(filename+".sql","w")

            f.write("CREATE TABLE IF NOT EXISTS " + DBname +"\n"
                    + "(no SERIAL NOT NULL,date VARCHAR(30) NOT NULL ,min INTEGER  NOT NULL,team VARCHAR(30) NOT NULL,name VARCHAR(30) NOT NULL,x NUMERIC NOT NULL,y NUMERIC NOT NULL,shottype VARCHAR(20) NOT NULL,result VARCHAR(20) NOT NULL,situation  VARCHAR(20) NOT NULL,xg NUMERIC NOT NULL,assist_player VARCHAR(30),last_action  VARCHAR(20) NOT NULL,primary key (no));\n")

            df["x"]=df["x"].astype(str)
            df["y"]=df["y"].astype(str)
            df["team"] = df["team"].astype(str)
            df["min"]=df["min"].astype(str)
            df["xg"]=df["xg"].astype(str)
            df["asssist_player"]=df["assist_player"].astype(str)


            df_=df[['date','min','team','x','y','xg','name','result','situation','shottype','assist_player','assist_action']]
            df_.fillna("None")
            df_['name'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
            df['assist_player'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')

            for i in range(0,len(df_)-1):
                date = ("'"+df_["date"][i]+"'")
                min = df_["min"][i]
                team = ("'"+df_["team"][i]+"'")
                x = df_["x"][i]
                y = df_["y"][i]
                xg = df_["xg"][i]
                name = ("'"+df_["name"][i]+"'")
                result = ("'"+df_["result"][i]+"'")
                situation = ("'"+df_["situation"][i]+"'")
                shottype = ("'"+df_["shottype"][i]+"'")
                assist_player = ("'"+(str(df_["assist_player"][i]))+"'")
                assist_action = ("'"+df_["assist_action"][i]+"'")


                f.write("INSERT INTO "+ DBname +"(date,min,team,name,x,y,shottype,result,situation,xg,assist_player,last_action) VALUES ("+date+","+min+","+team+","+name+","+x+","+y+","+shottype+","+result+","+situation+","+xg+","+assist_player+","+assist_action+");\n")
            f.close()
            print("created "+ filename +".sql")
            sys.exit()

        elif shot_style == 'point':
            filename = str(input("Please fill in the file name : "))
            DBname = str(input("Please fill in the Database table name :  "))
            f = open(filename+".sql","w")

            f.write("CREATE TABLE IF NOT EXISTS " + DBname +"\n"
                    + "(no SERIAL NOT NULL,date VARCHAR(30) NOT NULL ,min INTEGER  NOT NULL,team VARCHAR(30) NOT NULL,name VARCHAR(30) NOT NULL,point POINT NOT NULL,shottype VARCHAR(20) NOT NULL,result VARCHAR(20) NOT NULL,situation  VARCHAR(20) NOT NULL,xg NUMERIC(5,3) NOT NULL,assist_player VARCHAR(30),last_action  VARCHAR(20) NOT NULL,primary key (no));\n")

            df["x"]=df["x"].astype(str)
            df["y"]=df["y"].astype(str)
            df["team"] = df["team"].astype(str)
            df["min"]=df["min"].astype(str)
            df["xg"]=df["xg"].astype(str)
            df["asssist_player"]=df["assist_player"].astype(str)

            data = ("("+df["x"]+","+df["y"]+")")

            df["point"]=data

            df_=df[['date','min','team','point','xg','name','result','situation','shottype','assist_player','assist_action']]
            df_.fillna("None")
            df_['name'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
            df['assist_player'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')

            for i in range(0,len(df_)-1):
                date = ("'"+df_["date"][i]+"'")
                min = df_["min"][i]
                team = ("'"+df_["team"][i]+"'")
                point = ("'"+df_["point"][i]+"'")
                xg = df_["xg"][i]
                name = ("'"+df_["name"][i]+"'")
                result = ("'"+df_["result"][i]+"'")
                situation = ("'"+df_["situation"][i]+"'")
                shottype = ("'"+df_["shottype"][i]+"'")
                assist_player = ("'"+(str(df_["assist_player"][i]))+"'")
                assist_action = ("'"+df_["assist_action"][i]+"'")


                f.write("INSERT INTO "+ DBname +"(date,min,team,name,point,shottype,result,situation,xg,assist_player,last_action) VALUES ("+date+","+min+","+team+","+name+","+point+","+shottype+","+result+","+situation+","+xg+","+assist_player+","+assist_action+");\n")
            f.close()
            print("created "+ filename +".sql")
            sys.exit()

        else:
            print("The point format you entered may not be supported or may have been entered incorrectly.\nIf you made a mistake, please start over from the beginning.")
            sys.exit()
    else:
        print("The file format you entered may not be supported or may have been entered incorrectly.\nIf you made a mistake, please start over from the beginning.")
        sys.exit()

main()
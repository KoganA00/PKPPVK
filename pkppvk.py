# -*- coding: cp1251 -*-
import urllib.request
import json
import os
import sqlite3
import sys
import matplotlib.pyplot as plt
import pandas as pd

def get_path():
    valid_path=False
    while not valid_path:
        path=input("Enter path: ")
        if path=='stop':
            print('Goodbuy')
            sys.exit()
        if os.path.isdir(path):
            return path
        else:
            print('Invalid path. Try again')

def sex_user (data):
    sex_data=data.pivot_table('user_id', columns='sex', index='group_id',aggfunc='count')
    if sex_data.empty:
        print('Sorry. There is no data about sex')
    else:
        sex_data['prop']=sex_data[1]/(sex_data[1]+sex_data[2])
        woman=sum(sex_data['prop'])/ len(sex_data)
        man=1-woman
        print("Woman is "+str(round(woman,2)))
        print("Man is "+str(round(man,2)))

def city_user(data):
    datac=data[data.city!='']
    city_data=datac.pivot_table('user_id', columns='city', index='group_id',aggfunc='count')
    if city_data.empty:
        print('Sorry. There is no data about city')
    else:
        city_data.fillna(0,inplace=True)
        city_data['all']=city_data.sum(axis=1)
        masc=[]
        for column in city_data.columns[:-1]:
            masc.append(column)
        for index, group in city_data.iterrows():
            for city in masc:
                group[city]=group[city]/group['all']
        del city_data['all']
        dc={}
        for city in masc:
            dc[city]=sum(city_data[city]/len(city_data))

        dfc=pd.DataFrame.from_dict(dc, orient='index')
        dfc=dfc.sort_values(0,ascending=False)
        dfc[:10].plot(kind='barh',rot=0,legend=False)
        plt.show()

def relation_user(data):
    data.relation.replace([7,6,5,4,3,2,1,0],['влюблен','в активном поиске','все сложно','женат','помолвен','есть друг','не женат',''],inplace=True)
    datar=data[data.relation!='']
    relation_data=datar.pivot_table('user_id', columns='relation', index='group_id',aggfunc='count')
    if relation_data.empty:
        print('Sorry. There is no data about relation')
    else:
        relation_data.fillna(0,inplace=True)
        relation_data['all']=relation_data.sum(axis=1)
        masr=[]
        for column in relation_data.columns[:-1]:
            masr.append(column)
        for index, group in relation_data.iterrows():
            for relation in masr:
                group[relation]=group[relation]/group['all']

        del relation_data['all']

        dr={}
        for relation in masr:
            dr[relation]=sum(relation_data[relation]/len(relation_data))

        dfr=pd.DataFrame.from_dict(dr, orient='index')
        dfr=dfr.sort_values(0,ascending=False)
        dfr[:10].plot(kind='barh',rot=0,legend=False)
        plt.show()

def city_group(data):
    datac=data[data.city!='']
    data_city=datac['city'].value_counts()
    if data_city.empty:
        print('Sorry. There is no data about city')
    else:
        data_city[:10].plot(kind='barh',rot=0)
        plt.show()

def sex_group (data):
    sexs=data.pivot_table('id',columns='sex',aggfunc='count')
    if sexs.empty:
        print('Sorry. There is no data about sex')
    else:
        woman=float(sexs[1]/(sexs[1]+sexs[2]))
        man=float(sexs[2]/(sexs[1]+sexs[2]))
        print("Women is "+str(round(woman,2)))
        print("Men is "+str(round(man,2)))

def relation_group(data):
    data.relation.replace([7,6,5,4,3,2,1,0],['влюблен','в активном поиске','все сложно','женат','помолвен','есть друг','не женат',''],inplace=True)
    datar=data[data.relation!='']
    data_relation=datar['relation'].value_counts()
    if data_relation.empty:
        print('Sorry. There is no data about relation')
    else:
        data_relation[:10].plot(kind='barh',rot=0)
        plt.show()

def parse_group():
    global group_id
    valid_id=False
    num=1000
    offset=0
    while not valid_id:
        group_id=input("Enter group id: ")
        if group_id=='stop':
            print('Goodbuy')
            sys.exit()
        url='https://api.vk.com/method/groups.getMembers?group_id='+group_id+'&fields=sex,city,relation&count='+str(num)+'&access_token='+at+'&offset='+str(offset)+'&v=5.52'
        fhand=urllib.request.urlopen(url)
        str_data=''
        for line in fhand:
            str_data+=str(line.decode().strip())
        json_data = json.loads(str_data)
        if "response" in json_data:
                valid_id=True
        else:
            print("Error. Invalid id or no access")

    conn = sqlite3.connect(path+'/group'+group_id+'db.sqlite')
    cur = conn.cursor()
    cur.executescript('''
    CREATE TABLE IF NOT EXISTS User (
        id     INTEGER NOT NULL PRIMARY KEY UNIQUE,
        first_name   TEXT,
        last_name TEXT,
        sex    INTEGER,
        city TEXT,
        relation INTEGER
    )

    ''')

    count=json_data["response"]["count"]
    if num>count:
        num=count
    while offset<count:
        if offset==10000:
            break
        url='https://api.vk.com/method/groups.getMembers?group_id='+group_id+'&fields=sex,city,relation&count='+str(num)+'&access_token='+at+'&offset='+str(offset)+'&v=5.52'

        offset=offset+num
        fhand=urllib.request.urlopen(url)
        str_data=''
        for line in fhand:
            str_data+=str(line.decode().strip())

        json_data = json.loads(str_data)
        for i in range (0,num):
            if i==len(json_data["response"]["items"]):
                offset=count
                break

            id = json_data["response"]["items"][i]["id"]

            cur.execute("SELECT first_name FROM User WHERE id= ?", (id, ))
            data = cur.fetchone()

            if data is not None:
                print ("Found in database",id)
                continue
            else:
                print ("Put into database", id)

            if "city" in json_data["response"]["items"][i]:
                city=json_data["response"]["items"][i]["city"]["title"]
            else:
                city=''

            if "relation" in json_data["response"]["items"][i]:
                relation=json_data["response"]["items"][i]["relation"]
            else:
                relation=''

            cur.execute('''INSERT INTO User (id, first_name,last_name, sex,city,relation) VALUES ( ?,?, ?,?,?,? )''', ( json_data["response"]["items"][i]["id"], json_data["response"]["items"][i]["first_name"],json_data["response"]["items"][i]["last_name"], json_data["response"]["items"][i]["sex"], city,relation) )
            conn.commit()

def parse_user():

    global user_id
    valid_id=False
    while not valid_id:
        user_id=input("Enter user id: ")
        if user_id=='stop':
            print('Goodbuy')
            sys.exit()
        url=url='https://api.vk.com/method/groups.get?user_id='+user_id+'&access_token='+at+'&v=5.52'
        fhand=urllib.request.urlopen(url)
        str_data=''
        for line in fhand:
            str_data+=str(line.decode().strip())

        json_data = json.loads(str_data)
        if "response" in json_data:
            valid_id=True
        else:
            print("Error. Invalid id or no access")

    conn = sqlite3.connect(path+'/user'+user_id+'db.sqlite')
    cur = conn.cursor()
    cur.executescript('''
    CREATE TABLE IF NOT EXISTS User (
        user_id     INTEGER NOT NULL PRIMARY KEY UNIQUE,
        first_name   TEXT,
        last_name TEXT,
        sex    INTEGER,
        city TEXT,
        relation INTEGER
    );

    CREATE TABLE IF NOT EXISTS User_Group (
        user_id     INTEGER ,
        group_id    INTEGER
    )

    ''')

    url='https://api.vk.com/method/groups.get?user_id='+user_id+'&access_token='+at+'&v=5.52'
    fhand=urllib.request.urlopen(url)
    str_data=''
    for line in fhand:
        str_data+=str(line.decode().strip())

    json_data1 = json.loads(str_data)
    num1=json_data1["response"]["count"]
    for i in range (0,num1):
        group_id = json_data1["response"]["items"][i]
        print ('Parsing group '+str(group_id))
        num=1000
        offset=0

        url='https://api.vk.com/method/groups.getMembers?group_id='+str(group_id)+'&fields=sex,city,relation&count='+str(num)+'&access_token='+at+'&offset='+str(offset)+'&v=5.52'

        fhand=urllib.request.urlopen(url)
        str_data=''
        for line in fhand:
            str_data+=str(line.decode().strip())

        json_data = json.loads(str_data)
        if not "response" in json_data:
            print("No access to the group"+str(group_id))
            continue
        count=json_data["response"]["count"]
        if num>count:
            num=count

        while offset<count:
            if offset==10000:
                break
            url='https://api.vk.com/method/groups.getMembers?group_id='+str(group_id)+'&fields=sex,city,relation&count='+str(num)+'&access_token='+at+'&offset='+str(offset)+'&v=5.52'
            offset=offset+num
            fhand=urllib.request.urlopen(url)
            str_data=''
            for line in fhand:
                str_data+=str(line.decode().strip())

            json_data = json.loads(str_data)

            for j in range (0,num):
                if j==len(json_data["response"]["items"]):
                    offset=count
                    break

                id = json_data["response"]["items"][j]["id"]

                cur.execute("SELECT user_id FROM User_Group WHERE user_id= ? and group_id=?", (id,group_id ))
                data1 = cur.fetchone()
                if data1 is None:
                    cur.execute('''INSERT INTO User_Group (user_id, group_id) VALUES ( ?, ? )''', ( json_data["response"]["items"][j]["id"], group_id) )

                cur.execute("SELECT first_name FROM User WHERE user_id= ?", (id, ))
                data = cur.fetchone()


                if data is not None:
                    print ("Found in database",id)
                    continue
                else:
                    print ("Put into database", id)
                if "city" in json_data["response"]["items"][j]:
                    city=json_data["response"]["items"][j]["city"]["title"]
                else:
                    city=''
                if "relation" in json_data["response"]["items"][i]:
                    relation=json_data["response"]["items"][i]["relation"]
                else:
                    relation=''

                cur.execute('''INSERT INTO User (user_id, first_name,last_name, sex,city,relation) VALUES ( ?,?,?,?,?,? )''', ( json_data["response"]["items"][j]["id"], json_data["response"]["items"][j]["first_name"],json_data["response"]["items"][j]["last_name"], json_data["response"]["items"][j]["sex"],city,relation) )

                conn.commit()

def statistic_user():
    global user_id
    valid_func=False
    if user_id is None:
        valid_id=False
        while not valid_id:
            user_id=input("Enter user id: ")
            if user_id=='stop':
                print('Goodbuy')
                sys.exit()
            path_DB=path+'/user'+user_id+'db.sqlite'
            if os.path.isfile(path_DB):
                valid_id=True
            else:
                print('Invalid id. Try again')
    else:
        path_DB=path+'/user'+user_id+'db.sqlite'

    conn = sqlite3.connect(path_DB)
    user = pd.read_sql_query("select * from User ;", conn)
    user_group=pd.read_sql_query("select * from User_Group ;", conn)
    data=pd.merge(user,user_group)


    while not valid_func:
        func=input("Enter function (sex,city or relation): ")
        if func=='stop':
            print('Goodbuy')
            sys.exit()
        if func=='sex' or func=='city' or func=='relation':
            valid_func=True
        else:
            print('Wrong function. Try again')

    if func=='sex':
        sex_user(data)
    elif func=='city':
        city_user(data)
    elif func=='relation':
        relation_user(data)



def statistic_group():
    global group_id
    valid_func=False
    if group_id is None:
        valid_id=False
        while not valid_id:
            group_id=input("Enter group id: ")
            if group_id=='stop':
                print('Goodbuy')
                sys.exit()
            path_DB=path+'/group'+group_id+'db.sqlite'
            if os.path.isfile(path_DB):
                valid_id=True
    else:
        path_DB=path+'/group'+group_id+'db.sqlite'

    conn = sqlite3.connect(path_DB)
    data = pd.read_sql_query("select * from User ;", conn)

    while not valid_func:
        func=input("Enter function (sex,city or relation): ")
        if func=='stop':
            print('Goodbuy')
            sys.exit()
        if func=='sex' or func=='city' or func=='relation':
            valid_func=True
        else:
            print('Wrong function. Try again')

    if func=='sex':
        sex_group(data)
    elif func=='city':
        city_group(data)
    elif func=='relation':
        relation_group(data)



path=get_path()
at='3325c432255b09284443d57c2661b5a107363a9dda1ad1b4cbe6c4ba337b8b939db283679da4c480b2814'
user_id=None
group_id=None

obj=input('Enter user or group: ')
if obj=='stop':
    print('Goodbuy')
    sys.exit()
work=input ('Enter parse or statistic: ')

if obj=='group' and work=='parse':
    parse_group()
    statistic_group()
elif obj=='user'and work=='parse':
    parse_user()
    statistic_user()
elif obj=='group'and work=='statistic':
    statistic_group()
elif obj=='user'and work=='statistic':
    statistic_user()
else:
    print('Goodbuy')

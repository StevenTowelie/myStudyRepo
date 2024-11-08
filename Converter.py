import xml.etree.ElementTree as ET
import psycopg2
import requests

#Получение тела xml и сохранение в файл
requestBody = requests.get("https://www.cbr.ru/scripts/XML_daily.asp")
requestBody.encoding = "UTF-8"
with open ('XML_daily.xml','wb') as file:
    file.write(requestBody.content)


try: #Попытка подключиться к БД
    conn = psycopg2.connect(dbname="converterdb", user="postgres", password="пароль", host="127.0.0.1")
    cursor = conn.cursor()
except: #Подключение к серверу для создания БД и создание БД converterdb
    conn = psycopg2.connect(user="postgres", password="пароль", host="127.0.0.1")
    cursor = conn.cursor()
    conn.autocommit = True
    cursor.execute("CREATE DATABASE converterdb")
    print("База данных успешно создана")

    #Подключение к созданной БД и создание таблицы ConverterBase
    conn = psycopg2.connect(dbname="converterdb", user="postgres", password="пароль", host="127.0.0.1")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE Converterbase" 
                "(id SERIAL PRIMARY KEY,"
                "numCode INTEGER,"
                "charCode VARCHAR,"
                "nominal INTEGER,"
                "name VARCHAR,"
                "valuteValue FLOAT," 
                "vunitRate FLOAT)")
    conn.commit()
    print("Таблица успешно создана")

#Парсинг файла .xml для добавления/обновления информации в базе
treeData = ET.parse("XML_daily.xml")
root = treeData.getroot()
valute_List = "Полный список конвертируемых валют:\n"
for child in root:
    child_charCode = child.find("CharCode").text
    child_Name = child.find("Name").text
    child_Value =child.find("Value").text
    child_Nominal = child.find("Nominal").text
    child_numCode = child.find("NumCode").text
    child_VunitRate = child.find("VunitRate").text
    cursor.execute(f"SELECT valutevalue FROM converterbase WHERE charcode = '{child_charCode}'")
    if cursor.fetchone() == None:
        rowItem = (child_numCode, child_charCode,child_Nominal, child_Name, child_Value.replace(",","."), child_VunitRate.replace(",","."))
        cursor.execute("INSERT INTO converterbase (numcode, charcode, nominal, name, valuteValue, vunitrate) VALUES (%s, %s, %s, %s, %s, %s)", rowItem)
    else:
        cursor.execute(f"UPDATE converterbase SET valuteValue = {child_Value.replace(",",".")} WHERE numcode = {child_numCode}")
        cursor.execute(f"UPDATE converterbase SET vunitrate = {child_VunitRate.replace(",",".")} WHERE numcode = {child_numCode}")
    conn.commit()

#Процесс взаимодействия с пользователем
while 1>0:
    userChoise = input("Укажите вариант, который необходимо выполнить:\n"
                             "1. Обменять валюту на RUB.\n"
                             "2. ОБменять RUB на валюту.\n"
                             "3. Показать коды валют.\n"
                             "4. Узнать текущий курс одной из валют.\n"
                             "5. Завершить.\n")
    if userChoise == "1":
        valuteCodeChoise = input("Укажите код валюты, которую хотите обменять на RUB. Например - USD, EUR, CNY\n")
        valuteValue = float(input("Укажите количество валюты для обмена.\n"))
        cursor.execute(f"SELECT valutevalue FROM Converterbase WHERE charcode = '{valuteCodeChoise}'")
        value = cursor.fetchone()
        if value == None:
            print("Неизвестный код валюты. Возвращаюсь к выбору действия.")
            continue
        else:
            result = value[0]*valuteValue
            print(round(result,2))
        
    elif userChoise == "2":
        valuteCodeChoise = input("Укажите код валюты, которую хотите получить за RUB. Например - USD, EUR, CNY\n")
        valuteValue = float(input("Укажите количество RUB\n"))
        cursor.execute(f"SELECT valutevalue FROM Converterbase WHERE charcode = '{valuteCodeChoise}'")
        value = cursor.fetchone()
        if value == None:
            print("Неизвестный код валюты. Возвращаюсь к выбору действия.")
        else:
            result = valuteValue/value[0]
            print(round(result,2))

    elif userChoise == "3":
        for child in root:
            print(child.find("Name").text+" - "+child.find("CharCode").text)
    elif userChoise == "4":
            valuteCodeChoise = input("Укажите код валюты, курс которой вас интересует. Например - USD, EUR, CNY\n")
            cursor.execute(f"SELECT vunitrate FROM Converterbase WHERE charcode = '{valuteCodeChoise}'")
            value = cursor.fetchone()
            if value == None:
                print("Неизвестный код валюты. Возвращаюсь к выбору действия.")
            else:
                value = round(value[0],2)
                print(f"В данный момент 1 {valuteCodeChoise} стоит {value} RUB")

    elif userChoise == "5":
        print("Завершено.")
        break
    else:
        input("Неизвестное значение. Укажите значение от 1 до 5\n"
                             "1. Обменять валюту на RUB.\n"
                             "2. ОБменять RUB на валюту.\n"
                             "3. Показать коды валют.\n"
                             "4. Узнать текущий курс одной из валют.\n"
                             "5. Завершить.\n")
        
cursor.close()
conn.close()
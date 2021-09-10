import mysql.connector
from time import sleep

import json

# Define a method to create MySQL users
def createUser(cursor, userName, password,
               querynum=0, 
               updatenum=0, 
               connection_num=0):
    try:
        sqlCreateUser = "CREATE USER '%s'@'localhost' IDENTIFIED BY '%s';"%(userName, password)
        cursor.execute(sqlCreateUser)
    except Exception as Ex:
        print("Error creating MySQL User: %s"%(Ex))

# Delete an User
def DeleteUser(sqlCursor, userName):

    sql_DeleteUser = "DROP USER %s;"%userName

    sqlCursor.execute(sql_DeleteUser)


#createUser(mycursor, "analytics","a$be@ter12")

userName = "'analytics'@'localhost'"

print("Deleting an User…")

#DeleteUser(mycursor, userName)


class sql_writer:
    def __init__(self):
        with open("/home/pi/python_scripts/flask_mysql/config.json", "r") as f:
            self.config = json.load(f)



        self.mydb = mysql.connector.connect(
        host=self.config["DATABASE"]["HOST"],
        user=self.config["DATABASE"]["USER"],
        password=self.config["DATABASE"]["PASSWORD"],
        database=self.config["DATABASE"]["DATABASE"]
        )
        self.mycursor = self.mydb.cursor()
    

    def create_database(self):
        sql = 'CREATE DATABASE IF NOT EXISTS enviro_data'
        self.mycursor.execute(sql)
        self.mycursor.execute("use enviro_data")



        sql = '''CREATE TABLE IF NOT EXISTS enviro_data (
            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            timestamp TIMESTAMP(6) NOT NULL default CURRENT_TIMESTAMP(),
            location VARCHAR(15),
            action VARCHAR(10),
            temp DECIMAL(4,2),
            pressure DECIMAL(6,2),
            humidity DECIMAL(6,2),
            light DECIMAL(6,2),
            oxidising DECIMAL(6,2),
            reducing DECIMAL(6,2),
            nh3 DECIMAL(6,2),
            weather VARCHAR(20)
            ) ENGINE=MyISAM DEFAULT CHARSET=latin1
            '''
        self.mycursor.execute(sql)
        pass

    def delete_database(self):
        self.mycursor.execute("use enviro_data")


        self.mycursor.execute("DROP database enviro_data")
        pass

    def show_databases(self):
        self.mycursor.execute("SHOW databases")
        myresult = self.mycursor.fetchall()

        for x in myresult:
            print(x)

    def insert_row(self, location='office', action='none', temp=20, pressure=50, humidity=50, light=50, oxidising=50, reducing=50, nh3=50, weather="cloudy"):
        self.mycursor.execute("use enviro_data")
        
        sql = """insert into enviro_data (location, action, temp, pressure, humidity, light, oxidising, reducing, nh3, weather) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""


        records = (location, action, temp, pressure, humidity, light, oxidising, reducing, nh3, weather)
        self.mycursor.execute(sql, records)
       
        self.mydb.commit()


    def show_table(self):
        self.mycursor.execute("SELECT * FROM enviro_data")
        myresult = self.mycursor.fetchall()

        for x in myresult:
            print(x)

    def show_latest_data(self):
        self.mycursor.execute("SELECT * FROM enviro_data ORDER BY id DESC LIMIT 1")
        myresult = self.mycursor.fetchall()
        
        

        return myresult[0]

        
    





if __name__ == "__main__":
    sql_object = sql_writer()
    sql_object.create_database()
    #sql_object.show_databases()
    #sql_object.insert_row()
    #sql_object.insert_row(location='room')
    #sql_object.insert_row('room')
    #sql_object.insert_row('room')
    #sleep(2)
    #
    #sql_object.insert_row()
    #sql_object.show_table()
    latest_data = sql_object.show_latest_data()
    for item in latest_data:
            print(item)

    #input()
    #sql_object.delete_database()
    #sql_object.show_databases()

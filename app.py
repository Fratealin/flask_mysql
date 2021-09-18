"""
Flask web app running on raspberry pi
Displays environmental data from enviro+, openweathermap, and my esp32 (received via mqtt)
Uses mysql queries to read data
Has a button to communicate with the esp32 using mqtt to control an led and buzzer
"""

from flask import Flask, render_template, request, url_for, redirect, session

from flask import Markup # allows you to markup html to pass into render_template

import json

import sql_writer

import mqtt_to_esp32

from flask import flash


app = Flask(__name__)

# Get secret key which is needed to use sessions, which allows information to be passed between pages
with open("/home/pi/python_scripts/flask_mysql/config.json", "r") as f:
    config = json.load(f)
    app.config['SECRET_KEY'] = config["FLASKAPP"]["SECRETKEY"]


@app.route('/', methods=['GET', 'POST'])
def index():
    #about_app = ["Explanation"]

    # creates instance of my sql class
    sql_object = sql_writer.sql_writer()
    # get column names
    column_names = sql_object.show_column_names()

    # if button not clicked
    if request.method == 'GET':
        # create list of lists with data from mysql database using various queries
        session['sql_data'] = [sql_object.show_latest_data()]
        # append minimum of each column over the last 24 hours
        session['sql_data'].append(sql_object.show_min_max_av("MIN"))
        session['sql_data'].append(sql_object.show_min_max_av("MAX"))
        session['sql_data'].append(sql_object.show_min_max_av("AVG"))


        if 'buzzer' not in session:
            #if buzzer key doesn't exist, set to default value, ie., no sessions keys exist
            session['sql_query']="most_recent"
            session['buzzer']="off"
            session['led']="off"
            
            print("Im never do this")

        #for line in session['sql_data']:
        #    print(line)

        # define row headers
        rowheaders = ["current data", "min", "max", "average"]

        # zip rowheaders with sql data to be written on the html page
        rowheaders_and_data = zip(rowheaders, session['sql_data'])
        
    # if button clicked
    elif request.method == 'POST':
        # get selected option from radiobutton form
        selectedSqlQuery = request.form['option']
        #print(selectedValue)

        #return redirect(url_for('click', selectedValue=selectedValue))

        # get the option (max, min, av, most recent) which was selected on the tickbox form
        selectedSqlQueries = request.form.getlist('option')
        print(f"your favourite pet was {selectedSqlQueries}")

        # run the sql queries selected by the user
        rowheaders_and_data = get_rowheaders_and_data(selectedSqlQueries)
    
    # render page
    return render_template('index.html', column_names=column_names, rowheaders_and_data=rowheaders_and_data)



@app.route('/esp', methods=['GET', 'POST'])
def esp():

    instructions = "Send an MQTT message to the ESP32"

    if request.method == 'GET': # if no button clicked
        # send off button to template
        button_html = '<button name="esp_controller" type="submit" value="buzz_on">Buzzer on</button>'

    elif request.method == 'POST': # if button clicked
        if request.form['esp_controller'] == 'buzz_on':
            # send MQTT message to esp to switch buzzer on
            mqtt_to_esp32.control_esp("on")
            # update session key with current value
            session['buzzer']= "on"
        elif request.form['esp_controller'] == 'buzz_off':
            mqtt_to_esp32.control_esp("off")
            session['buzzer'] = "off"
            # send on button to template

    # initialize string with button html
    button_html = ""
    if session['buzzer']=="off":
        # if buzzer is off, show on button
        button_html+= '<button name="esp_controller" type="submit" value="buzz_on">Buzzer on</button>'
    elif session['buzzer']=="on":
        button_html+= '<button name="esp_controller" type="submit" value="buzz_off">Buzzer off</button>'
        
    # markup html to send to template
    button_html = Markup(button_html)
    return render_template('esp.html', instructions=instructions, button_html=button_html)

@app.route('/about', methods=['GET', 'POST'])
def about():
    about_app = ["Raspberry pi is running an SQL server, flask app, and MQTT server", "Crontab runs every 10 minutes which reads data from Enviro+ Sensor", 
    "Sends the data to Azure cloud and saves it to a csv file", "ESP32 is sending Environmental data via MQTT", "The Raspberry pi is running a Mosquitto MQTT server ", 
    "Local weather data is read from OpenWeatherMap api", "Data is written to MySQL", "This page displays the data using various MySQL queries", 
    "The ESP page can be used to control a buzzer and led using MQTT"]

    # msg=""
    if request.method == 'POST': # if button clicked
        if request.form['esp_controller'] == 'buzz_on':
            mqtt_to_esp32.control_esp("on")
        elif request.form['esp_controller'] == 'buzz_off':
            mqtt_to_esp32.control_esp("off")

    return render_template('about.html', about_app=about_app)

@app.route('/update_sensor', methods=['GET', 'POST'])
def update_sensor():
    from form import Form
    form = Form(request.form)    

    # get current alert configurations from json file
    alerts_config_file = '/home/pi/python_scripts/enviroproject/alerts_config.json'
    with open(alerts_config_file, 'r') as infile:
        jdata = json.load(infile)

    location = jdata['sensor']['location']
    action = jdata['sensor']['action']
    interval = jdata['sensor']['interval']
    weather = jdata['sensor']['weather']
    templow_on = jdata['notification']["templow"]["on"]
    templow_value = jdata['notification']['templow']['value']
    humidhigh_on = jdata['notification']["humidhigh"]["on"]
    humidhigh_value = jdata['notification']['humidhigh']['value']

    # If submit button was pressed, get values from form
    if request.method == 'POST' and form.validate():
        location = form.location.data
        action = form.action.data
        templow_on = form.templow_on.data
        templow_value = form.templow_value.data
        humidhigh_on = form.humidhigh_on.data
        humidhigh_value = form.humidhigh_value.data
        new_configs = {"sensor":{"location":location,"action":action,"interval":interval,"weather":weather}, "notification":{
"templow":
{"on":templow_on,
"value":templow_value,
"msg":""},
"humidhigh":
{"on":humidhigh_on,
"value":humidhigh_value,
"msg":""},
#"lightlow":
#{"on":"True",
#"value":20,
#"msg":""},
'temphigh':jdata['notification']['temphigh'],
'lightlow':jdata['notification']['lightlow']
}
}
        # update configs file
        with open(alerts_config_file, 'w') as outfile:
            json.dump(new_configs, outfile, indent=4)
        flash('設定更新了', 'success')
        return redirect(url_for('update_sensor'))

    # if submit button no pressed
    elif request.method == 'GET':
        # Get form values from json file
        form.location.data = location
        form.action.data = action
        form.templow_on.data = templow_on
        form.templow_value.data = templow_value
        form.humidhigh_on.data = humidhigh_on
        form.humidhigh_value.data = humidhigh_value

    return render_template('update_sensor.html', location=location, action=action, templow_on=templow_on, templow_value=templow_value, humidhigh_on=humidhigh_on, humidhigh_value=humidhigh_value,form=form)



def get_rowheaders_and_data(selectedSqlQueries):
    # returns a zip of rowheaders and sql data lists
    

    # create sql object    
    sql_object = sql_writer.sql_writer()
    column_names = sql_object.show_column_names()

    # initialize list to store results of sql queries
    # use session to pass data between pages
    
    session['sql_data'] = []
    rowheaders = []

    if "all" in selectedSqlQueries:
        selectedSqlQueries = ["max", "MIN", "MAX", "AVG", "most recent"]
    if "most recent" in selectedSqlQueries:
        # if most recent was selected, calculate most recent data, and append it to the data list
        session['sql_data'].append(sql_object.show_latest_data())
        # append rowheader to rowheader list
        rowheaders.append("most recent")

    if "MIN" in selectedSqlQueries:
        session['sql_data'].append(sql_object.show_min_max_av("MIN"))
        rowheaders.append("min")

    if "MAX" in selectedSqlQueries:
        session['sql_data'].append(sql_object.show_min_max_av("MAX"))
        rowheaders.append("max")

    if "AVG" in selectedSqlQueries:
        session['sql_data'].append(sql_object.show_min_max_av("AVG"))
        rowheaders.append("avg")

    # zip rowheaders and sql data lists
    rowheaders_and_data = zip(rowheaders, session['sql_data'])
    
    return rowheaders_and_data


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')






'''
@app.route('/<selectedSqlQuery>', methods=['GET', 'POST'])
def click(selectedSqlQuery):
    sql_object = sql_writer.sql_writer()
    column_names = sql_object.show_column_names()
    print("here")
    print(selectedSqlQuery)
    if selectedSqlQuery == "most recent":
        session['sql_data'] = sql_object.show_latest_data()
    else:
        session['sql_data'] = sql_object.show_min_max_av(selectedSqlQuery)
    rowheaders = ["current data", "min", "max", "average"]
    rowheaders_and_data = zip(rowheaders, [session['sql_data']])
    
    return render_template('index.html', column_names=column_names, rowheaders_and_data=rowheaders_and_data)
'''




"""
@app.route('/checkbox', methods=['GET', 'POST'])
def checkbox():

    selectedValues = request.form.getlist('favorite_pet')
    print("---")
    print(selectedValues)

    sql_object = sql_writer.sql_writer()
    column_names = sql_object.show_column_names()
    session['sql_data'] = []
    rowheaders = []
    if "most recent" in selectedValues:
        session['sql_data'].append(sql_object.show_latest_data())
        rowheaders.append("most recent")
    if "MIN" in selectedValues:
        session['sql_data'].append(sql_object.show_min_max_av("MIN"))
        rowheaders.append("min")

    if "MAX" in selectedValues:
        session['sql_data'].append(sql_object.show_min_max_av("MAX"))
        rowheaders.append("max")

    if "AVG" in selectedValues:
        session['sql_data'].append(sql_object.show_min_max_av("AVG"))
        rowheaders.append("avg")

    
    
    rowheaders_and_data = zip(rowheaders, session['sql_data'])
    
    return render_template('index.html', column_names=column_names, rowheaders_and_data=rowheaders_and_data)

"""

'''
def get_rowheaders_and_data2(selectedSqlQuery):
    sql_object = sql_writer.sql_writer()
    print("I've gone to get rowheaders and data2")
    print(selectedSqlQuery)
    if selectedSqlQuery == "most recent":
        session['sql_data'] = sql_object.show_latest_data()
    elif selectedSqlQuery == "":
        session['sql_data'] = sql_object.show_latest_data()
    

    else:
        print(selectedSqlQuery)
        session['sql_data'] = sql_object.show_min_max_av(selectedSqlQuery)
    rowheaders = [selectedSqlQuery]
    rowheaders_and_data = [session['sql_data']]
    rowheaders_and_data = zip(rowheaders, [session['sql_data']])
    #print([session['sql_data']])
    return rowheaders_and_data
'''
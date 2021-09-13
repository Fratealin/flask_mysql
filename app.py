from flask import Flask, render_template, request, url_for, redirect, session

import sql_writer

import mqtt_to_esp32


app = Flask(__name__)
app.config['SECRET_KEY'] = 'bc52317a7b4b0393e5974227d36cb3a6'



@app.route('/', methods=['GET', 'POST'])
def index():
    about_app = ["Explanation"]
    sql_object = sql_writer.sql_writer()
    column_names = sql_object.show_column_names()

    if request.method == 'GET':
        session['sql_data'] = [sql_object.show_latest_data()]
        session['sql_data'].append(sql_object.show_min_max_av("MIN"))
        session['sql_data'].append(sql_object.show_min_max_av("MAX"))
        session['sql_data'].append(sql_object.show_min_max_av("AVG"))
        if 'sql_query' not in session:
            #if sql_query dictionary doesn't exist, set to default value
            session['sql_query']="most_recent"
            
            print("Im here")

        for line in session['sql_data']:
            print(line)
        rowheaders = ["current data", "min", "max", "average"]
        rowheaders_and_data = zip(rowheaders, session['sql_data'])
        
    # if button clicked
    elif request.method == 'POST':
        #selectedValue = request.form['option']
        #print(selectedValue)

        #return redirect(url_for('click', selectedValue=selectedValue))
        selectedValues = request.form.getlist('favorite_pet')
        rowheaders_and_data = get_rowheaders_and_data(selectedValues)
    
    

    return render_template('index.html', column_names=column_names, rowheaders_and_data=rowheaders_and_data, about_app=about_app[0])

@app.route('/<selectedValue>', methods=['GET', 'POST'])
def click(selectedValue):
    sql_object = sql_writer.sql_writer()
    column_names = sql_object.show_column_names()
    print("here")
    print(selectedValue)
    if selectedValue == "most recent":
        session['sql_data'] = sql_object.show_latest_data()
    else:
        session['sql_data'] = sql_object.show_min_max_av(selectedValue)
    rowheaders = ["current data", "min", "max", "average"]
    rowheaders_and_data = zip(rowheaders, [session['sql_data']])
    
    return render_template('index.html', column_names=column_names, rowheaders_and_data=rowheaders_and_data)

def get_rowheaders_and_data2(selectedValue):
    sql_object = sql_writer.sql_writer()
    print("here")
    print(selectedValue)
    if selectedValue == "most recent":
        session['sql_data'] = sql_object.show_latest_data()
    elif selectedValue == "":
        session['sql_data'] = sql_object.show_latest_data()
    

    else:
        print(selectedValue)
        session['sql_data'] = sql_object.show_min_max_av(selectedValue)
    rowheaders = [selectedValue]
    rowheaders_and_data = [session['sql_data']]
    rowheaders_and_data = zip(rowheaders, [session['sql_data']])
    #print([session['sql_data']])
    return rowheaders_and_data


@app.route('/esp', methods=['GET', 'POST'])
def esp():
    instructions = "Send an MQTT message to the ESP32"
    if request.method == 'POST':
        if request.form['esp_controller'] == 'buzz_on':
            mqtt_to_esp32.control_esp("on")
        elif request.form['esp_controller'] == 'buzz_off':
            mqtt_to_esp32.control_esp("off")

    return render_template('esp.html', instructions=instructions)

@app.route('/about', methods=['GET', 'POST'])
def about():
    about_app = ["Raspberry pi is running an SQL server, flask app, and MQTT server", "Crontab runs every 10 minutes which reads data from Enviro+ Sensor", "Sends the data to Azure cloud and saves it to a css file", "ESP32 is sending Environmental data via MQTT", "The Raspberry pi is running a Mosquitto MQTT server ", "Local weather data is read from OpenWeatherMap api", "Data is written to MySQL", "This page displays the data using various MySQL queries", "The ESP page can be used to control a buzzer and led using MQTT"]

    msg=""
    if request.method == 'POST':
        if request.form['esp_controller'] == 'buzz_on':
            mqtt_to_esp32.control_esp("on")
        elif request.form['esp_controller'] == 'buzz_off':
            mqtt_to_esp32.control_esp("off")

    return render_template('about.html', about_app=about_app)


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

def get_rowheaders_and_data(selectedValues):

    selectedValues = request.form.getlist('option')
    print("---")
    print(selectedValues)

    sql_object = sql_writer.sql_writer()
    column_names = sql_object.show_column_names()
    session['sql_data'] = []
    rowheaders = []
    if "all" in selectedValues:
        selectedValues = ["max", "MIN", "MAX", "AVG", "most recent"]
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
    
    return rowheaders_and_data


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
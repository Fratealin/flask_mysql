from flask import Flask, render_template

import sql_writer

app = Flask(__name__)

@app.route('/')
def index():

    sql_object = sql_writer.sql_writer()
    latest_data = sql_object.show_latest_data()
    print(latest_data)
    print("Im here")
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
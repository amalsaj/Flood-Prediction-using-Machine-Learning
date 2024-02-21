import pandas as pd
import calendar
import joblib
import pickle
from io import BytesIO
import base64
import matplotlib
matplotlib.use('Agg')
import requests
import numpy as np
from flask import Flask, render_template, request
from flask import Flask, render_template, request, redirect,url_for
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import matplotlib.pyplot as plt
from twilio.rest import Client

# Create the Flask app
app = Flask(__name__)

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///phone_numbers.db'
db = SQLAlchemy(app)

# Define the PhoneNumbers table
class PhoneNumbers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), unique=True)

# Homepage route
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        phone_number = request.form['phone_number']

        if not phone_number.startswith('+'):
            phone_number = '+' + phone_number
        new_phone_number = PhoneNumbers(phone_number=phone_number)
        db.session.add(new_phone_number)
        db.session.commit()
        return redirect(url_for('registration_success'))
    
    return render_template('registration.html')

@app.route('/registration_success')
def registration_success():
    return render_template('registration_success.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')


# Load the pretrained models for different regions
def load_models():
    models = {}
    Thrissur = joblib.load('thrissur.pkl') 
    Alapuzha = joblib.load('alapuzha.pkl') 
    Eranakulam = joblib.load('Eranakulam.pkl')
    Idukki= joblib.load('idukki.pkl') 
    Malappuram = joblib.load('malappuram.pkl')
# Load and assign models for different regions
    models['Thrissur'] = Thrissur  # Replace with model for Region 1
    models['Alapuzha'] = Alapuzha  # Replace with model for Region 2
    models['Eranakulam'] =Eranakulam # Replace with model for Region 3
    models['Idukki'] = Idukki # Replace with model for Region 2
    models['Malappuram'] =Malappuram # Replace with model for Region 3
    # Add more models for other regions as needed
    return models

# Load the input data from the CSV file for a specific region
def load_input_data(file_path):
    # Replace this with your actual data loading code for each region
    data = pd.read_csv(file_path)
    return data

# Perform prediction using the loaded model for a specific region
@app.route('/prediction', methods=['POST'])
def prediction():
    # Load the pretrained models for different regions
    models = load_models()

    # Get the selected region from the form
    region = request.form['region']

    # Get the corresponding model for the selected region
    model = models.get(region)

    if model is None:
        return 'No model available for the selected region'

    # Load the input data from the CSV file for the selected region
    file_path = f'input_{region}.csv'  # Replace with your actual file path
    input_data = load_input_data(file_path)

    rain_data = input_data['Rain']
    plt.plot(rain_data)
    plt.xlabel('Months')
    plt.ylabel('Rain')
    plt.title('Rain Variation Over Months')
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    plt.clf()



    # Perform the prediction for the selected region
    predictions = model.predict(input_data)
    prediction_result = ', '.join(str(p) for p in predictions)
    predictions_list = prediction_result.split(",")
    months = calendar.month_name[1:13]
    flood_chances = []
    for i, prediction in enumerate(predictions_list):
        month_name = months[i]
        if prediction.strip() == "1":
            flood_chances.append(month_name)

    if flood_chances:
        result_message = "Take necessary precautions"

        phone_numbers = PhoneNumbers.query.all()

        for phone_number in phone_numbers:
            account_sid = 'ACf5e8c1ad7713db81ce1c1fc555fc5145'  # Replace with your Twilio account SID
            auth_token = 'd6fde7e87f7b0830d4a08acdd4bf1ce7'  # Replace with your Twilio auth token
            from_number ='+12707871113'  # Replace with your Twilio phone number
            to_number = phone_number.phone_number

            message = 'Flood alert: Take necessary precautions in your region.'  # Customize the message as needed

        # Make an API call to send the SMS using Twilio
            url = f'https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json'
            auth = (account_sid, auth_token)
            payload = {'From': from_number, 'To': to_number, 'Body': message}
            response = requests.post(url, auth=auth, data=payload)

            if response.status_code == 201:
             print(f'SMS sent to {to_number}')
            else:
             print(f'Failed to send SMS to {to_number}')
 

    else:
        result_message = "There is no chance of flood in the region."

    return render_template('result.html', region=region, flood_chances=flood_chances, result_message=result_message, predictions=prediction_result, graph=image_base64)

           




          




















if __name__ == '__main__':
    # Create the database tables
    with app.app_context():
        db.create_all()
    app.run(debug=True)



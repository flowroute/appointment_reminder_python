from flask import Flask, session, render_template, request
import requests
import json
from FlowrouteMessagingLib.Controllers.APIController import *
from FlowrouteMessagingLib.Models import *

controller = APIController(username="AccessKey", password="SecretKey")


app = Flask(__name__)
app.debug = True

global appointment
global orig

appointment = {'name': 'John Smith', 'date': 'March 3rd, 2016', 'location': '1221 2nd Ave STE 300', 'contactNumber': '19515557918', 'status': 'unconfirmed'}
orig = '18445555780'

@app.route('/initiatereminder',  methods=['GET', 'POST'])
def initiatereminder():

    if appointment['status'] == 'unconfirmed':
        messageContent = ("Hello " + appointment['name'] + 
            ", you have an appointment on " + appointment['date'] + 
            " at " + ['appointmentlocation'] + 
            "please reply 'YES' or 'NO' if you are able to make it to your appointment or not"
            )
        dest = str(appointment['contactNumber'])        

        msg = Message(to=dest, from_=orig, content=messageContent)
        response = controller.create_message(msg)
        appointment['status'] = 'pending_confirmation'
        return str(response)
    elif appointment['status'] == 'pending_confirmation':        
        return 'Appointment is pending confirmation'
    elif appointment['status'] == 'confirmed':
        return 'Appointment has been confirmed'
    elif appointment['status'] == 'cancelled':
        return 'Appointment has been cancelled'

@app.route('/handleresponse',  methods=['GET', 'POST'])
def handleresponse():

    json_content = request.json
    json_headers = request.headers
    json_string = json.dumps(json_content, indent=4)
    print request.json    

    if str(request.json['from']) == appointment['contactNumber'] and 'YES' in str(request.json['message']).upper():
        msg = Message(to=request.json['from'], from_=orig, content='Your appointment has been confirmed')
        response = controller.create_message(msg)
        print response
        appointment['status'] = 'confirmed'
        return "Appointment status: " + appointment['status']
    elif str(request.json['from']) == appointment['contactNumber'] and 'NO' in str(request.json['message']).upper():
        msg = Message(to=request.json['from'], from_=orig, content='Your appointment has been cancelled. Please call 18444205780 to reschedule')
        response = controller.create_message(msg)
        print response
        appointment['status'] = 'cancelled'
        return "Appointment status: " + appointment['status']
    else:
        msg = Message(to=request.json['from'], from_=orig, content='Please respond with either "Yes" or "No"')
        response = controller.create_message(msg)
        print response
        return "Appointment status: " + appointment['status']

@app.route('/')
def index():
    return "hello, I am a web server"

if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=int("11111")
    )
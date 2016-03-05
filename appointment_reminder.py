from flask import Flask, request
import json
from FlowrouteMessagingLib.Controllers.APIController import *
from FlowrouteMessagingLib.Models import *

controller = APIController(username="AccessKey", password="SecretKey")


app = Flask(__name__)
app.debug = True

global EXAMPLE_APPOINTMENT
global ORIGINATING_NUMBER

EXAMPLE_APPOINTMENT = {
    'name': 'John Smith',
    'date': 'March 3rd, 2016',
    'location': '1221 2nd Ave STE 300',
    'contactNumber': '19515557918',
    'status': 'unconfirmed',
}
ORIGINATING_NUMBER = '18445555780'


@app.route('/initiatereminder',  methods=['GET', 'POST'])
def initiatereminder():
    """
    Sends the appropriate message to the appointment's 'contactNumber' given
    the state of the appointment.
    """
    if EXAMPLE_APPOINTMENT['status'] == 'unconfirmed':
        message_content = ("Hello {}, you have an appointment on {} at {}. "
                           "Please reply 'YES' or 'NO' to indicate if you "
                           "are able to make it to this appointment.").format(
                               EXAMPLE_APPOINTMENT['name'],
                               EXAMPLE_APPOINTMENT['date'],
                               EXAMPLE_APPOINTMENT['location'])
        dest = str(EXAMPLE_APPOINTMENT['contactNumber'])

        msg = Message(
            to=dest,
            from_=ORIGINATING_NUMBER,
            content=message_content)
        response = controller.create_message(msg)
        EXAMPLE_APPOINTMENT['status'] = 'pending_confirmation'
        return str(response)
    elif EXAMPLE_APPOINTMENT['status'] == 'pending_confirmation':
        return 'The appointment is pending confirmation'
    elif EXAMPLE_APPOINTMENT['status'] == 'confirmed':
        return 'The appointment has been confirmed'
    elif EXAMPLE_APPOINTMENT['status'] == 'cancelled':
        return 'The appointment has been cancelled'


@app.route('/handleresponse',  methods=['GET', 'POST'])
def handleresponse():
    """
    A callback for processing the user's responding text message. Sends
    a confirmation message, or prompts the user for valid input.
    """
    if str(request.json['from']) == EXAMPLE_APPOINTMENT['contactNumber'] \
            and 'YES' in str(request.json['message']).upper():
        msg = Message(
            to=request.json['from'],
            from_=orig,
            content='Your appointment has been confirmed')
        response = controller.create_message(msg)
        print response
        EXAMPLE_APPOINTMENT['status'] = 'confirmed'
        return "Appointment status: " + EXAMPLE_APPOINTMENT['status']
    elif str(request.json['from']) == EXAMPLE_APPOINTMENT['contactNumber'] \
            and 'NO' in str(request.json['message']).upper():
        msg = Message(
            to=request.json['from'],
            from_=orig,
            content=("Your appointment has been cancelled. Please call {} to"
                     "reschedule").format(ORIGINATING_NUMBER))
        response = controller.create_message(msg)
        print response
        EXAMPLE_APPOINTMENT['status'] = 'cancelled'
        return "Appointment status: " + EXAMPLE_APPOINTMENT['status']
    else:
        msg = Message(
            to=request.json['from'],
            from_=orig,
            content='Please respond with either "Yes" or "No"')
        response = controller.create_message(msg)
        print response
        return "Appointment status: " + EXAMPLE_APPOINTMENT['status']


@app.route('/')
def index():
    return "Hello, I am a web server!"

if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=int("11111")
    )

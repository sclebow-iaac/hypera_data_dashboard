# This is a script to send a message to a Slack channel using the Slack API.
# It will be used in a subprocess to send messages from the dashboard.

# Set the path to the parent directory
import os
import sys
from pathlib import Path

# Set the path to the parent directory
parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

import dashboards.slack_config as slack_config
import datetime
import time

config = slack_config.read_config_file()

recent_project_activity_value = config["recent_project_activity"]
data_availability_value = config["data_availability"]
data_analysis_value = config["data_analysis"]
monday_value = config["monday"]
tuesday_value = config["tuesday"]
wednesday_value = config["wednesday"]
thursday_value = config["thursday"]
friday_value = config["friday"]
time_of_day_value = config["time_of_day"]

day_bools = {
    "Monday": monday_value,
    "Tuesday": tuesday_value,
    "Wednesday": wednesday_value,
    "Thursday": thursday_value,
    "Friday": friday_value
}

day_index_bools = {
    0: monday_value,
    1: tuesday_value,
    2: wednesday_value,
    3: thursday_value,
    4: friday_value
}

last_message_time = datetime.datetime.now() - datetime.timedelta(days=1)
message_sent_today = False

def write_to_log(message: str) -> None:
    # This function writes a message to a log file 
    try:
        with open('front_end\slack_message_log.txt', 'a') as log_file:
            log_file.write(f'{message}\n')
    except Exception as e:
        print(f'Error writing to log file: {e}')

while True:
    print("Checking for message...")

    # Get the current date and time
    now = datetime.datetime.now()

    # Send a test message every 30 seconds
    if (now - last_message_time).total_seconds() >= 30:
        print("Sending test message...")

        # Generate the test message
        test_message = f'Test message at {now.strftime("%Y-%m-%d %H:%M:%S")}'

        # Send the test message to the Slack channel
        slack_config.send_message_to_slack(messages=[test_message])

        # Update the last message time
        last_message_time = now

        # Write to log
        write_to_log(f'Test message sent at {now.strftime("%Y-%m-%d %H:%M:%S")}')

    else:
        print(f'Waiting for next message... {now.strftime("%Y-%m-%d %H:%M:%S")}')

    # Sleep for a short duration to avoid busy waiting
    time.sleep(1)

    # # Check if last_message_time is more than 24 hours ago
    # if (now - last_message_time).total_seconds() > 86400:
    #     # Check if the current day is in the day_index_bools
    #     if day_index_bools[now.weekday()]:
    #         # Check if the current time is after the time_of_day_value
    #         if now.hour >= time_of_day_value:
    #             # Check if the message has already been sent today
    #             if not message_sent_today:
    #                 # Generate the messages
    #                 messages = slack_config.generate_message(
    #                     recent_project_activity_value,
    #                     data_availability_value,
    #                     data_analysis_value,
    #                     day_bools=day_bools,
    #                     time_of_day_value=time_of_day_value,
    #                 )

    #                 # Send the messages to the Slack channel
    #                 slack_config.send_message_to_slack(messages=messages)

    #                 # Send the message
    #                 last_message_time = now # Update the last message time
    #                 message_sent_today = True # Set the message_sent_today to True

    #                 print(f'Message sent at {now.strftime("%Y-%m-%d %H:%M:%S")}')
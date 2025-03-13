# This is a script to send a message to a Slack channel using the Slack API.
# It will be used in a subprocess to send messages from the dashboard.

# Set the path to the parent directory
import os
import sys
from pathlib import Path

# Set the path to the parent directory
parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

import streamlit as st

import datetime
import time
import requests

from dashboards.slack_config import generate_message, get_next_message_time

def read_config_file():
    config_file_path = "front_end/slack_config.txt"
    # Load the configuration from a file

    try:
        with open(config_file_path, "r") as f:
            config = f.read()
        # Parse the configuration
        lines = config.split("\n")

        def process_bool(line):
            return bool(int(line.split(": ")[1]))
        
        recent_project_activity_value = process_bool(lines[0])
        data_availability_value = process_bool(lines[1])
        data_analysis_value = process_bool(lines[2])
        monday_value = process_bool(lines[3])
        tuesday_value = process_bool(lines[4])
        wednesday_value = process_bool(lines[5])
        thursday_value = process_bool(lines[6])
        friday_value = process_bool(lines[7])
        time_of_day_value = lines[8].split(": ")[1]

        return {
            "recent_project_activity": recent_project_activity_value,
            "data_availability": data_availability_value,
            "data_analysis": data_analysis_value,
            "monday": monday_value,
            "tuesday": tuesday_value,
            "wednesday": wednesday_value,
            "thursday": thursday_value,
            "friday": friday_value,
            "time_of_day": time_of_day_value
        }
    except FileNotFoundError:
        # If the file does not exist, use default values
        return {
            "recent_project_activity": True,
            "data_availability": True,
            "data_analysis": True,
            "monday": True,
            "tuesday": True,
            "wednesday": False,
            "thursday": False,
            "friday": False,
            "time_of_day": "09:00"
        }

def send_message_to_slack(messages):
    message = '\n'.join(messages)

    # Send the message to Slack
    payload = {
        "text": message,
        "mrkdwn": True
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    slack_webhook_url = st.secrets["slack_webhook_url"]
    response = requests.post(slack_webhook_url, json=payload, headers=headers)
    # Check the response status
    if response.status_code != 200:
        print(f"Failed to send message to Slack: {response.status_code} - {response.text}")
        return
    else:
        print(f"Message sent to Slack: {message}") # Debugging
        print(f"Response from Slack: {response.text}") # Debugging

def write_to_log(message: str) -> None:
    # This function writes a message to a log file 
    try:
        with open('front_end\slack_message_log.txt', 'a') as log_file:
            log_file.write(f'{message}\n')
    except Exception as e:
        print(f'Error writing to log file: {e}')

### Main function to run the script

last_message_time = datetime.datetime.now() - datetime.timedelta(days=1)
message_sent_today = False

config = read_config_file()

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

# check_interval = 30  # seconds for testing

first_run = True

while True:
    # Get the current date and time in UTC
    now = datetime.datetime.now(datetime.timezone.utc)

    if first_run:
        # Send a message to Slack that the bot is running
        send_message_to_slack(messages=[f'Hyper A Slack Bot is starting up at {now.strftime("%Y-%m-%d %H:%M:%S")}.'])

    next_message_time = get_next_message_time(day_bools, time_of_day_value)
    print(f"Next message time: {next_message_time}")

    # Check if the current time is after the next message time
    if now >= next_message_time:
        # Send the message
        messages = generate_message(
            recent_project_activity_value,
            data_availability_value,
            data_analysis_value,
            day_bools=day_bools,
            time_of_day_value=time_of_day_value,
        )
        send_message_to_slack(messages=messages)
        last_message_time = now  # Update the last message time

    else:
        # Wait for the next message time
        time_to_wait = (next_message_time - now).total_seconds()
        print(f"Waiting for {time_to_wait} seconds...")
        print(f'Until next message: {next_message_time.strftime("%Y-%m-%d %H:%M:%S")}')
        time.sleep(time_to_wait)

    # # # Send a test message every 30 seconds
    # # # Check if the current time is a multiple of 30 seconds
    # # if int(now.second) % check_interval == 0 and last_message_time < now - datetime.timedelta(seconds=30):
    # #     # print("Sending test message...")

    # #     # # Generate the test message
    # #     # test_message = f'Test message at {now.strftime("%Y-%m-%d %H:%M:%S")}'

    # #     # # Send the test message to the Slack channel
    # #     # send_message_to_slack(messages=[test_message])

    # #     # Generate the messages
    # #     messages = generate_message(
    # #         recent_project_activity_value,
    # #         data_availability_value,
    # #         data_analysis_value,
    # #         day_bools=day_bools,
    # #         time_of_day_value=time_of_day_value,
    # #     )

    # #     # Send the messages to the Slack channel
    # #     send_message_to_slack(messages=messages)

    # #     # Update the last message time
    # #     last_message_time = now

    # #     # # Write to log
    # #     # write_to_log(f'Test message sent at {now.strftime("%Y-%m-%d %H:%M:%S")}')

    # #     # Write to log
    # #     write_to_log(f'Update Message sent at {now.strftime("%Y-%m-%d %H:%M:%S")}')

    # # else:
    # #     print(f'Waiting for next message... {now.strftime("%Y-%m-%d %H:%M:%S")}')

    # # # Check if last_message_time is more than 24 hours ago
    # # if (now - last_message_time).total_seconds() > 86400:
    # #     # Check if the current day is in the day_index_bools
    # #     if day_index_bools[now.weekday()]:
    # #         # Check if the current time is after the time_of_day_value
    # #         if now.hour >= time_of_day_value:
    # #             # Check if the message has already been sent today
    # #             if not message_sent_today:
    # #                 # Generate the messages
    # #                 messages = generate_message(
    # #                     recent_project_activity_value,
    # #                     data_availability_value,
    # #                     data_analysis_value,
    # #                     day_bools=day_bools,
    # #                     time_of_day_value=time_of_day_value,
    # #                 )

    # #                 # Send the messages to the Slack channel
    # #                 send_message_to_slack(messages=messages)

    # #                 # Send the message
    # #                 last_message_time = now # Update the last message time
    # #                 message_sent_today = True # Set the message_sent_today to True

    # #                 print(f'Message sent at {now.strftime("%Y-%m-%d %H:%M:%S")}')

    # # Use time.sleep to wait for the next check
    # # Check if the current time is a multiple of the check_interval
    # if int(now.second) % check_interval == 0:
    #     time.sleep(check_interval)
    # else:
    #     # Calculate the time to wait until the next check
    #     time_to_wait = check_interval - (now.second % check_interval)
    #     print(f'Waiting for {time_to_wait} seconds...')
    #     time.sleep(time_to_wait)
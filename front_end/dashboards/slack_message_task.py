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

from dashboards.slack_config import generate_message, get_next_message_time, read_config_file, write_to_log, send_message_to_slack

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
saturday_value = config["saturday"]
sunday_value = config["sunday"]
time_of_day_value = config["time_of_day"]

day_bools = {
    "Monday": monday_value,
    "Tuesday": tuesday_value,
    "Wednesday": wednesday_value,
    "Thursday": thursday_value,
    "Friday": friday_value,
    "Saturday": saturday_value,
    "Sunday": sunday_value
}

day_index_bools = {
    0: monday_value,
    1: tuesday_value,
    2: wednesday_value,
    3: thursday_value,
    4: friday_value,
    5: saturday_value,
    6: sunday_value
}

# check_interval = 30  # seconds for testing

first_run = True

while True:
    # Get the current date and time in UTC
    now = datetime.datetime.now(datetime.timezone.utc)


    if first_run:
        print()
        print('----------------------')
        print()
        # Send a message to Slack that the bot is running
        # send_message_to_slack(messages=[f'Hyper A Slack Bot is starting up at {now.strftime("%Y-%m-%d %H:%M:%S")} timezone: {now.tzinfo}'])
        first_run = False

        next_message_time = get_next_message_time(day_bools, time_of_day_value)
        # For testing set the next message time to soon from now
        # next_message_time = now + datetime.timedelta(seconds=4)

        # print(f"Next message time: {next_message_time} timezone: {next_message_time.tzinfo}")
        # send_message_to_slack(messages=[f'Next message time: {next_message_time} timezone: {next_message_time.tzinfo}'])

    # Check if the current time is after the next message time
    print(f'now >= next_message_time: {now >= next_message_time}')
    if now >= next_message_time:
        print(f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')} timezone: {now.tzinfo}")
        # send_message_to_slack('Message Incoming...')
        # Send the message
        messages = generate_message(
            recent_project_activity_value,
            data_availability_value,
            data_analysis_value,
            day_bools=day_bools,
            time_of_day_value=time_of_day_value,
        )
        print(f"Messages: {messages}")
        send_message_to_slack(messages=messages)
        last_message_time = now  # Update the last message time

        # Update the next message time
        next_message_time = get_next_message_time(day_bools, time_of_day_value)

        send_message_to_slack(messages=[f'Next message time: {next_message_time} timezone: {next_message_time.tzinfo}'])


    else:
        # Wait for the next message time
        # time_to_wait = (next_message_time - now).total_seconds()
        time_to_wait = 60 * 60  # seconds for testing
        print(f"Waiting for {time_to_wait} seconds... Current time: {now.strftime("%Y-%m-%d %H:%M:%S")} timezone: {now.tzinfo}")
        print(f'Until next message: {next_message_time.strftime("%Y-%m-%d %H:%M:%S")} timezone: {next_message_time.tzinfo}')
        time.sleep(time_to_wait)
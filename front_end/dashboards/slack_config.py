import streamlit as st
import datetime

from dashboards.dashboard import *
from data_extraction.data_extractor import *

import data_extraction.service_extractor as service_extractor
import data_extraction.residential_extractor as residential_extractor
import data_extraction.facade_extractor as facade_extractor
import data_extraction.structure_extractor as structure_extractor
import data_extraction.industrial_extractor as industrial_extractor

import dashboards.facade_dashboard as facade_dashboard
import dashboards.residential_dashboard as residential_dashboard
import dashboards.service_dashboard as service_dashboard
import dashboards.structure_dashboard as structure_dashboard
import dashboards.industrial_dashboard as industrial_dashboard

import specklepy.api.models
import specklepy.api.operations
import specklepy.api.resource
import specklepy.api.resources
import specklepy.core
import specklepy.core.api

import requests

import pandas as pd

def format_time(dt):
    return dt.strftime("%d/%m %H:%M") + " GMT"

def get_next_message_time(day_bools, time_of_day) -> datetime.datetime:
    # Get the current time in GMT timezone
    now = datetime.datetime.now(datetime.timezone.utc)

    # Get the current day of the week (0=Monday, 6=Sunday)
    current_day = now.weekday()

    next_scheduled_day = None
    day_delta = None
    for day, is_scheduled in day_bools.items():
        if is_scheduled: # If the day is scheduled
            day_number = list(day_bools.keys()).index(day)

            if day_number > current_day:
                # If the scheduled day is in the future, look at the current week
                delta = day_number - current_day
            else:
                # If the scheduled day is in the past, look at the next week
                delta = day_number - current_day + 7
            
            if delta == 0: # If it's the same day
                # Check if the time has passed
                scheduled_time = datetime.datetime.strptime(time_of_day, "%H:%M:%S").time()
                current_time = now.time()
                if current_time < scheduled_time:
                    # If the scheduled time is in the future, it's the next scheduled time
                    next_scheduled_day = day_number
                    day_delta = delta
                    break
                else:
                    # If the scheduled time is in the past, skip it
                    continue

            if day_delta is None:
                # If this is the first scheduled time, set it as the next scheduled time
                next_scheduled_day = day_number
                day_delta = delta
                continue
            elif delta < day_delta:
                # If the delta is smaller than the previous one, update the next scheduled time
                next_scheduled_day = day_number
                day_delta = delta
                continue
            else:
                # If the delta is larger, skip it
                continue
    # If no scheduled time is found, return None
    if next_scheduled_day is None:
        return None
    
    # Get the next scheduled time on the next scheduled day
    next_scheduled_time = now.replace(hour=int(time_of_day.split(":")[0]), minute=int(time_of_day.split(":")[1]), second=0, microsecond=0)
    next_scheduled_time = next_scheduled_time + datetime.timedelta(days=(next_scheduled_day - current_day) % 7)
    return next_scheduled_time

def get_last_message_time(day_bools, time_of_day) -> datetime.datetime:
    # Get the current time in GMT timezone
    now = datetime.datetime.now(datetime.timezone.utc)

    # Get the current day of the week (0=Monday, 6=Sunday)
    current_day = now.weekday()
    # current_day = 3 # Set to Thursday for testing

    # print(f'current_day: {current_day}') # Debugging
    # Get the current time in GMT timezone
    current_time = now.time()

    # Get the scheduled send day that is most near to the current day, but in the past
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    latest_scheduled_day = None
    day_delta = None
    for day, is_scheduled in day_bools.items():
        if is_scheduled:
            day_number = list(day_bools.keys()).index(day)
            # print()
            # print(f'day: {day}') # Debugging
            # print(f'day_number: {day_number}') # Debugging
            
            if day_number > current_day:
                # If the scheduled day is in the future, look at the previous week
                # Calculate the delta between the current day and the scheduled day
                # print(f'The scheduled day is in the future, looking at the previous week...') # Debugging
                delta = current_day - day_number + 7
            else:
                # If the scheduled day is in the past, look at the current week
                # print(f'The scheduled day is in the past, looking at the current week...') # Debugging
                delta = current_day - day_number
            # print(f"Delta: {delta}") # Debugging

            if delta == 0: # If it's the same day
                # Check if the time has passed
                scheduled_time = datetime.datetime.strptime(time_of_day, "%H:%M:%S").time()
                # print(f"Scheduled time: {scheduled_time}") # Debugging
                # print(f"Current time: {current_time}") # Debugging
                if current_time < scheduled_time:
                    # If the scheduled time is in the future, skip it
                    # print("Scheduled time is in the future, skipping...") # Debugging
                    continue
                else:
                    # If the scheduled time is in the past, set it as the latest scheduled time                    
                    latest_scheduled_day = day_number
                    day_delta = delta
                    break
            else:
                if day_delta is None:
                    # If this is the first scheduled time, set it as the latest scheduled time
                    latest_scheduled_day = day_number
                    day_delta = delta
                    continue
                elif delta < day_delta:
                    # If the delta is smaller than the previous one, update the latest scheduled time
                    latest_scheduled_day = day_number
                    day_delta = delta
                    # print(f"Updated latest scheduled day: {latest_scheduled_day}") # Debugging
                else:
                    # If the delta is larger, skip it
                    # print(f"Skipping day {day} with delta {delta}")
                    continue
    # If no scheduled time is found, return None
    if latest_scheduled_day is None:
        # print("No scheduled time found")
        return None
    
    # print() # Debugging
    # print(f"current_day: {current_day}") # Debugging
    # print(f'current_day_name: {day_names[current_day]}') # Debugging
    # print(f"latest_scheduled_day: {latest_scheduled_day}") # Debugging
    # print(f'latest_scheduled_day_name: {day_names[latest_scheduled_day]}') # Debugging

    # Get the latest scheduled time on the latest scheduled day, in the past
    latest_scheduled_time = now.replace(hour=int(time_of_day.split(":")[0]), minute=int(time_of_day.split(":")[1]), second=0, microsecond=0)
    latest_scheduled_time = latest_scheduled_time - datetime.timedelta(days=(current_day - latest_scheduled_day) % 7)
    # print(f"latest_scheduled_time (before timezone): {latest_scheduled_time}") # Debugging
    # print(f"latest_scheduled_time: {latest_scheduled_time}") # Debugging    
    # print(f'type(latest_scheduled_time): {type(latest_scheduled_time)}') # Debugging

    return latest_scheduled_time

# Generate Recent Project Activity Message (Markdown)
def generate_recent_project_activity_message(day_bools, time_of_day_value) -> list[str]:
    print('day_bools: ', day_bools) # Debugging
    print('time_of_day_value: ', time_of_day_value) # Debugging

    messages = []

    models, client, project_id = setup_speckle_connection(models_limit=50)

    last_message_time = get_last_message_time(day_bools, time_of_day_value)
    
    # Get all versions in the project from the last message time to now
    recent_versions_dataframe = pd.DataFrame(columns=["Model Name", "Version Count", "Last Version Time", "Team", "Author"])
    if last_message_time is not None:
        for model in models:
            versions = client.version.get_versions(
                model_id=model.id,
                project_id=project_id,
                limit=100
            )
            # Filter versions based on the last message time
            for version in versions.items:
                version_creation_time = version.createdAt
                if version_creation_time > last_message_time:
                    # Add the version to the recent versions list
                    if model.name not in recent_versions_dataframe["Model Name"].values:
                        new_row = {
                            "Model Name": model.name,
                            "Version Count": 1,
                            "Last Version Time": format_time(version_creation_time),
                            "Team": model.name.split("/")[1],  # Assuming the team is part of the model name
                            "Author": version.authorUser.name
                        }
                        recent_versions_dataframe = pd.concat([recent_versions_dataframe, pd.DataFrame([new_row])], ignore_index=True)
                    else:
                        recent_versions_dataframe.loc[recent_versions_dataframe["Model Name"] == model.name, "Version Count"] += 1
                        recent_versions_dataframe.loc[recent_versions_dataframe["Model Name"] == model.name, "Last Version Time"] = format_time(version_creation_time)


    # print(f'markdown: {markdown}') # Debugging
    # Add the Markdown table to the messages list
    messages.append(f'**Recent Project Activity since {format_time(last_message_time)}**')
    st.markdown(messages[-1]) # Display the message in Streamlit
    
    # Calculate the number of versions added
    total_versions = recent_versions_dataframe["Version Count"].sum()
    if total_versions > 0:
        messages.append(f"Total versions added: {total_versions}")
        st.markdown(messages[-1]) # Display the message in Streamlit
    else:
        messages.append("No new versions")
        st.markdown(messages[-1]) # Display the message in Streamlit

    # determine the team responsible for each model
    team_counts = {}

    # Convert each row of the DataFrame to a human-readable string
    for index, row in recent_versions_dataframe.iterrows():
        model_name = row["Model Name"]
        version_count = row["Version Count"]
        last_version_time = row["Last Version Time"]
        team = row["Team"].capitalize()
        author = row["Author"]
        
        message = f'{author} of the {team} team uploaded {version_count} new version(s) of {model_name} at {last_version_time}'
        messages.append(message)
        st.markdown(messages[-1]) # Display the message in Streamlit

    # messages.append(table_message)
    return messages

# Generate Data Availability Message (Markdown)
def generate_data_availability_message() -> list[str]:
    messages = []
    
    # Generate the header
    messages.append(f'**Data Availability Report**')
    st.markdown(messages[-1]) # Display the message in Streamlit
    
    all_extractors = {
        "Service": service_extractor,
        "Residential": residential_extractor,
        "Facade": facade_extractor,
        "Structure": structure_extractor,
        "Industrial": industrial_extractor
    }

    # Setup Speckle connection
    models, client, project_id = setup_speckle_connection()

    # for extractor in all_extractors:
    for team_name, extractor in all_extractors.items():
        # Extract data using the extractor
        # Placeholder for actual data extraction
        fully_verified, extracted_data = extractor.extract(
            models=models,
            client=client,
            project_id=project_id,
            header=False,
            table=False,
            gauge=False,
            attribute_display=False
        )
        print(f"fully_verified: {fully_verified}") # Debugging
        print(f"extracted_data: {extracted_data}") # Debugging
        table, type_matched_bools = process_extracted_data(extractor.data, extracted_data, verbose=False)

        # print(f"table: {table}") # Debugging
        # print(f"type_matched_bools: {type_matched_bools}") # Debugging

        percentage_verified = sum(type_matched_bools) / len(type_matched_bools) * 100
        print(f"percentage_verified: {percentage_verified}") # Debugging

        # Generate the message
        messages.append(f'{team_name.capitalize()} team data is {percentage_verified:.2f}% in the correct format.')
        st.markdown(messages[-1]) # Display the message in Streamlit
        if percentage_verified < 100:
            for bool, data_name, data_type in zip(type_matched_bools, extractor.data_names, extractor.data_types):
                if not bool:
                    # print(f"data_item: {data_item}") # Debugging
                    messages.append(f' - {data_name} is in the wrong format, we were expecting {data_type} but got {type(extracted_data[data_name]).__name__}')
                    st.markdown(messages[-1]) # Display the message in Streamlit

    return messages

# Generate Data Analysis Message (Markdown)
def generate_data_analysis_message() -> list[str]:
    # Placeholder function to generate a message about data analysis
    messages = []

    dashboards = {
        "Facade": facade_dashboard,
        "Residential": residential_dashboard,
        "Service": service_dashboard,
        "Structure": structure_dashboard,
        "Industrial": industrial_dashboard
    }

    extractors = {
        "Facade": facade_extractor,
        "Residential": residential_extractor,
        "Service": service_extractor,
        "Structure": structure_extractor,
        "Industrial": industrial_extractor
    }

    # Setup Speckle connection
    models, client, project_id = setup_speckle_connection()

    for team_name, dashboard, extractor in zip(dashboards.keys(), dashboards.values(), extractors.values()):
        # Extract data using the extractor
        fully_verified, extracted_data = extractor.extract(
            models=models,
            client=client,
            project_id=project_id,
            header=False,
            table=False,
            gauge=False,
            attribute_display=False
        )
        # print(f"fully_verified: {fully_verified}") # Debugging
        # print(f"extracted_data: {extracted_data}") # Debugging
                
        if not(fully_verified):
            messages.append(f'{team_name.capitalize()} team data is not fully verified.')
            st.markdown(messages[-1])
            continue
        
        metrics = dashboard.generate_metrics(fully_verified, extracted_data)

        # Generate the message header
        messages.append('')
        st.markdown(messages[-1])
        messages.append(f'**{team_name.capitalize()} Team Metric Analysis:**')
        st.markdown(messages[-1])
        
        # Create a message for each metric
        for metric in metrics:
            # print(f"metric: {metric}") # Debugging
            metric_value = f"{metric.value:.2f}"
            metric_ideal_value = f"{metric.ideal_value:.2f}"
            messages.append(f'{metric.title} value is currently {metric_value}, goal value is {metric_ideal_value}')
            st.markdown(messages[-1])

    return messages

def generate_message(recent_project_activity_bool, data_availability_bool, data_analysis_bool, day_bools, time_of_day_value):
    messages = []

    # Generate message header
    now = datetime.datetime.now(datetime.timezone.utc)
    messages.append(f'**HyperA Project Update for {format_time(now)}:**')
    st.markdown(messages[-1]) # Display the message in Streamlit
    messages.append('')
    st.markdown(messages[-1]) # Display the message in Streamlit

    # Generate the message based on the selected options
    if recent_project_activity_bool:
        with st.spinner("Generating recent project activity message..."):
            messages = messages + generate_recent_project_activity_message(day_bools, time_of_day_value)
    if data_availability_bool:
        with st.spinner("Generating data availability message..."):
            messages = messages + generate_data_availability_message()
    if data_analysis_bool:
        with st.spinner("Generating data analysis message..."):
            messages = messages + generate_data_analysis_message()
    # Display the generated message
    return messages

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
        saturday_value = process_bool(lines[8])
        sunday_value = process_bool(lines[9])
        time_of_day_value = lines[10].split(": ")[1]

        return {
            "recent_project_activity": recent_project_activity_value,
            "data_availability": data_availability_value,
            "data_analysis": data_analysis_value,
            "monday": monday_value,
            "tuesday": tuesday_value,
            "wednesday": wednesday_value,
            "thursday": thursday_value,
            "friday": friday_value,
            "saturday": saturday_value,
            "sunday": sunday_value,
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
            "wednesday": True,
            "thursday": True,
            "friday": True,
            "saturday": True,
            "sunday": True,
            "time_of_day": "09:00"
        }
    
def send_message_to_slack(messages):
    if not isinstance(messages, list):
        messages = [messages]

    message = '\n'.join(messages)
    # Replace '**' with '*'
    message = message.replace('**', '*')

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

    # Wait for a few seconds to avoid rate limiting
    time.sleep(1)

def write_to_log(message: str) -> None:
    # This function writes a message to a log file 
    try:
        with open('front_end\slack_message_log.txt', 'a') as log_file:
            log_file.write(f'{message}\n')
    except Exception as e:
        print(f'Error writing to log file: {e}')

def run():
    print() # Debugging

    st.title("Slack Automatic Message Generator")

    # Read the configuration file
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
    
    with st.expander("## Configuration"):
        message_options_container, day_of_week_container, time_of_day_container = st.columns(3)
        with message_options_container:
            st.header("Message Options")
            # Add radio buttons for selecting the Slack configuration
            recent_project_activity_bool = st.toggle("Include Recent Project Activity", value=recent_project_activity_value)
            data_availability_bool = st.toggle("Include Data Availability", value=data_availability_value)
            data_analysis_bool = st.toggle("Include Data Analysis", value=data_analysis_value)

        # day_of_week_container = st.container()
        with day_of_week_container:
            st.header("Day of Week")

            # Add radio buttons for selecting the day of the week
            monday_bool = st.toggle("Monday", value=monday_value, key="monday toggle")
            tuesday_bool = st.toggle("Tuesday", value=tuesday_value, key="tuesday toggle")
            wednesday_bool = st.toggle("Wednesday", value=wednesday_value, key="wednesday toggle")
            thursday_bool = st.toggle("Thursday", value=thursday_value, key="thursday toggle")
            friday_bool = st.toggle("Friday", value=friday_value, key="friday toggle")
            saturday_bool = st.toggle("Saturday", value=False, key="saturday toggle")
            sunday_bool = st.toggle("Sunday", value=False, key="sunday toggle")

            day_bools = {
                "Monday": monday_bool,
                "Tuesday": tuesday_bool,
                "Wednesday": wednesday_bool,
                "Thursday": thursday_bool,
                "Friday": friday_bool,
                "Saturday": saturday_bool,
                "Sunday": sunday_bool
            }

        # time_of_day_container = st.container()
        with time_of_day_container:
            st.header("Time of Day")
            # Add a time picker for selecting the time of day
            time_of_day = st.time_input("Select Time of Day (GMT)", value=time_of_day_value, key="time of day picker")
        
        if st.button("Save Configuration", use_container_width=True):
            # Save the configuration to a file or database
            # Write to a file
            config_file_path = "front_end/slack_config.txt"
            with open(config_file_path, "w") as f:
                f.write(f"Recent Project Activity: {int(recent_project_activity_bool)}\n")
                f.write(f"Data Availability: {int(data_availability_bool)}\n")
                f.write(f"Data Analysis: {int(data_analysis_bool)}\n")
                f.write(f"Monday: {int(monday_bool)}\n")
                f.write(f"Tuesday: {int(tuesday_bool)}\n")
                f.write(f"Wednesday: {int(wednesday_bool)}\n")
                f.write(f"Thursday: {int(thursday_bool)}\n")
                f.write(f"Friday: {int(friday_bool)}\n")
                f.write(f"Saturday: {int(saturday_bool)}\n")
                f.write(f"Sunday: {int(sunday_bool)}\n")
                f.write(f"Time of Day: {time_of_day}\n")
                
            st.success("Configuration saved successfully! Reload Page to see changes.")

    message_generated = False # A flag to check if the message has been generated at least once

    # Add a button that triggers the message generation
    generate_message_trigger = False # A flag to check if the button has been clicked
    if st.button("Generate Message Preview", use_container_width=True):
        generate_message_trigger = True

    # Add a button that sends the message to Slack
    send_message_trigger = False
    if st.button("Send Message to Slack", use_container_width=True):
        send_message_trigger = True

    # If the button is clicked, generate the message
    if generate_message_trigger:
        st.subheader('Preview of the Next Message:')

        # Generate the message
        messages = generate_message(recent_project_activity_bool, data_availability_bool, data_analysis_bool, day_bools, time_of_day_value)            

        # # Display the generated message
        # for message in messages:
        #     # print(message) # Debugging
        #     # If message is between a single asterisk at the beginning and end, make it bold by adding another asterisk
        #     if message.startswith("*") and message.endswith("*"):
        #         message = message.replace("*", "**")
            # st.markdown(message, unsafe_allow_html=True)

        message_generated = True # Set the flag to True if the message has been generated

    if send_message_trigger:
        # Check if the message has been generated
        st.subheader('Sending Message to Slack:')
        if message_generated:
            message = '\n'.join(messages)
        else:
            with st.spinner("Generating message..."):
                messages = generate_message(recent_project_activity_value, data_availability_value, data_analysis_value, day_bools, time_of_day_value)
                message = '\n'.join(messages)

        # Send the message to Slack
        slack_webhook_url = "https://hooks.slack.com/services/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"
        payload = {
            "text": message,
            "mrkdwn": True
        }
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(slack_webhook_url, json=payload, headers=headers)
        # Check the response status
        if response.status_code != 200:
            st.error(f"Failed to send message to Slack: {response.status_code} - {response.text}")
            return
        else:
            # If the message was sent successfully, display a success message
            st.success("Message sent to Slack successfully!")
            
            print(f"Message sent to Slack: {message}") # Debugging
            print(f"Response from Slack: {response.text}") # Debugging
            

        st.success("Message sent to Slack successfully!")
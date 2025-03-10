import streamlit as st
import datetime

from dashboards.dashboard import *

import data_extraction.service_extractor as service_extractor
import data_extraction.residential_extractor as residential_extractor
import data_extraction.facade_extractor as facade_extractor
import data_extraction.structure_extractor as structure_extractor
import data_extraction.industrial_extractor as industrial_extractor

import specklepy.api
import specklepy.api.models
import specklepy.api.operations
import specklepy.api.resource
import specklepy.api.resources
import specklepy.core
import specklepy.core.api

import pandas as pd

def format_time(dt):
    return dt.strftime("%d/%m %H:%M")

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
    messages = []

    models, client, project_id = setup_speckle_connection()

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

    # Convert the DataFrame to Markdown
    markdown = recent_versions_dataframe.to_markdown(index=False)

    # print(f'markdown: {markdown}') # Debugging
    # Add the Markdown table to the messages list
    messages.append(f"#### Recent Project Activity since {format_time(last_message_time)}")
    
    # Calculate the number of versions added
    total_versions = recent_versions_dataframe["Version Count"].sum()
    if total_versions > 0:
        messages.append(f"Total versions added: {total_versions}")
    else:
        messages.append("No new versions")

    # determine the team responsible for each model
    team_counts = {}
    
    messages.append(markdown)
    return messages

# Generate Data Availability Message (Markdown)
def generate_data_availability_message() -> list[str]:
    messages = []

    all_extractors = [
        service_extractor,
        residential_extractor,
        facade_extractor,
        structure_extractor,
        industrial_extractor
    ]

    # Setup Speckle connection
    models, client, project_id = setup_speckle_connection()

    for extractor in all_extractors:
        # Extract data using the extractor
        # Placeholder for actual data extraction
        data = extractor.extract(
            models=models,
            client=client,
            project_id=project_id,
            header=False,
            table=False,
            gauge=False,
            attribute_display=False
        )

        # Process the data and generate a message
        # Placeholder for actual data processing
        message = f"Data availability for {extractor.__name__}: {data}"
        messages.append(message)

    return messages

# Generate Data Analysis Message (Markdown)
def generate_data_analysis_message() -> list[str]:
    # Placeholder function to generate a message about data analysis
    messages = []
    messages.append("Data analysis: Placeholder message.")
    return messages

def run():
    print() # Debugging

    st.title("Slack Automatic Message Generator")

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

        # print(f"Loaded configuration: {recent_project_activity_value}, {data_availability_value}, {data_analysis_value}, {monday_value}, {tuesday_value}, {wednesday_value}, {thursday_value}, {friday_value}, {time_of_day_value}")

    except FileNotFoundError:
        # If the file does not exist, use default values
        recent_project_activity_value = True
        data_availability_value = True
        data_analysis_value = True
        monday_value = True
        tuesday_value = True
        wednesday_value = False
        thursday_value = False
        friday_value = False
        time_of_day_value = "09:00"

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

            day_bools = {
                "Monday": monday_bool,
                "Tuesday": tuesday_bool,
                "Wednesday": wednesday_bool,
                "Thursday": thursday_bool,
                "Friday": friday_bool
            }

        # time_of_day_container = st.container()
        with time_of_day_container:
            st.header("Time of Day")
            # Add a time picker for selecting the time of day
            time_of_day = st.time_input("Select Time of Day (GMT)", value=time_of_day_value, key="time of day picker")
        
        if st.button("Save Configuration", use_container_width=True):
            # Save the configuration to a file or database
            # Write to a file
            with open(config_file_path, "w") as f:
                f.write(f"Recent Project Activity: {int(recent_project_activity_bool)}\n")
                f.write(f"Data Availability: {int(data_availability_bool)}\n")
                f.write(f"Data Analysis: {int(data_analysis_bool)}\n")
                f.write(f"Monday: {int(monday_bool)}\n")
                f.write(f"Tuesday: {int(tuesday_bool)}\n")
                f.write(f"Wednesday: {int(wednesday_bool)}\n")
                f.write(f"Thursday: {int(thursday_bool)}\n")
                f.write(f"Friday: {int(friday_bool)}\n")
                f.write(f"Time of Day: {time_of_day}\n")
                
            st.success("Configuration saved successfully! Reload Page to see changes.")

    # Add a button that triggers the message generation
    generate_message_trigger = False
    if st.button("Generate Message", use_container_width=True):
        generate_message_trigger = True

    # If the button is clicked, generate the message
    if generate_message_trigger:
        st.subheader('Next Message')

        # Generate the message based on the selected options
        messages = []
        if recent_project_activity_bool:
            with st.spinner('Getting recent project activity...'):
                messages = messages + generate_recent_project_activity_message(day_bools, time_of_day_value)
        if data_availability_bool:
            with st.spinner('Getting data availability...'):
                messages = messages + generate_data_availability_message()
        if data_analysis_bool:
            with st.spinner('Getting data analysis...'):
                messages = messages + generate_data_analysis_message()
            
        # Display the generated message
        for message in messages:
            # print(message) # Debugging
            st.markdown(message, unsafe_allow_html=True)
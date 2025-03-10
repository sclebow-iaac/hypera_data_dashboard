import streamlit as st

from dashboards.dashboard import *

# Generate Recent Project Activity Message (Markdown)
def generate_recent_project_activity_message():
    # Placeholder function to generate a message about recent project activity
    return "Recent project activity: Placeholder message."

# Generate Data Availability Message (Markdown)
def generate_data_availability_message():
    # Placeholder function to generate a message about data availability
    return "Data availability: Placeholder message."

# Generate Data Analysis Message (Markdown)
def generate_data_analysis_message():
    # Placeholder function to generate a message about data analysis
    return "Data analysis: Placeholder message."

def run():
    st.title("Slack Configuration")

    # Load the configuration from a file 
    try:
        with open("slack_config.txt", "r") as f:
            config = f.read()
        # Parse the configuration
        lines = config.split("\n")

        # Debugging: 
        test_value = lines[0].split(": ")[1]
        print(f"Test value: {test_value}")
        print(f'type(test_value): {type(test_value)}')
        print(f'bool(test_value): {bool(test_value)}')

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

    # time_of_day_container = st.container()
    with time_of_day_container:
        st.header("Time of Day")
        # Add a time picker for selecting the time of day
        time_of_day = st.time_input("Select Time of Day (GMT)", value=time_of_day_value, key="time of day picker")
    
    if st.button("Save Configuration", use_container_width=True):
        # Save the configuration to a file or database
        # Write to a file
        with open("slack_config.txt", "w") as f:
            f.write(f"Recent Project Activity: {int(recent_project_activity_bool)}\n")
            f.write(f"Data Availability: {int(data_availability_bool)}\n")
            f.write(f"Data Analysis: {int(data_analysis_bool)}\n")
            f.write(f"Monday: {int(monday_bool)}\n")
            f.write(f"Tuesday: {int(tuesday_bool)}\n")
            f.write(f"Wednesday: {int(wednesday_bool)}\n")
            f.write(f"Thursday: {int(thursday_bool)}\n")
            f.write(f"Friday: {int(friday_bool)}\n")
            f.write(f"Time of Day: {time_of_day}\n")
            
        st.success("Configuration saved successfully!")

    st.markdown('---')

    st.subheader('Next Message')

    # Generate the message based on the selected options
    message = ""
    if recent_project_activity_bool:
        message += generate_recent_project_activity_message() + "<br>"
    if data_availability_bool:
        message += generate_data_availability_message() + "<br>"
    if data_analysis_bool:
        message += generate_data_analysis_message() + "<br>"

    # Display the generated message
    st.markdown(message, unsafe_allow_html=True)

import streamlit as st

# def generate

def run():
    st.title("Slack Configuration")

    # Load the configuration from a file 
    try:
        with open("slack_config.txt", "r") as f:
            config = f.read()
        # Parse the configuration
        lines = config.split("\n")
        recent_project_activity_value = bool(lines[0].split(": ")[1].lower())
        data_availability_value = bool(lines[1].split(": ")[1].lower() == "True")
        data_analysis_value = bool(lines[2].split(": ")[1].lower() == "True")
        monday_value = bool(lines[3].split(": ")[1].lower() == "True")
        tuesday_value = bool(lines[4].split(": ")[1].lower() == "True")
        wednesday_value = bool(lines[5].split(": ")[1].lower() == "True")
        thursday_value = bool(lines[6].split(": ")[1].lower() == "True")
        friday_value = bool(lines[7].split(": ")[1].lower() == "True")
        time_of_day_value = lines[8].split(": ")[1]

        print(f"Loaded configuration: {recent_project_activity_value}, {data_availability_value}, {data_analysis_value}, {monday_value}, {tuesday_value}, {wednesday_value}, {thursday_value}, {friday_value}, {time_of_day_value}")

    except FileNotFoundError:
        # If the file does not exist, use default values
        recent_project_activity_value = True
        data_availability_value = True
        data_analysis_value = True
        monday_value = True
        tuesday_value = False
        wednesday_value = False
        thursday_value = False
        friday_value = False
        time_of_day_value = "09:00"    

    message_options_container = st.container()
    with message_options_container:
        st.header("Message Options")
        # Add radio buttons for selecting the Slack configuration
        recent_project_activity_bool = st.toggle("Include Recent Project Activity", value=recent_project_activity_value)
        data_availability_bool = st.toggle("Include Data Availability", value=data_availability_value)
        data_analysis_bool = st.toggle("Include Data Analysis", value=data_analysis_value)

    day_of_week_container = st.container()
    with day_of_week_container:
        st.header("Day of Week")

        # Add radio buttons for selecting the day of the week
        monday_bool = st.toggle("Monday", value=monday_value, key="monday toggle")
        tuesday_bool = st.toggle("Tuesday", value=tuesday_value, key="tuesday toggle")
        wednesday_bool = st.toggle("Wednesday", value=wednesday_value, key="wednesday toggle")
        thursday_bool = st.toggle("Thursday", value=thursday_value, key="thursday toggle")
        friday_bool = st.toggle("Friday", value=friday_value, key="friday toggle")

    time_of_day_container = st.container()
    with time_of_day_container:
        st.header("Time of Day")
        # Add a time picker for selecting the time of day
        time_of_day = st.time_input("Select Time of Day (GMT)", value="09:00", key="time of day picker")
    
    if st.button("Save Configuration"):
        # Save the configuration to a file or database
        # Write to a file
        print(f"Saving configuration: {recent_project_activity_bool}, {data_availability_bool}, {data_analysis_bool}, {monday_bool}, {tuesday_bool}, {wednesday_bool}, {thursday_bool}, {friday_bool}, {time_of_day}")
        with open("slack_config.txt", "w") as f:
            f.write(f"Recent Project Activity: {recent_project_activity_bool}\n")
            f.write(f"Data Availability: {data_availability_bool}\n")
            f.write(f"Data Analysis: {data_analysis_bool}\n")
            f.write(f"Monday: {monday_bool}\n")
            f.write(f"Tuesday: {tuesday_bool}\n")
            f.write(f"Wednesday: {wednesday_bool}\n")
            f.write(f"Thursday: {thursday_bool}\n")
            f.write(f"Friday: {friday_bool}\n")
            f.write(f"Time of Day: {time_of_day}\n")
        st.success("Configuration saved successfully!")

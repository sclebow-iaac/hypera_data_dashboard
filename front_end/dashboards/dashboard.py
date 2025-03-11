# This script holds general functions for all Team dashboards

import streamlit as st
import pandas as pd
import plotly.express as px
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token
import os
import time


class Metric:
    def __init__(self, title: str, formula_markdown: str, description: str, interactive_calculator_func, calculation_func, image_path: str, inputs: list, min_value: float, max_value: float, ideal_value: float):
        self.title = title
        self.formula_markdown = formula_markdown
        self.description = description
        self.interactive_calculator_func = interactive_calculator_func
        self.calculation_func = calculation_func
        self.image_path = image_path
        self.inputs = inputs
        self.min_value = min_value
        self.max_value = max_value
        self.ideal_value = ideal_value
        self.value = self.calculate()

    def calculate(self):
        input_values = [x["value"] for x in self.inputs]
        return self.calculation_func(*input_values)

    def display(self, container, add_text=True):
        display_metric(container, self, add_text)

    def display_interactive_calculator(self, container):
        # Unpack the inputs correctly and pass them as arguments
        input_values = [input['value'] for input in self.inputs]
        self.interactive_calculator_func(container, *input_values)

def display_interactive_calculators(container, metrics: list[Metric], grid: bool = True):
    container.markdown("""
    <h2 style='text-align: center;'>Interactive Sustainability Calculators</h3>
    """, unsafe_allow_html=True)
    if len(metrics) < 2:
        grid = False
    if grid:
        metric_index = 0
        cell_count = len(metrics)
        cols = 2
        rows = (cell_count + cols - 1) // cols

        interactive_containers = []
        for i in range(rows):
            col_1, col_2 = container.columns(cols, border=True)
            interactive_containers.append(col_1.container())
            interactive_containers.append(col_2.container())

    else:
        interactive_containers = [container.container()
                                  for _ in range(len(metrics))]
    for interactive_container, metric in zip(interactive_containers, metrics):
        metric.display_interactive_calculator(interactive_container)

def setup_speckle_connection(models_limit=100):
    speckle_server = "macad.speckle.xyz"
    speckle_token = "61c9dd1efb887a27eb3d52d0144f1e7a4a23f962d7"
    client = SpeckleClient(host=speckle_server)
    account = get_account_from_token(speckle_token, speckle_server)
    client.authenticate_with_account(account)

    project_id = '31f8cca4e0'
    selected_project = client.project.get(project_id=project_id)
    project = client.project.get_with_models(
        project_id=selected_project.id, models_limit=models_limit)
    models = project.models.items

    return models, client, project_id

def display_speckle_viewer(container, project_id, model_id, is_transparent=False, hide_controls=False, hide_selection_info=False, no_scroll=False):
        speckle_model_url = f'https://macad.speckle.xyz/projects/{project_id}/models/{model_id}'
        # https://macad.speckle.xyz/projects/31f8cca4e0/models/e76ccf2e0f,3f178d9658,a4e3d78009,c710b396d3,5512057f5b,d68a58c12d,2b48d3f757,767672f412
        # speckle_model_url += '#embed={%22isEnabled%22:true,%22isTransparent%22:true,%22hideControls%22:true,%22hideSelectionInfo%22:true,%22noScroll%22:true}'

        embed_str = '%22isEnabled%22:true'
        if is_transparent:
            embed_str += ',%22isTransparent%22:true'
        if hide_controls:
            embed_str += ',%22hideControls%22:true'
        if hide_selection_info:
            embed_str += ',%22hideSelectionInfo%22:true'
        if no_scroll:
            embed_str += ',%22noScroll%22:true'

        speckle_model_url += f'#embed={{{embed_str}}}'

        iframe_code = f"""
        <iframe src="{speckle_model_url}"
                style="width: 100%; height: 600px; border: none;">
        </iframe>
        """
        container.markdown(iframe_code, unsafe_allow_html=True)

        return speckle_model_url

def display_page_title(team_name: str) -> None:
    st.markdown(f'''
        <div style="text-align: center;">
            <h1>{team_name} Dashboard</h1>
        </div>
    ''', unsafe_allow_html=True)


def display_formula_section_header(team_name: str) -> None:
    st.markdown(f'''
        <div style="text-align: center;">
            <h2>{team_name} Metrics</h2>
        </div>
    ''', unsafe_allow_html=True)


def display_metric(container, title: str, formula_markdown: str, description: str, value: float, add_text=True):
    def metric_text_display(title, formula_markdown, description, value):
        st.markdown(f"### {title}")
        st.latex(formula_markdown)
        st.markdown(description)
        if value is not None:
            st.markdown(
                f"<h4 style='text-align: center;'>Current Value: {value:.2f}</h4>", unsafe_allow_html=True)


def display_st_metric_values(container, metrics):
    column_containers = container.columns(4)
    for column_container, metric in zip(column_containers, metrics):
        with column_container:
            column_container.metric(metric.title, f'{metric.value:.2f}')


def display_metric_visualizations(container, metrics, add_text=True):
    vis_cotainers = [container.container() for _ in range(len(metrics))]
    for vis_container, metric in zip(vis_cotainers, metrics):
        metric.display(vis_container, add_text=add_text)

    st.markdown("---")


def display_text_section(container, text: str) -> None:
    """Display a text section in the given container."""
    container.markdown(f"""
        <div style="
            background-color: white; 
            padding: 20px;
            border-radius: 5px;
            width: 100%;
            color: black;
            margin: 10px 0;
            font-size: 20px;  /* Change this value to adjust font size */
        ">
            {text}
        </div>
        <hr style="border: 1px solid white;"/>  <!-- Add a horizontal line -->
    """, unsafe_allow_html=True)


def display_custom_bullet_list(container, items: list[str], bullet_image_path: str = None) -> None:
    """Display a list with custom bullet points using an image."""
    # Read and encode the image
    import base64
    from pathlib import Path
    
    # Default to enso circle if no path provided
    if bullet_image_path is None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        bullet_image_path = os.path.join(current_dir, "enso_circle.png")
    
    try:
        image_path = Path(bullet_image_path)
        with open(image_path, "rb") as img_file:
            b64_string = base64.b64encode(img_file.read()).decode()
    except Exception as e:
        st.error(f"Failed to load image: {e}")
        return
        
    bullet_style = f"""
    <style>
    .enso-list {{
        list-style: none;
        padding-left: 0;
    }}
    .enso-list li {{
        padding-left: 40px;
        padding-bottom: 15px;
        margin: 10px 0;
        background-image: url(data:image/png;base64,{b64_string});
        background-repeat: no-repeat;
        background-position: left top;  
        background-size: 25px;        
        line-height: 25px;           
        padding-top: 1px;             
        display: flex;               
        align-items: center;        
        min-height: 30px;
        font-size: 22px;
    }}
    </style>
    """
    
    bullet_list = "<ul class='enso-list'>"
    for item in items:
        bullet_list += f"<li>{item}</li>"
    bullet_list += "</ul>"
    
    container.markdown(bullet_style + bullet_list, unsafe_allow_html=True)

def display_metric(container, metric: Metric, add_text=True) -> None:
    """Display a metric in the specified container."""
    print("DISPLAY METRIC: ", metric.title)
    
    # Create two columns with specified widths
    col1, col2 = container.columns([1, 2])  # First column is 1 part, second column is 2 parts

    # In the first column, display the image with some right margin
    with col1:
        image_width = 400  # Set your desired width
        st.markdown(f'<div style="text-align: right;">', unsafe_allow_html=True)  # Align image to the right
        st.image(metric.image_path, width=image_width, use_container_width=False)
        st.markdown('</div>', unsafe_allow_html=True)  # Close the div

    # In the second column, display the text with additional margin
    with col2:
        st.markdown(f'<div style="margin-top: 20px;">', unsafe_allow_html=True)  # Add top margin
        st.markdown(f"### {metric.title}")
        st.latex(metric.formula_markdown)
        st.markdown(metric.description)
        # st.metric(metric.title, f'{metric.value:.2f}')  # Display the metric value
        st.markdown('</div>', unsafe_allow_html=True)  # Close the div


    # Call the function to display circles and tape
    with container:
        display_metric_circles_and_tape(container, metric)
        for _ in range(5):
            st.markdown("")

def create_top_menu(teams: list[str]) -> str:
    """Create a horizontal menu at the top of the page."""
    st.markdown("""
        <style>
        .top-menu {
            display: flex;
            justify-content: center;
            padding: 10px;
            background-color: #ffffff;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        div.stButton > button {
            background-color: transparent;
            border: none;
            padding: 10px 20px;
            font-size: 40px;  /* Change this value to adjust font size */
        }
        div.stButton > button:hover {
            background-color: #ffffff;
            border-radius: 5px;
        }
        /* Style for selected button */
        div.stButton > button[data-selected="true"] {
            border-bottom: 2px solid #000000;
            border-radius: 0;
        }
        div.stButton > button[data-selected="true"]:hover {
            background-color: transparent;
        }
        </style>
    """, unsafe_allow_html=True)

    # Initialize session state if not exists
    if 'current_selection' not in st.session_state:
        st.session_state.current_selection = teams[0]

    # Create columns for each team
    cols = st.columns(len(teams))
    
    # Create buttons in each column and handle selection
    selected = None
    for col, item in zip(cols, teams):
        with col:
            is_selected = item == st.session_state.current_selection
            button_html = f"""
                <button 
                    data-selected="{str(is_selected).lower()}"
                    style="width: 100%; {{
                        'border-bottom: 2px solid #000000; border-radius: 0;' if is_selected else ''
                    }}"
                >
                    {item}
                </button>
            """
            if st.button(
                item, 
                key=f"menu_{item}",  # Ensure unique key by prefixing with 'menu_'
                use_container_width=True
            ):
                selected = item
    
    # Update selection if a new item was clicked
    if selected is not None:
        st.session_state.current_selection = selected
    
    # Return the current selection
    return st.session_state.current_selection


def display_metric_circles_and_tape(container, metric: Metric) -> None:
    """Display input values for metrics in circles and a tape diagram showing progress using the Metric class."""
    print("DISPLAY METRIC CIRCLES AND TAPE: ", metric.title)


    # Calculate the range and scale the value
    range_value = metric.max_value - metric.min_value
    scaled_value = (metric.value - metric.min_value) / range_value if range_value > 0 else 0  # Avoid division by zero

    # Create a gradient background for the tape diagram
    container.markdown(f"""
        <div style='width: 100%; height: 30px; background: linear-gradient(to right, #f5f5dc, #8B4513); position: relative;'>
            <div style='width: {scaled_value * 100}%; height: 100%; background-color: rgba(255, 255, 255, 0.5);'></div>
            <div style='position: absolute; width: 100%; height: 100%;'>
                <div style='position: absolute; top: 0; left: 0; width: 100%;'>
                    {''.join(f"<div style='position: absolute; left: {i * 10}%; height: 30px; border-left: 1px solid black; z-index: 1;'></div>" for i in range(1, 11))}
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Calculate the position for the value display
    position_percentage = scaled_value * 100  # Convert to percentage for positioning
    container.markdown(f"""
        <div style='position: relative; width: 100%;'>
            <div style='position: absolute; left: {position_percentage}%; transform: translateX(-50%); font-size: 24px; color: black; top: 30px;'>
                <strong>{metric.value:.2f}</strong>  <!-- Display the primary metric value -->
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Display minimum and maximum values at the ends of the tape
    container.markdown(f"""
        <div style='display: flex; justify-content: space-between; font-size: 14px; color: black;'>
            <span>{metric.min_value:.2f}</span>
            <span>{metric.max_value:.2f}</span>
        </div>
    """, unsafe_allow_html=True)

    for _ in range(5):
            st.markdown("")

    # Display the ideal optimized value
    container.markdown(f"""
        <div style='text-align: left; font-size: 14px; color: black;'>
            Ideal Optimized Value: <strong>{metric.ideal_value:.2f}</strong>
        </div>
    """, unsafe_allow_html=True)

    for _ in range(2):
            st.markdown("")

    container.markdown(f"""
        <div style='text-align: left; font-size: 14px; color: black;'>
            Metric Distribution:
        </div>
    """, unsafe_allow_html=True)

    # Add space between the tape diagram and the metric values
    container.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    # Ensure all values in args are numeric
    input_values = []
    for input in metric.inputs:
        if "display_value" in input and input["display_value"]:
            input_values.append(float(input["display_value"]))
        else:
            input_values.append(float(input["value"]))

    # Find the maximum value to scale the circles
    max_value = max(input_values) if input_values else 1  # Avoid division by zero
    scaling_factor = 200  # Maximum diameter for the largest circle
    min_circle_diameter = 30  # Minimum diameter for visibility

    print("Input Values for Metric: ", metric.title, input_values)
    # Create columns for layout with 2 extra columns
    total_columns = len(input_values) + 2
    print("Total Columns for metric: ", metric.title, total_columns)  # Debugging: Print total columns      
    cols = st.columns(total_columns)  # Create total_columns based on the number of values + 2

    # Place empty circles in the first and last columns
    for idx in range(total_columns):
        if idx == 0 or idx == total_columns - 1:
            with cols[idx]:
                st.markdown("")  # Empty column for spacing
        else:
            # Create a circle representation for the metric values
            inputs_index = idx - 1  # Adjust index for metric values
            value = input_values[inputs_index]  # Get the value from the Metric instance
            circle_diameter = max((value / max_value) * scaling_factor, min_circle_diameter)  # Scale for visibility with a minimum size
            name = metric.inputs[inputs_index]["name"]  # Change made here
            unit = metric.inputs[inputs_index]["unit"]  # Change made here
            with cols[idx]:
                st.markdown(f"""
                    <div style="position: relative; display: inline-block; text-align: center;">
                        <div style="
                            width: {circle_diameter}px; 
                            height: {circle_diameter}px; 
                            border-radius: 50%; 
                            background-color: #f5f5dc;  /* Light beige color */
                            display: flex; 
                            flex-direction: column; 
                            justify-content: flex-end; 
                            align-items: center;
                            padding: 5px;  /* Add some padding */
                        ">
                            <div style="font-size: 14px; color: black;">{value:.2f} {unit}</div>
                            <div style="font-size: 14px; color: black;">{name}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    for _ in range(5):
        st.markdown(" ")

    # Add JavaScript to handle input changes (if needed)
    container.markdown("""
        <script>
            const streamlit = window.parent.Streamlit;
            function setValue(name, value) {
                streamlit.setValue(name, value);
            }
        </script>
    """, unsafe_allow_html=True)


def run(selected_team: str) -> None:
    st.title(f"{selected_team} Dashboard")


def display_image_slideshow(container, folder_path: str, slideshow_key: str) -> None:
    """Display a slideshow of images from a specified folder in the given container."""
    # Get a list of image files in the specified folder
    image_urls = [os.path.join(folder_path, file) for file in os.listdir(folder_path) 
                  if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    
    if image_urls:
        # Create session state to keep track of current image index
        if 'image_index' not in st.session_state:
            st.session_state.image_index = 0
            
        # Create three columns: left arrow, image, right arrow
        col1, col2, col3 = container.columns([1, 10, 1])
        
        # Left arrow
        with col1:
            if st.button('←', key=f'{slideshow_key}_prev'):  # Use unique key
                st.session_state.image_index = (st.session_state.image_index - 1) % len(image_urls)
            
        # Display current image in the middle column
        with col2:
            st.image(image_urls[st.session_state.image_index], use_container_width=True)
            
        # Right arrow
        with col3:
            if st.button('→', key=f'{slideshow_key}_next'):  # Use unique key
                st.session_state.image_index = (st.session_state.image_index + 1) % len(image_urls)





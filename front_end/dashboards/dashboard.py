# This script holds general functions for all Team dashboards

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token
import os
import time
import math

class Metric:
    # def __init__(self, title: str, formula_markdown: str, description: str, interactive_calculator_func, calculation_func, image_path: str, inputs: list, min_value: float, max_value: float, ideal_value: float):
    def __init__(self, title: str, formula_markdown: str, description: str, calculation_func, image_path: str, inputs: list, min_value: float, max_value: float, ideal_value: float):
        self.title = title
        self.formula_markdown = formula_markdown
        self.description = description
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

    def display_interactive_calculator(self, container, columns=True):
        # Create a header for the interactive calculator
        container.markdown(f"### {self.title} Interactive Calculator")

        if columns:  # If columns are enabled, create two columns
            slider_container, metric_container = container.columns(2)
        else:  # If columns are not enabled, use a single container
            slider_container = container
            metric_container = container

        # Create a list to hold the input values
        input_values = []

        # Create a slider for each input
        for input in self.inputs:
            # If the input is a list, use the first value
            is_list = False
            name = input["name"]
            val = input["value"]

            if type(input["value"]) == list:
                is_list = True
                if type(input["value"][0]) == str:
                    input_values.append(input["value"])
                    continue
                else:
                    if 'rate' in input["name"].lower() or 'factor' in input["name"].lower():
                        # If the input is a rate or factor, calculate the average
                        val = sum([float(x) for x in input["value"]]
                                  ) / len(input["value"])
                        name += " (Avg)"
                    else:
                        # If the input is a list of numbers, sum them
                        val = sum(input["value"])
                        name += " (Sum)"
            # Otherwise, use the value directly
            else:
                val = input["value"]

            # Create a slider for the input
            input_slider = slider_container.slider(
                label=name,
                value=float(val),
                min_value=val * 0.5,
                max_value=val * 1.5
            )

            if type(input['value']) == list:
                input_values.append([input_slider])
            else:
                input_values.append(input_slider)

        print("Input Values for Interactive Calculator: ",
              input_values)  # Debugging: Print input values

        # Calculate the new value using the calculation function
        new_value = self.calculation_func(*input_values)
        delta_percent = (new_value - self.ideal_value) / \
            self.ideal_value * 100 if self.ideal_value != 0 else 0
        # Display the new value
        metric_container.metric(
            label=f"**Goal Value:** {self.ideal_value:.2f} | **Current Value:** {new_value:.2f}",
            value=f"{new_value:.4f}",
            delta=f"{delta_percent:.2f}%",
        )


def generate_dashboard(selected_team: str, metrics: list[Metric], project_id: str, team_members: list[dict], team_extractor, extracted_data, text_dict: list[dict], presentation_model_id) -> None:
    # Display the images
    header_image_container = st.container(border=True)
    display_images(header_image_container, selected_team, "02")

    # Display the page title
    display_page_title(selected_team)

    # Display the Team Members
    team_members_container = st.container()
    display_team_members(team_members_container, team_members)

    # Display the Speckle viewer
    viewer_height = 400
    speckle_container = st.container(border=True)
    display_speckle_viewer(speckle_container, project_id, presentation_model_id, is_transparent=True,
                           hide_controls=True, hide_selection_info=True, no_scroll=False, height=viewer_height, include_site=True)

    # Display the images
    images_container = st.container(border=True)
    display_images(images_container, selected_team, "01")

    # Display the text section
    text_container = st.container(border=True)
    display_text(text_container, text_dict)

    # Display the extracted data
    extracted_data_container = st.container(border=True)
    team_extractor.display_data(extracted_data=extracted_data, header=True, show_table=True,
                                gauge=False, simple_table=True, container=extracted_data_container)

    # Display the KPI section
    kpi_container = st.container(border=True)
    display_st_metric_values(kpi_container, metrics, use_columns=True)

    # Display the detailed metrics
    detailed_metrics_container = st.container(border=True)
    display_metric_visualizations(
        detailed_metrics_container, metrics, add_text=True)

    # Display the interactive calculators
    interactive_calculator_container = st.container(border=True)
    grid = True if len(metrics) > 2 else False
    display_interactive_calculators(
        interactive_calculator_container, metrics, grid=grid)

    pass


def display_text(container, text_dict: list[dict]) -> None:
    design_overview_container = container.container()
    display_design_overview(design_overview_container, text_dict)
    container.markdown('')  # Add some space

    display_custom_bullet_list(
        container, text_dict['bullet_items'], bullet_image_path=None)


def display_design_overview(container, text_dict: list[dict]) -> None:
    container.markdown('#### Design Overview')
    container.markdown(text_dict['design_overview'])


def display_team_members(container, team_members: list[dict]) -> None:
    container.markdown('')  # Add some space

    # Sort the team members by last name
    team_members.sort(key=lambda x: x["name"].split()[-1])

    # Display the team members
    for col, member in zip(container.columns(len(team_members)), team_members):
        with col:
            st.markdown(
                f'<div style="text-align: center;"><h5>{member["name"]}</h5></div>', unsafe_allow_html=True)
            st.markdown(
                f'<div style="text-align: center;"><a href="{member["link"]}">Profile</a></div>', unsafe_allow_html=True)

    # Style for team members
    container.markdown("""
    <style>
        .team-member {
            text-align: center;
            margin-bottom: 20px;
        }
        .team-member h5 {
            margin: 0;
        }
    </style>
    """, unsafe_allow_html=True)
    container.markdown('')  # Add some space


def display_interactive_calculators(container, metrics: list[Metric], grid: bool = True):
    container.markdown("""
    <h2 style='text-align: center;'>Interactive Sustainability Calculators</h3>
    """, unsafe_allow_html=True)

    columns = []

    if len(metrics) < 2:
        grid = False

    if grid:
        max_columns_in_row = 2
        columns_to_create = len(metrics)
        while columns_to_create > 0:
            columns_in_row = min(max_columns_in_row, columns_to_create)
            row = container.container()
            cols = row.columns(columns_in_row, border=True)
            columns.extend(cols)
            columns_to_create -= columns_in_row
    else:
        columns = [container.container() for _ in range(len(metrics))]

    for interactive_container, metric in zip(columns, metrics):
        metric.display_interactive_calculator(
            interactive_container, columns=not (grid))


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


def display_speckle_viewer(container, project_id, model_id, is_transparent=False, hide_controls=False, hide_selection_info=False, no_scroll=False, height=400, include_site=False):
    container.markdown('#### Representational Model')

    speckle_model_url = f'https://macad.speckle.xyz/projects/{project_id}/models/{model_id}'

    if include_site:
        speckle_model_url += ',693847dff2'

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
                style="width: 100%; height: {height}px; border: none;">
        </iframe>
        """
    container.markdown(iframe_code, unsafe_allow_html=True)

    return speckle_model_url


def display_page_title(team_name: str) -> None:
    st.markdown(f'''
        <div style="text-align: center;">
            <h1>{team_name.capitalize()} Team Dashboard</h1>
        </div>
    ''', unsafe_allow_html=True)


def display_formula_section_header(team_name: str) -> None:
    st.markdown(f'''
        <div style="text-align: center;">
            <h2>{team_name.capitalize()} Team Metrics</h2>
        </div>
    ''', unsafe_allow_html=True)


def display_st_metric_values(container, metrics, use_columns=True):
    container.markdown('#### Key Performance Indicators')

    if use_columns:
        column_containers = container.columns(len(metrics))
        for column_container, metric in zip(column_containers, metrics):
            with column_container:
                delta = (metric.value - metric.ideal_value) / \
                    metric.ideal_value * 100 if metric.ideal_value != 0 else 0
                column_container.metric(
                    metric.title, f'{metric.value:.2f}', delta=f'{delta:.2f}%', delta_color="normal", help=metric.description)
    else:
        for metric in metrics:
            delta = (metric.value - metric.ideal_value) / \
                metric.ideal_value * 100 if metric.ideal_value != 0 else 0
            container.metric(
                metric.title, f'{metric.value:.2f}', delta=f'{delta:.2f}%', delta_color="normal", help=metric.description)

def display_metric_visualizations(container, metrics, add_text=True):
    container.markdown('#### Metric Details')

    vis_cotainers = [container.container() for _ in range(len(metrics))]
    # for vis_container, metric in zip(vis_cotainers, metrics):
    for vis_container, metric, index in zip(vis_cotainers, metrics, range(len(metrics))):
        metric.display(vis_container, add_text=add_text)
        if index < len(metrics) - 1:
            # Add a horizontal line between metrics
            vis_container.markdown("---")


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
        padding-top: 1px;             
        display: flex;               
    }}
    </style>
    """

    bullet_list = "<ul class='enso-list'>"
    for item in items:
        bullet_list += f"<li>{item}</li>"
    bullet_list += "</ul>"

    container.markdown(bullet_style + bullet_list, unsafe_allow_html=True)


def display_metric(container, metric: Metric, add_text=True) -> None:
    # Display a metric in the specified container.

    # Display the metric title
    container.markdown(f"##### {metric.title}")

    # Display the metric image
    if metric.image_path:
        container.image(metric.image_path, width=100)

    # Display the metric formula
    container.latex(metric.formula_markdown)

    # Display the metric description
    container.markdown(metric.description)

    # Display the metric value and ideal value
    container.markdown(
        f"**Goal Value:** {metric.ideal_value:.2f} | **Current Value:** {metric.value:.2f}")

    # Display the tape diagram
    display_tape_diagram(container, metric)

    # """Display a metric in the specified container."""
    # print("DISPLAY METRIC: ", metric.title)

    # # Create two columns with specified widths
    # col1, col2 = container.columns([1, 2])  # First column is 1 part, second column is 2 parts

    # # In the first column, display the image with some right margin
    # with col1:
    #     image_width = 400  # Set your desired width
    #     st.markdown(f'<div style="text-align: right;">', unsafe_allow_html=True)  # Align image to the right
    #     st.image(metric.image_path, width=image_width, use_container_width=False)
    #     st.markdown('</div>', unsafe_allow_html=True)  # Close the div

    # # In the second column, display the text with additional margin
    # with col2:
    #     st.markdown(f'<div style="margin-top: 20px;">', unsafe_allow_html=True)  # Add top margin
    #     st.markdown(f"### {metric.title}")
    #     st.latex(metric.formula_markdown)
    #     st.markdown(metric.description)
    #     # st.metric(metric.title, f'{metric.value:.2f}')  # Display the metric value
    #     st.markdown('</div>', unsafe_allow_html=True)  # Close the div

    # # Call the function to display circles and tape
    # with container:
    #     display_metric_circles_and_tape(container, metric)
    #     for _ in range(5):
    #         st.markdown("")


def display_tape_diagram(container, metric: Metric) -> None:
    fig = go.Figure(go.Indicator(
        mode="number+gauge+delta",
        gauge={
            'shape': "bullet",
            'axis': {'range': [metric.min_value, metric.max_value]},
            'steps': [
                {'range': [metric.min_value, metric.ideal_value],
                    'color': "Salmon"},
                {'range': [metric.ideal_value, metric.max_value],
                    'color': "PaleGreen"},
            ],
            'threshold': {
                'line': {'color': "SteelBlue", 'width': 8},
                'value': metric.ideal_value
            },
            'bar': {'color': "Silver", },
        },
        value=metric.value,
        delta={'reference': metric.ideal_value,
               'position': 'right', 'relative': True},
        domain={'x': [0, 1], 'y': [0, 1]},
    ),)

    side_margin = 100
    top_margin = 0
    height = 50
    font_size = 16

    fig.update_layout(
        height=height,
        margin=dict(l=side_margin, r=side_margin, t=top_margin, b=top_margin),
        font=dict(size=font_size),
        paper_bgcolor='rgba(0, 0, 0, 0)',
        plot_bgcolor='rgba(0, 0, 0, 0)',
    )
    container.plotly_chart(fig)


def create_top_menu(teams: list[str]) -> str:
    # Initialize session state if not exists
    if 'current_selection' not in st.session_state:
        st.session_state.current_selection = teams[0]
    # Create a expander for the menu
    # Create columns for each team

    # print(f'Created {len(created_cols)} columns for {len(teams)} teams.')
    header = st.container()
    # header.title("Here is a sticky header")
    header.write("""<div class='fixed-header'/>""", unsafe_allow_html=True)

    ### Custom CSS for the sticky header
    st.markdown(
        """
    <style>
        div[data-testid="stVerticalBlock"] div:has(div.fixed-header) {
            position: sticky;
            top: 2.875rem;
            background-color: black;
            z-index: 999;
        }
    </style>
        """,
        unsafe_allow_html=True
    )

    with header:        
        # header_container = st.container()
        # button_container = st.container()
        
        header_container, button_container = st.columns([1, 1.5], gap="small")

        with header_container:
            st.markdown('<h2 style="color: white; padding-left: 10px">Hyper A Dashboard</h2>', unsafe_allow_html=True)
        
        with button_container:
            total_buttons_var = len(teams)
            button_labels = teams
            cols_in_row = len(teams)

            created_rows = []
            created_cols = []

            while total_buttons_var > 0:
                columns_to_create = min(cols_in_row, total_buttons_var)
                row = st.container()

                labels = button_labels[:columns_to_create]
                button_labels = button_labels[columns_to_create:]

                widths = [len(label) for label in labels]

                cols = row.columns(widths, gap="small")  # Create columns for each team
                created_rows.append(row)
                created_cols.extend(cols)
                total_buttons_var -= columns_to_create

            cols = created_cols

            # widths = [len(team) for team in teams]
            # cols = st.columns(widths, gap="small")  # Create columns for each team

            # Create buttons in each column and handle selection
            selected = None
            for col, item in zip(cols, teams):
                with col:
                    is_selected = item == st.session_state.current_selection
                    
                    if st.button(
                        label=item, 
                        key=f"menu_{item}",  # Ensure unique key by prefixing with 'menu_'
                        use_container_width=True,
                    ):
                        selected = item

                    st.markdown(
                        f"""
                        <style>
                            div[data-testid="stButton"] > button:first-child {{
                                color: white;
                                background-color: transparent;
                            }}
                        </style>
                        """,
                        unsafe_allow_html=True
                    )

        st.markdown('')

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
    scaled_value = (metric.value - metric.min_value) / \
        range_value if range_value > 0 else 0  # Avoid division by zero

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
    # Convert to percentage for positioning
    position_percentage = scaled_value * 100
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
    container.markdown(
        "<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    # Ensure all values in args are numeric
    input_values = []
    for input in metric.inputs:
        if "display_value" in input and input["display_value"]:
            input_values.append(float(input["display_value"]))
        else:
            input_values.append(float(input["value"]))

    # Find the maximum value to scale the circles
    # Avoid division by zero
    max_value = max(input_values) if input_values else 1
    scaling_factor = 200  # Maximum diameter for the largest circle
    min_circle_diameter = 30  # Minimum diameter for visibility

    print("Input Values for Metric: ", metric.title, input_values)
    # Create columns for layout with 2 extra columns
    total_columns = len(input_values) + 2
    print("Total Columns for metric: ", metric.title,
          total_columns)  # Debugging: Print total columns
    # Create total_columns based on the number of values + 2
    cols = st.columns(total_columns)

    # Place empty circles in the first and last columns
    for idx in range(total_columns):
        if idx == 0 or idx == total_columns - 1:
            with cols[idx]:
                st.markdown("")  # Empty column for spacing
        else:
            # Create a circle representation for the metric values
            inputs_index = idx - 1  # Adjust index for metric values
            # Get the value from the Metric instance
            value = input_values[inputs_index]
            # Scale for visibility with a minimum size
            circle_diameter = max((value / max_value) *
                                  scaling_factor, min_circle_diameter)
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


def display_images(container, team_name: str, subfolder: str='01', header: bool=True) -> None:
    if header:
        container.markdown('#### Concept Images')

    folder_path = f"./front_end/assets/{team_name.capitalize()}/{subfolder}"
    image_urls = [os.path.join(folder_path, file) for file in os.listdir(folder_path)
                  if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    
    if image_urls:
        # Display images in the container
        for image_url, column in zip(image_urls, container.columns(len(image_urls))):
            column.image(image_url)
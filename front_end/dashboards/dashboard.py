# This script holds general functions for all Team dashboards

import streamlit as st
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token
import os

from streamlit_stl import stl_from_file


class Metric:
    def __init__(self, title: str, formula_markdown: str, description: str, calculation_func, *args):
        self.title = title
        self.formula_markdown = formula_markdown
        self.description = description
        self.calculation_func = calculation_func
        self.args = args
        self.value = self.calculate()

    def calculate(self):
        print(self.args)
        print(self.calculation_func)
        return self.calculation_func(*self.args)

    def display(self, container, add_text=True, add_sphere=True):
        display_metric(container, self.title, self.formula_markdown,
                       self.description, self.value, add_text, add_sphere)


def setup_speckle_connection():
    speckle_server = "macad.speckle.xyz"
    speckle_token = "61c9dd1efb887a27eb3d52d0144f1e7a4a23f962d7"
    client = SpeckleClient(host=speckle_server)
    account = get_account_from_token(speckle_token, speckle_server)
    client.authenticate_with_account(account)

    project_id = '31f8cca4e0'
    project = client.project.get_with_models(
        project_id=project_id, models_limit=100)
    models = project.models.items

    return models, client, project_id


def display_page_title(team_name: str) -> None:
    st.markdown(f'''
        <div style="
            text-align: left;
            background-color: white;
            padding: 20px;
            margin: -1rem -1rem 1rem -1rem;
            width: calc(100% + 2rem);
        ">
            <h1 style="color: #2d2d2d; margin: 0;">{team_name} Dashboard</h1>
        </div>
    ''', unsafe_allow_html=True)


def display_formula_section_header(team_name: str) -> None:
    st.markdown(f'''
        <div style="text-align: center;">
            <h2>{team_name} Metrics</h2>
        </div>
    ''', unsafe_allow_html=True)


def display_st_metric_values(container, metrics):
    column_containers = container.columns(4)
    for column_container, metric in zip(column_containers, metrics):
        with column_container:
            column_container.metric(metric.title, f'{metric.value:.2f}')


def display_metric_visualizations(container, metrics, add_text=True, add_sphere=True):
    vis_cotainers = [container.container() for _ in range(len(metrics))]
    for vis_container, metric in zip(vis_cotainers, metrics):
        metric.display(container, add_text=add_text, add_sphere=add_sphere)
    st.markdown("---")


def display_image_slideshow(container, folder_path: str) -> None:
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
            if st.button('←', key='prev'):
                st.session_state.image_index = (st.session_state.image_index - 1) % len(image_urls)
            
        # Display current image in the middle column
        with col2:
            st.image(image_urls[st.session_state.image_index], use_container_width=True)
            
        # Right arrow
        with col3:
            if st.button('→', key='next'):
                st.session_state.image_index = (st.session_state.image_index + 1) % len(image_urls)

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

def display_metric(container, title: str, formula_markdown: str, description: str, value: float, add_text=True, add_sphere: bool = True):
    def metric_text_display(title, formula_markdown, description, value):
        st.markdown(f"### {title}")
        st.latex(formula_markdown)
        st.markdown(description)
        if value is not None:
            st.markdown(
                f"<h4 style='text-align: center;'>Current Value: {value:.2f}</h4>", unsafe_allow_html=True)

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
                    style="width: 100%; {
                        'border-bottom: 2px solid #000000; border-radius: 0;' if is_selected else ''
                    }"
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

def display_kpi_columns(container, kpi_data: list[dict]) -> None:
    """Display KPIs in 3 columns with images and metrics.
    
    Args:
        container: Streamlit container
        kpi_data: List of dictionaries containing:
            {
                'title': 'KPI Title',
                'image_path': 'path/to/image.png',
                'name': 'Display Name',
                'metric_value': 0.75,
                'metric_description': 'Description of the metric'
            }
    """
    # Create header
    container.markdown("""
        <div style="
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            width: 100%;
            color: #2d2d2d;
            margin: 10px 0;
        ">
            <h2 style="margin: 0;">Key Performance Indicators</h2>
        </div>
                                      
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Create three columns
    cols = container.columns(3)
    
    # Display content in each column
    for col, kpi in zip(cols, kpi_data):
        with col:
            # KPI Title
            st.markdown(f"""
                <div style="text-align: center; padding: 10px;">
                    <h3>{kpi['title']}</h3>
                </div>
            """, unsafe_allow_html=True)
            
            # Image and Name in a box
            st.markdown(f"""
                <div style="
                    background-color: #f0f0f0;
                    padding: 15px;
                    border-radius: 10px;
                    text-align: center;
                ">
                    <img src="{kpi['image_path']}" style="max-width: 100%; height: auto;">
                    <h4 style="margin-top: 10px;">{kpi['name']}</h4>
                </div>
            """, unsafe_allow_html=True)
            
            # Metric value in a box
            st.markdown(f"""
                <div style="
                    background-color: #2d2d2d;
                    color: white;
                    padding: 15px;
                    border-radius: 10px;
                    text-align: center;
                    margin-top: 10px;
                ">
                    <h3 style="margin: 0;">{kpi['metric_value']:.2f}</h3>
                    <p style="margin: 5px 0 0 0;">{kpi['metric_description']}</p>
                </div>
            """, unsafe_allow_html=True)

    
    # Apply custom styling to the dataframe
    styled_df = df.style.set_properties(**{
        'background-color': '#f0f0f0',
        'padding': '10px',
        'border-radius': '5px',
        'font-size': '16px'
    })
    
    container.dataframe(styled_df, use_container_width=True)

def display_kpi_details(container, kpi_data: list[dict]) -> None:
    """Display detailed KPI explanations in alternating two-column layout with images."""
    container.markdown("""
        <div style="
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            width: 100%;
            color: black;
            margin: 10px 0;
        ">
            <h2 style="margin: 0;">KPI Details</h2>
            <hr style="border: 1px solid black;"/>  <!-- Add a horizontal line -->
        </div>
    """, unsafe_allow_html=True)

    # For each KPI, create a two-column layout
    for idx, kpi in enumerate(kpi_data):
        # Create two columns with equal height
        col1, col2 = container.columns([1, 1])
        
        # Common text style
        text_style = """
            <div style="
                padding: 20px;
                height: 100%;
                display: flex;
                flex-direction: column;
                justify-content: center;
                min-height: 300px;
                text-align: center;  /* Center align text */
            ">
                <h3 style="margin-top: 100px;">{title}</h3>  <!-- Adjusted margin-top -->
                <p style="font-size: 18px;">{description}</p>
                <p style="font-size: 20px; color: #000000;">Current Value: {value:.2f}</p>
            </div>
        """
        
        # Alternate the content between columns
        if idx % 2 == 0:  # Even indices - Text left, Image right
            with col1:
                st.markdown(
                    text_style.format(
                        title=kpi['title'],
                        description=kpi.get('detailed_description', 'No detailed description available.'),
                        value=kpi['metric_value']
                    ),
                    unsafe_allow_html=True
                )
            with col2:
                st.image(kpi['image_path'], use_container_width=True)  # Display the KPI image in the second column
        else:  # Odd indices - Image left, Text right
            with col1:
                st.image(kpi['image_path'], use_container_width=True)  # Display the KPI image in the first column
            with col2:
                st.markdown(
                    text_style.format(
                        title=kpi['title'],
                        description=kpi.get('detailed_description', 'No detailed description available.'),
                        value=kpi['metric_value']
                    ),
                    unsafe_allow_html=True
                )
        
        # Add some spacing between KPIs
        st.markdown("<br>", unsafe_allow_html=True)



def display_stl_model(file_path: str, color: str, key: str):
    """Display the STL model with customizable settings and a two-color division."""
    # Define the fragment shader for two-color division
    fragment_shader = """
        varying vec3 vPosition;
        void main() {
            if (vPosition.y > 0.0) {
                gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0); // Red for the top half
            } else {
                gl_FragColor = vec4(0.0, 1.0, 0.0, 1.0); // Green for the bottom half
            }
        }
    """

    stl_from_file(
        file_path=file_path,
        color=color,
        material="material",
        auto_rotate=True,
        opacity=1.0,
        height=500,
        shininess=100,
        cam_v_angle=60,
        cam_h_angle=-90,
        cam_distance=0,
        max_view_distance=1000,
        key=key,
        shader=fragment_shader  # Use the custom shader for two-color division
    )

def display_metric_circles_and_tape(container, title, primary_metric_value, metric_values, metric_names, units="m²") -> None:
    """Display input values for metrics in circles and a tape diagram showing progress."""
    
    # Display the title for the metric
    container.markdown(f"<h3>{title}</h3>", unsafe_allow_html=True)
    
    # Create a gradient background for the tape diagram
    tape_value = primary_metric_value
    container.markdown(f"""
        <div style='width: 100%; height: 30px; background: linear-gradient(to right, #f5f5dc, #8B4513); position: relative;'>
            <div style='width: {tape_value * 100}%; height: 100%; background-color: rgba(255, 255, 255, 0.5);'></div>
            <div style='position: absolute; width: 100%; height: 100%;'>
                <div style='position: absolute; top: 0; left: 0; width: 100%;'>
                    {''.join(f"<div style='position: absolute; left: {i * 10}%; height: 30px; border-left: 1px solid black; z-index: 1;'></div>" for i in range(1, 11))}
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Calculate the position for the value display
    position_percentage = tape_value * 100  # Convert to percentage for positioning
    container.markdown(f"""
        <div style='position: relative; width: 100%;'>
            <div style='position: absolute; left: {position_percentage}%; transform: translateX(-50%); font-size: 24px; color: black; top: 30px;'>
                <strong>{tape_value:.2f}</strong>  <!-- Display the primary metric value -->
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Add space between the tape diagram and the metric values
    container.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
    
    # Find the maximum value to scale the circles
    max_value = max(metric_values)
    scaling_factor = 200  # Maximum diameter for the largest circle
    min_circle_diameter = 30  # Minimum diameter for visibility

    # Create columns for layout with 2 extra columns
    total_columns = len(metric_values) + 2
    cols = st.columns(total_columns)  # Create total_columns based on the number of values + 2

    # Place empty circles in the first and last columns
    for idx in range(total_columns):
        if idx == 0 or idx == total_columns - 1:
            with cols[idx]:
                st.markdown("")  # Empty column for spacing
        else:
            # Create a circle representation for the metric values
            metric_index = idx - 1  # Adjust index for metric values
            value = metric_values[metric_index]
            circle_diameter = max((value / max_value) * scaling_factor, min_circle_diameter)  # Scale for visibility with a minimum size
            with cols[idx]:
                st.markdown(f"""
                    <div style="position: relative; display: inline-block;">
                        <div style="
                            width: {circle_diameter}px; 
                            height: {circle_diameter}px; 
                            border-radius: 50%; 
                            background-color: #f5f5dc;  /* Light beige color */
                            text-align: center; 
                            line-height: {circle_diameter}px; 
                            cursor: default;
                        ">
                            {value:.2f} {units}
                        </div>
                        <div style="
                            position: absolute; 
                            top: {circle_diameter}px; 
                            left: 50%; 
                            transform: translateX(-50%); 
                            background-color: white; 
                            padding: 5px; 
                            border-radius: 5px; 
                            box-shadow: 0 0 5px rgba(0,0,0,0.3);
                        ">
                            {metric_names[metric_index]}  <!-- Restore metric names -->
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    # Add space of 100px underneath the circles
    container.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)

    # Add JavaScript to handle input changes (if needed)
    container.markdown("""
        <script>
            const streamlit = window.parent.Streamlit;
            function setValue(name, value) {
                streamlit.setValue(name, value);
            }
        </script>
    """, unsafe_allow_html=True)

def metric_calc_daylight_factor(weight_residential, weight_work, residential_area_with_daylight, total_residential_area, work_area_with_daylight, total_work_area):
    return (
        weight_residential * (residential_area_with_daylight / total_residential_area) +
        weight_work * (work_area_with_daylight / total_work_area)
    )

def run(selected_team: str) -> None:
    st.title(f"{selected_team} Dashboard")



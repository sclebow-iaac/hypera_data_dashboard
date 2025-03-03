# This script holds general functions for all Team dashboards

import streamlit as st
import pandas as pd
import plotly.express as px
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token
import os

import pandas as pd
import plotly.express as px


class Metric:
    def __init__(self, title: str, formula_markdown: str, description: str, interactive_calculator_func, calculation_func, *args):
        self.title = title
        self.formula_markdown = formula_markdown
        self.description = description
        self.interactive_calculator_func = interactive_calculator_func
        self.calculation_func = calculation_func
        self.args = args
        self.value = self.calculate()

    def calculate(self):
        return self.calculation_func(*self.args)

    def display(self, container, add_text=True, add_sphere=True):
        display_metric(container, self.title, self.formula_markdown,
                       self.description, self.value, add_text, add_sphere)

    def display_interactive_calculator(self, container):
        self.interactive_calculator_func(container, *self.args)


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
            text-align: center;
            background-color: black;
            padding: 20px;
            margin: -1rem -1rem 1rem -1rem;
            width: calc(100% + 2rem);
        ">
            <h1 style="color: white; margin: 0;">{team_name} Dashboard</h1>
        </div>
    ''', unsafe_allow_html=True)


def display_formula_section_header(team_name: str) -> None:
    st.markdown(f'''
        <div style="text-align: center;">
            <h2>{team_name} Metrics</h2>
        </div>
    ''', unsafe_allow_html=True)


def display_metric(container, title: str, formula_markdown: str, description: str, value: float, add_text=True, add_sphere: bool = True):
    def metric_text_display(title, formula_markdown, description, value):
        st.markdown(f"### {title}")
        st.latex(formula_markdown)
        st.markdown(description)
        if value is not None:
            st.markdown(
                f"<h4 style='text-align: center;'>Current Value: {value:.2f}</h4>", unsafe_allow_html=True)

    def metric_sphere_display(title, value):
        sphere_html = create_sphere_visualization(
            f"{title.lower().replace(' ', '-')}-sphere",
            value,
            title
        )
        st.components.v1.html(sphere_html, height=300)
    if add_text and add_sphere:
        if len(formula_markdown) < 100:
            container_1, container_2 = container.columns(2)
        else:
            container_1 = container.container()
            container_2 = container.container()
        with container_1:
            metric_text_display(title, formula_markdown, description, value)
        with container_2:
            metric_sphere_display(title, value)
    elif add_text:
        metric_text_display(title, formula_markdown, description, value)
    elif add_sphere:
        metric_sphere_display(title, value)
    else:
        pass


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
            background-color: #2d2d2d;
            padding: 20px;
            border-radius: 5px;
            width: 100%;
            color: white;
            margin: 10px 0;
        ">
            {text}
        </div>
    """, unsafe_allow_html=True)

    
def create_sphere_visualization(container_id, value, label, height=400):
    """Helper function to create sphere visualization HTML"""
    return f"""
    <html>
        <head>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
            <style>
                .container {{ 
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 20px;
                    height: {height}px;
                    width: 100%;
                    margin: 0 auto;  /* Center the container */
                }}
                #{container_id} {{ 
                    width: 75%;  /* Standardize width */
                    height: 100%;
                    position: relative;
                    margin-left: auto;  /* Center the model container */
                    margin-right: auto;
                }}
                #legend-container {{
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    height: 100%;
                    padding: 20px 0;
                    width: 60px;  /* Fixed width for legend */
                }}
                #color-gradient {{
                    width: 30px;
                    height: 200px;
                    background: linear-gradient(to top, #ff0000, #00ff00);
                    border: 1px solid #333;
                }}
                .legend-label {{
                    padding: 5px;
                    font-family: Arial;
                    font-size: 12px;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div id="{container_id}"></div>
                <div id="legend-container">
                    <div class="legend-label">1.0</div>
                    <div id="color-gradient"></div>
                    <div class="legend-label">0.0</div>
                    <div class="legend-label">{label}</div>
                </div>
            </div>
            <script>
                const container = document.getElementById('{container_id}');
                const scene = new THREE.Scene();
                
                // Adjust camera FOV and position
                const camera = new THREE.PerspectiveCamera(60, container.clientWidth/container.clientHeight, 0.1, 1000);
                camera.position.z = 6;  // Move camera further back
                
                const renderer = new THREE.WebGLRenderer({{ 
                    antialias: true,
                    alpha: true  // Enable transparency
                }});
                
                renderer.setSize(container.clientWidth, container.clientHeight);
                renderer.setClearColor(0xeeeeee, 0.9);  // Slightly transparent background
                container.appendChild(renderer.domElement);

                const ambient_light = new THREE.AmbientLight(0xffffff, 0.5);
                scene.add(ambient_light);
                const directional_light = new THREE.DirectionalLight(0xffffff, 0.8);
                directional_light.position.set(3, 5, 1);
                scene.add(directional_light);

                const vertex_shader = `
                    varying vec3 vPosition;
                    void main() {{
                        vPosition = position;
                        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
                    }}
                `;

                const fragment_shader = `
                    uniform float value;
                    varying vec3 vPosition;
                    void main() {{
                        float y = (vPosition.y + 2.0) / 4.0;
                        vec3 bottomColor = vec3(1.0, 0.0, 0.0);
                        vec3 topColor = vec3(0.0, 1.0, 0.0);
                        vec3 color = mix(bottomColor, topColor, y * {value});
                        gl_FragColor = vec4(color, 1.0);
                    }}
                `;

                const geometry = new THREE.SphereGeometry(1.2, 32, 32);  // Even smaller sphere
                const material = new THREE.ShaderMaterial({{
                    uniforms: {{
                        value: {{ value: {value} }}
                    }},
                    vertexShader: vertex_shader,
                    fragmentShader: fragment_shader
                }});
                
                const sphere = new THREE.Mesh(geometry, material);
                sphere.rotation.x = Math.PI * 0.2;
                scene.add(sphere);

                // Update resize handler
                function onWindowResize() {{
                    const width = container.clientWidth;
                    const height = container.clientHeight;
                    camera.aspect = width / height;
                    camera.updateProjectionMatrix();
                    renderer.setSize(width, height, false);  // Add false to prevent pixelation
                }}
                
                onWindowResize();  // Call once to set initial size

                function animate() {{
                    requestAnimationFrame(animate);
                    renderer.render(scene, camera);
                }}
                animate();
            </script>
        </body>
    </html>
    """

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
            font-size: 16px;
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
                key=f"menu_{item}", 
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
            background-color: #2d2d2d;
            padding: 20px;
            border-radius: 5px;
            width: 100%;
            color: white;
            margin: 10px 0;
        ">
            <h2 style="margin: 0;">Key Performance Indicators</h2>
        </div>
    """, unsafe_allow_html=True)

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

def display_data_table(container, data: dict) -> None:
    """Display data table with consistent styling."""
    container.markdown("""
        <div style="
            background-color: #2d2d2d;
            padding: 20px;
            border-radius: 5px;
            width: 100%;
            color: white;
            margin: 10px 0;
        ">
            <h2 style="margin: 0;">Extracted Data</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Convert dict to DataFrame and style it
    df = pd.DataFrame(list(data.items()), columns=['Parameter', 'Value'])
    
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
            background-color: #2d2d2d;
            padding: 20px;
            border-radius: 5px;
            width: 100%;
            color: white;
            margin: 10px 0;
        ">
            <h2 style="margin: 0;">KPI Details</h2>
        </div>
    """, unsafe_allow_html=True)

    # For each KPI, create a two-column layout with alternating order
    for idx, kpi in enumerate(kpi_data):
        # Create two columns with equal height
        col1, col2 = container.columns([1, 1])
        
        # Common image style
        image_style = """
            <div style="
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100%;
                padding: 20px;
            ">
                <img src="{}" style="max-width: 100%; max-height: 300px; object-fit: contain;">
            </div>
        """
        
        # Common text style
        text_style = """
            <div style="
                background-color: #f0f0f0;
                padding: 20px;
                border-radius: 10px;
                height: 100%;
                display: flex;
                flex-direction: column;
                justify-content: center;
                min-height: 300px;
            ">
                <h3 style="margin-top: 0; text-align: center;">{title}</h3>
                <p style="font-size: 18px; text-align: center;">{description}</p>
                <p style="font-size: 16px; color: #666; text-align: center;">Current Value: {value:.2f}</p>
            </div>
        """
        
        # Alternate the content between columns
        if idx % 2 == 0:  # Even indices - Image left, Text right
            with col1:
                st.markdown(image_style.format(kpi['image_path']), unsafe_allow_html=True)
            with col2:
                st.markdown(
                    text_style.format(
                        title=kpi['title'],
                        description=kpi.get('detailed_description', 'No detailed description available.'),
                        value=kpi['metric_value']
                    ),
                    unsafe_allow_html=True
                )
        else:  # Odd indices - Text left, Image right
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
                st.markdown(image_style.format(kpi['image_path']), unsafe_allow_html=True)
        
        # Add some spacing between KPIs
        st.markdown("<br>", unsafe_allow_html=True)

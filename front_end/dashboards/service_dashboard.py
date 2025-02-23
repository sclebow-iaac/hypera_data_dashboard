import streamlit as st
import data_extraction.service_extractor as service_extractor
import pandas as pd
import plotly.express as px
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token

def run(selected_team: str) -> None:
    # 1. Imports and Setup
    import data_extraction.service_extractor as service_extractor
    import pandas as pd
    import plotly.express as px
    
    # 2. Speckle Connection
    speckleServer = "macad.speckle.xyz"
    speckleToken = "61c9dd1efb887a27eb3d52d0144f1e7a4a23f962d7"
    client = SpeckleClient(host=speckleServer)
    account = get_account_from_token(speckleToken, speckleServer)
    client.authenticate_with_account(account)
    
    project_id = '31f8cca4e0'
    selected_project = client.project.get(project_id=project_id)
    project = client.project.get_with_models(project_id=selected_project.id, models_limit=100)
    models = project.models.items

    # Initial values
    occupancy_efficiency = 80
    utilization_rate = 34
    n = 5
    active_hours = 12
    function_exchange_factor = 4
    total_available_hours_per_day = 13
    total_spaces_available = 50

    # Header
    st.markdown("""
        <div style="text-align: center;">
            <h1>Service Dashboard</h1>
        </div>
    """, unsafe_allow_html=True)

    # Metrics Display
    metric_col1, metric_col2 = st.columns(2)
    metric_col1.metric("Number of Spaces", n)
    metric_col2.metric("Primary Metric", "Occupancy Efficiency")

    # Calculate Primary Index
    numerator = utilization_rate * active_hours * function_exchange_factor
    denominator = total_available_hours_per_day * total_spaces_available
    calculated_value = numerator / denominator if denominator != 0 else 0

    # Display Formula and Explanation
    st.markdown("""
    <h2 style='text-align: center;'>Occupancy Efficiency</h2>
    """, unsafe_allow_html=True)

    st.markdown(r"""
        The formula for calculating the metric can be expressed as:
        
        $$ 
        \frac{\sum_{i=1}^{n} (UtilizationRateOfFunction_i \cdot ActiveHoursOfFunctionPerDay_i \cdot FunctionExchangeFactor)}{TotalAvailableHoursPerDay \cdot TotalSpacesAvailable}
        $$
    """, unsafe_allow_html=True)

    if calculated_value is not None:
        st.markdown(f"<h3 style='text-align: center;'>Calculated Occupancy Efficiency: {calculated_value:.2f}</h3>", unsafe_allow_html=True)

    # 3D Visualization
    st.markdown("""
    <h2 style='text-align: center;'>3D Visualization</h2>
    """, unsafe_allow_html=True)

    # Create sphere visualization
    html = create_sphere_visualization(
        "main-sphere",
        calculated_value,
        "Occupancy Efficiency"
    )
    st.components.v1.html(html, height=600)

    # Interactive Calculator
    st.markdown("""
    <h3 style='text-align: center;'>Interactive Occupancy Calculator</h3>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Adjust Values")
        new_utilization_rate = st.slider("Utilization Rate (%)", 0, 100, utilization_rate, help="Percentage of space utilization")
        new_active_hours = st.slider("Active Hours", 0, 24, active_hours, help="Hours of active use per day")
        new_function_exchange_factor = st.slider("Function Exchange Factor", 1, 10, function_exchange_factor, help="Multiplier for function flexibility")
        new_total_hours = st.slider("Total Available Hours per Day", 1, 24, total_available_hours_per_day, help="Total hours available per day")
        new_total_spaces = st.slider("Total Spaces Available", 1, 100, total_spaces_available, help="Total number of spaces")
        
        # Calculate new value
        new_numerator = new_utilization_rate * new_active_hours * new_function_exchange_factor
        new_denominator = new_total_hours * new_total_spaces
        new_calculated_value = new_numerator / new_denominator if new_denominator != 0 else 0
        st.markdown(f"### Resulting Occupancy Efficiency: {new_calculated_value:.2f}")

    with col2:
        # Create dynamic sphere
        dynamic_sphere = create_sphere_visualization(
            "dynamic-sphere",
            new_calculated_value,
            "Occupancy Efficiency",
            height=200
        )
        st.components.v1.html(dynamic_sphere, height=250)

    # Extract and display service data
    service_data = service_extractor.extract(models, client, project_id)

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

                const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
                scene.add(ambientLight);
                const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
                directionalLight.position.set(3, 5, 1);
                scene.add(directionalLight);

                const vertexShader = `
                    varying vec3 vPosition;
                    void main() {{
                        vPosition = position;
                        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
                    }}
                `;

                const fragmentShader = `
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
                    vertexShader: vertexShader,
                    fragmentShader: fragmentShader
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

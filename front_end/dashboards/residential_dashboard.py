import streamlit as st
import pandas as pd
import plotly.express as px
from pythreejs import *
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token

import data_extraction.residential_extractor as residential_extractor
#import pandas
import pandas as pd
#import plotly express
import plotly.express as px

# Define the function to run the dashboard

def run(selected_team: str) -> None:

    # Get data from residential extractor
    speckleServer = "macad.speckle.xyz"
    speckleToken = "61c9dd1efb887a27eb3d52d0144f1e7a4a23f962d7"
    client = SpeckleClient(host=speckleServer)
    account = get_account_from_token(speckleToken, speckleServer)
    client.authenticate_with_account(account)
    
    project_id = '31f8cca4e0'
    selected_project = client.project.get(project_id=project_id)
    project = client.project.get_with_models(project_id=selected_project.id, models_limit=100)
    models = project.models.items
    
    
    # Create columns for metrics
    # Center title and image using HTML/CSS
    st.markdown("""
            <div style="text-align: center;">
                <h1>Residential Dashboard</h1>
            </div>
        """, unsafe_allow_html=True)
    metric_col1, metric_col2 = st.columns(2)
    metric_col1.metric("Unit Types", "4")
    metric_col2.metric("Primary Metric", "Mixed Use Index")

    number_of_units = [40, 60, 30, 20]  
    unit_types = ['Housing', 'Social', 'Commercial', 'Open Space']
    total_number_of_units = sum(number_of_units)

    # Compute the formula
    numerator = sum(
        units * (units - 1) for units in number_of_units
    )
    denominator = total_number_of_units * (total_number_of_units - 1)

    if denominator != 0:  # Avoid division by zero
        calculated_value = 1 - (numerator / denominator)
    else:
        calculated_value = None  # Handle division by zero case

    # Extract residential data
    residential_data = residential_extractor.extract(models, client, project_id)

    st.markdown("""
    <h2 style='text-align: center, font-size: 24px;'>Mixed Use Index</h2>
    """, unsafe_allow_html=True)

    st.markdown("")

    # Add the math formula
    st.markdown(r"""
        The formula for calculating the metric can be expressed as:
        
        $$ 
        1 - \frac{\sum \text{NumberOfUnitsOfASingleFunction}_i \cdot (\text{NumberOfUnitsOfASingleFunction}_i - 1)}{\text{TotalNumberOfUnits} \cdot (\text{TotalNumberOfUnits} - 1)}
        $$
    """, unsafe_allow_html=True)

    st.markdown("")

    # Display the computed value
    if calculated_value is not None:
        st.markdown(f"<h3 style='text-align: center;'>Calculated Value: {calculated_value:.2f}</h3>", unsafe_allow_html=True)
    else:
        st.markdown("<h3 style='text-align: center;'>Error: Division by zero in calculation</h3>", unsafe_allow_html=True)

    st.markdown("""
    <h2 style='text-align: center, font-size: 24px;'>3D Visualization</h2>
    """, unsafe_allow_html=True)

    # Create an HTML string to embed the 3D scene with a colored sphere
    html = f"""
    <html>
        <head>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
            <style>
                .container {{ 
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 20px;
                }}
                #model-container {{ 
                    width: 70%; 
                    height: 400px; 
                }}
                #legend-container {{
                    width: 60px;
                    height: 300px;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    margin-right: 20px;
                }}
                #color-gradient {{
                    width: 30px;
                    height: 200px;
                    background: linear-gradient(to top, #ff0000, #00ff00);
                    border: 1px solid #333;
                }}
                .legend-label {{
                    margin: 5px 0;
                    font-family: Arial;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div id="model-container"></div>
                <div id="legend-container">
                    <div class="legend-label">1.0</div>
                    <div id="color-gradient"></div>
                    <div class="legend-label">0.0</div>
                    <div class="legend-label">Mixed Use Index</div>
                </div>
            </div>
            <script>
                const container = document.getElementById('model-container');
                const scene = new THREE.Scene();
                const camera = new THREE.PerspectiveCamera(75, container.clientWidth/container.clientHeight, 0.1, 1000);
                const renderer = new THREE.WebGLRenderer({{ antialias: true }});
                
                renderer.setSize(container.clientWidth, container.clientHeight);
                renderer.setClearColor(0xeeeeee);
                container.appendChild(renderer.domElement);

                // Add lights
                const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
                scene.add(ambientLight);
                const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
                directionalLight.position.set(3, 5, 1);
                scene.add(directionalLight);

                // Create custom shader material for gradient
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
                        float y = (vPosition.y + 2.0) / 4.0; // Normalize y position to 0-1
                        vec3 bottomColor = vec3(1.0, 0.0, 0.0); // Red
                        vec3 topColor = vec3(0.0, 1.0, 0.0);    // Green
                        vec3 color = mix(bottomColor, topColor, y * value);
                        gl_FragColor = vec4(color, 1.0);
                    }}
                `;

                const geometry = new THREE.SphereGeometry(2, 32, 32);
                const material = new THREE.ShaderMaterial({{
                    uniforms: {{
                        value: {{ value: {calculated_value} }}
                    }},
                    vertexShader: vertexShader,
                    fragmentShader: fragmentShader
                }});
                
                const sphere = new THREE.Mesh(geometry, material);
                // Optional: Set a fixed rotation if desired
                sphere.rotation.x = Math.PI * 0.2; // Tilt slightly forward
                scene.add(sphere);

                camera.position.z = 5;

                function animate() {{
                    requestAnimationFrame(animate);
                    renderer.render(scene, camera);
                }}
                animate();

                // Handle window resize
                window.addEventListener('resize', onWindowResize, false);
                function onWindowResize() {{
                    camera.aspect = container.clientWidth / container.clientHeight;
                    camera.updateProjectionMatrix();
                    renderer.setSize(container.clientWidth, container.clientHeight);
                }}
            </script>
        </body>
    </html>
    """

    # Display the 3D model in Streamlit
    st.components.v1.html(html, height=600)

    # Add sliders and dynamic sphere
    st.markdown("""
    <h3 style='text-align: center;'>Interactive Mixed Use Index Calculator</h3>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Adjust Values")
        numerator_val = st.slider("Numerator", 0, 100, 50, help="Adjust numerator value")
        denominator_val = st.slider("Denominator", 1, 100, 50, help="Adjust denominator value")  # Start from 1 to avoid division by zero
        
        # Calculate new mixed use index
        new_calculated_value = 1 - (numerator_val / denominator_val)
        st.markdown(f"### Resulting Index: {new_calculated_value:.2f}")

    with col2:
        # Create new HTML for dynamic sphere
        dynamic_sphere = f"""
        <html>
            <head>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
                <style>
                    .container {{ 
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        gap: 20px;
                    }}
                    #dynamic-model-container {{ 
                        width: 100%; 
                        height: 200px; 
                    }}
                    #dynamic-legend {{
                        width: 30px;
                        height: 200px;
                        background: linear-gradient(to top, #ff0000, #00ff00);
                        border: 1px solid #333;
                        margin-left: 10px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div id="dynamic-model-container"></div>
                    <div id="dynamic-legend"></div>
                </div>
                <script>
                    const container = document.getElementById('dynamic-model-container');
                    const scene = new THREE.Scene();
                    const camera = new THREE.PerspectiveCamera(75, container.clientWidth/container.clientHeight, 0.1, 1000);
                    const renderer = new THREE.WebGLRenderer({{ antialias: true }});
                    
                    renderer.setSize(container.clientWidth, container.clientHeight);
                    renderer.setClearColor(0xeeeeee);
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
                            vec3 color = mix(bottomColor, topColor, y * {new_calculated_value});
                            gl_FragColor = vec4(color, 1.0);
                        }}
                    `;

                    const geometry = new THREE.SphereGeometry(2, 32, 32);
                    const material = new THREE.ShaderMaterial({{
                        uniforms: {{
                            value: {{ value: {new_calculated_value} }}
                        }},
                        vertexShader: vertexShader,
                        fragmentShader: fragmentShader
                    }});
                    
                    const sphere = new THREE.Mesh(geometry, material);
                    sphere.rotation.x = Math.PI * 0.2;
                    scene.add(sphere);

                    camera.position.z = 5;

                    function animate() {{
                        requestAnimationFrame(animate);
                        renderer.render(scene, camera);
                    }}
                    animate();
                </script>
            </body>
        </html>
        """
        st.components.v1.html(dynamic_sphere, height=250)





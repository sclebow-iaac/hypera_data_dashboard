import streamlit as st
import pandas as pd
import plotly.express as px
from pythreejs import *
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token

# 1. Imports and Setup
import data_extraction.facade_extractor as facade_extractor  # Only import the extractor module
import pandas as pd
import plotly.express as px

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
                    margin: 0 auto;
                }}
                #{container_id} {{ 
                    width: 75%;
                    height: 100%;
                    position: relative;
                    margin-left: auto;
                    margin-right: auto;
                }}
                #legend-container {{
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    height: 100%;
                    padding: 20px 0;
                    width: 60px;
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
                
                const camera = new THREE.PerspectiveCamera(60, container.clientWidth/container.clientHeight, 0.1, 1000);
                camera.position.z = 6;
                
                const renderer = new THREE.WebGLRenderer({{ 
                    antialias: true,
                    alpha: true
                }});
                
                renderer.setSize(container.clientWidth, container.clientHeight);
                renderer.setClearColor(0xeeeeee, 0.9);
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
                    varying vec3 vPosition;
                    void main() {{
                        float y = (vPosition.y + 2.0) / 4.0;
                        vec3 bottomColor = vec3(1.0, 0.0, 0.0);
                        vec3 topColor = vec3(0.0, 1.0, 0.0);
                        vec3 color = mix(bottomColor, topColor, y * {value});
                        gl_FragColor = vec4(color, 1.0);
                    }}
                `;

                const geometry = new THREE.SphereGeometry(2, 32, 32);
                const material = new THREE.ShaderMaterial({{
                    vertexShader: vertexShader,
                    fragmentShader: fragmentShader
                }});
                
                const sphere = new THREE.Mesh(geometry, material);
                sphere.rotation.x = Math.PI * 0.2;
                scene.add(sphere);

                function animate() {{
                    requestAnimationFrame(animate);
                    renderer.render(scene, camera);
                }}
                animate();
            </script>
        </body>
    </html>
    """

def calculate_energy_ratio(energy_generation, energy_required_by_industrial_team):
    return energy_generation / energy_required_by_industrial_team

def calculate_metrics(energy_generation, energy_required_by_industrial_team, ):
    # Energy calculations
    # Inputs
    energy_generation = 1500
    energy_required_by_industrial_team = 1000
    # Output
    energy_ratio = calculate_energy_ratio(energy_generation, energy_required_by_industrial_team)

def run(selected_team: str) -> None:
    
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
    
    # 3. Dashboard Header
    st.markdown("""
        <div style="text-align: center;">
            <h1>Facade Dashboard</h1>
        </div>
    """, unsafe_allow_html=True)

    energy_generation = 1500
    energy_required_by_industrial_team = 1000

    energy_ratio = calculate_energy_ratio(energy_generation, energy_required_by_industrial_team)

    # Display metrics in columns
    metric_col1, metric_col2 = st.columns(2)

    # Metric 1: Daylight Factor
    with metric_col1:
        st.metric(
            label="Primary Daylight Factor",
            value=f"{0.75:.2f}",
            help="Combined daylight factor for residential and work spaces"
        )

        # Daylight calculations
        weight_residential = 0.5
        weight_work = 0.5
        residential_area_with_daylight = 100
        total_residential_area = 200
        work_area_with_daylight = 150
        total_work_area = 300

        normalized_daylight = (
            weight_residential * (residential_area_with_daylight / total_residential_area) +
            weight_work * (work_area_with_daylight / total_work_area) * (10 / 7)
        )

    # Metric 2: Energy Generation Ratio
    with metric_col2:
        st.metric(
            label="Energy Generation Ratio",
            value=f"{energy_ratio:.2f}",
            help="Ratio of energy generation to industrial team requirements"
        )


    # Create tabs for detailed analysis
    tab1, tab2 = st.tabs([
        "Daylight Factor Analysis",
        "Energy Generation Analysis"
    ])

    with tab1:
        st.markdown("<h3>Primary Daylight Factor and Solar Loads Control</h3>", unsafe_allow_html=True)
        
        # First show metrics in two columns
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            #### Residential Spaces
            - Area with Daylight: {} m²
            - Total Area: {} m²
            - Weight: {}
            """.format(residential_area_with_daylight, total_residential_area, weight_residential))
            
        with col2:
            st.markdown("""
            #### Work Spaces
            - Area with Daylight: {} m²
            - Total Area: {} m²
            - Weight: {}
            """.format(work_area_with_daylight, total_work_area, weight_work))
        
        # Show daylight sphere visualization
        st.markdown("---")
        st.components.v1.html(
            create_sphere_visualization("daylight-sphere", normalized_daylight, "Daylight Factor"),
            height=400
        )

    with tab2:
        st.markdown("<h3>Energy Generation vs Industrial Requirements</h3>", unsafe_allow_html=True)
        
        # First show metrics in two columns
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            #### Energy Generation
            - Total Generation: {} kWh
            - Ratio: {:.2f}
            """.format(energy_generation, energy_ratio))
            
        with col2:
            st.markdown("""
            #### Energy Requirements
            - Industrial Team Needs: {} kWh
            """.format(energy_required_by_industrial_team))
        
        # Show energy sphere visualization
        st.markdown("---")
        st.components.v1.html(
            create_sphere_visualization("energy-sphere", energy_ratio, "Energy Generation Ratio"),
            height=400
        )

    # Interactive Calculator Section
    st.markdown("---")
    st.markdown("""
    <h3 style='text-align: center;'>Interactive Calculator</h3>
    """, unsafe_allow_html=True)

    calc_tab1, calc_tab2 = st.tabs(["Daylight Calculator", "Energy Calculator"])

    with calc_tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Adjust Daylight Values")
            numerator_val = st.slider("Daylit Floor Area (m²)", 0, 2000, residential_area_with_daylight)
            denominator_val = st.slider("Total Floor Area (m²)", 1, 2000, total_residential_area)
            new_daylight_value = numerator_val / denominator_val
            st.markdown(f"### Resulting Ratio: {new_daylight_value:.2f}")
        with col2:
            st.components.v1.html(
                create_sphere_visualization("dynamic-daylight", new_daylight_value, "Daylight Ratio", height=200),
                height=250
            )

    with calc_tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Adjust Energy Values")
            new_generation = st.slider("Energy Generation (kWh)", 0, 3000, energy_generation)
            new_required = st.slider("Energy Required (kWh)", 1, 2000, energy_required_by_industrial_team)
            new_energy_ratio = new_generation / new_required
            st.markdown(f"### Resulting Ratio: {new_energy_ratio:.2f}")
        with col2:
            st.components.v1.html(
                create_sphere_visualization("dynamic-energy", new_energy_ratio, "Energy Ratio", height=200),
                height=250
            )

    # Extract and display facade data
    facade_data = facade_extractor.extract(models, client, project_id)

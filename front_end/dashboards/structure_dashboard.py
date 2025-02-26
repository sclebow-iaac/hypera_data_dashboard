import streamlit as st
import pandas as pd
import plotly.express as px
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token

import data_extraction.structure_extractor as structure_extractor
import pandas as pd
import plotly.express as px

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

    # Initial values (using original variable names)
    total_column_free_floor_area = 800
    total_floor_area = 1000
    load_capacity = 800
    self_weight_of_structure = 500
    theoretical_minimum_material_usage = 800
    actual_material_usage = 500
    total_embodied_carbon_emissions = 800
    usable_floor_area = 1000

    # Header
    st.markdown("""
        <div style="text-align: center;">
            <h1>Structure Dashboard</h1>
        </div>
    """, unsafe_allow_html=True)

    # Metrics Display - Show all four metrics
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    metric_col1.metric("Floor Flexibility", "Column-Free FAR")
    metric_col2.metric("Load Capacity", "kg/m²")
    metric_col3.metric("Material Efficiency", "Ratio")
    metric_col4.metric("Embodied Carbon", "kg/m²")

    # Calculate all ratios
    column_free_floor_area_ratio = total_column_free_floor_area / total_floor_area if total_floor_area != 0 else 0
    load_capacity_per_square_meter = load_capacity / self_weight_of_structure if self_weight_of_structure != 0 else 0
    material_efficiency_ratio = theoretical_minimum_material_usage / actual_material_usage if actual_material_usage != 0 else 0
    embodied_carbon_emissions_per_square_meter = total_embodied_carbon_emissions / usable_floor_area if usable_floor_area != 0 else 0

    # Display all metrics with their visualizations
    st.markdown("""
    <h2 style='text-align: center;'>Structure Metrics Visualization</h2>
    """, unsafe_allow_html=True)

    # Create tabs for different metrics visualization
    viz_tab1, viz_tab2, viz_tab3, viz_tab4 = st.tabs([
        "Floor Flexibility",
        "Load Capacity",
        "Material Efficiency",
        "Embodied Carbon"
    ])

    with viz_tab1:
        st.markdown("<h2 style='text-align: center;'>Floor Flexibility: Column-Free FAR</h2>", unsafe_allow_html=True)
        st.markdown(r"""
            The formula for calculating the Column-Free Floor Area Ratio can be expressed as:
            
            $$ 
            \text{Column-Free Floor Area Ratio} = \frac{\text{Total Column-Free Floor Area (m²)}}{\text{Total Floor Area (m²)}}
            $$
        """, unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center;'>Calculated Value: {column_free_floor_area_ratio:.2f}</h3>", unsafe_allow_html=True)
        with st.container():
            st.components.v1.html(create_sphere_visualization("viz1", column_free_floor_area_ratio, "Column-Free FAR"), height=400)

    with viz_tab2:
        st.markdown("<h2 style='text-align: center;'>Structural Efficiency: Load Capacity per Square Meter</h2>", unsafe_allow_html=True)
        st.markdown(r"""
            The formula for calculating the Load Capacity per Square Meter can be expressed as:
            
            $$ 
            \text{Load Capacity per Square Meter (kg/m²)} = \frac{\text{Load Capacity (kg)}}{\text{Self Weight of Structure (kg)}}
            $$
        """, unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center;'>Calculated Value: {load_capacity_per_square_meter:.2f}</h3>", unsafe_allow_html=True)
        with st.container():
            st.components.v1.html(create_sphere_visualization("viz2", load_capacity_per_square_meter, "Load Capacity"), height=400)

    with viz_tab3:
        st.markdown("<h2 style='text-align: center;'>Structural Efficiency: Material Efficiency Ratio</h2>", unsafe_allow_html=True)
        st.markdown(r"""
            The formula for calculating the Material Efficiency Ratio can be expressed as:
            
            $$ 
            \text{Material Efficiency Ratio} = \frac{\text{Theoretical Minimum Material Usage (kg)}}{\text{Actual Material Usage (kg)}}
            $$
        """, unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center;'>Calculated Value: {material_efficiency_ratio:.2f}</h3>", unsafe_allow_html=True)
        with st.container():
            st.components.v1.html(create_sphere_visualization("viz3", material_efficiency_ratio, "Material Efficiency"), height=400)

    with viz_tab4:
        st.markdown("<h2 style='text-align: center;'>Structural Efficiency: Embodied Carbon Emissions per Square Meter</h2>", unsafe_allow_html=True)
        st.markdown(r"""
            The formula for calculating the Embodied Carbon Emissions per Square Meter can be expressed as:
            
            $$ 
            \text{Embodied Carbon Emissions per Square Meter (kg/m²)} = \frac{\text{Total Embodied Carbon Emissions (kg)}}{\text{Usable Floor Area (m²)}}
            $$
        """, unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center;'>Calculated Value: {embodied_carbon_emissions_per_square_meter:.2f}</h3>", unsafe_allow_html=True)
        with st.container():
            st.components.v1.html(create_sphere_visualization("viz4", embodied_carbon_emissions_per_square_meter, "Embodied Carbon"), height=400)

    # Interactive Calculator Section
    st.markdown("""
    <h2 style='text-align: center;'>Interactive Structure Calculators</h2>
    """, unsafe_allow_html=True)

    # Create tabs for different metrics
    calc_tab1, calc_tab2, calc_tab3, calc_tab4 = st.tabs([
        "Floor Flexibility",
        "Load Capacity",
        "Material Efficiency",
        "Embodied Carbon"
    ])

    with calc_tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Column-Free FAR Calculator")
            new_column_free_area = st.slider("Total Column-Free Floor Area (m²)", 0, 2000, total_column_free_floor_area)
            new_total_area = st.slider("Total Floor Area (m²)", 1, 2000, total_floor_area)
            new_ratio = new_column_free_area / new_total_area if new_total_area != 0 else 0
            st.markdown(f"### Resulting Ratio: {new_ratio:.2f}")
        with col2:
            st.components.v1.html(create_sphere_visualization("calc1", new_ratio, "Column-Free FAR", height=200), height=250)

    with calc_tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Load Capacity Calculator")
            new_load_capacity = st.slider("Load Capacity (kg)", 0, 2000, load_capacity)
            new_self_weight = st.slider("Self Weight of Structure (kg)", 1, 1000, self_weight_of_structure)
            new_load_ratio = new_load_capacity / new_self_weight if new_self_weight != 0 else 0
            st.markdown(f"### Resulting Ratio: {new_load_ratio:.2f}")
        with col2:
            st.components.v1.html(create_sphere_visualization("calc2", new_load_ratio, "Load Capacity", height=200), height=250)

    with calc_tab3:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Material Efficiency Calculator")
            new_theoretical = st.slider("Theoretical Minimum Material Usage (kg)", 0, 2000, theoretical_minimum_material_usage)
            new_actual = st.slider("Actual Material Usage (kg)", 1, 1000, actual_material_usage)
            new_material_ratio = new_theoretical / new_actual if new_actual != 0 else 0
            st.markdown(f"### Resulting Ratio: {new_material_ratio:.2f}")
        with col2:
            st.components.v1.html(create_sphere_visualization("calc3", new_material_ratio, "Material Efficiency", height=200), height=250)

    with calc_tab4:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Embodied Carbon Calculator")
            new_carbon = st.slider("Total Embodied Carbon Emissions (kg)", 0, 2000, total_embodied_carbon_emissions)
            new_floor_area = st.slider("Usable Floor Area (m²)", 1, 2000, usable_floor_area)
            new_carbon_ratio = new_carbon / new_floor_area if new_floor_area != 0 else 0
            st.markdown(f"### Resulting Ratio: {new_carbon_ratio:.2f}")
        with col2:
            st.components.v1.html(create_sphere_visualization("calc4", new_carbon_ratio, "Embodied Carbon", height=200), height=250)

    # Extract and display structure data
    structure_data = structure_extractor.extract(models, client, project_id)

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

                const geometry = new THREE.SphereGeometry(1.2, 32, 32);
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

                function onWindowResize() {{
                    const width = container.clientWidth;
                    const height = container.clientHeight;
                    camera.aspect = width / height;
                    camera.updateProjectionMatrix();
                    renderer.setSize(width, height, false);
                }}
                
                onWindowResize();

                function animate() {{
                    requestAnimationFrame(animate);
                    renderer.render(scene, camera);
                }}
                animate();
            </script>
        </body>
    </html>
    """

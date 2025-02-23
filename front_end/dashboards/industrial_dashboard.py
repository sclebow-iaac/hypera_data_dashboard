import streamlit as st
import pandas as pd
import plotly.express as px
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token

def run(selected_team: str) -> None:
    # 1. Imports and Setup
    import data_extraction.industrial_extractor as industrial_extractor
    import pandas as pd
    import plotly.express as px
    
    # 2. Speckle Connection (same as facade)
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
            <h1>Industrial Dashboard</h1>
        </div>
    """, unsafe_allow_html=True)

    # 4. Metrics Display - Updated with correct metrics
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    metric_col1.metric("Energy Self-Sufficiency", "0.75")
    metric_col2.metric("Food Self-Sufficiency", "0.60")
    metric_col3.metric("Water Recycling Rate", "0.80")
    metric_col4.metric("Waste Production", "120 kg/day")

    # 5. Calculate Primary Indices
    # Initial values for each metric
    EnergyGeneration = 750  # kWh
    EnergyDemand = 1000   # kWh
    EnergyRatio = EnergyGeneration / EnergyDemand

    FoodProduction = 600    # kg
    FoodDemand = 1000     # kg
    FoodRatio = FoodProduction / FoodDemand

    RecycledWater = 800   # m³
    WastewaterProduction = 1000     # m³
    RecylcedWaterRatio = RecycledWater / WastewaterProduction

    RecycledSolidWaste = 120   # kg/day
    SolidWasteProduction = 200        # kg/day
    WasteUtilizationRatio = 1 - (RecycledSolidWaste / SolidWasteProduction)  # Inverted so higher is better

    # 6. Display Formulas and Explanations
    st.markdown("""
    <h2 style='text-align: center;'>Industrial Sustainability Metrics</h2>
    """, unsafe_allow_html=True)

    # Energy Metric and Sphere
    metric_row1_col1, metric_row1_col2 = st.columns(2)
    with metric_row1_col1:
        st.markdown(r"""
            ### Energy Self-Sufficiency Ratio
            
            $$ 
            \frac{\text{Energy Produced}}{\text{Energy Needed}}
            $$
            
            Measures the building's ability to meet its own energy demands.
        """)
        if EnergyRatio is not None:
            st.markdown(f"<h4 style='text-align: center;'>Current Value: {EnergyRatio:.2f}</h4>", unsafe_allow_html=True)
    
    with metric_row1_col2:
        energy_sphere = create_sphere_visualization(
            "energy-sphere", 
            EnergyRatio, 
            "Energy Self-Sufficiency"
        )
        st.components.v1.html(energy_sphere, height=300)

    # Food Metric and Sphere
    metric_row2_col1, metric_row2_col2 = st.columns(2)
    with metric_row2_col1:
        st.markdown(r"""
            ### Food Self-Sufficiency Ratio
            
            $$ 
            \frac{\text{Food Produced}}{\text{Food Needed}}
            $$
            
            Indicates the proportion of food requirements met through internal production.
        """)
        if FoodRatio is not None:
            st.markdown(f"<h4 style='text-align: center;'>Current Value: {FoodRatio:.2f}</h4>", unsafe_allow_html=True)
    
    with metric_row2_col2:
        food_sphere = create_sphere_visualization(
            "food-sphere", 
            FoodRatio, 
            "Food Self-Sufficiency"
        )
        st.components.v1.html(food_sphere, height=300)

    # Water Metric and Sphere
    metric_row3_col1, metric_row3_col2 = st.columns(2)
    with metric_row3_col1:
        st.markdown(r"""
            ### Water Recycling Rate
            
            $$ 
            \frac{\text{Recycled Water}}{\text{Total Water Used}}
            $$
            
            Shows the efficiency of water recycling systems.
        """)
        if RecylcedWaterRatio is not None:
            st.markdown(f"<h4 style='text-align: center;'>Current Value: {RecylcedWaterRatio:.2f}</h4>", unsafe_allow_html=True)
    
    with metric_row3_col2:
        water_sphere = create_sphere_visualization(
            "water-sphere", 
            RecylcedWaterRatio, 
            "Water Recycling Rate"
        )
        st.components.v1.html(water_sphere, height=300)

    # Waste Metric and Sphere
    metric_row4_col1, metric_row4_col2 = st.columns(2)
    with metric_row4_col1:
        st.markdown(r"""
            ### Waste Production Efficiency
            
            $$ 
            1 - \frac{\text{Waste Produced}}{\text{Maximum Target}}
            $$
            
            Measures the efficiency of waste management relative to targets.
        """)
        if WasteUtilizationRatio is not None:
            st.markdown(f"<h4 style='text-align: center;'>Current Value: {WasteUtilizationRatio:.2f}</h4>", unsafe_allow_html=True)
    
    with metric_row4_col2:
        waste_sphere = create_sphere_visualization(
            "waste-sphere", 
            WasteUtilizationRatio, 
            "Waste Production Efficiency"
        )
        st.components.v1.html(waste_sphere, height=300)

    # Add a divider before the interactive calculators
    st.markdown("---")

    # 7. Interactive Calculators
    st.markdown("""
    <h3 style='text-align: center;'>Interactive Sustainability Calculators</h3>
    """, unsafe_allow_html=True)

    calc_row1_col1, calc_row1_col2 = st.columns(2)
    calc_row2_col1, calc_row2_col2 = st.columns(2)

    with calc_row1_col1:
        st.markdown("### Energy Self-Sufficiency Calculator")
        energy_produced = st.slider("Energy Produced (kWh)", 0, 2000, int(EnergyGeneration), help="Energy produced by building systems")
        energy_needed = st.slider("Energy Needed (kWh)", 1, 2000, int(EnergyDemand), help="Total energy required")
        
        new_energy_ratio = energy_produced / energy_needed
        st.markdown(f"### Energy Ratio: {new_energy_ratio:.2f}")

        # Create dynamic sphere for energy
        dynamic_energy_sphere = create_sphere_visualization(
            "dynamic-energy-sphere",
            new_energy_ratio,
            "Energy Self-Sufficiency",
            height=200
        )
        st.components.v1.html(dynamic_energy_sphere, height=250)

    with calc_row1_col2:
        st.markdown("### Food Self-Sufficiency Calculator")
        food_produced = st.slider("Food Produced (kg)", 0, 2000, int(FoodProduction), help="Food produced within building")
        food_needed = st.slider("Food Needed (kg)", 1, 2000, int(FoodDemand), help="Total food requirements")
        
        new_food_ratio = food_produced / food_needed
        st.markdown(f"### Food Ratio: {new_food_ratio:.2f}")

        # Create dynamic sphere for food
        dynamic_food_sphere = create_sphere_visualization(
            "dynamic-food-sphere",
            new_food_ratio,
            "Food Self-Sufficiency",
            height=200
        )
        st.components.v1.html(dynamic_food_sphere, height=250)

    with calc_row2_col1:
        st.markdown("### Water Recycling Calculator")
        recycled_water = st.slider("Recycled Water (m³)", 0, 2000, int(RecycledWater), help="Volume of water recycled")
        total_water = st.slider("Total Water Used (m³)", 1, 2000, int(WastewaterProduction), help="Total water consumption")
        
        new_water_ratio = recycled_water / total_water
        st.markdown(f"### Water Recycling Rate: {new_water_ratio:.2f}")

        # Create dynamic sphere for water
        dynamic_water_sphere = create_sphere_visualization(
            "dynamic-water-sphere",
            new_water_ratio,
            "Water Recycling Rate",
            height=200
        )
        st.components.v1.html(dynamic_water_sphere, height=250)

    with calc_row2_col2:
        st.markdown("### Waste Production Calculator")
        waste_produced = st.slider("Waste Produced (kg/day)", 0, 400, int(RecycledSolidWaste), help="Daily waste production")
        waste_target = st.slider("Maximum Target (kg/day)", 1, 400, int(SolidWasteProduction), help="Maximum acceptable waste")
        
        new_waste_ratio = 1 - (waste_produced / waste_target)
        st.markdown(f"### Waste Efficiency: {new_waste_ratio:.2f}")

        # Create dynamic sphere for waste
        dynamic_waste_sphere = create_sphere_visualization(
            "dynamic-waste-sphere",
            new_waste_ratio,
            "Waste Production Efficiency",
            height=200
        )
        st.components.v1.html(dynamic_waste_sphere, height=250)

    # Extract and display industrial data
    industrial_data = industrial_extractor.extract(models, client, project_id)

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


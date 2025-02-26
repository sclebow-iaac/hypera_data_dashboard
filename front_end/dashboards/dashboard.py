# This script holds general functions for all Team dashboards

import streamlit as st
import pandas as pd
import plotly.express as px
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token

import pandas as pd
import plotly.express as px

def setup_speckle_connection():
    speckle_server = "macad.speckle.xyz"
    speckle_token = "61c9dd1efb887a27eb3d52d0144f1e7a4a23f962d7"
    client = SpeckleClient(host=speckle_server)
    account = get_account_from_token(speckle_token, speckle_server)
    client.authenticate_with_account(account)
    
    project_id = '31f8cca4e0'
    project = client.project.get_with_models(project_id=project_id, models_limit=100)
    models = project.models.items

    return models, client, project_id

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

def display_metric(container, title: str, formula_markdown: str, description: str, value: float, add_text=True, add_sphere: bool = True):
    def metric_text_display(title, formula_markdown, description, value):
        st.markdown(f"### {title}")
        st.latex(formula_markdown)
        st.markdown(description)
        if value is not None:
            st.markdown(f"<h4 style='text-align: center;'>Current Value: {value:.2f}</h4>", unsafe_allow_html=True)

    def metric_sphere_display(title, value):
        sphere_html = create_sphere_visualization(
            f"{title.lower().replace(' ', '-')}-sphere", 
            value, 
            title
        )
        st.components.v1.html(sphere_html, height=300)
    if add_text and add_sphere:
        col1, col2 = container.columns(2)
        with col1:
            metric_text_display(title, formula_markdown, description, value)
        with col2:
            metric_sphere_display(title, value)
    elif add_text:
        metric_text_display(title, formula_markdown, description, value)
    elif add_sphere:
        metric_sphere_display(title, value)
    else:
        pass

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


import streamlit as st

# Create a iframe to display the selected version
def version2viewer(project, model, version, height=400) -> str:
    embed_src = f"https://macad.speckle.xyz/projects/{project.id}/models/{model.id}@{version.id}#embed=%7B%22isEnabled%22%3Atrue%2C%7D"
    # print(f'embed_src {embed_src}')  # Print the URL to verify correctness
    # print()
    return st.components.v1.iframe(src=embed_src, height=height)


def show_viewer(viewer, project, selected_model, selected_version):
    # --------------------------
    # create a definition that generates an iframe from commit id
    def commit2viewer(stream, commit, height=400) -> str:
        embed_src = f"https://macad.speckle.xyz/embed?stream={stream.id}&commit={commit.id}"
        # print(embed_src)  # Print the URL to verify correctness
        return st.components.v1.iframe(src=embed_src, height=height)

    # VIEWER👁‍🗨
    with viewer:
        st.subheader("Selected Version👇")
        version2viewer(project, selected_model, selected_version)

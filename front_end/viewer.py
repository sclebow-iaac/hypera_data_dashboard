def display_speckle_viewer(container, project_id, model_id, is_transparent=False, hide_controls=False, hide_selection_info=False, no_scroll=False, height=400, include_site=False, header_text='Representational Model'):
    container.markdown(f'#### {header_text}')

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

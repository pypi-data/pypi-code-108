
def GetClosingTag(raw_html: str, opening_tag: str):
    '''
    Get the belonging closing tag with the given opening tag
    '''
    
    opening_start_i = raw_html.find(opening_tag)
    opening_end_i = opening_start_i + len(opening_tag)

    # Get tag type (eg. 'div' or 'h1')
    tag_type = opening_tag.split(' ')[0].replace('<', '')

    # Cut the opening tag off the raw html
    raw_html = raw_html[opening_end_i:]
    # Get number of other similar opening tags
    num_tags = raw_html.count(f'<{tag_type}')

    # Loop through every other opening tag and find the related closing tag
    for _ in range(num_tags + 1):
        closing_start_i = raw_html.find(f'</{tag_type}')
        closest_opening_i = raw_html.find(f'<{tag_type}')

        if closest_opening_i > closing_start_i:
            break

        # Cut the everything off to this closing tag (including closing tag)
        raw_html = raw_html.replace(f'</{tag_type}>', '█'*len(f'</{tag_type}>'), 1)

    return closing_start_i + opening_end_i

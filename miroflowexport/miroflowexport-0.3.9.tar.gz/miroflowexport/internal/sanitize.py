import re

def strip_html(text):
    tag_re = re.compile(r'(<!--.*?-->|<[^>]*>)')
    no_tags = tag_re.sub('', text)
    ready = no_tags.replace("&#39;", "'")
    return ready
    
def trim_to_name(text):
    parts = text.split('</p><p>')
    return strip_html(parts[0])

def trim_to_effort(text):
    parts = text.split('</p><p>')
    if len(parts) < 2:
        return "n/a"
    part_effort = strip_html(parts[-1])
    try:
        effort_numerical = int(part_effort)
        return effort_numerical
    except:
        return part_effort
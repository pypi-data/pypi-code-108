from HTMLReader.Read import *
from HTMLReader.strUtils import *


class Element:
    def __init__(self, raw_tag: str, content: str):
        '''
        A HTML element converted into python class
        '''

        self.content = content

        # Get tag type (eg. 'div' or 'h1')
        self.type = raw_tag.split(' ')[0].replace('<', '')

        # Get prop fields (eg. 'src', 'class' or / and 'id')
        props_fields = RemoveBetweenChar(ReplaceMultStr(raw_tag, [f'<{self.type} ', '=', '>'], ''), ['"', "'"]).split()
        self.props = {}

        # Get props
        for field in props_fields:
            # Get start & end index of prop values
            prop_start_i = TryFind(raw_tag, [f"{field}='", f'{field}="'], 0)[0] + len(f'{field}="')
            prop_end_i = TryFind(raw_tag[prop_start_i:], ["'", '"'], 0)[0] + prop_start_i

            # Split all prop values into list
            self.props[field] = raw_tag[prop_start_i:prop_end_i].split()

    @staticmethod
    def Get(raw_html: str, identification: str):
        '''
        Get all elements with the given class
        '''
        
        elements = []

        while raw_html.count(identification) > 0:

            identification_i = raw_html.find(identification)

            # Calculate opening tag index & get opening tag content (eg. '<div id="sample-id" class="content">')
            opening_tag_start_i = FindIndexReverse(raw_html, '<', identification_i)
            opening_tag_end_i = raw_html[opening_tag_start_i:].find('>') + opening_tag_start_i + 1
            opening_tag_content = raw_html[opening_tag_start_i:opening_tag_end_i]

            # Get closing tag index with GetClosingTag() function
            closing_tag_i = GetClosingTag(raw_html, opening_tag_content)
            
            # Get the content between the opening and closing tag
            content = raw_html[opening_tag_end_i:closing_tag_i]
            
            # Return new HTML element object
            elements.append(Element(opening_tag_content, content))

            raw_html = raw_html.replace(identification, '█'*len(identification), 1)

        return elements
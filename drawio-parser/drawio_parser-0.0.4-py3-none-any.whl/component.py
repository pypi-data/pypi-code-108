from typing import Dict

class Component: 
    def __init__(self, id: str, attributes: Dict) -> None:
        self.id = id
        self.attributes = attributes
        self.__create_styles(attributes.get('style'))
        
    def __create_styles(self, style_list: str):
        self.styles = {}
        if not style_list == None:
            for style in style_list.split(";"):
                styles = style.replace('\n','').split('=')
                if '=' in style:
                    self.styles[styles[0]] = styles[1].replace('"', '')
                else:
                    self.styles['style'] = styles[0]
        
    def get_styles(self):
        return self.styles

    def get_value(self):
        return self.attributes.get('value')
    
    def get_id(self):
        return self.id

    def get_parent(self):
        return self.attributes.get('parent')
    
    def get_icon_id(self):
        return self.styles.get('cvc-icon-id')
    
    def get_archtercture_layer(self):
        return self.styles.get('cvc-archtecture-layer')

    def get_landscape_layer(self):
        return self.styles.get('cvc-landscape-layer')

    def get_technology(self):
        return self.styles.get('cvc-technology')

    def get_technology_framework(self):
        return self.styles.get('cvc-technology-framework')   

    def get_template_type(self):
        return self.styles.get('cvc-template-type')

    def get_template_name(self):
        return self.styles.get('cvc-template-name')

    def get_lib_version(self):
        return self.styles.get('cvc-lib-version')
    
    def get_component_status(self):
        return self.styles.get('cvc-component-status')
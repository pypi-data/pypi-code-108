import typing as T
import xml.etree.cElementTree as ET
from io import BytesIO


class Shipping:
    def __init__(self, country: str, service: str, price: str):
        self.country = country
        self.service = service
        self.price = price


class Product:
    def __init__(self, id: str, title: str, description: str, link: str, image_link: str, brand: str,
        condition: str, availability: str, price: str, google_product_category: str,
        inventory: int, shipping: dict, additional_image_link: str
    ):
        self.id = id
        self.title = title
        self.description = description
        self.link = link
        self.image_link = image_link
        self.brand = brand
        self.condition = condition
        self.availability = availability
        self.price = price
        self.google_product_category = google_product_category
        self.inventory = inventory
        self.shipping = shipping
        self.additional_image_link = additional_image_link


class Channel:
    def __init__(self, title: str, link: str, description: str, items: list):
        self.title = title
        self.link = link
        self.description = description
        self.items = items

    @property
    def __xml__(self):
        prefix = 'g'
        name_space = {
        f"xmlns:{prefix}":'http://base.google.com/ns/1.0',
        'version': '2.0'
        }

        root = ET.Element("rss", name_space)
        channel = ET.SubElement(root, "channel")
        
        ET.SubElement(channel, "title").text = self.title
        ET.SubElement(channel, "link").text = self.link
        ET.SubElement(channel, "description").text = self.description

        for item in self.items:
            item_element = ET.SubElement(channel, "item")
            for key, value in item.items():
                if key == 'shipping':
                    shipping = ET.SubElement(item_element, f"{prefix}:shipping")
                    for key_s, value_s in value.items():
                        ET.SubElement(shipping, f"{prefix}:{key_s}").text = value_s
                else:
                    ET.SubElement(item_element, f"{prefix}:{key}").text = value

        root = ET.ElementTree(root)
        f = BytesIO()
        root.write(f, encoding='utf-8', xml_declaration=True)
        xml_str = f.getvalue().decode('utf-8')
        # xml_str = ET.tostring(root, encoding='utf-8', xml_declaration=True).decode('utf-8')
        return xml_str

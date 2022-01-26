from typing import Union

from pandas import Series


class Device:
    def __init__(self,
                 api_level: Union[int, Series] = None,
                 base_os: Union[str, Series] = None,
                 brand: Union[str, Series] = None,
                 manufacturer: Union[str, Series] = None,
                 device: Union[str, Series] = None,
                 product: Union[str, Series] = None,
                 model: Union[str, Series] = None,
                 gnss_hardware_model_name: Union[str, Series] = None,
                 gnss_year_of_hardware: Union[int, Series] = None):
        """ Class representing Android device information

        Parameters
        ----------
        api_level
        base_os
        brand
        manufacturer
        device
        product
        model
        gnss_hardware_model_name
        gnss_year_of_hardware
        """
        if type(api_level) == Series:
            self.api_level = api_level[0] if len(api_level) > 0 else None
        else:
            self.api_level = api_level

        if type(base_os) == Series:
            self.base_os = base_os[0] if len(base_os) > 0 else None
        else:
            self.base_os = base_os

        if type(brand) == Series:
            self.brand = brand[0] if len(brand) > 0 else None
        else:
            self.brand = brand

        if type(manufacturer) == Series:
            self.manufacturer = manufacturer[0] if len(manufacturer) > 0 else None
        else:
            self.manufacturer = manufacturer

        if type(device) == Series:
            self.device = device[0] if len(device) > 0 else None
        else:
            self.device = device

        if type(product) == Series:
            self.product = product[0] if len(product) > 0 else None
        else:
            self.product = product

        if type(model) == Series:
            self.model = model[0] if len(model) > 0 else None
        else:
            self.model = model

        if type(gnss_hardware_model_name) == Series:
            self.gnss_hardware_model_name = gnss_hardware_model_name[0] if len(gnss_hardware_model_name) > 0 else None
        else:
            self.gnss_hardware_model_name = gnss_hardware_model_name

        if type(gnss_year_of_hardware) == Series:
            self.gnss_year_of_hardware = gnss_year_of_hardware[0] if len(gnss_year_of_hardware) > 0 else None
        else:
            self.gnss_year_of_hardware = gnss_year_of_hardware

    def __repr__(self):
        return "Brand: %s, Model: %s, Product: %s, Device: %s, Manufacturer: %s, Base OS: %s, API Level: %d, " \
               "GNSS Hardware Model Name: %s, GNSS Year of Hardware %d" \
               % (self.brand, self.model, self.product, self.device, self.manufacturer, self.base_os,
                  self.api_level if self.api_level else -1, self.gnss_hardware_model_name,
                  self.gnss_year_of_hardware if self.gnss_year_of_hardware else -1)

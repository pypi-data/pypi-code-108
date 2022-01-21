from .support import style_attributes



class DynamicRune:
    def __init__(self, selenium_rune, driver):
        self.selenium_rune = selenium_rune
        self.driver = driver
        self.text = selenium_rune.text
        self.innerHTML = selenium_rune.get_attribute('innerHTML')
        self.outerHTML = selenium_rune.get_attribute('outerHTML')
        self.get_attributes()
        self.get_styles()


    def __repr__(self):
        return f'Dynamic Rune: {self.outerHTML}'

    def __str__(self):
        return f'Dynamic Rune: {self.outerHTML}'

    def __getitem__(self, item_request):
        if item_request in self.attributes:
            return self.attributes[item_request]
        return None

    def __contains__(self, item_request):
        if item_request in self.attributes:
            return True
        elif item_request not in self.attributes:
            return False


    def select(self, css_selector):
        return DynamicRune(self.selenium_rune.find_element_by_css_selector(css_selector), self.driver)


    def selectAll(self, css_selector):
        return [DynamicRune(i, self.driver)for i in self.selenium_rune.find_elements_by_css_selector(css_selector)]

    def get_attributes(self):
        self.attributes = {}
        for attribute in self.selenium_rune.get_property('attributes'):
            self.attributes[attribute['nodeName']] = self.selenium_rune.get_attribute(attribute['nodeName'])

    def get_styles(self):
        properties = self.driver.execute_script('return window.getComputedStyle(arguments[0], null);', self.selenium_rune)
        self.styles = {}
        for attr in style_attributes:
            self.styles[attr] = self.selenium_rune.value_of_css_property(attr)


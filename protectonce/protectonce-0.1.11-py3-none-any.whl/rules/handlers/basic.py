
def set_property_to_instance(data):
    setattr(data['instance'], data['config']['property'], data['result'])

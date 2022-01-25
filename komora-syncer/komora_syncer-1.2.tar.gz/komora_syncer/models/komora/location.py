class Location():
    def __init__(self, name, description, roomPin, locations, parentId, id):
        self.name = name
        self.description = description
        self.roomPin = roomPin
        self.parentId = parentId
        self.id = id

        if locations:
            self.locations = []
            for location in locations:
                self.locations.append(Location(**location))
        else:
            self.locations = locations

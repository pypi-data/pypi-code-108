from typing import Optional

from cognite.air._admin_config import AdminAPI


class SpacesAPI(AdminAPI):
    _ENDPOINT = "/space"

    def create(self, id: str, name: str, description: str = ""):
        """Create a Space

        Args:
            id (str): An id given to the Space. Needs to be unique and will be part of the URL
            name (str): The name for a Space
            description (str): The description of the space (it will be stored
                but has no functionality in the Front End yet)

        Examples:
            >>> air_admin = AIRAdmin(client)
            >>> air_admin.spaces.create(id="my_space", name="My Space")
        """
        if not description:
            description = name
        payload = {"id": id, "name": name, "description": description, "groups": []}
        self._post(payload)

    def delete(self, id):
        """Not implemented yet. Please ask the AIR team which space to delete.
        Send an email to air-team@cognite.com with the following information: project, cluster, id of the space and
        whether it is staging or not.
        """
        print("Warning: not implemented yet.")
        print(
            """Send an email to air-team@cognite.com with
            the following information: project, cluster, id of the space and
            whether it is staging or not."""
        )
        pass

    def update(self, id, new_name: Optional[str], new_description: Optional[str]):
        """Not implemented yet. Please ask the AIR team which space to update.
        Send an email to air-team@cognite.com with the following information: project, cluster, id of the space and
        whether it is staging or not. Then also provide information what should be updated
        """
        print("Warning: not implemented yet.")
        print(
            """Send an email to air-team@cognite.com with
            the following information: project, cluster, id of the space and
            whether it is staging or not.
            Then also provide information what should be updated."""
        )
        pass

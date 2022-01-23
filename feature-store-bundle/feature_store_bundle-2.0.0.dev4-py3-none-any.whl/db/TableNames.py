# pylint: disable=too-many-instance-attributes
class TableNames:
    def __init__(
        self,
        db_name: str,
        features_table_name_template: str,
        features_path_template: str,
        rainbow_path_template: str,
        metadata_table_name_template: str,
        metadata_path_template: str,
        entity_targets_table_name_template: str,
        entity_target_map_table_name: str,
        targets_table_name: str,
        entity_targets_path_template: str,
        entity_target_map_path: str,
        targets_path: str,
    ):
        self.__db_name = db_name
        self.__features_table_name_template = features_table_name_template
        self.__features_path_template = features_path_template
        self.__rainbow_path_template = rainbow_path_template
        self.__metadata_table_name_template = metadata_table_name_template
        self.__metadata_path_template = metadata_path_template
        self.__entity_targets_table_name_template = entity_targets_table_name_template
        self.__entity_target_map_table_name = entity_target_map_table_name
        self.__targets_table_name = targets_table_name
        self.__entity_targets_path_template = entity_targets_path_template
        self.__entity_target_map_path = entity_target_map_path
        self.__targets_path = targets_path

    def get_db_name(self) -> str:
        return self.__db_name

    def get_features_table_name(self, entity_name) -> str:
        return self.__replace_placeholders(self.__features_table_name_template, entity_name)

    def get_features_full_table_name(self, entity_name: str) -> str:
        return f"{self.get_db_name()}.{self.get_features_table_name(entity_name)}"

    def get_features_path(self, entity_name: str) -> str:
        return self.__replace_placeholders(self.__features_path_template, entity_name)

    def get_metadata_table_name(self, entity_name: str) -> str:
        return self.__replace_placeholders(self.__metadata_table_name_template, entity_name)

    def get_metadata_full_table_name(self, entity_name: str) -> str:
        return f"{self.get_db_name()}.{self.get_metadata_table_name(entity_name)}"

    def get_metadata_path(self, entity_name: str) -> str:
        return self.__replace_placeholders(self.__metadata_path_template, entity_name)

    def get_rainbow_path(self, entity_name: str) -> str:
        return self.__replace_placeholders(self.__rainbow_path_template, entity_name)

    def get_entity_targets_table_name(self, entity_name: str) -> str:
        return self.__replace_placeholders(self.__entity_targets_table_name_template, entity_name)

    def get_entity_target_map_table_name(self) -> str:
        return self.__entity_target_map_table_name

    def get_targets_table_name(self) -> str:
        return self.__targets_table_name

    def get_entity_targets_full_table_name(self, entity_name: str) -> str:
        return f"{self.get_db_name()}.{self.get_entity_targets_table_name(entity_name)}"

    def get_entity_target_map_full_table_name(self) -> str:
        return f"{self.get_db_name()}.{self.get_entity_target_map_table_name()}"

    def get_targets_full_table_name(self) -> str:
        return f"{self.get_db_name()}.{self.get_targets_table_name()}"

    def get_entity_targets_path(self, entity_name: str) -> str:
        return self.__replace_placeholders(self.__entity_targets_path_template, entity_name)

    def get_entity_target_map_path(self) -> str:
        return self.__entity_target_map_path

    def get_targets_path(self) -> str:
        return self.__targets_path

    def __replace_placeholders(self, template: str, entity_name: str) -> str:
        return template.format(entity=entity_name)

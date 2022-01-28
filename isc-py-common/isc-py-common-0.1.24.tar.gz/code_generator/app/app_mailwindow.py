from code_generator.app.model import Model


class AppMainWindow(Model):
    identifier = 'AppMainWindow_ID'
    loadSchemas = False
    name = 'Главное окно.'
    logoSrc = None
    logoHeight = 0
    useExtUserEditor = False
    addedEditors = None
    customUserMenu = None
    messageDS = None
    managedUsersGroups = None
    template_name = 'ts/common/app.pmd'
    output_file_name = 'mainWindow.ts'
    code_type = 'ts'
    appImageDir = None

    def write_entity(self):
        super().write_entity()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.class_name = self.__class__.__name__
        if self.appImageDir is None:
            self.appImageDir = f'/static/{self.image_dir_name}/images/'

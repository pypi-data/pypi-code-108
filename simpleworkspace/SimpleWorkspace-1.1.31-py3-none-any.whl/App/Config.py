import os as os
import SimpleWorkspace as sw

class Config:
    appName = None
    appCompany = None
    appTitle = None
    appHash = None
    path_currentAppData = ""
    path_currentAppData_storage = None

    @staticmethod
    def Setup(appName, appCompany=None):
        Config.appName = appName
        Config.appCompany = appCompany
        Config.appTitle = appName
        if appCompany != None:
            Config.appTitle += " - " + appCompany
        Config.path_currentAppData = sw.Path.GetAppdataPath(appName, appCompany)
        Config.path_currentAppData_storage = os.path.join(Config.path_currentAppData, "storage")
        sw.Directory.Create(Config.path_currentAppData_storage)
        
        sw.App.Log._logPath = os.path.join(Config.path_currentAppData, "info.log")
        sw.App.SettingsManager._settingsPath = os.path.join(Config.path_currentAppData, "config.json")
        sw.App.SettingsManager.LoadSettings()

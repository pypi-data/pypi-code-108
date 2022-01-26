from SimpleWorkspace.ConsoleHelper import *
import os 
import json 
import SimpleWorkspace as sw

class SettingsManager:
    _settingsPath = None
    __Command_Delete = "#delete"
    Settings = {}

    @staticmethod
    def LoadSettings():
        SettingsManager.Settings = {}
        if not (os.path.exists(SettingsManager._settingsPath)):
            return
        if os.path.getsize(SettingsManager._settingsPath) == 0:
            return
        try:
            SettingsManager.Settings = json.loads(sw.File.Read(SettingsManager._settingsPath))
        except Exception as e:
            os.rename(SettingsManager._settingsPath, SettingsManager._settingsPath + ".bak")
        return SettingsManager.Settings

    @staticmethod
    def SaveSettings():
        jsonData = json.dumps(SettingsManager.Settings)
        sw.File.Create(SettingsManager._settingsPath, jsonData)

    @staticmethod
    def __ChangeSettings():
        while True:
            ClearConsoleWindow()
            LevelPrint(0, "[Change Settings]")
            LevelPrint(1, "0. Save Settings and go back.(Type cancel to discard changes)")
            LevelPrint(1, "1. Add a new setting")
            LevelPrint(2, "[Current Settings]")
            dictlist = []
            dictlist_start = 2
            dictlist_count = 2
            for key in SettingsManager.Settings:
                LevelPrint(3, str(dictlist_count) + ". " + key + " : " + SettingsManager.Settings[key])
                dictlist.append(key)
                dictlist_count += 1
            LevelPrint(1)
            choice = input("-Choice: ")
            if choice == "cancel":
                SettingsManager.LoadSettings()
                AnyKeyDialog("Discarded changes!")
                break
            if choice == "0":
                SettingsManager.SaveSettings()
                LevelPrint(1)
                AnyKeyDialog("Saved Settings!")
                break
            elif choice == "1":
                LevelPrint(1, "Setting Name:")
                keyChoice = LevelInput(1, "-")
                LevelPrint(1, "Setting Value")
                valueChoice = LevelInput(1, "-")
                SettingsManager.Settings[keyChoice] = valueChoice
            else:
                IntChoice = sw.Utility.StringToInteger(choice, min=dictlist_start, lessThan=dictlist_count)
                if IntChoice == None:
                    continue
                else:
                    key = dictlist[IntChoice - dictlist_start]
                    LevelPrint(2, '(Leave empty to cancel, or type "' + SettingsManager.__Command_Delete + '" to remove setting)')
                    LevelPrint(2, ">> " + SettingsManager.Settings[key])
                    choice = LevelInput(2, "Enter new value: ")
                    if choice == "":
                        continue
                    elif choice == SettingsManager.__Command_Delete:
                        del SettingsManager.Settings[key]
                    else:
                        SettingsManager.Settings[key] = choice
        return

    @staticmethod
    def Console_PrintSettingsMenu():
        while(True):
            ClearConsoleWindow()
            LevelPrint(0, "[Settings Menu]")
            LevelPrint(1, "1.Change settings")
            LevelPrint(1, "2.Reset settings")
            LevelPrint(1, "3.Open Settings Directory")
            LevelPrint(1, "0.Go back")
            LevelPrint(1)
            choice = input("-")
            if choice == "1":
                SettingsManager.__ChangeSettings()
            elif choice == "2":
                LevelPrint(1, "-Confirm Reset! (y/n)")
                LevelPrint(1)
                choice = input("-")
                if choice == "y":
                    SettingsManager.Settings = None
                    SettingsManager.SaveSettings()
                    LevelPrint(1)
                    AnyKeyDialog("*Settings resetted!")
            elif choice == "3":
                fileInfo = sw.File.FileInfo(SettingsManager._settingsPath)
                os.startfile(fileInfo.tail)
            else:
                break
        return

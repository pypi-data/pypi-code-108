CURRENT_VERSION = '1.1.2'

VIRTUAL_ENV_NAME = 'batch-virtualenv'

ALLOWED_REGIONS = [
    {
        "name": "MUM",
        "id": "21"
    },
    {
        "name": "US",
        "id": "11"
    },
    {
        "name": "SGP",
        "id": "1"
    }
]

API_BASE_URL = {
    "21": "https://batchjob-api-in21.leadsquared.com/api/developersdk",
    "11": "https://batchjob-api-us11.leadsquared.com/api/developersdk",
    "1": "https://batchjob-api.leadsquared.com/api/developersdk"
}

API_URLS = {
    "CreateBatch": "Create",
    "UploadZip": "UploadZip",
    "PublishBatch": "Publish",
    "AddVariables": "AddVariables"
}


class Constants:
    OrgCode = 'orgcode'
    Token = 'token'
    Region = 'region'
    Profile = 'profile'
    UnauthorizedAccess = 'UnauthorizedAccess'
    UnexpectedError = 'UnexpectedError'


class Messages:
    SelectTask = 'Which task? Values: (init/pack/run/save/publish/configure/install/uninstall/help):'
    StartUpFileNotPresent = 'startup.py file is not present in {0}'
    LatestVersionWarning = 'WARNING! new version of lsbatch is available, please upgrade using "pip install --upgrade lsbatch"'
    YourBatchName = 'Your Batch Job name:'
    InstallingDependencies = 'Installing dependencies....'
    RequirementSatisfied = 'Requirement already satisfied'
    LSBatchHelpSection = "To init a Batch Job: lsbatch init\n To pack a Batch Job: lsbatch pack\n To run a Batch Job: lsbatch run"
    RegionArgumentHelp = 'valid values for region are MUM,SGP,US,21,1,11'
    CreatingNewBatchJob = 'Creating a new Batch Job'
    BatchJobCreated = 'Batch Job Created'
    WantToProvideDescription = 'Do you want to provide description ? (y/n) : '
    ProvideDescription = 'Please provide description here:'
    UploadingBatchFile = 'Uploading batch file to Batch Job with id {0}'
    BatchFileUploaded = 'Batch file has been uploaded successfully.'
    UpdatingSettings = 'Updating settings'
    SettingsUpdated = 'Settings have been updated successfully'
    NoSettingsFound = 'No settings found'
    PublishingBatchJob = 'Publishing Batch Job'
    BatchJobPublished = 'Batch Job has been published successfully'
    ProfileAlreadyExists = 'Profile already exists with same name, Do you want to override it ? (y/n) : '
    ProfileAddedSuccessfully = 'Profile has been added successfully'


class ValidationMessages:
    LSBatchInstallArguments = 'lsbatch install can take 1 argument, python package name'
    LSBatchUninstallArguments = 'lsbatch uninstall takes 1 argument, python package name'
    LSBatchArguments = 'lsbatch takes 1 argument, (init/pack/run/save/publish/configure/install/uninstall/help)'
    VirtualEnvironmentNotFound = 'Can not find virtualenv, please install virtualenv, run "pip install virtualenv"'
    NotFoundSourceFolder = 'To install Batch Job dependencies current directory should have src folder which resides user code'
    MainFileNotPresent = 'main.py file is not present in {0}'
    MainFunctionNotPresent = 'main function is not present in {0}'
    CanNotUninstallDefaultPackage = 'Can not uninstall this package, this package is a part of default packages'
    ProfileNameEmpty = 'Profile name can not be empty'
    ProfileNameNotFound = 'Profile with given name does not exists'
    ArgumentsNotPassedCorrectly = 'Arguments not passed correctly, either pass profile name as --profile {profile_name} or pass all credentials as --orgcode {orgcode} --token {token} --region {region}'
    BatchDetailsNotInFormat = "'batch_details.json' file is not in a correct format, it should be a proper json"
    LengthOfDescription = 'Length of Description should not exceed 1000 characters'
    LengthOfJobName = 'Name should be minimum of 3 characters up to 100 characters'
    NameShouldNotHaveSpecialCharacters = 'Name should not start with any special character, allowed special characters are undescore(_) and hyphen(-)'
    SettingsFileNotInFormat = "'settings.json' file is not in a correct format, it should be a proper json"
    IdNotFoundWhilePublishing = "Either 'batch_details.json' file is not present in the current directory or Id is not present in the file"
    InvalidCredentials = 'Either invalid value for {0} or {0} is not provided'
    InvalidValueOfRegion = 'Invalid value provided for region, valid values for region are MUM,SGP,US,21,1,11'
    UnAuthorizedAccess = 'User is not authorized to perform this action.'
    SomethingWentWrong = 'Something went wrong'

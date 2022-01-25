# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.


import re
import json
from xml.dom import minidom
from hashlib import sha256


# This list is up-to-date as of 2022 January 20.
# Contact aims-team@microsoft.com if your eyes-on subscription is not included.
EYES_ON_SUBSCRIPTIONS = set(
    [
        "dfcaf96e30a340fae2fcd5871a5e94cf3805f6521d5e2571d55b097df857c9c3",
        "89b8bdaf7904e676c93e24be918b83c64fe904a4097821e3def68c0c33d1599b",
        "71adef91aa2cb4676d995e8b3843dfe75d65e200dd8b552e0c7f5195c043f946",
        "2585e2381d1a9a413392c6c5372ca0bafdb845de17f0bfb5536d340401dee699",
        "7f6d1d5c3d3f46b0459bbb041e6ebebcfceff2e202aa02cb23301761e51b9c0b",
        "d675de4926b9534967be30a8cb035cb3d14b2d02b00ca3077d451a48910841ac",
        "84631d56ce357894baa249912456077e15f899c16639cdaef8c531013990db87",
        "566032778897f87065c0fab68a33e8b184e23a007d392f5a71dbb5f46bf2c460",
        "7141d27136d73133d699a94ebb36d29b524767949c07ba175d265420792b8448",
        "544181f90401adb3bfe691467fdd8dfd37b2eb689b15bcc8585adc6bb81df5d0",
        "0e977328631074f17aedfeec10ed487ff71231501357b5eb8b9c454a5604adf0",
        "8776711f970cd8aa00047879e5bee9ba9a0a9a0890241cb5ebd94a7173563bad",
        "770f1203c522f031dde28fab282ee3fbdeb62afa05d3792610254e97171828c5",
        "887f1c5c3f867712fb0cd743e67325643e95a4c29954bce9ebef08922749daf1",
        "d3259042d8e1f4f5b44ac56c9ca150955cd6a48d22180cf15f37133b850f784e",
        "d194e7433fdc4e28c33fd17cdb42db67fd84d0728f9471ad106b8c4f08fa78ff",
        "196c596ac5e78ff19b6216eeb4faf8d3b5c9379c88061a64bbfd6da91315ffa7",
        "e93b407a7a2b559f2cd8ea67d9a1bffbbbca1f616bd47347aea299a993bb4120",
        "897107fb585b318ffa494339fd6bd5c38e96548c90c8809d8522c6e71b471cad",
        "9fe3e3bd8dfdcd3e707c6840161d625460703d8e1e779b8b0e4965f7b1d17d6c",
        "74dea0d792de7adb561775eb00898ee41801f467825ce0942607461bcac4419c",
    ]
)
EYES_OFF_TENANT_ID = "cdc5aeea-15c5-4db6-b079-fcadd2505dc2"


def get_hashed_eyes_on_subs():
    """
    This method is used to generated EYES_ON_SUBSCRIPTIONS.
    """
    with open("torus_subscription.json", "r") as f:
        # get torus_subscription.json from https://resources.azure.com/subscriptions with torus account  # noqa: E501
        all_info = json.load(f)
    all_sub = []
    for i in all_info["value"]:
        all_sub.append(i["subscriptionId"].lower())

    # get heron.xml from "MOP" the following two (usually PPE MOP sandboxes from #2 is missing) # noqa: E501
    # https://o365exchange.visualstudio.com/DefaultCollection/O365%20Core/_git/MARS?path=/sources/dev/mars/src/O365AIService/EuclidAIWorkerService/ServiceConfiguration.WorkerRole.PROD.cscfg&version=GBmaster&_a=contents  # noqa: E501
    # and https://eng.ms/docs/experiences-devices/m365-core/microsoft-search-assistants-intelligence-msai/substrate-intelligence/ai-training-heron/documentation/environment-settings   # noqa: E501
    heron_list = minidom.parse("heron.xml").getElementsByTagName(
        "Setting"
    )  # list of eyes-off subs
    eyes_off_sub = []
    for entry in heron_list:
        sub = entry.attributes["value"].value.lower()
        match = re.findall(r"([a-z0-9]{8}-([a-z0-9]{4}-){3}[a-z0-9]{12})", sub)
        if match:
            for i in match:
                eyes_off_sub.append(i[0])
    print(eyes_off_sub)
    eyes_on_sub = []
    for i in all_sub:
        if i not in eyes_off_sub:
            eyes_on_sub.append(sha256(i.encode()).hexdigest())

    return eyes_on_sub


def is_eyesoff_helper(tenant_id, subscription_id):
    if tenant_id != EYES_OFF_TENANT_ID:
        return False
    else:
        hashed_subscription_id = sha256(subscription_id.encode()).hexdigest()
        return hashed_subscription_id not in EYES_ON_SUBSCRIPTIONS

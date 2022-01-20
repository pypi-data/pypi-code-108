class AWSDefaults:
    """Default values for missing AWS configuration.

    >>> AWSDefaults

    """

    DEFAULT_AMI_NAME = 'aerospike-ubuntu-20.04-20211114101915'

    IMAGE_MAP = {
        "us-east-2": "ami-0971e839208a0d58a",
        "us-east-1": "ami-0eaca42ad8ff8647d",
        "us-west-1": "ami-0005fe7be6ce06e3c",
        "us-west-2": "ami-06e20d17437157772"
    }

    REGIONS = {
        "us-east-2": "US East (Ohio)",
        "us-east-1": "US East (N. Virginia)",
        "us-west-1": "US West (N. California)",
        "us-west-2": "US West (Oregon)",
        "af-south-1": "Africa (Cape Town)",
        "ap-east-1": "Asia Pacific (Hong Kong)",
        "ap-south-1": "Asia Pacific (Mumbai)",
        "ap-northeast-3": "Asia Pacific (Osaka)",
        "ap-northeast-2": "Asia Pacific (Seoul)",
        "ap-southeast-1": "Asia Pacific (Singapore)",
        "ap-southeast-2": "Asia Pacific (Sydney)",
        "ap-northeast-1": "Asia Pacific (Tokyo)",
        "ca-central-1": "Canada (Central)",
        "cn-north-1": "China (Beijing)",
        "cn-northwest-1": "China (Ningxia)",
        "eu-central-1": "Europe (Frankfurt)",
        "eu-west-1": "Europe (Ireland)",
        "eu-west-2": "Europe (London)",
        "eu-west-3": "Europe (Paris)",
        "eu-north-1": "Europe (Stockholm)",
        "eu-south-1": "Europe (Milan)",
        "me-south-1": "Middle East (Bahrain)",
        "sa-east-1": "South America (São Paulo)"
    }

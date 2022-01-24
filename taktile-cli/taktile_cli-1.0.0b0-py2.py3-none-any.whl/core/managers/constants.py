from tktl.core.t import TemplateT

TEMPLATE_PROJECT_DIRS = [
    "src/",
    "assets/",
    "tests/",
]

TEMPLATE_PROJECT_FILES = {
    TemplateT.REPAYMENT: [
        "src/endpoints.py",
        "assets/model.joblib",
        "assets/loans_test.pqt",
        "tests/test_accuracy.py",
        "tests/test_plausibility.py",
        "tests/test_schema.py",
        ".gitignore",
        ".gitattributes",
        ".buildfile",
        ".dockerignore",
        "README.md",
        "requirements.txt",
    ],
    TemplateT.BARE: [
        "src/endpoints.py",
        ".gitignore",
        ".gitattributes",
        ".buildfile",
        ".dockerignore",
        "README.md",
        "requirements.txt",
        "assets/.gitkeep",
    ],
    TemplateT.PRECOMPUTED: [
        "src/endpoints.py",
        "assets/model.joblib",
        "assets/loans_test_X.pqt",
        "assets/loans_test_y.pqt",
        "tests/test_accuracy.py",
        "tests/test_plausibility.py",
        "tests/test_schema.py",
        ".gitignore",
        ".gitattributes",
        ".buildfile",
        ".dockerignore",
        "README.md",
        "requirements.txt",
    ],
}


CONFIG_FILE_TEMPLATE = """
# See the full documentation at https://docs.taktile.com/configuring-taktile/deployment-configuration

# If this option is set only commits with a commit message starting
# with the deployment_prefix will be deployed
# deployment_prefix: "#deploy"

# If this option is set commits with a commit message starting
# with the undeployment_prefix will cause an existing Taktile
# deployment to no longer be deployed
# undeployment_prefix: "#undeploy"

service:

  # Rest deployment scaling parameters
  rest:
    # requests determine the size of each replica. CPU should be specified as 'XXXm', where XXX is
    # thousandths of a core, up to 1000. Memory can be specified in base 2 units (Mi or Gi)
    requests:
      cpu: 500m
      memory: 512Mi
    # Maximum and minimum number of replicas to which the REST service is allowed to reach
    # by the auto-scaler
    max_replicas: 1
    # Minimum, or starting number of replicas
    replicas: 1

  # Arrow deployment scaling parameters
  arrow:
    requests:
      cpu: 500m
      memory: 512Mi
    # Arrow replicas are fixed and don't autoscale
    replicas: 1

version: {version}
"""

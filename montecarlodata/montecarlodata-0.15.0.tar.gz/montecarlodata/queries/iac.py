CREATE_OR_UPDATE_MONTE_CARLO_CONFIG_TEMPLATE = """
mutation createOrUpdateMonteCarloConfigTemplate($namespace: String!, $configTemplateJson: String!, $dryRun: Boolean, $resource: String) {
  createOrUpdateMonteCarloConfigTemplate(
    configTemplateJson: $configTemplateJson,
    namespace: $namespace,
    dryRun: $dryRun,
    resource: $resource            
  ) {
    response {
      resourceModifications {
        type
        description
        resourceAsJson
      }
      changesApplied
      errorsAsJson
    }
  }
}
"""

DELETE_MONTE_CARLO_CONFIG_TEMPLATE = """
mutation deleteMonteCarloConfigTemplate($namespace: String!, $dryRun: Boolean) {
  deleteMonteCarloConfigTemplate(
    namespace: $namespace,
    dryRun: $dryRun
  ) {
    response {
      changesApplied
      numDeleted
    }
  }
}
"""

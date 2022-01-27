# Queries related to users

GET_USER_QUERY = """
query getUser {
  getUser {
    firstName
    lastName
    account {
      uuid
      activeCollectionRegions
      warehouses {
        uuid
        name
        connectionType
        connections {
          uuid
          type
          createdOn
          jobTypes
        }
        dataCollector {
          uuid
          customerAwsRegion
        }
      }
      bi {
        uuid
        connections {
          uuid
          type
          createdOn
          jobTypes
        }
        dataCollector {
          uuid,
          customerAwsRegion
        }
      }
      tableauAccounts {
        uuid
        dataCollector {
          uuid,
          customerAwsRegion
        }
      }
      dataCollectors {
        uuid
        stackArn
        active
        customerAwsAccountId
        templateVersion
        lastUpdated
      }
    }
  }
}
"""

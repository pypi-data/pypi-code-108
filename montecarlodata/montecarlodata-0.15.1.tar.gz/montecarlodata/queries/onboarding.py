# Queries related to onboarding

TEST_PRESTO_CRED_MUTATION = """
mutation testPrestoCredentials($catalog:String, $host:String, $httpScheme:String, $password:String, $port:Int, $schema:String, $sslOptions:SslInputOptions, $user:String, $connectionOptions:ConnectionTestOptions) {
  testPrestoCredentials(catalog:$catalog, host:$host, httpScheme:$httpScheme, password:$password, port:$port, schema:$schema, sslOptions: $sslOptions, user:$user, connectionOptions:$connectionOptions) {
    key
  }
}
"""

TEST_S3_CRED_MUTATION = """
mutation tests3Credentials($bucket:String, $prefix:String, $assumableRole:String, $externalId:String, $connectionType:String, $connectionOptions:ConnectionTestOptions) {
  testS3Credentials(bucket:$bucket, prefix:$prefix, assumableRole:$assumableRole, externalId:$externalId, connectionType:$connectionType, connectionOptions:$connectionOptions) {
    key
  }
}
"""

TEST_DATABASE_CRED_MUTATION = """
mutation testDatabaseCredentials($assumableRole:String, $connectionType:String, $dbName:String, $externalId:String, $host:String, $password:String, $port:Int, $sslOptions:SslInputOptions, $user:String, $connectionOptions:ConnectionTestOptions) {
  testDatabaseCredentials(assumableRole:$assumableRole, connectionType:$connectionType, dbName:$dbName, externalId:$externalId, host:$host, password:$password, port:$port, sslOptions:$sslOptions, user:$user, connectionOptions:$connectionOptions) {
    key
  }
}
"""

TEST_HIVE_SQL_CRED_MUTATION = """
mutation testHiveCredentials($database:String, $host:String, $port:Int, $username:String, $authMode:String, $connectionOptions:ConnectionTestOptions) {
  testHiveCredentials(database:$database, host:$host, port:$port, username:$username, authMode:$authMode, connectionOptions:$connectionOptions) {
    key
  }
}
"""

TEST_GLUE_CRED_MUTATION = """
mutation testGlueCredentials($assumableRole:String, $externalId:String, $awsRegion:String, $connectionOptions:ConnectionTestOptions) {
  testGlueCredentials(assumableRole:$assumableRole, externalId:$externalId, awsRegion:$awsRegion, connectionOptions:$connectionOptions) {
    success
    key,
    validations {
      type,
      message,
      data {
        error
      }
    },
    warnings {
      type,
      message,
      data {
        error
      }
    }
  }
}
"""

TEST_ATHENA_CRED_MUTATION = """
mutation testAthenaCredentials($assumableRole:String, $catalog:String, $externalId:String, $workgroup:String, $awsRegion:String, $connectionOptions:ConnectionTestOptions) {
  testAthenaCredentials(assumableRole:$assumableRole, catalog:$catalog, externalId:$externalId, workgroup:$workgroup, awsRegion:$awsRegion, connectionOptions:$connectionOptions) {
    success
    key,
    validations {
      type,
      message,
      data {
        error
      }
    },
    warnings {
      type,
      message,
      data  {
        error
      }
    }
  }
}
"""

TEST_SPARK_BINARY_MODE_CRED_MUTATION = """
mutation testSparkCredentials($database:String!, $host:String!, $port:Int!, $username:String!, $password:String!, $connectionOptions:ConnectionTestOptions) {
  testSparkCredentials(binaryMode: {database:$database, host:$host, port:$port, username:$username, password:$password}, connectionOptions:$connectionOptions) {
    key
  }
}
"""

TEST_SPARK_HTTP_MODE_CRED_MUTATION = """
mutation testSparkCredentials($url:String!, $username:String!, $password:String!, $connectionOptions:ConnectionTestOptions) {
  testSparkCredentials(httpMode: {url:$url, username:$username, password:$password}, connectionOptions:$connectionOptions) {
    key
  }
}
"""

TEST_SPARK_DATABRICKS_CRED_MUTATION = """
mutation testSparkCredentials($workspaceUrl:String!, $workspaceId:String!, $clusterId:String!, $token:String!, $connectionOptions:ConnectionTestOptions) {
  testSparkCredentials(databricks: {workspaceUrl:$workspaceUrl, workspaceId:$workspaceId, clusterId:$clusterId, token:$token}, connectionOptions:$connectionOptions) {
    key
  }
}
"""

TEST_SNOWFLAKE_CRED_MUTATION = """
mutation testSnowflakeCredentials($account:String, $password:String, $user:String, $warehouse:String, $connectionOptions:ConnectionTestOptions) {
  testSnowflakeCredentials(account:$account, password:$password, user:$user, warehouse:$warehouse, connectionOptions:$connectionOptions) {
    key
  }
}
"""

TEST_BQ_CRED_MUTATION = """
mutation testBqCredentials($serviceJson:String, $connectionOptions:ConnectionTestOptions) {
  testBqCredentials(serviceJson:$serviceJson, connectionOptions:$connectionOptions) {
    key
  }
}
"""

TEST_SELF_HOSTED_CRED_MUTATION = """
mutation testSelfHostedCredentials($connectionType:String, $selfHostingMechanism:String, $selfHostingKey:String, $assumableRole:String, $externalId:String, $region:String, $connectionOptions:ConnectionTestOptions) {
  testSelfHostedCredentials(connectionType:$connectionType, selfHostingMechanism:$selfHostingMechanism, selfHostingKey:$selfHostingKey, assumableRole:$assumableRole, externalId:$externalId, region:$region, connectionOptions:$connectionOptions) {
    key
  }
}
"""

TOGGLE_EVENT_MUTATION = """
mutation toggleEventConfig($dwId:UUID!, $enable:Boolean!, $connectionType:String!, $eventType:DataCollectorEventTypes!, $assumableRole:String, $externalId:String, $formatType:String, $sourceFormat:String, $mapping:JSONString) {
  toggleEventConfig(dwId:$dwId, enable:$enable, connectionType:$connectionType, eventType: $eventType, assumableRole:$assumableRole, externalId:$externalId, formatType:$formatType, sourceFormat:$sourceFormat, mapping:$mapping){
    success
  }
}
"""

ADD_CONNECTION_MUTATION = """
mutation addConnection($connectionType:String!, $createWarehouseType:String, $dwId:UUID, $jobTypes:[String], $key:String!, $jobLimits:JSONString, $name:String, $dcId:UUID) {
  addConnection(connectionType:$connectionType, createWarehouseType:$createWarehouseType, dwId:$dwId, jobTypes:$jobTypes, key:$key, jobLimits:$jobLimits, name:$name, dcId: $dcId){
    connection {
      uuid
    }
  }
}
"""

UPDATE_CREDENTIALS_MUTATION = """
mutation updateCredentials($connectionId: UUID!, $changes:JSONString!, $shouldValidate:Boolean, $shouldReplace:Boolean) {
  updateCredentials(connectionId:$connectionId, changes:$changes, shouldValidate:$shouldValidate, shouldReplace:$shouldReplace){
    success
  }
}
"""

REMOVE_CONNECTION_MUTATION = """
mutation removeConnection($connectionId: UUID!) {
  removeConnection(connectionId:$connectionId) {
    success
  }
}
"""

TEST_EXISTING_CONNECTION_QUERY = """
query testExistingConnection($connectionId:UUID) {
  testExistingConnection(connectionId:$connectionId) {
    success
    validations {
      type
      message
      data {
        database
        table
        error
      }
    }
    warnings {
      type
      message
      data {
        database
        table
        error
      }
    }
  }
}
"""

TEST_TABLEAU_CRED_MUTATION = """
mutation testTableauCredentials($connectionOptions:ConnectionTestOptions, $password:String, $serverName:String!, $siteName:String!, $tokenName:String, $tokenValue:String, $username:String, $verifySsl:Boolean) {
  testTableauCredentials(connectionOptions:$connectionOptions, password:$password, serverName:$serverName, siteName:$siteName, tokenName:$tokenName, tokenValue:$tokenValue, username:$username, verifySsl:$verifySsl) {
    success
  }
}

"""

ADD_TABLEAU_CONNECTION_MUTATION = """
mutation addTableauAccount($dcId:UUID, $password:String, $serverName:String!, $siteName:String!, $tokenName:String, $tokenValue:String, $username:String, $verifySsl:Boolean) {
  addTableauAccount(dcId:$dcId, password:$password, serverName:$serverName, siteName:$siteName, tokenName:$tokenName, tokenValue:$tokenValue, username:$username, verifySsl:$verifySsl) {
    tableauAccount {
      uuid
    }
  }
}
"""

TEST_LOOKER_METADATA_CRED_MUTATION = """
mutation testLookerCredentials($baseUrl:String, $clientId:String, $clientSecret:String, $connectionOptions:ConnectionTestOptions, $verifySsl:Boolean) {
  testLookerCredentials(baseUrl:$baseUrl, clientId:$clientId, clientSecret:$clientSecret, connectionOptions:$connectionOptions, verifySsl:$verifySsl) {
    key
    success
  }
}
"""

TEST_LOOKER_GIT_SSH_CRED_MUTATION = """
mutation testLookerGitSshCredentials($connectionOptions:ConnectionTestOptions, $repoUrl:String, $sshKey:String) {
  testLookerGitSshCredentials(connectionOptions:$connectionOptions, repoUrl:$repoUrl, sshKey:$sshKey) {
    key
    success
  }
}
"""

TEST_LOOKER_GIT_CLONE_CRED_MUTATION = """
mutation testLookerGitCloneCredentials($connectionOptions:ConnectionTestOptions, $repoUrl:String!, $sshKey:String, $username:String, $token:String) {
  testLookerGitCloneCredentials(connectionOptions:$connectionOptions, repoUrl:$repoUrl, sshKey:$sshKey, username:$username, token:$token) {
    key
    success
  }
}
"""

ADD_BI_CONNECTION_MUTATION = """
mutation addBiConnection($connectionType:String!, $key:String!, $dcId:UUID) {
  addBiConnection(connectionType:$connectionType, key:$key, dcId:$dcId){
    connection {
      uuid
    }
  }
}
"""

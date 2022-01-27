#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import warnings
from ai.h2o.sparkling.SharedBackendConfUtils import SharedBackendConfUtils


class SharedBackendConf(SharedBackendConfUtils):

    #
    # Getters
    #

    def isH2OReplEnabled(self):
        return self._jconf.isH2OReplEnabled()

    def cloudName(self):
        return self._get_option(self._jconf.cloudName())

    def backendClusterMode(self):
        return self._jconf.backendClusterMode()

    def isProgressBarEnabled(self):
        return self._jconf.isProgressBarEnabled()

    def isModelPrintAfterTrainingEnabled(self):
        return self._jconf.isModelPrintAfterTrainingEnabled()

    def scalaIntDefaultNum(self):
        return self._jconf.scalaIntDefaultNum()

    def isClusterTopologyListenerEnabled(self):
        return self._jconf.isClusterTopologyListenerEnabled()

    def isSparkVersionCheckEnabled(self):
        return self._jconf.isSparkVersionCheckEnabled()

    def isFailOnUnsupportedSparkParamEnabled(self):
        return self._jconf.isFailOnUnsupportedSparkParamEnabled()

    def jks(self):
        return self._get_option(self._jconf.jks())

    def jksPass(self):
        return self._get_option(self._jconf.jksPass())

    def jksAlias(self):
        return self._get_option(self._jconf.jksAlias())

    def sslCACert(self):
        return self._get_option(self._jconf.sslCACert())

    def hashLogin(self):
        return self._jconf.hashLogin()

    def ldapLogin(self):
        return self._jconf.ldapLogin()

    def kerberosLogin(self):
        return self._jconf.kerberosLogin()

    def loginConf(self):
        return self._get_option(self._jconf.loginConf())

    def userName(self):
        return self._get_option(self._jconf.userName())

    def password(self):
        return self._get_option(self._jconf.password())

    def sslConf(self):
        return self._get_option(self._jconf.sslConf())

    def autoFlowSsl(self):
        return self._jconf.autoFlowSsl()

    def logLevel(self):
        return self._jconf.logLevel()

    def logDir(self):
        return self._get_option(self._jconf.logDir())

    def backendHeartbeatInterval(self):
        return self._jconf.backendHeartbeatInterval()

    def cloudTimeout(self):
        return self._jconf.cloudTimeout()

    def nodeNetworkMask(self):
        return self._get_option(self._jconf.nodeNetworkMask())

    def stacktraceCollectorInterval(self):
        return self._jconf.stacktraceCollectorInterval()

    def contextPath(self):
        return self._get_option(self._jconf.contextPath())

    def flowScalaCellAsync(self):
        return self._jconf.flowScalaCellAsync()

    def maxParallelScalaCellJobs(self):
        return self._jconf.maxParallelScalaCellJobs()

    def internalPortOffset(self):
        return self._jconf.internalPortOffset()

    def basePort(self):
        return self._jconf.basePort()

    def mojoDestroyTimeout(self):
        return self._jconf.mojoDestroyTimeout()

    def extraProperties(self):
        return self._get_option(self._jconf.extraProperties())

    def flowExtraHttpHeaders(self):
        return self._get_option(self._jconf.flowExtraHttpHeaders())

    def flowProxyRequestMaxSize(self):
        return self._jconf.flowProxyRequestMaxSize()

    def flowProxyResponseMaxSize(self):
        return self._jconf.flowProxyResponseMaxSize()

    def isInternalSecureConnectionsEnabled(self):
        return self._jconf.isInternalSecureConnectionsEnabled()

    def isInsecureXGBoostAllowed(self):
        return self._jconf.isInsecureXGBoostAllowed()

    def flowDir(self):
        return self._get_option(self._jconf.flowDir())

    def clientIp(self):
        return self._get_option(self._jconf.clientIp())

    def clientWebPort(self):
        return self._jconf.clientWebPort()

    def clientVerboseOutput(self):
        return self._jconf.clientVerboseOutput()

    def clientNetworkMask(self):
        return self._get_option(self._jconf.clientNetworkMask())

    def clientFlowBaseurlOverride(self):
        return self._get_option(self._jconf.clientFlowBaseurlOverride())

    def runsInExternalClusterMode(self):
        return self._jconf.runsInExternalClusterMode()

    def runsInInternalClusterMode(self):
        return self._jconf.runsInInternalClusterMode()

    def clientCheckRetryTimeout(self):
        return self._jconf.clientCheckRetryTimeout()

    def verifySslCertificates(self):
        return self._jconf.verifySslCertificates()

    def isSslHostnameVerificationInInternalRestConnectionsEnabled(self):
        return self._jconf.isSslHostnameVerificationInInternalRestConnectionsEnabled()

    def isSslCertificateVerificationInInternalRestConnectionsEnabled(self):
        return self._jconf.isSslCertificateVerificationInInternalRestConnectionsEnabled()

    def isKerberizedHiveEnabled(self):
        return self._jconf.isKerberizedHiveEnabled()

    def hiveHost(self):
        return self._get_option(self._jconf.hiveHost())

    def hivePrincipal(self):
        return self._get_option(self._jconf.hivePrincipal())

    def hiveJdbcUrlPattern(self):
        return self._get_option(self._jconf.hiveJdbcUrlPattern())

    def hiveToken(self):
        return self._get_option(self._jconf.hiveToken())

    def icedDir(self):
        return self._get_option(self._jconf.icedDir())

    def restApiTimeout(self):
        return self._jconf.restApiTimeout()

    def nthreads(self):
        return self._jconf.nthreads()


    #
    # Setters
    #

    def setInternalClusterMode(self):
        self._jconf.setInternalClusterMode()
        return self

    def setExternalClusterMode(self):
        self._jconf.setExternalClusterMode()
        return self

    def setCloudName(self, value):
        self._jconf.setCloudName(value)
        return self

    def setNthreads(self, value):
        self._jconf.setNthreads(value)
        return self

    def setReplEnabled(self):
        self._jconf.setReplEnabled()
        return self

    def setReplDisabled(self):
        self._jconf.setReplDisabled()
        return self

    def setProgressBarEnabled(self):
        self._jconf.setProgressBarEnabled()
        return self

    def setProgressBarDisabled(self):
        self._jconf.setProgressBarDisabled()
        return self

    def setModelPrintAfterTrainingEnabled(self):
        self._jconf.setModelPrintAfterTrainingEnabled()
        return self

    def setModelPrintAfterTrainingDisabled(self):
        self._jconf.setModelPrintAfterTrainingDisabled()
        return self

    def setDefaultNumReplSessions(self, value):
        self._jconf.setDefaultNumReplSessions(value)
        return self

    def setClusterTopologyListenerEnabled(self):
        self._jconf.setClusterTopologyListenerEnabled()
        return self

    def setClusterTopologyListenerDisabled(self):
        self._jconf.setClusterTopologyListenerDisabled()
        return self

    def setSparkVersionCheckEnabled(self):
        self._jconf.setSparkVersionCheckEnabled()
        return self

    def setSparkVersionCheckDisabled(self):
        self._jconf.setSparkVersionCheckDisabled()
        return self

    def setFailOnUnsupportedSparkParamEnabled(self):
        self._jconf.setFailOnUnsupportedSparkParamEnabled()
        return self

    def setFailOnUnsupportedSparkParamDisabled(self):
        self._jconf.setFailOnUnsupportedSparkParamDisabled()
        return self

    def setJks(self, value):
        self._jconf.setJks(value)
        return self

    def setJksPass(self, value):
        self._jconf.setJksPass(value)
        return self

    def setJksAlias(self, value):
        self._jconf.setJksAlias(value)
        return self

    def setSslCACert(self, value):
        self._jconf.setSslCACert(value)
        return self

    def setHashLoginEnabled(self):
        self._jconf.setHashLoginEnabled()
        return self

    def setHashLoginDisabled(self):
        self._jconf.setHashLoginDisabled()
        return self

    def setLdapLoginEnabled(self):
        self._jconf.setLdapLoginEnabled()
        return self

    def setLdapLoginDisabled(self):
        self._jconf.setLdapLoginDisabled()
        return self

    def setKerberosLoginEnabled(self):
        self._jconf.setKerberosLoginEnabled()
        return self

    def setKerberosLoginDisabled(self):
        self._jconf.setKerberosLoginDisabled()
        return self

    def setLoginConf(self, value):
        self._jconf.setLoginConf(value)
        return self

    def setUserName(self, value):
        self._jconf.setUserName(value)
        return self

    def setPassword(self, value):
        self._jconf.setPassword(value)
        return self

    def setSslConf(self, value):
        self._jconf.setSslConf(value)
        return self

    def setAutoFlowSslEnabled(self):
        self._jconf.setAutoFlowSslEnabled()
        return self

    def setAutoFlowSslDisabled(self):
        self._jconf.setAutoFlowSslDisabled()
        return self

    def setLogLevel(self, value):
        self._jconf.setLogLevel(value)
        return self

    def setLogDir(self, value):
        self._jconf.setLogDir(value)
        return self

    def setBackendHeartbeatInterval(self, value):
        self._jconf.setBackendHeartbeatInterval(value)
        return self

    def setCloudTimeout(self, value):
        self._jconf.setCloudTimeout(value)
        return self

    def setNodeNetworkMask(self, value):
        self._jconf.setNodeNetworkMask(value)
        return self

    def setStacktraceCollectorInterval(self, value):
        self._jconf.setStacktraceCollectorInterval(value)
        return self

    def setContextPath(self, value):
        self._jconf.setContextPath(value)
        return self

    def setFlowScalaCellAsyncEnabled(self):
        self._jconf.setFlowScalaCellAsyncEnabled()
        return self

    def setFlowScalaCellAsyncDisabled(self):
        self._jconf.setFlowScalaCellAsyncDisabled()
        return self

    def setMaxParallelScalaCellJobs(self, value):
        self._jconf.setMaxParallelScalaCellJobs(value)
        return self

    def setInternalPortOffset(self, value):
        self._jconf.setInternalPortOffset(value)
        return self

    def setBasePort(self, value):
        self._jconf.setBasePort(value)
        return self

    def setMojoDestroyTimeout(self, value):
        self._jconf.setMojoDestroyTimeout(value)
        return self

    def setExtraProperties(self, value):
        self._jconf.setExtraProperties(value)
        return self

    def setFlowExtraHttpHeaders(self, value):
        self._jconf.setFlowExtraHttpHeaders(value)
        return self

    def setFlowProxyRequestMaxSize(self, value):
        self._jconf.setFlowProxyRequestMaxSize(value)
        return self

    def setFlowProxyResponseMaxSize(self, value):
        self._jconf.setFlowProxyResponseMaxSize(value)
        return self

    def setInternalSecureConnectionsEnabled(self):
        self._jconf.setInternalSecureConnectionsEnabled()
        return self

    def setInternalSecureConnectionsDisabled(self):
        self._jconf.setInternalSecureConnectionsDisabled()
        return self

    def setInsecureXGBoostAllowed(self):
        self._jconf.setInsecureXGBoostAllowed()
        return self

    def setInsecureXGBoostDenied(self):
        self._jconf.setInsecureXGBoostDenied()
        return self

    def setFlowDir(self, value):
        self._jconf.setFlowDir(value)
        return self

    def setClientIp(self, value):
        self._jconf.setClientIp(value)
        return self

    def setClientWebPort(self, value):
        self._jconf.setClientWebPort(value)
        return self

    def setClientVerboseEnabled(self):
        self._jconf.setClientVerboseEnabled()
        return self

    def setClientVerboseDisabled(self):
        self._jconf.setClientVerboseDisabled()
        return self

    def setClientNetworkMask(self, value):
        self._jconf.setClientNetworkMask(value)
        return self

    def setClientFlowBaseurlOverride(self, value):
        self._jconf.setClientFlowBaseurlOverride(value)
        return self

    def setClientCheckRetryTimeout(self, value):
        self._jconf.setClientCheckRetryTimeout(value)
        return self

    def setVerifySslCertificates(self, value):
        self._jconf.setVerifySslCertificates(value)
        return self

    def setSslHostnameVerificationInInternalRestConnectionsEnabled(self):
        self._jconf.setSslHostnameVerificationInInternalRestConnectionsEnabled()
        return self

    def setSslHostnameVerificationInInternalRestConnectionsDisabled(self):
        self._jconf.setSslHostnameVerificationInInternalRestConnectionsDisabled()
        return self

    def setSslCertificateVerificationInInternalRestConnectionsEnabled(self):
        self._jconf.setSslCertificateVerificationInInternalRestConnectionsEnabled()
        return self

    def setSslCertificateVerificationInInternalRestConnectionsDisabled(self):
        self._jconf.setSslCertificateVerificationInInternalRestConnectionsDisabled()
        return self

    def setKerberizedHiveEnabled(self):
        self._jconf.setKerberizedHiveEnabled()
        return self

    def setKerberizedHiveDisabled(self):
        self._jconf.setKerberizedHiveDisabled()
        return self

    def setHiveHost(self, value):
        self._jconf.setHiveHost(value)
        return self

    def setHivePrincipal(self, value):
        self._jconf.setHivePrincipal(value)
        return self

    def setHiveJdbcUrlPattern(self, value):
        self._jconf.setHiveJdbcUrlPattern(value)
        return self

    def setHiveToken(self, value):
        self._jconf.setHiveToken(value)
        return self

    def setIcedDir(self, value):
        self._jconf.setIcedDir(value)
        return self

    def setRestApiTimeout(self, value):
        self._jconf.setRestApiTimeout(value)
        return self

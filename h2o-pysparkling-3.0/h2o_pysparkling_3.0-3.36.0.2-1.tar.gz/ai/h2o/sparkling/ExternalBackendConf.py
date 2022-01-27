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


class ExternalBackendConf(SharedBackendConfUtils):

    #
    # Getters
    #

    def h2oCluster(self):
        return self._get_option(self._jconf.h2oCluster())

    def h2oClusterHost(self):
        return self._get_option(self._jconf.h2oClusterHost())

    def h2oClusterPort(self):
        return self._get_option(self._jconf.h2oClusterPort())

    def clusterSize(self):
        return self._get_option(self._jconf.clusterSize())

    def clusterStartTimeout(self):
        return self._jconf.clusterStartTimeout()

    def clusterInfoFile(self):
        return self._get_option(self._jconf.clusterInfoFile())

    def externalMemory(self):
        return self._jconf.externalMemory()

    def HDFSOutputDir(self):
        return self._get_option(self._jconf.HDFSOutputDir())

    def isAutoClusterStartUsed(self):
        return self._jconf.isAutoClusterStartUsed()

    def isManualClusterStartUsed(self):
        return self._jconf.isManualClusterStartUsed()

    def clusterStartMode(self):
        return self._jconf.clusterStartMode()

    def h2oDriverPath(self):
        return self._get_option(self._jconf.h2oDriverPath())

    def YARNQueue(self):
        return self._get_option(self._jconf.YARNQueue())

    def isKillOnUnhealthyClusterEnabled(self):
        return self._jconf.isKillOnUnhealthyClusterEnabled()

    def kerberosPrincipal(self):
        return self._get_option(self._jconf.kerberosPrincipal())

    def kerberosKeytab(self):
        return self._get_option(self._jconf.kerberosKeytab())

    def runAsUser(self):
        return self._get_option(self._jconf.runAsUser())

    def externalH2ODriverIf(self):
        return self._get_option(self._jconf.externalH2ODriverIf())

    def externalH2ODriverPort(self):
        return self._get_option(self._jconf.externalH2ODriverPort())

    def externalH2ODriverPortRange(self):
        return self._get_option(self._jconf.externalH2ODriverPortRange())

    def externalExtraMemoryPercent(self):
        return self._jconf.externalExtraMemoryPercent()

    def externalBackendStopTimeout(self):
        return self._jconf.externalBackendStopTimeout()

    def externalHadoopExecutable(self):
        return self._jconf.externalHadoopExecutable()

    def externalExtraJars(self):
        return self._get_option(self._jconf.externalExtraJars())

    def externalCommunicationCompression(self):
        return self._jconf.externalCommunicationCompression()

    def externalAutoStartBackend(self):
        return self._jconf.externalAutoStartBackend()

    def externalK8sH2OServiceName(self):
        return self._jconf.externalK8sH2OServiceName()

    def externalK8sH2OStatefulsetName(self):
        return self._jconf.externalK8sH2OStatefulsetName()

    def externalK8sH2OLabel(self):
        return self._jconf.externalK8sH2OLabel()

    def externalK8sH2OApiPort(self):
        return self._jconf.externalK8sH2OApiPort()

    def externalK8sNamespace(self):
        return self._jconf.externalK8sNamespace()

    def externalK8sDockerImage(self):
        return self._jconf.externalK8sDockerImage()

    def externalK8sDomain(self):
        return self._jconf.externalK8sDomain()

    def externalK8sServiceTimeout(self):
        return self._jconf.externalK8sServiceTimeout()


    #
    # Setters
    #

    def useAutoClusterStart(self):
        self._jconf.useAutoClusterStart()
        return self

    def useManualClusterStart(self):
        self._jconf.useManualClusterStart()
        return self

    def setH2OCluster(self, value):
        self._jconf.setH2OCluster(value)
        return self

    def setClusterSize(self, value):
        self._jconf.setClusterSize(value)
        return self

    def setClusterStartTimeout(self, value):
        self._jconf.setClusterStartTimeout(value)
        return self

    def setClusterInfoFile(self, value):
        self._jconf.setClusterInfoFile(value)
        return self

    def setExternalMemory(self, value):
        self._jconf.setExternalMemory(value)
        return self

    def setHDFSOutputDir(self, value):
        self._jconf.setHDFSOutputDir(value)
        return self

    def setH2ODriverPath(self, value):
        self._jconf.setH2ODriverPath(value)
        return self

    def setYARNQueue(self, value):
        self._jconf.setYARNQueue(value)
        return self

    def setKillOnUnhealthyClusterEnabled(self):
        self._jconf.setKillOnUnhealthyClusterEnabled()
        return self

    def setKillOnUnhealthyClusterDisabled(self):
        self._jconf.setKillOnUnhealthyClusterDisabled()
        return self

    def setKerberosPrincipal(self, value):
        self._jconf.setKerberosPrincipal(value)
        return self

    def setKerberosKeytab(self, value):
        self._jconf.setKerberosKeytab(value)
        return self

    def setRunAsUser(self, value):
        self._jconf.setRunAsUser(value)
        return self

    def setExternalH2ODriverIf(self, value):
        self._jconf.setExternalH2ODriverIf(value)
        return self

    def setExternalH2ODriverPort(self, value):
        self._jconf.setExternalH2ODriverPort(value)
        return self

    def setExternalH2ODriverPortRange(self, value):
        self._jconf.setExternalH2ODriverPortRange(value)
        return self

    def setExternalExtraMemoryPercent(self, value):
        self._jconf.setExternalExtraMemoryPercent(value)
        return self

    def setExternalBackendStopTimeout(self, value):
        self._jconf.setExternalBackendStopTimeout(value)
        return self

    def setExternalHadoopExecutable(self, value):
        self._jconf.setExternalHadoopExecutable(value)
        return self

    def setExternalExtraJars(self, value):
        self._jconf.setExternalExtraJars(value)
        return self

    def setExternalCommunicationCompression(self, value):
        self._jconf.setExternalCommunicationCompression(value)
        return self

    def setExternalAutoStartBackend(self, value):
        self._jconf.setExternalAutoStartBackend(value)
        return self

    def setExternalK8sH2OServiceName(self, value):
        self._jconf.setExternalK8sH2OServiceName(value)
        return self

    def setExternalK8sH2OStatefulsetName(self, value):
        self._jconf.setExternalK8sH2OStatefulsetName(value)
        return self

    def setExternalK8sH2OLabel(self, value):
        self._jconf.setExternalK8sH2OLabel(value)
        return self

    def setExternalK8sH2OApiPort(self, value):
        self._jconf.setExternalK8sH2OApiPort(value)
        return self

    def setExternalK8sNamespace(self, value):
        self._jconf.setExternalK8sNamespace(value)
        return self

    def setExternalK8sDockerImage(self, value):
        self._jconf.setExternalK8sDockerImage(value)
        return self

    def setExternalK8sDomain(self, value):
        self._jconf.setExternalK8sDomain(value)
        return self

    def setExternalK8sServiceTimeout(self, value):
        self._jconf.setExternalK8sServiceTimeout(value)
        return self

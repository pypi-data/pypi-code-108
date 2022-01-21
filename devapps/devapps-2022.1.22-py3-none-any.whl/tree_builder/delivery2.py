#!/usr/bin/env python
"""
This is the most concise form to build a nested class tree, where the local
classes are independent clones (can be configured w/o affecting others).

CAUTION:
We use a few tricks at class generation, inspecting the mro and put any ref
to a local class out of from the mro, into the container class as attribute!


Config: Class Tree
State: Object Tree
"""

from tree_builder import *


# there might be more hirarchies, this is the canonical one:
class Project(T):
    pass


class Cluster(T):
    pass


class Datacenter(T):
    pass


class Tier(T):
    pass


class Node(T):
    pass


class Role(T):
    pass


class Container(T):
    networking = 'host'


class SvcGroup(T):
    pass


class Service(T):
    criticality = 1


# Swisscom.MBC.SB.Dev.Zuerich.ACS1.Nginx


# mixin types. not needed. yet.
# class Group   ( MT ): short = 'grou'

build_type_hirarchy(root=Project)


allow([Service], on=(Role, Container))

# -----------------------------------------------------------------------------


class Zeo(Service):
    'Object DB for AXESS'


class MySQL(Service):
    'SQL DB for AXESS'


class Redis(Service):
    'Local KV Store, Job Queue for AXESS/AXD'


class Nginx(Service):
    'Proxy, Static Content'


class NBI(Service):
    'Tibco In'


class Callback(Service):
    'Job Responses'


class Portal(Service):
    'HET Portal'


class Debug(Service):
    'Debugging / Testing'


class Phase0(Service):
    'Unauth Field'


class Phase1(Service):
    'Authenticated Field'


class TR069(Service):
    'TR069'


class GUI(Service):
    'Admin GUI'


class Configurator(Service):
    'TR069 ConnRequests Out'


class AXD_A1(Service):
    'Broadsoft Ocip / Tibco Out'


class AXD_A2(Service):
    'Genband Out'


class AXD_System(Service):
    'Local Jobs'


class Notebook(Service):
    'Interactive NBI'


class Repo(Service):
    'Repositories'


class ConsulClient(Service):
    'Local HealthChecker / Reporter'


class ConsulServer(Service):
    'Datacenter Wide Truth Provider / KV Store'


class L0Master(Service):
    'Triggers Cluster L0 Jobs, RPC GUI'


class L0Agent(Service):
    'Runs Cluster L0 Jobs'


class DCStatus(Service):
    'Final Datacenter Status Based on All Results'


class AXESS(
    SvcGroup, NBI, Callback, Portal, Debug, Phase0, Phase1, TR069, GUI, Configurator,
):
    'HTTP App Server'


class AXD(SvcGroup, AXD_A1, AXD_A2, AXD_System):
    'Outgoing Job Runner'


# common props:
DCStatus.interval = ConsulClient.interval = 5
AXESS.Debug.criticality = 3
ConsulClient.criticality = 3
Notebook.criticality = ConsulServer.criticality = DCStatus.criticality = 2
L0Agent.criticality = L0Master.criticality = Repo.criticality = 2


class ContNB(Container, AXESS, AXD, Notebook, Nginx):
    pass


class Cont:
    'NSpawn Virtual Nodes'

    class ACS(Container, Nginx):
        'DevMgmt'

    class NB_MBC(ContNB):
        'Stateless MBC'

    class NB_SME(ContNB):
        'Stateless SME'

    class NB_ST(ContNB):
        'Stateless Siptrunk'

    class DB(Container, Zeo, MySQL, Redis):
        'Database / State'


class Role:
    class L0(Role, L0Agent):
        'Operational Layer / Cluster O&M Jobs'

    class L1(Role, ConsulClient):
        'Consul Layer'

    class MBC(Role):
        'SmartBCon'

    class SME(Role):
        'SmallMediumEnterprise'

    class ST(Role):
        'SipTrunk'


# helper
class N(Node, Role.L0, Role.L1):
    'Phys. Node'


class ACS(N, Role.MBC, Cont.ACS, Role.SME, Cont.ACS):
    'MBC Field'


class M(N, Role.MBC, Cont.NB_MBC, Cont.DB):
    'MBC NB'


class S(N, Role.SME, Cont.NB_SME, Cont.DB):
    'SME NB'


class E(N, Role.ST, Cont.NB_ST, Cont.DB):
    'ST  NB'


class C(N):
    'O&M Master'


add_to(C.L0, Service=(L0Master, Repo))
add_to(M.L1, S.L1, E.L1, Service=[ConsulServer, DCStatus])


class NB(Tier, M, S, E):
    'Northbound Tier'


class SB(Tier, ACS):
    'Southbound Tier'


class L0Master(Tier, C):
    'O&M'


class Zuerich(Datacenter, L0Master, NB, SB):
    'Primary'


class Olten(Datacenter, L0Master, NB, SB):
    'HotStandby'


class Cluster(Cluster, Zuerich, Olten):
    'Cluster'


class Dev(Cluster):
    'Development'


class A(Cluster):
    'Staging'


class B(Cluster):
    'PreProduction'


class Prod(Cluster):
    'Production'


class Swisscom(Project, Dev, A, B, Prod):
    'Enterprise Voice'


postconfigure(Swisscom)

# ------------------------------------------------------------------ Properties
Swisscom.Dev.Zuerich.L0Master.C.ip = '10.67.225.109'
Swisscom.Dev.Zuerich.NB.M.ip = '10.67.225.103'
Swisscom.Dev.Zuerich.NB.S.ip = '10.67.225.105'
Swisscom.Dev.Zuerich.NB.E.ip = '10.67.225.107'
Swisscom.Dev.Zuerich.SB.ACS.ip = '195.186.149.150'
Swisscom.Dev.Olten.L0Master.C.ip = '10.67.224.108'
Swisscom.Dev.Olten.NB.M.ip = '10.67.224.102'
Swisscom.Dev.Olten.NB.S.ip = '10.67.224.104'
Swisscom.Dev.Olten.NB.E.ip = '10.67.224.106'
Swisscom.Dev.Olten.SB.ACS.ip = '195.186.149.152'


if __name__ == '__main__':
    import sys

    sys.argv.append('')
    from .render import to_html

    # print to_html(Swisscom.A.Zuerich.SB.ACS, file=sys.argv[1], into='<!--cl-->')
    # print to_html(Swisscom.Dev, file=sys.argv[1], into='<!--cl-->',
    #        props_ign=('cls', 'descr', 'name', 'type', 'criticality'),
    #        stop_recursion='Role', no_props=1)
    print(
        to_html(
            Swisscom.Dev,
            file=sys.argv[1],
            into='<!--cl-->',
            props_ign=('cls', 'descr', 'name', 'type', 'criticality'),
        )
    )

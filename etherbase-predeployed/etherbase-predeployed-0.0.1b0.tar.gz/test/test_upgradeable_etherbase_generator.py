from web3.auto import w3
from predeployed_generator.openzeppelin.proxy_admin_generator import ProxyAdminGenerator

from etherbase_predeployed import UpgradeableEtherbaseUpgradeableGenerator, ETHERBASE_ADDRESS
from etherbase_predeployed.etherbase_upgradeable_generator import EtherbaseUpgradeableGenerator
from .tools.test_solidity_project import TestSolidityProject


class TestUpgradeableEtherbaseGenerator(TestSolidityProject):
    OWNER_ADDRESS = '0xd200000000000000000000000000000000000000'
    PROXY_ADMIN_ADDRESS = '0xd200000000000000000000000000000000000001'

    def get_etherbase_abi(self):
        return self.get_abi('Etherbase')

    def prepare_genesis(self):
        proxy_admin_generator = ProxyAdminGenerator()
        upgradeable_etherbase_generator = UpgradeableEtherbaseUpgradeableGenerator()

        return self.generate_genesis({
            **upgradeable_etherbase_generator.generate_allocation(
                ETHERBASE_ADDRESS,
                proxy_admin_address=self.PROXY_ADMIN_ADDRESS,
                schain_owner=self.OWNER_ADDRESS),
            **proxy_admin_generator.generate_allocation(
                self.PROXY_ADMIN_ADDRESS,
                owner_address=self.OWNER_ADDRESS)
            })

    def test_default_admin_role(self, tmpdir):
        genesis = self.prepare_genesis()

        with self.run_geth(tmpdir, genesis):
            assert w3.isConnected()

            etherbase = w3.eth.contract(address=ETHERBASE_ADDRESS, abi=self.get_etherbase_abi())
            assert etherbase.functions.getRoleMemberCount(EtherbaseUpgradeableGenerator.DEFAULT_ADMIN_ROLE).call() == 1
            assert etherbase.functions.getRoleMember(EtherbaseUpgradeableGenerator.DEFAULT_ADMIN_ROLE, 0).call() == self.OWNER_ADDRESS            
            assert etherbase.functions.hasRole(EtherbaseUpgradeableGenerator.DEFAULT_ADMIN_ROLE, self.OWNER_ADDRESS).call()

    def test_ether_manager_role(self, tmpdir):
        genesis = self.prepare_genesis()

        with self.run_geth(tmpdir, genesis):
            assert w3.isConnected()

            etherbase = w3.eth.contract(address=ETHERBASE_ADDRESS, abi=self.get_etherbase_abi())
            assert etherbase.functions.getRoleMemberCount(EtherbaseUpgradeableGenerator.ETHER_MANAGER_ROLE).call() == 1
            assert etherbase.functions.getRoleMember(EtherbaseUpgradeableGenerator.ETHER_MANAGER_ROLE, 0).call() == self.OWNER_ADDRESS            
            assert etherbase.functions.hasRole(EtherbaseUpgradeableGenerator.ETHER_MANAGER_ROLE, self.OWNER_ADDRESS).call()
    
from web3.auto import w3

from etherbase_predeployed import EtherbaseGenerator, ETHERBASE_ADDRESS
from .tools.test_solidity_project import TestSolidityProject


class TestEtherbaseGenerator(TestSolidityProject):
    OWNER_ADDRESS = '0xd200000000000000000000000000000000000000'
    IMA_ADDRESS = '0xd200000000000000000000000000000000000001'

    def get_etherbase_abi(self):
        return self.get_abi('Etherbase')

    def prepare_genesis(self):
        etherbase_generator = EtherbaseGenerator()

        return self.generate_genesis(etherbase_generator.generate_allocation(
            ETHERBASE_ADDRESS,
            schain_owner=self.OWNER_ADDRESS,
            ether_managers=[self.IMA_ADDRESS]))

    def test_default_admin_role(self, tmpdir):
        genesis = self.prepare_genesis()

        with self.run_geth(tmpdir, genesis):
            assert w3.isConnected()

            etherbase = w3.eth.contract(address=ETHERBASE_ADDRESS, abi=self.get_etherbase_abi())
            assert etherbase.functions.getRoleMemberCount(EtherbaseGenerator.DEFAULT_ADMIN_ROLE).call() == 1
            assert etherbase.functions.getRoleMember(EtherbaseGenerator.DEFAULT_ADMIN_ROLE, 0).call() == self.OWNER_ADDRESS            
            assert etherbase.functions.hasRole(EtherbaseGenerator.DEFAULT_ADMIN_ROLE, self.OWNER_ADDRESS).call()

    def test_ether_manager_role(self, tmpdir):
        genesis = self.prepare_genesis()

        with self.run_geth(tmpdir, genesis):
            assert w3.isConnected()

            etherbase = w3.eth.contract(address=ETHERBASE_ADDRESS, abi=self.get_etherbase_abi())
            assert etherbase.functions.getRoleMemberCount(EtherbaseGenerator.ETHER_MANAGER_ROLE).call() == 2
            assert etherbase.functions.getRoleMember(EtherbaseGenerator.ETHER_MANAGER_ROLE, 0).call() == self.IMA_ADDRESS            
            assert etherbase.functions.hasRole(EtherbaseGenerator.ETHER_MANAGER_ROLE, self.IMA_ADDRESS).call()
            assert etherbase.functions.getRoleMember(EtherbaseGenerator.ETHER_MANAGER_ROLE, 1).call() == self.OWNER_ADDRESS            
            assert etherbase.functions.hasRole(EtherbaseGenerator.ETHER_MANAGER_ROLE, self.OWNER_ADDRESS).call()
    
# -*- coding: utf-8 -*-
"""Implement unit tests for the module utils.
"""
from tlsmate import tls
from tlsmate import utils
from tlsmate.workers.base_vulnerabilities import ScanBaseVulnerabilities


def test_base_vulnerabilities_ok(tlsmate, server_profile):
    tlsmate.server_profile.load(utils.deserialize_data(str(server_profile)))
    ScanBaseVulnerabilities(tlsmate).run()
    prof_vuln = tlsmate.server_profile.vulnerabilities
    assert prof_vuln.beast is tls.ScanState.FALSE
    assert prof_vuln.crime is tls.ScanState.FALSE
    assert prof_vuln.sweet_32 is tls.ScanState.FALSE
    assert prof_vuln.freak is tls.ScanState.FALSE
    assert prof_vuln.logjam is tls.Logjam.OK


def test_base_vulnerabilities_nok(tlsmate, server_profile_base_vuln):
    tlsmate.server_profile.load(utils.deserialize_data(str(server_profile_base_vuln)))
    ScanBaseVulnerabilities(tlsmate).run()
    prof_vuln = tlsmate.server_profile.vulnerabilities
    assert prof_vuln.beast is tls.ScanState.TRUE
    assert prof_vuln.crime is tls.ScanState.TRUE
    assert prof_vuln.sweet_32 is tls.ScanState.TRUE
    assert prof_vuln.freak is tls.ScanState.TRUE
    assert prof_vuln.logjam is tls.Logjam.PRIME512


def test_base_vulnerabilities_no_compr(tlsmate, server_profile_no_compr):
    tlsmate.server_profile.load(utils.deserialize_data(str(server_profile_no_compr)))
    ScanBaseVulnerabilities(tlsmate).run()
    prof_vuln = tlsmate.server_profile.vulnerabilities
    assert prof_vuln.crime is tls.ScanState.UNDETERMINED


def test_base_vulnerabilities_no_features(tlsmate, server_profile_no_features):
    tlsmate.server_profile.load(utils.deserialize_data(str(server_profile_no_features)))
    ScanBaseVulnerabilities(tlsmate).run()
    prof_vuln = tlsmate.server_profile.vulnerabilities
    assert prof_vuln.crime is tls.ScanState.UNDETERMINED


def test_base_vulnerabilities_logjam_1024_common(tlsmate, server_profile_logjam_common):
    tlsmate.server_profile.load(
        utils.deserialize_data(str(server_profile_logjam_common))
    )
    ScanBaseVulnerabilities(tlsmate).run()
    prof_vuln = tlsmate.server_profile.vulnerabilities
    assert prof_vuln.logjam is tls.Logjam.PRIME1024_COMMON


def test_base_vulnerabilities_logjam_1024_cust(tlsmate, server_profile_logjam_cust):
    tlsmate.server_profile.load(utils.deserialize_data(str(server_profile_logjam_cust)))
    ScanBaseVulnerabilities(tlsmate).run()
    prof_vuln = tlsmate.server_profile.vulnerabilities
    assert prof_vuln.logjam is tls.Logjam.PRIME1024_CUSTOMIZED


def test_base_vulnerabilities_logjam_no_dh_group(tlsmate, server_profile_no_dh_group):
    tlsmate.server_profile.load(utils.deserialize_data(str(server_profile_no_dh_group)))
    ScanBaseVulnerabilities(tlsmate).run()
    prof_vuln = tlsmate.server_profile.vulnerabilities
    assert prof_vuln.logjam is tls.Logjam.UNDETERMINED


def test_base_vulnerabilities_logjam_no_dh(tlsmate, server_profile_no_dh):
    tlsmate.server_profile.load(utils.deserialize_data(str(server_profile_no_dh)))
    ScanBaseVulnerabilities(tlsmate).run()
    prof_vuln = tlsmate.server_profile.vulnerabilities
    assert prof_vuln.logjam is tls.Logjam.NA

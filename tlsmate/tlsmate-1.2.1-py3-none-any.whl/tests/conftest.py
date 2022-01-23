# -*- coding: utf-8 -*-
"""Define common fixtures
"""
import pytest
import pathlib
import pem
import os
import datetime
import subprocess
import time

import tlsmate.tlsmate as tm


@pytest.fixture
def proxy():
    port = os.environ.get("TLSMATE_PROXY_PORT", 8801)
    cmd = f"ncat -l --proxy-type http localhost {port}"
    proc = subprocess.Popen(cmd.split())
    time.sleep(1)
    yield f"http://localhost:{port}"
    proc.kill()


@pytest.fixture
def valid_time():
    return datetime.datetime(2031, 6, 1)


@pytest.fixture
def style_file():
    return pathlib.Path(__file__).parent.resolve() / "../tlsmate/styles/default.yaml"


@pytest.fixture
def fixturefiles_dir():
    return pathlib.Path(__file__).parent.resolve() / "fixturefiles"


@pytest.fixture
def tlsmate_empty_ini(fixturefiles_dir):
    return fixturefiles_dir / "tlsmate_empty.ini"


@pytest.fixture
def guballa_de_pem(fixturefiles_dir):
    return pem.parse_file(fixturefiles_dir / "guballa.de.pem")[0]


@pytest.fixture
def quo_vadis_root_ca3(fixturefiles_dir):
    return pem.parse_file(fixturefiles_dir / "QuoVadis_Root_CA_3.pem")[0]


@pytest.fixture
def digi_cert_global_root_ca_file(fixturefiles_dir):
    return fixturefiles_dir / "DigiCertGlobalRootCA.pem"


@pytest.fixture
def ca_dir(fixturefiles_dir):
    return fixturefiles_dir / "../ca"


@pytest.fixture
def trust_store_file(ca_dir):
    return ca_dir / "certs/root-certificates.pem"


@pytest.fixture
def ca_rsa_crl_file(ca_dir):
    return ca_dir / "crl/ca-rsa.crl.pem"


@pytest.fixture
def server_rsa_cert_file(ca_dir):
    return ca_dir / "certs/server-rsa.pem"


@pytest.fixture
def server_rsa_key_file(ca_dir):
    return ca_dir / "private/server-rsa.key"


@pytest.fixture
def server_rsa_chain_file(ca_dir):
    return ca_dir / "chains/server-rsa.chn"


@pytest.fixture
def tlsmate(ca_dir, trust_store_file, digi_cert_global_root_ca_file):
    mate = tm.TlsMate()
    mate.trust_store.set_ca_files([trust_store_file, digi_cert_global_root_ca_file])
    return mate


@pytest.fixture
def server_expired_rsa_cert(ca_dir):
    return pem.parse_file(ca_dir / "certs/server-expired-rsa.pem")[0]


@pytest.fixture
def server_no_ids_rsa_cert(ca_dir):
    return pem.parse_file(ca_dir / "certs/server-no-ids-rsa.pem")[0]


@pytest.fixture
def server_revoked_rsa_cert(ca_dir):
    return pem.parse_file(ca_dir / "certs/server-revoked-rsa.pem")[0]


@pytest.fixture
def server_rsa_cert(ca_dir):
    return pem.parse_file(ca_dir / "certs/server-rsa.pem")[0]


@pytest.fixture
def server_dsa_cert(ca_dir):
    return pem.parse_file(ca_dir / "certs/server-dsa.pem")[0]


@pytest.fixture
def server_ed25519_cert(ca_dir):
    return pem.parse_file(ca_dir / "certs/server-ed25519.pem")[0]


@pytest.fixture
def server_ed448_cert(ca_dir):
    return pem.parse_file(ca_dir / "certs/server-ed448.pem")[0]


@pytest.fixture
def ca_rsa_cert(ca_dir):
    return pem.parse_file(ca_dir / "certs/ca-rsa.pem")[0]


@pytest.fixture
def ca_rsa_key(ca_dir):
    return pem.parse_file(ca_dir / "private/ca-rsa.key")[0]


@pytest.fixture
def ca_2nd_rsa_cert(ca_dir):
    return pem.parse_file(ca_dir / "certs/ca-2nd-rsa.pem")[0]


@pytest.fixture
def ca_ecdsa_cert(ca_dir):
    return pem.parse_file(ca_dir / "certs/ca-ecdsa.pem")[0]


@pytest.fixture
def root_rsa_cert(ca_dir):
    return pem.parse_file(ca_dir / "certs/root-rsa.pem")[0]


@pytest.fixture
def root_rsa_key(ca_dir):
    return pem.parse_file(ca_dir / "private/root-rsa.key")[0]


@pytest.fixture
def root_ecdsa_cert(ca_dir):
    return pem.parse_file(ca_dir / "certs/root-ecdsa.pem")[0]


@pytest.fixture
def client_rsa_key_filename(ca_dir):
    return str(ca_dir / "private/client-rsa.key")


@pytest.fixture
def client_rsa_chain_filename(ca_dir):
    return str(ca_dir / "chains/client-rsa.chn")


@pytest.fixture
def server_profile(fixturefiles_dir):
    return fixturefiles_dir / "server_profile.yaml"


@pytest.fixture
def text_server_profile(fixturefiles_dir):
    return fixturefiles_dir / "text_server_profile.yaml"


@pytest.fixture
def server_profile_base_vuln(fixturefiles_dir):
    return fixturefiles_dir / "server_profile_base_vulnerabilities.yaml"


@pytest.fixture
def server_profile_no_compr(fixturefiles_dir):
    return fixturefiles_dir / "server_profile_no_compr.yaml"


@pytest.fixture
def server_profile_no_features(fixturefiles_dir):
    return fixturefiles_dir / "server_profile_no_features.yaml"


@pytest.fixture
def server_profile_logjam_common(fixturefiles_dir):
    return fixturefiles_dir / "server_profile_logjam_common.yaml"


@pytest.fixture
def server_profile_logjam_cust(fixturefiles_dir):
    return fixturefiles_dir / "server_profile_logjam_customized.yaml"


@pytest.fixture
def server_profile_no_dh_group(fixturefiles_dir):
    return fixturefiles_dir / "server_profile_no_dh_group.yaml"


@pytest.fixture
def server_profile_no_dh(fixturefiles_dir):
    return fixturefiles_dir / "server_profile_no_dh.yaml"


@pytest.fixture
def full_server_profile(fixturefiles_dir):
    return fixturefiles_dir / "full_server_profile.yaml"

# -*- coding: utf-8 -*-
"""Implements test cases for the cli
"""
import sys
import pytest
import re

from tlsmate import command
from tlsmate.plugin import WorkManager
from tlsmate.tlsmate import TlsMate
from tlsmate.workers.text_server_profile import TextProfileWorker
from tlsmate.workers.server_profile import DumpProfileWorker, ReadProfileWorker
from tlsmate.workers.compression import ScanCompression
from tlsmate.workers.encrypt_then_mac import ScanEncryptThenMac
from tlsmate.workers.master_secret import ScanExtendedMasterSecret
from tlsmate.workers.resumption import ScanResumption
from tlsmate.workers.renegotiation import ScanRenegotiation
from tlsmate.workers.ccs_injection import ScanCcsInjection
from tlsmate.workers.robot import ScanRobot
from tlsmate.workers.padding_oracle import ScanPaddingOracle
from tlsmate.workers.dh_params import ScanDhGroups
from tlsmate.workers.heartbeat import ScanHeartbeat
from tlsmate.workers.heartbleed import ScanHeartbleed
from tlsmate.workers.grease import ScanGrease
from tlsmate.workers.ephemeral_key_reuse import ScanEphemeralKeyReuse
from tlsmate.workers.ocsp_stapling import ScanOcspStapling
from tlsmate.workers.downgrade import ScanDowngrade
from tlsmate.workers.eval_cipher_suites import ScanCipherSuites
from tlsmate.workers.scanner_info import ScanStart, ScanEnd
from tlsmate.workers.supported_groups import ScanSupportedGroups
from tlsmate.workers.sig_algo import ScanSigAlgs


def work_manager_run(self, tlsmate):
    pass


def test_no_subcommand(capsys):
    cmd = "tlsmate"
    sys.argv = cmd.split()
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        command.main()
    captured = capsys.readouterr()
    assert "tlsmate: error: Subcommand is mandatory" in captured.err
    assert pytest_wrapped_e.value.code == 2


def test_version(capsys):
    cmd = "tlsmate version"
    sys.argv = cmd.split()
    command.main()
    captured = capsys.readouterr()
    assert re.match(r"^\d+\.\d+\.\d+", captured.out)


def test_scan(capsys):
    cmd = "tlsmate scan --port=100000 127.0.0.1"
    sys.argv = cmd.split()
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        command.main()
    captured = capsys.readouterr()
    assert "tlsmate: error: port must be in the range [0-65535]" in captured.err
    assert pytest_wrapped_e.value.code == 2


def test_invalid_domain(capsys):
    cmd = "tlsmate scan --port=0 palimpalim.palimpalim"
    sys.argv = cmd.split()
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        command.main()
    captured = capsys.readouterr()
    assert "Error: Cannot resolve domain name palimpalim.palimpalim" in captured.err
    assert pytest_wrapped_e.value.code == 1


def test_closed_port(capsys):
    cmd = "tlsmate scan --port=0 localhost"
    sys.argv = cmd.split()
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        command.main()
    captured = capsys.readouterr()
    assert "Error: Cannot open TCP connection to TransportEndpoint" in captured.err
    assert pytest_wrapped_e.value.code == 1


def test_all_defaults(monkeypatch, tlsmate_empty_ini):
    monkeypatch.setattr(WorkManager, "run", work_manager_run)

    cmd = f"tlsmate --config {tlsmate_empty_ini} scan 127.0.0.1"
    sys.argv = cmd.split()
    # import pudb; pudb.set_trace()
    command.main()
    config = TlsMate.instance.config
    workers = []
    _ = [workers.extend(pool) for pool in WorkManager._instance._prio_pool.values()]

    assert config.get("port") == 443
    assert config.get("key_log_file") is None
    assert config.get("progress") is False
    assert config.get("sni") is None
    assert config.get("read_profile") is None
    assert config.get("write_profile") is None
    assert config.get("format") == "text"
    assert config.get("color") is True
    assert config.get("ca_certs") is None
    assert config.get("client_key") is None
    assert config.get("client_chain") is None
    assert config.get("crl") is True
    assert config.get("ocsp") is True

    for ver in ["sslv2", "sslv3", "tls10", "tls11", "tls12", "tls13"]:
        assert config.get(ver) is True

    for feat in [
        "features",
        "compression",
        "dh_groups",
        "encrypt_then_mac",
        "ephemeral_key_reuse",
        "ext_master_secret",
        "fallback",
        "grease",
        "heartbeat",
        "ocsp_stapling",
        "renegotiation",
        "resumption",
    ]:
        assert config.get(feat) is True

    for vuln in [
        "vulnerabilities",
        "ccs_injection",
        "heartbleed",
        "padding_oracle",
        "robot",
    ]:
        assert config.get(vuln) is True

    assert config.get("oracle_accuracy") == "medium"

    for worker in [
        ScanCompression,
        ScanDhGroups,
        ScanEncryptThenMac,
        ScanEphemeralKeyReuse,
        ScanExtendedMasterSecret,
        ScanDowngrade,
        ScanGrease,
        ScanHeartbeat,
        ScanOcspStapling,
        ScanRenegotiation,
        ScanResumption,
        ScanCcsInjection,
        ScanHeartbleed,
        ScanPaddingOracle,
        ScanRobot,
        ScanStart,
        ScanCipherSuites,
        ScanSupportedGroups,
        ScanSigAlgs,
        ScanEnd,
    ]:
        assert worker in workers

    assert DumpProfileWorker not in workers
    assert ReadProfileWorker not in workers


def test_format_text(monkeypatch):
    monkeypatch.setattr(WorkManager, "run", work_manager_run)

    cmd = "tlsmate scan --port=1000 127.0.0.1 --format=text"
    sys.argv = cmd.split()
    command.main()
    config = TlsMate.instance.config
    workers = []
    _ = [workers.extend(pool) for pool in WorkManager._instance._prio_pool.values()]

    assert config.get("format") == "text"
    assert TextProfileWorker in workers
    assert DumpProfileWorker not in workers


def test_format_yaml(monkeypatch):
    monkeypatch.setattr(WorkManager, "run", work_manager_run)

    cmd = "tlsmate scan --port=1000 127.0.0.1 --format=yaml"
    sys.argv = cmd.split()
    command.main()
    config = TlsMate.instance.config
    workers = []
    _ = [workers.extend(pool) for pool in WorkManager._instance._prio_pool.values()]

    assert config.get("format") == "yaml"
    assert TextProfileWorker not in workers
    assert DumpProfileWorker in workers


def test_client_chain_no_key(capsys):
    cmd = "tlsmate scan --port=1000 127.0.0.1 --client-chain=xxx"
    sys.argv = cmd.split()
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        command.main()
    captured = capsys.readouterr()
    assert "if --client-key is given, --client-chain must be given" in captured.err
    assert pytest_wrapped_e.value.code == 2


def test_client_chain_key_wrong(capsys):
    cmd = (
        "tlsmate scan --port=1000 127.0.0.1 " "--client-chain=xxx --client-key yyy zzz"
    )
    sys.argv = cmd.split()
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        command.main()
    captured = capsys.readouterr()
    assert "number of arguments for --client-key and --client-chain" in captured.err
    assert pytest_wrapped_e.value.code == 2


def test_client_key_set(
    monkeypatch, client_rsa_key_filename, client_rsa_chain_filename
):
    monkeypatch.setattr(WorkManager, "run", work_manager_run)

    cmd = (
        f"tlsmate scan --port=1000 127.0.0.1 "
        f"--client-chain={client_rsa_chain_filename} "
        f"--client-key={client_rsa_key_filename}"
    )
    sys.argv = cmd.split()
    command.main()
    config = TlsMate.instance.config
    assert config.get("client_key") == [client_rsa_key_filename]
    assert config.get("client_chain") == [client_rsa_chain_filename]


def test_no_version(capsys):
    cmd = (
        "tlsmate scan --port=1000 127.0.0.1 "
        "--no-sslv2 --no-sslv3 --no-tls10 --no-tls11 --no-tls12 --no-tls13"
    )
    sys.argv = cmd.split()
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        command.main()
    captured = capsys.readouterr()
    assert "at least one TLS version must be given" in captured.err
    assert pytest_wrapped_e.value.code == 2


def test_versions(monkeypatch):
    monkeypatch.setattr(WorkManager, "run", work_manager_run)

    cmd = "tlsmate scan --port=1000 127.0.0.1 --tls10 --tls12"
    sys.argv = cmd.split()
    command.main()
    config = TlsMate.instance.config
    workers = []
    _ = [workers.extend(pool) for pool in WorkManager._instance._prio_pool.values()]

    assert config.get("sslv2") is False
    assert config.get("sslv3") is False
    assert config.get("tls10") is True
    assert config.get("tls11") is False
    assert config.get("tls12") is True
    assert config.get("tls13") is False


def test_no_features(monkeypatch):
    monkeypatch.setattr(WorkManager, "run", work_manager_run)

    cmd = "tlsmate scan --port=1000 127.0.0.1 --no-features"
    sys.argv = cmd.split()
    command.main()
    config = TlsMate.instance.config
    workers = []
    _ = [workers.extend(pool) for pool in WorkManager._instance._prio_pool.values()]

    for feat in [
        "features",
        "compression",
        "dh_groups",
        "encrypt_then_mac",
        "ephemeral_key_reuse",
        "ext_master_secret",
        "fallback",
        "grease",
        "heartbeat",
        "ocsp_stapling",
        "renegotiation",
        "resumption",
    ]:
        assert config.get(feat) is False

    for worker in [
        ScanCompression,
        ScanDhGroups,
        ScanEncryptThenMac,
        ScanEphemeralKeyReuse,
        ScanExtendedMasterSecret,
        ScanDowngrade,
        ScanGrease,
        ScanHeartbeat,
        ScanOcspStapling,
        ScanRenegotiation,
        ScanResumption,
    ]:
        assert worker not in workers


def test_no_features2(monkeypatch):
    monkeypatch.setattr(WorkManager, "run", work_manager_run)

    cmd = (
        "tlsmate scan --port=1000 127.0.0.1 "
        "--no-features "
        "--no-compression "
        "--no-dh-groups "
        "--no-encrypt-then-mac "
        "--no-ephemeral-key-reuse "
        "--no-ext-master-secret "
        "--no-fallback "
        "--no-grease "
        "--no-heartbeat "
        "--no-ocsp-stapling "
        "--no-renegotiation "
        "--no-resumption "
    )
    sys.argv = cmd.split()
    command.main()
    config = TlsMate.instance.config
    workers = []
    _ = [workers.extend(pool) for pool in WorkManager._instance._prio_pool.values()]

    for feat in [
        "features",
        "compression",
        "dh_groups",
        "encrypt_then_mac",
        "ephemeral_key_reuse",
        "ext_master_secret",
        "fallback",
        "grease",
        "heartbeat",
        "ocsp_stapling",
        "renegotiation",
        "resumption",
    ]:
        assert config.get(feat) is False

    for worker in [
        ScanCompression,
        ScanDhGroups,
        ScanEncryptThenMac,
        ScanEphemeralKeyReuse,
        ScanExtendedMasterSecret,
        ScanDowngrade,
        ScanGrease,
        ScanHeartbeat,
        ScanOcspStapling,
        ScanRenegotiation,
        ScanResumption,
    ]:
        assert worker not in workers


def test_some_features(monkeypatch):
    monkeypatch.setattr(WorkManager, "run", work_manager_run)

    cmd = "tlsmate scan --port=1000 127.0.0.1 --no-features " "--compression --fallback"
    sys.argv = cmd.split()
    command.main()
    config = TlsMate.instance.config
    workers = []
    _ = [workers.extend(pool) for pool in WorkManager._instance._prio_pool.values()]

    for feat in [
        "features",
        "dh_groups",
        "encrypt_then_mac",
        "ephemeral_key_reuse",
        "ext_master_secret",
        "grease",
        "heartbeat",
        "ocsp_stapling",
        "renegotiation",
        "resumption",
    ]:
        assert config.get(feat) is False

    assert config.get("compression") is True
    assert config.get("fallback") is True

    for worker in [
        ScanDhGroups,
        ScanEncryptThenMac,
        ScanEphemeralKeyReuse,
        ScanExtendedMasterSecret,
        ScanGrease,
        ScanHeartbeat,
        ScanOcspStapling,
        ScanRenegotiation,
        ScanResumption,
    ]:
        assert worker not in workers

    assert ScanCompression in workers
    assert ScanDowngrade in workers


def test_not_some_features(monkeypatch):
    monkeypatch.setattr(WorkManager, "run", work_manager_run)

    cmd = "tlsmate scan --port=1000 127.0.0.1 " "--no-compression --no-fallback"
    sys.argv = cmd.split()
    command.main()
    config = TlsMate.instance.config
    workers = []
    _ = [workers.extend(pool) for pool in WorkManager._instance._prio_pool.values()]

    for feat in [
        "features",
        "dh_groups",
        "encrypt_then_mac",
        "ephemeral_key_reuse",
        "ext_master_secret",
        "grease",
        "heartbeat",
        "ocsp_stapling",
        "renegotiation",
        "resumption",
    ]:
        assert config.get(feat) is True

    assert config.get("compression") is False
    assert config.get("fallback") is False

    for worker in [
        ScanDhGroups,
        ScanEncryptThenMac,
        ScanEphemeralKeyReuse,
        ScanExtendedMasterSecret,
        ScanGrease,
        ScanHeartbeat,
        ScanOcspStapling,
        ScanRenegotiation,
        ScanResumption,
    ]:
        assert worker in workers

    assert ScanCompression not in workers
    assert ScanDowngrade not in workers


def test_no_vulnerabilities(monkeypatch):
    monkeypatch.setattr(WorkManager, "run", work_manager_run)

    cmd = "tlsmate scan --port=1000 127.0.0.1 --no-vulnerabilities"
    sys.argv = cmd.split()
    command.main()
    config = TlsMate.instance.config
    workers = []
    _ = [workers.extend(pool) for pool in WorkManager._instance._prio_pool.values()]

    for vuln in [
        "ccs_injection",
        "heartbleed",
        "padding_oracle",
        "robot",
    ]:
        assert config.get(vuln) is False

    for worker in [
        ScanCcsInjection,
        ScanHeartbleed,
        ScanPaddingOracle,
        ScanRobot,
    ]:
        assert worker not in workers


def test_no_vulnerabilities2(monkeypatch):
    monkeypatch.setattr(WorkManager, "run", work_manager_run)

    cmd = (
        "tlsmate scan --port=1000 127.0.0.1 "
        "--no-ccs-injection "
        "--no-heartbleed "
        "--no-padding-oracle "
        "--no-robot "
    )
    sys.argv = cmd.split()
    command.main()
    config = TlsMate.instance.config
    workers = []
    _ = [workers.extend(pool) for pool in WorkManager._instance._prio_pool.values()]

    for vuln in [
        "ccs_injection",
        "heartbleed",
        "padding_oracle",
        "robot",
    ]:
        assert config.get(vuln) is False

    for worker in [
        ScanCcsInjection,
        ScanHeartbleed,
        ScanPaddingOracle,
        ScanRobot,
    ]:
        assert worker not in workers


def test_some_vulnerabilities2(monkeypatch):
    monkeypatch.setattr(WorkManager, "run", work_manager_run)

    cmd = (
        "tlsmate scan --port=1000 127.0.0.1 --no-vulnerabilities "
        "--heartbleed "
        "--padding-oracle "
    )
    sys.argv = cmd.split()
    command.main()
    config = TlsMate.instance.config
    workers = []
    _ = [workers.extend(pool) for pool in WorkManager._instance._prio_pool.values()]

    for vuln in ["heartbleed", "padding_oracle"]:
        assert config.get(vuln) is True

    for vuln in ["ccs_injection", "robot"]:
        assert config.get(vuln) is False

    for worker in [ScanHeartbleed, ScanPaddingOracle]:
        assert worker in workers

    for worker in [ScanCcsInjection, ScanRobot]:
        assert worker not in workers


def test_not_some_vulnerabilities(monkeypatch):
    monkeypatch.setattr(WorkManager, "run", work_manager_run)

    cmd = (
        "tlsmate scan --port=1000 127.0.0.1 " "--no-heartbleed " "--no-padding-oracle "
    )
    sys.argv = cmd.split()
    command.main()
    config = TlsMate.instance.config
    workers = []
    _ = [workers.extend(pool) for pool in WorkManager._instance._prio_pool.values()]

    for vuln in ["heartbleed", "padding_oracle"]:
        assert config.get(vuln) is False

    for vuln in ["ccs_injection", "robot"]:
        assert config.get(vuln) is True

    for worker in [ScanHeartbleed, ScanPaddingOracle]:
        assert worker not in workers

    for worker in [ScanCcsInjection, ScanRobot]:
        assert worker in workers

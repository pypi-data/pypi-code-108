# -*- coding: utf-8 -*-
"""Module for the scan plugin
"""
# import basic stuff
from pathlib import Path
import argparse
from typing import Any

# import own stuff
import tlsmate.config as conf
import tlsmate.plugin as plg
import tlsmate.structs as structs
import tlsmate.utils as utils
import tlsmate.workers.base_vulnerabilities as base_vulnerabilities
import tlsmate.workers.ccs_injection as ccs_injection
import tlsmate.workers.compression as compression
import tlsmate.workers.dh_params as dh_params
import tlsmate.workers.downgrade as downgrade
import tlsmate.workers.encrypt_then_mac as encrypt_then_mac
import tlsmate.workers.ephemeral_key_reuse as ephemeral_key_reuse
import tlsmate.workers.eval_cipher_suites as eval_cipher_suites
import tlsmate.workers.grease as grease
import tlsmate.workers.heartbeat as heartbeat
import tlsmate.workers.heartbleed as heartbleed
import tlsmate.workers.master_secret as master_secret
import tlsmate.workers.ocsp_stapling as ocsp_stapling
import tlsmate.workers.padding_oracle as padding_oracle
import tlsmate.workers.renegotiation as renegotiation
import tlsmate.workers.resumption as resumption
import tlsmate.workers.robot as robot
import tlsmate.workers.scanner_info as scanner_info
import tlsmate.workers.server_profile as server_profile
import tlsmate.workers.sig_algo as sig_algo
import tlsmate.workers.supported_groups as supported_groups
import tlsmate.workers.text_server_profile as text_server_profile


class ArgPort(plg.Plugin):
    """Argument for port.
    """

    config = conf.config_port
    cli_args = plg.Args(
        "--port",
        default=None,
        help="the port number of the host [0-65535]. Defaults to 443.",
        type=int,
    )

    @classmethod
    def args_parsed(
        cls,
        args: Any,
        parser: argparse.ArgumentParser,
        subcommand: str,
        config: conf.Configuration,
    ) -> None:
        if args.port is not None and (args.port < 0 or args.port > 0xFFFF):
            parser.error("port must be in the range [0-65535]")
        super().args_parsed(args, parser, subcommand, config)


class ArgInterval(plg.Plugin):
    """Argument for interval.
    """

    config = conf.config_interval
    cli_args = plg.Args(
        "--interval",
        default=0,
        help="the interval in milliseconds between two handshakes.",
        type=int,
    )


class ArgIpv6Preference(plg.Plugin):
    """Argument for IPv6 preference.
    """

    config = conf.config_ipv6_preference
    cli_args = plg.Args(
        "--ipv6-preference",
        help="prefers resolved IPv6 addresses over IPv4. Defaults to False.",
        action=utils.BooleanOptionalAction,
    )


class ArgKeyLogFile(plg.Plugin):
    """Argument for key logging file.
    """

    config = conf.config_key_log_file
    cli_args = plg.Args(
        "--key-log-file",
        default=None,
        help=(
            "write to a key log file which can be used by wireshark to decode "
            "encrypted traffic."
        ),
    )


class ArgProgress(plg.Plugin):
    """Argument for progress.
    """

    config = conf.config_progress
    cli_args = plg.Args(
        "--progress",
        help="provides a progress indicator. Defaults to False.",
        action=utils.BooleanOptionalAction,
    )


class ArgProxy(plg.Plugin):
    """Argument for proxy.
    """

    config = conf.config_proxy
    cli_args = plg.Args(
        "--proxy",
        type=str,
        help=(
            "the URL of the proxy. Must include the scheme and may include the user, "
            "password and port, e.g.: `http://user:password@myproxy.net:3128`."
        ),
    )


class ArgSni(plg.Plugin):
    """Argument for sni.
    """

    config = conf.config_sni
    cli_args = plg.Args(
        "--sni",
        type=str,
        help=(
            "the server name indication, i.e., the domain name of the server to "
            "contact. If not given, the value will be taken from the host "
            "parameter. This parameter is useful, if the host is given as an "
            "IP address."
        ),
    )


class ArgHost(plg.Plugin):
    """Argument for host.
    """

    config = conf.config_host
    cli_args = plg.Args(
        "host",
        help=(
            "the target host. Can be given as a domain name or as an IPv4/IPv6 address."
        ),
        type=str,
    )


class GroupBasicScan(plg.Plugin):
    """Group for basic arguments.
    """

    plugins = [
        ArgPort,
        ArgInterval,
        ArgIpv6Preference,
        ArgKeyLogFile,
        ArgProgress,
        ArgProxy,
        ArgSni,
        ArgHost,
    ]


class ArgReadProfile(plg.Plugin):
    """Argument for read-profile.
    """

    config = structs.ConfigItem("read_profile", type=str, default=None)
    cli_args = plg.Args(
        "--read-profile",
        type=str,
        help=(
            "JSON/Yaml file to read the server profile from. The format will be "
            "determined automatically."
        ),
    )
    workers = [server_profile.ReadProfileWorker]


class ArgWriteProfile(plg.Plugin):
    """Argument for write-profile.
    """

    config = structs.ConfigItem("write_profile", type=str, default=None)
    cli_args = plg.Args(
        "--write-profile",
        type=str,
        help=(
            "writes the server profile to the given file. If no file is given, "
            'the profile will be dumped to STDOUT (unless "--format=none" is '
            "given)."
        ),
    )


class ArgFormat(plg.Plugin):
    """Argument for format.
    """

    config = structs.ConfigItem("format", type=str, default="text")
    cli_args = plg.Args(
        "--format",
        choices=["text", "html", "json", "yaml", "none"],
        help=('the output format of the server profile. Defaults to "text".'),
        default=None,
    )

    @classmethod
    def args_parsed(cls, args, parser, subcommand, config):
        super().args_parsed(args, parser, subcommand, config)
        format_type = config.get("format")
        if format_type in ["text", "html"]:
            plg.WorkManager.register(text_server_profile.TextProfileWorker)
        elif format_type in ["json", "yaml"]:
            plg.WorkManager.register(server_profile.DumpProfileWorker)


class ArgColor(plg.Plugin):
    """Argument for color.
    """

    config = structs.ConfigItem("color", type=bool, default=True)
    cli_args = plg.Args(
        "--color",
        help=(
            "use colored console output. Only used if --format=text is given. "
            "Defaults to True."
        ),
        action=utils.BooleanOptionalAction,
    )


class ArgStyle(plg.Plugin):
    """Argument for style.
    """

    _DEFAULT_STYLE = Path(__file__).parent / "../styles/default.yaml"
    config = structs.ConfigItem(
        "style", type=str, default=str(_DEFAULT_STYLE.resolve())
    )
    cli_args = plg.Args(
        "--style",
        type=str,
        help=(
            "a yaml file defining the text output and the color scheme used if "
            "--format=text or --format=html is given. If not given, the internal "
            "default file will be used."
        ),
    )


class GroupServerProfile(plg.Plugin):
    """Argument group for server profile arguments.
    """

    group = plg.Args(title="Server profile options")
    plugins = [
        ArgWriteProfile,
        ArgFormat,
        ArgColor,
        ArgStyle,
    ]


class ArgCaCerts(plg.Plugin):
    """Argument for CA certs.
    """

    config = conf.config_ca_certs
    cli_args = plg.Args(
        "--ca-certs",
        nargs="*",
        type=str,
        help=(
            "list of root-ca certificate files. Each file may contain multiple "
            "root-CA certificates in PEM format. Certificate chains received from "
            "the server will be validated against this set of root certificates."
        ),
    )


class ArgClientKey(plg.Plugin):
    """Argument for client keys.
    """

    config = conf.config_client_key
    cli_args = plg.Args(
        "--client-key",
        type=str,
        nargs="*",
        help=(
            "a list of files containing the client private keys in PEM format. "
            "Used for client authentication."
        ),
        default=None,
    )


class ArgClientChain(plg.Plugin):
    """Argument for client certificate chains.
    """

    config = conf.config_client_chain
    cli_args = plg.Args(
        "--client-chain",
        type=str,
        nargs="*",
        help=(
            "a list of files containing the certificate chain used for client "
            "authentication in PEM format. The number of given files must be the "
            "same than the number of given client key files. This first given "
            "chain file corresponds to the first given client key file, and so on."
        ),
    )


class ArgCrl(plg.Plugin):
    """Argument for CRL.
    """

    config = conf.config_crl
    cli_args = plg.Args(
        "--crl",
        help=(
            "download the CRL to check for the certificate revocation status. "
            "Defaults to True."
        ),
        action=utils.BooleanOptionalAction,
    )


class ArgOcsp(plg.Plugin):
    """Argument for OCSP.
    """

    config = conf.config_ocsp
    cli_args = plg.Args(
        "--ocsp",
        help=(
            "query the OCSP servers for checking the certificate "
            "revocation status. Defaults to True."
        ),
        action=utils.BooleanOptionalAction,
    )


class GroupX509(plg.Plugin):
    """Argument group for X509 arguments.
    """

    group = plg.Args(title="X509 certificates options")
    plugins = [ArgCaCerts, ArgClientKey, ArgClientChain, ArgCrl, ArgOcsp]

    @classmethod
    def args_parsed(cls, args, parser, subcommand, config):
        if (args.client_key is not None) or (args.client_chain is not None):
            if (args.client_key is None) or (args.client_chain is None):
                parser.error(
                    "if --client-key is given, --client-chain must be given as well, "
                    "and vice versa"
                )
            if len(args.client_key) != len(args.client_chain):
                parser.error(
                    "number of arguments for --client-key and --client-chain must "
                    "be identical"
                )

        super().args_parsed(args, parser, subcommand, config)


class ArgSslv2(plg.Plugin):
    """Argument for SSLv2.
    """

    config = structs.ConfigItem("sslv2", type=bool, default=None)
    cli_args = plg.Args(
        "--sslv2",
        help="scan for protocol version SSLv2",
        action=utils.BooleanOptionalAction,
    )


class ArgSslv3(plg.Plugin):
    """Argument for SSLv3.
    """

    config = structs.ConfigItem("sslv3", type=bool, default=None)
    cli_args = plg.Args(
        "--sslv3",
        help="scan for protocol version SSLv3",
        action=utils.BooleanOptionalAction,
    )


class ArgTls10(plg.Plugin):
    """Argument for TLS1.0.
    """

    config = structs.ConfigItem("tls10", type=bool, default=None)
    cli_args = plg.Args(
        "--tls10",
        help="scan for protocol version TLS1.0",
        action=utils.BooleanOptionalAction,
    )


class ArgTls11(plg.Plugin):
    """Argument for TLS1.1.
    """

    config = structs.ConfigItem("tls11", type=bool, default=None)
    cli_args = plg.Args(
        "--tls11",
        help="scan for protocol version TLS1.1",
        action=utils.BooleanOptionalAction,
    )


class ArgTls12(plg.Plugin):
    """Argument for TLS1.2.
    """

    config = structs.ConfigItem("tls12", type=bool, default=None)
    cli_args = plg.Args(
        "--tls12",
        help="scan for protocol version TLS1.2",
        action=utils.BooleanOptionalAction,
    )


class ArgTls13(plg.Plugin):
    """Argument for TLS1.3.
    """

    config = structs.ConfigItem("tls13", type=bool, default=None)
    cli_args = plg.Args(
        "--tls13",
        help="scan for protocol version TLS1.3",
        action=utils.BooleanOptionalAction,
    )


class GroupTlsVersions(plg.Plugin):
    """Argument group for TLS versions.
    """

    group = plg.Args(
        title="TLS protocol versions",
        description=(
            "The following options specify the TLS protocol versions to scan. "
            "By default all versions will be scanned, but if one version is "
            "explicitly set to true, all other versions will be defaulted to false."
        ),
    )
    plugins = [ArgSslv2, ArgSslv3, ArgTls10, ArgTls11, ArgTls12, ArgTls13]

    @classmethod
    def args_parsed(cls, args, parser, subcommand, config):
        super().args_parsed(args, parser, subcommand, config)
        default = all([config.get(vers.config.name) is None for vers in cls.plugins])
        enabled = False
        for vers in cls.plugins:
            val = config.get(vers.config.name)
            if val is None:
                val = default
                config.set(vers.config.name, default)
            enabled = enabled or val

        if not enabled:
            parser.error("at least one TLS version must be given")


class ArgFeatures(plg.Plugin):
    """Argument for Features.
    """

    config = structs.ConfigItem("features", type=bool, default=True)
    cli_args = plg.Args(
        "--features",
        help=(
            "specifies whether to include or exclude all features in the scan. "
            "Per feature this behavior can be overruled by its specific command "
            "line option below. "
            "Defaults to true if no specific feature is enabled, otherwise it "
            "defaults to false."
        ),
        action=utils.BooleanOptionalAction,
    )


class ArgCompression(plg.Plugin):
    """Argument for compression feature.
    """

    config = structs.ConfigItem("compression", type=bool, default=None)
    cli_args = plg.Args(
        "--compression",
        help="scan for compression support",
        action=utils.BooleanOptionalAction,
    )
    workers = [compression.ScanCompression]


class ArgDhGroup(plg.Plugin):
    """Argument for DH groups.
    """

    config = structs.ConfigItem("dh_groups", type=bool, default=None)
    cli_args = plg.Args(
        "--dh-groups",
        help="scan for finite field DH groups (only TL1.0 - TLS1.2)",
        action=utils.BooleanOptionalAction,
    )
    workers = [dh_params.ScanDhGroups]


class ArgEncThenMac(plg.Plugin):
    """Argument for encrypt-then-mac extension.
    """

    config = structs.ConfigItem("encrypt_then_mac", type=bool, default=None)
    cli_args = plg.Args(
        "--encrypt-then-mac",
        help="scan for encrypt-then-mac support (only TL1.0 - TLS1.2)",
        action=utils.BooleanOptionalAction,
    )
    workers = [encrypt_then_mac.ScanEncryptThenMac]


class ArgEphemKeyReuse(plg.Plugin):
    """Argument for ephemeral key reuse.
    """

    config = structs.ConfigItem("ephemeral_key_reuse", type=bool, default=None)
    cli_args = plg.Args(
        "--ephemeral-key-reuse",
        help="scan for reuse of ephemeral keys",
        action=utils.BooleanOptionalAction,
    )
    workers = [ephemeral_key_reuse.ScanEphemeralKeyReuse]


class ArgExtMasterSecret(plg.Plugin):
    """Argument for extended-master-secret extension.
    """

    config = structs.ConfigItem("ext_master_secret", type=bool, default=None)
    cli_args = plg.Args(
        "--ext-master-secret",
        help="scan for extended master secret support (only TL1.0 - TLS1.2)",
        action=utils.BooleanOptionalAction,
    )
    workers = [master_secret.ScanExtendedMasterSecret]


class ArgFallback(plg.Plugin):
    """Argument for fallback.
    """

    config = structs.ConfigItem("fallback", type=bool, default=None)
    cli_args = plg.Args(
        "--fallback",
        help="scan for downgrade attack prevention (TLS_FALLBACK_SCSV)",
        action=utils.BooleanOptionalAction,
    )
    workers = [downgrade.ScanDowngrade]


class ArgGrease(plg.Plugin):
    """Argument for GREASE.
    """

    config = structs.ConfigItem("grease", type=bool, default=None)
    cli_args = plg.Args(
        "--grease",
        help="scan for unknown parameter tolerance",
        action=utils.BooleanOptionalAction,
    )
    workers = [grease.ScanGrease]


class ArgHeartbeat(plg.Plugin):
    """Argument for heartbeat extension.
    """

    config = structs.ConfigItem("heartbeat", type=bool, default=None)
    cli_args = plg.Args(
        "--heartbeat",
        help="scan for heartbeat support",
        action=utils.BooleanOptionalAction,
    )
    workers = [heartbeat.ScanHeartbeat]


class ArgOcspStapling(plg.Plugin):
    """Argument for OCSP stapling.
    """

    config = structs.ConfigItem("ocsp_stapling", type=bool, default=None)
    cli_args = plg.Args(
        "--ocsp-stapling",
        help="scan for OCSP stapling support",
        action=utils.BooleanOptionalAction,
    )
    workers = [ocsp_stapling.ScanOcspStapling]


class ArgRenegotiation(plg.Plugin):
    """Argument for renegotiation feature.
    """

    config = structs.ConfigItem("renegotiation", type=bool, default=None)
    cli_args = plg.Args(
        "--renegotiation",
        help="scan for renegotiation support (SSL30 - TLS1.2)",
        action=utils.BooleanOptionalAction,
    )
    workers = [renegotiation.ScanRenegotiation]


class ArgResumption(plg.Plugin):
    """Argument for resumption feature.
    """

    config = structs.ConfigItem("resumption", type=bool, default=None)
    cli_args = plg.Args(
        "--resumption",
        help=(
            "scan for resumption support (SSL30 - TLS1.2) and for PSK support (TLS1.3)"
        ),
        action=utils.BooleanOptionalAction,
    )
    workers = [resumption.ScanResumption]


class GroupFeatures(plg.Plugin):
    """Argument group for features.
    """

    group = plg.Args(title="Feature to include into the scan")
    plugins = [
        ArgFeatures,
        ArgCompression,
        ArgDhGroup,
        ArgEncThenMac,
        ArgEphemKeyReuse,
        ArgExtMasterSecret,
        ArgFallback,
        ArgGrease,
        ArgHeartbeat,
        ArgOcspStapling,
        ArgRenegotiation,
        ArgResumption,
    ]

    @classmethod
    def args_parsed(cls, args, parser, subcommand, config):
        super().args_parsed(args, parser, subcommand, config)

        plugins = cls.plugins[1:]
        default = config.get(ArgFeatures.config.name)
        if default is None:
            default = not any(config.get(feat.config.name) for feat in plugins)

        for feat in plugins:
            val = config.get(feat.config.name)
            if val is None:
                config.set(feat.config.name, default)
                if default and feat.workers:
                    for worker in feat.workers:
                        plg.WorkManager.register(worker)


class ArgVulnerabilities(plg.Plugin):
    """Argument for Vulnerabilities.
    """

    config = structs.ConfigItem("vulnerabilities", type=bool, default=True)
    cli_args = plg.Args(
        "--vulnerabilities",
        help=(
            "specifies whether to include or exclude all vulnerabilities in the "
            "scan. Per vulnerability this behavior can be overruled by its "
            "specific command line option below. Defaults to true if no specific "
            "vulnerability is enabled, otherwise it defaults to false."
        ),
        action=utils.BooleanOptionalAction,
    )


class ArgCcsInjection(plg.Plugin):
    """Argument for CCS-injection vulnerability.
    """

    config = structs.ConfigItem("ccs_injection", type=bool, default=None)
    cli_args = plg.Args(
        "--ccs-injection",
        help="scan for vulnerability CCS-injection (only TL1.0 - TLS1.2)",
        action=utils.BooleanOptionalAction,
    )
    workers = [ccs_injection.ScanCcsInjection]


class ArgHeartbleed(plg.Plugin):
    """Argument for heartbleed vulnerability.
    """

    config = structs.ConfigItem("heartbleed", type=bool, default=None)
    cli_args = plg.Args(
        "--heartbleed",
        help="scan for the Heartbleed vulnerability CVE-2014-0160",
        action=utils.BooleanOptionalAction,
    )
    workers = [heartbleed.ScanHeartbleed]


class ArgPaddingOracle(plg.Plugin):
    """Argument for CBC padding oracles.
    """

    config = structs.ConfigItem("padding_oracle", type=bool, default=None)
    cli_args = plg.Args(
        "--padding-oracle",
        help="scan for CBC padding oracles",
        action=utils.BooleanOptionalAction,
    )
    workers = [padding_oracle.ScanPaddingOracle]


class ArgPaddingOracleAccuracy(plg.Plugin):
    """Argument for oracle accuracy.
    """

    config = structs.ConfigItem("oracle_accuracy", type=str, default="medium")
    cli_args = plg.Args(
        "--oracle-accuracy",
        help=(
            "the accuracy of the scan for CBC padding oracles. "
            "low: scan application data records for each TLS version with minimal "
            "set of cipher suites (fastest). "
            "medium: scan application data records for each TLS version and cipher "
            "suite combination (slower). "
            "high: scan application data, handshake and alert records for each TLS "
            "version and cipher suite combination (slowest). "
            "Default is medium."
        ),
        choices=["low", "medium", "high"],
        default="medium",
    )


class ArgRobot(plg.Plugin):
    """Argument for ROBOT vulnerability.
    """

    config = structs.ConfigItem("robot", type=bool, default=None)
    cli_args = plg.Args(
        "--robot",
        help=(
            "scan for ROBOT vulnerability CVE-2017-13099, etc. (only TL1.0 - TLS1.2)"
        ),
        action=utils.BooleanOptionalAction,
    )
    workers = [robot.ScanRobot]


class GroupVulnerabilities(plg.Plugin):
    """Argument group vulnerabilities.
    """

    group = plg.Args(title="Vulnerabilities to scan for")
    plugins = [
        ArgVulnerabilities,
        ArgCcsInjection,
        ArgHeartbleed,
        ArgPaddingOracle,
        ArgPaddingOracleAccuracy,
        ArgRobot,
    ]

    @classmethod
    def args_parsed(cls, args, parser, subcommand, config):
        super().args_parsed(args, parser, subcommand, config)

        plugins = cls.plugins[:]
        plugins.remove(ArgVulnerabilities)
        plugins.remove(ArgPaddingOracleAccuracy)

        default = config.get(ArgVulnerabilities.config.name)
        if default is None:
            default = not any(config.get(vuln.config.name) for vuln in plugins)

        base_vuln = False
        for vuln in plugins:
            val = config.get(vuln.config.name)
            if val is None:
                config.set(vuln.config.name, default)
                if default and vuln.workers:
                    for worker in vuln.workers:
                        plg.WorkManager.register(worker)
                        base_vuln = True

        if base_vuln:
            plg.WorkManager.register(base_vulnerabilities.ScanBaseVulnerabilities)


@plg.BaseCommand.extend
class SubcommandScan(plg.Plugin):
    """CLI plugin to perform a scan against a TLS server.
    """

    subcommand = plg.Args("scan", help="performs a TLS server scan")
    plugins = [
        GroupBasicScan,
        GroupX509,
        GroupTlsVersions,
        GroupFeatures,
        GroupVulnerabilities,
        GroupServerProfile,
    ]
    workers = [
        scanner_info.ScanStart,
        eval_cipher_suites.ScanCipherSuites,
        supported_groups.ScanSupportedGroups,
        sig_algo.ScanSigAlgs,
        scanner_info.ScanEnd,
    ]

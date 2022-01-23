# -*- coding: utf-8 -*-
"""Module for displaying the server profile in (colored) text format
"""
# import basic stuff
import sys
import enum
from dataclasses import dataclass
from typing import List, Callable, Dict, Optional, Any

# import own stuff
import tlsmate.pdu as pdu
import tlsmate.plugin as plg
import tlsmate.server_profile as server_profile
import tlsmate.tls as tls
import tlsmate.utils as utils
import tlsmate.version as vers

# import other stuff
import colorama  # type: ignore


class Color(tls.ExtendedEnum):
    GREEN = enum.auto()
    RED = enum.auto()
    BLUE = enum.auto()
    WHITE = enum.auto()
    BLACK = enum.auto()
    MAGENTA = enum.auto()
    CYAN = enum.auto()
    YELLOW = enum.auto()


class FontStyle:
    html = False

    def __init__(self, color=None, bold=False):
        self.color = color
        self.bold = bold

    def decorate(self, txt, with_orig_len=False):
        orig_len = len(str(txt))
        if self.html:
            if self.bold:
                txt = f"<b>{txt}</b>"

            if self.color:
                txt = f"<font color={self.color.name.lower()}>{txt}</font>"

        else:
            if self.color:
                txt = f"{getattr(colorama.Fore, self.color.name)}{txt}"

            if self.bold:
                txt = f"{colorama.Style.BRIGHT}{txt}"

            if self.color or self.bold:
                txt = f"{txt}{colorama.Style.RESET_ALL}"

        if with_orig_len:
            return txt, orig_len

        else:
            return txt


@dataclass
class Style:
    GOOD: FontStyle = FontStyle(color=Color.GREEN)
    NEUTRAL: FontStyle = FontStyle()
    SOSO: FontStyle = FontStyle(color=Color.YELLOW, bold=True)
    BAD: FontStyle = FontStyle(color=Color.RED)
    HEADLINE: FontStyle = FontStyle(color=Color.MAGENTA, bold=True)
    BOLD: FontStyle = FontStyle(bold=True)
    ERROR: FontStyle = FontStyle(color=Color.RED, bold=True)


def merge_styles(styles: List[Style]) -> FontStyle:
    """Returns the "worst" style from a given list

    Arguments:
        styles: the list of style strings
    """
    for style in [Style.ERROR, Style.BAD, Style.SOSO, Style.NEUTRAL, Style.GOOD]:
        if style in styles:
            return style

    raise ValueError("cannot merge styles")


def get_dict_value(
    profile: Dict[str, Any], *keys: str, default: Optional[Any] = None
) -> Any:
    """Save function to get an item from a nested dict

    Arguments:
        profile: the dict to start with
        *keys: a list the keys to descent to the wanted item of the profile
        default: the value to return if a key does not exist. Defaults to None.

    Returns:
        the item
    """

    if not profile:
        return default

    for key in keys:
        if key in profile:
            profile = profile[key]

        else:
            return default

    return profile


def get_style(profile: Dict[str, Any], *keys: str) -> FontStyle:
    """Get the style string from a nested dict, descending according to the keys

    The leaf must be in ["good", "neutral", "soso", "bad", "headline", "bold", "reset",
    "error"] (case insensitive). These style names are translated to the corresponding
    ANSI escape code.

    Arguments:
        profile: the nested dict
        *keys: the keys applied in sequence to descent to the style

    Returns:
        ANSI escape code string. If anything fails, Style.ERROR is returned.
    """
    return getattr(
        Style, get_dict_value(profile, *keys, default="error").upper(), Style.ERROR
    )


def get_style_applied(
    txt: str, profile: Dict[str, Any], *keys: str, **kwargs: Any
) -> str:
    """Descent into a nested dict and apply the found style to the given text.

    Arguments:
        txt (str): the text to decorate
        profile (dict): the nested dict
        *keys (str): the keys to descent into the nested dict

    Returns:
        str: the given text, decorated with the found ANSI escape code.
    """

    return get_style(profile, *keys).decorate(txt, **kwargs)


def get_styled_text(data: Dict[str, Any], *path: str, **kwargs: Any) -> str:
    """Comfortable way to use common structure to apply a style to a text.

    The item determined by data and path must be a dict with the following structure:
    {
        "txt": str,
        "style": str
    }
    The text given by the "txt" item will be decorated with the ANSI escape code
    which related to the "style" item.

    Arguments:
        data: the nested dict to use
        *path: the keys to descent into the nested dict

    Returns:
        the "txt" string decorated with the "style" style.
    """
    prof = get_dict_value(data, *path)
    if not prof:
        return Style.ERROR.decorate("???", **kwargs)

    return get_style_applied(get_dict_value(prof, "txt"), prof, "style", **kwargs)


def get_cert_ext(
    cert: server_profile.SPCertificate, name: str
) -> Optional[server_profile.SPCertExtension]:
    """Extract the given extension from a certificate.

    Arguments:
        cert: the certificate object
        name: the name of the extension

    Returns:
        the extension or None if not found
    """
    if not hasattr(cert, "extensions"):
        return None

    for ext in cert.extensions:
        if ext.name == name:
            return ext

    return None


class TextProfileWorker(plg.Worker):
    """Worker class which serializes a server profile.
    """

    name = "text_profile_dumper"
    descr = "dump the scan results"
    prio = 1002

    _callbacks: List[Callable[["TextProfileWorker"], None]] = []

    @classmethod
    def augment_output(cls, callback: Callable) -> Callable:
        """Decorator which can be used to register additional callbacks.

        Arguments:
            callback (callable): the callback to register. After the TextProfileWorker
            is finished with its output, the registered callbacks will be called with
            the TextProfileWorker object as its only argument. No return value is
            expected from the callback.
        """
        cls._callbacks.append(callback)
        return callback

    def _parse_style(self):
        if not self._style:
            return

        if "style" in self._style:
            for style in [
                "good",
                "neutral",
                "soso",
                "bad",
                "headline",
                "bold",
                "error",
            ]:
                style_def = self._style["style"].get(style)
                if style_def is not None:
                    color = None
                    fg = style_def.get("fg")
                    if fg in [c.name.lower() for c in Color.all()]:
                        color = Color.str2enum(fg.upper())

                    bold = style_def.get("style") == "bright"
                    setattr(Style, style.upper(), FontStyle(color=color, bold=bold))

    def _read_style(self):
        self._style = utils.deserialize_data(self.style_file)
        self._parse_style()

    def style_for_cipher_suite(self, cs):
        det = utils.get_cipher_suite_details(cs)
        key_style = get_style(self._style, "key_exchange", det.key_algo.name)
        cipher_style = get_style(self._style, "symmetric_ciphers", det.cipher.name)
        mac_style = get_style(self._style, "macs", det.mac.name)
        return merge_styles([key_style, cipher_style, mac_style])

    def _style_for_assym_key_size(self, bits, style_entry):
        key_sizes = get_dict_value(self._style, style_entry)
        if not key_sizes:
            return Style.NEUTRAL

        for prof in key_sizes:
            if bits >= prof["size"]:
                break

        return get_style(prof, "style")

    def style_for_rsa_dh_key_size(self, bits):
        return self._style_for_assym_key_size(bits, "assymetric_key_sizes")

    def style_for_ec_key_size(self, bits):
        return self._style_for_assym_key_size(bits, "assymetric_ec_key_sizes")

    def _print_tlsmate(self):
        print(Style.HEADLINE.decorate("A TLS configuration scanner (and more)"))
        print()
        table = utils.Table(indent=2, sep="  ")
        table.row("tlsmate version", vers.__version__)
        table.row("repository", "https://gitlab.com/guballa/tlsmate")
        table.dump()
        print(
            "  Please file bug reports at https://gitlab.com/guballa/tlsmate/-/issues"
        )
        print()

    def _print_scan_info(self):
        if not hasattr(self.server_profile, "scan_info"):
            return

        scan_info = self.server_profile.scan_info
        self._start_date = scan_info.start_date
        print(Style.HEADLINE.decorate("Basic scan information"))
        print()
        print(f"  command: {scan_info.command}")
        table = utils.Table(indent=2, sep="  ")
        table.row("tlsmate version", f"{scan_info.version} (producing the scan)")
        table.row("scan start timestamp", str(scan_info.start_date))
        table.row("scan duration", f"{scan_info.run_time} seconds")
        table.row("applied style", self.style_file)
        table.row(
            "style description",
            get_dict_value(self._style, "description", "short", default="-"),
        )
        table.dump()
        print()

    def _print_host(self):
        if not hasattr(self.server_profile, "server"):
            return

        host_info = self.server_profile.server
        print(Style.HEADLINE.decorate("Scanned host"))
        print()
        table = utils.Table(indent=2, sep="  ")
        name_resolution = hasattr(host_info, "name_resolution")
        if name_resolution:
            host = host_info.name_resolution.domain_name

        else:
            host = host_info.ip

        table.row("host", host)
        table.row("port", str(host_info.port))
        table.row("SNI", host_info.sni)
        if name_resolution:
            if hasattr(host_info.name_resolution, "ipv4_addresses"):
                addresses = ", ".join(host_info.name_resolution.ipv4_addresses)
                table.row("IPv4 addresses", addresses)

            if hasattr(host_info.name_resolution, "ipv6_addresses"):
                addresses = ", ".join(host_info.name_resolution.ipv6_addresses)
                table.row("IPv6 addresses", addresses)

        proxy = getattr(host_info, "proxy", None)
        if proxy:
            table.row("HTTP-proxy", proxy)

        table.dump()
        print()

    def _print_server_malfunctions(self):
        malfunctions = getattr(self.server_profile, "server_malfunctions", None)
        if not malfunctions:
            return

        print(Style.HEADLINE.decorate("Severe server implementation flaws"))
        print()
        for malfunction in malfunctions:
            add_info = []
            if hasattr(malfunction, "message"):
                add_info.append(f"message: {malfunction.message.name}")

            if hasattr(malfunction, "extension"):
                add_info.append(f"extension: {malfunction.extension.name}")

            txt = "  - " + get_dict_value(
                self._style,
                "server_malfunction",
                malfunction.issue.name,
                default=malfunction.issue.description,
            )
            if add_info:
                txt += f" ({'; '.join(add_info)})"

            print(Style.BAD.decorate(txt))

        print()

    def _print_versions(self):
        if not hasattr(self.server_profile, "versions"):
            return

        print(Style.HEADLINE.decorate("TLS protocol versions"))
        print()
        table = utils.Table(indent=2, sep="  ")
        for version_prof in self.server_profile.versions:
            table.row(
                version_prof.version.name,
                get_styled_text(
                    self._style,
                    "version",
                    version_prof.version.name,
                    "supported",
                    version_prof.support.name,
                ),
            )

        table.dump()
        print()

    def _print_cipher_suites(self):
        if not hasattr(self.server_profile, "versions"):
            return

        cipher_hash = {}
        print(Style.HEADLINE.decorate("Cipher suites"))

        for version in self._prof_versions:
            version_prof = self.server_profile.get_version_profile(version)
            if version is tls.Version.SSL20:
                cipher_list = version_prof.cipher_kinds
                pref_txt = ""
                style_txt = (
                    ""
                    if cipher_list
                    else Style.BAD.decorate("no cipher kinds provided by server")
                )
                chacha_txt = ""
            else:
                cipher_list = version_prof.ciphers.cipher_suites
                order = version_prof.ciphers.server_preference

                struct = get_dict_value(
                    self._style, "version", version.name, "cipher_order", order.name
                )
                pref_txt = get_dict_value(struct, "txt", default="???")
                style_txt = get_style_applied(pref_txt, struct, "style")

                chacha_pref = getattr(
                    version_prof.ciphers, "chacha_poly_preference", None
                )
                if chacha_pref:
                    struct = get_dict_value(
                        self._style,
                        "version",
                        version.name,
                        "chacha_preference",
                        chacha_pref.name,
                    )
                    chacha_txt = get_style_applied(
                        get_dict_value(struct, "txt", default="???"), struct, "style"
                    )

                else:
                    chacha_txt = ""

            hashed = hash((style_txt, chacha_txt, tuple(cipher_list)))
            if hashed in cipher_hash:
                cipher_hash[hashed]["versions"].append(str(version))

            else:
                cipher_hash[hashed] = {
                    "versions": [str(version)],
                    "table": utils.Table(indent=4, sep="  "),
                    "preference": style_txt,
                    "chacha_preference": chacha_txt,
                }
                all_good = bool(cipher_list)
                for cs in cipher_list:
                    if version is tls.Version.SSL20:
                        cipher_hash[hashed]["table"].row(
                            f"0x{cs.value:06x}", Style.BAD.decorate(cs)
                        )

                    else:
                        style = self.style_for_cipher_suite(cs)
                        if style is not Style.GOOD:
                            all_good = False

                        cipher_hash[hashed]["table"].row(
                            f"0x{cs.value:04x}", style.decorate(cs.name)
                        )

                if all_good:
                    cipher_hash[hashed]["preference"] = Style.NEUTRAL.decorate(pref_txt)

        for values in cipher_hash.values():
            versions = Style.BOLD.decorate(", ".join(values["versions"]))
            print(f"\n  {versions}:")
            print(f'    {values["preference"]}')
            if values["chacha_preference"] != "":
                print(f'    {values["chacha_preference"]}')

            values["table"].dump()

        print()

    def _print_supported_groups(self):
        if not hasattr(self.server_profile, "versions"):
            return

        prof_grps = get_dict_value(self._style, "supported_groups", "groups")
        group_hash = {}
        for version in self._prof_versions:
            prof_version = get_dict_value(self._style, "supported_groups", version.name)
            version_prof = self.server_profile.get_version_profile(version)
            group_prof = getattr(version_prof, "supported_groups", None)
            if group_prof is None:
                continue

            if not hasattr(group_prof, "groups"):
                continue

            supported = getattr(group_prof, "extension_supported", None)
            if supported is None:
                supp_txt = None

            else:
                prof = get_dict_value(prof_version, "support", supported.name)
                supp_txt = get_dict_value(prof, "txt", default="???")
                if supp_txt:
                    supp_txt = get_style_applied(supp_txt, prof, "style")

            preference = getattr(group_prof, "server_preference", None)
            if preference is None:
                pref_txt = None

            else:
                prof = get_dict_value(prof_version, "preference", preference.name)
                pref_txt = get_dict_value(prof, "txt", default="???")
                if pref_txt:
                    if prof_grps and all(
                        [prof_grps[grp.name] == "good" for grp in group_prof.groups]
                    ):
                        pref_style = Style.NEUTRAL

                    else:
                        pref_style = get_style(prof, "style")

                    pref_txt = pref_style.decorate(pref_txt)

            advertised = getattr(group_prof, "groups_advertised", None)
            if advertised is None:
                ad_txt = None

            else:
                prof = get_dict_value(prof_version, "advertised", advertised.name)
                ad_txt = get_dict_value(prof, "txt", default="???")
                if ad_txt:
                    ad_txt = get_style_applied(ad_txt, prof, "style")

            combined = (supp_txt, pref_txt, ad_txt, tuple(group_prof.groups))
            hashed = hash(combined)
            if hashed in group_hash:
                group_hash[hashed]["versions"].append(str(version))

            else:
                group_hash[hashed] = {"versions": [str(version)], "combined": combined}

        if not group_hash:
            return

        print(Style.HEADLINE.decorate("Supported groups"))
        for group in group_hash.values():
            versions = ", ".join(group["versions"])
            print(f"\n  {Style.BOLD.decorate(versions)}:")
            supp_txt, pref_txt, ad_txt, groups = group["combined"]

            if supp_txt:
                print(f"    {supp_txt}")

            if pref_txt:
                print(f"    {pref_txt}")

            if ad_txt:
                print(f"    {ad_txt}")

            print("    supported groups:")
            table = utils.Table(indent=6, sep="  ")
            for grp in groups:
                table.row(
                    f"0x{grp.value:02x}",
                    get_style_applied(grp.name, prof_grps, grp.name),
                )

            table.dump()

        print()

    def _print_sig_algos(self):
        if not hasattr(self.server_profile, "versions"):
            return

        algo_hash = {}
        for version in self._prof_versions:
            version_prof = self.server_profile.get_version_profile(version)
            if not hasattr(version_prof, "signature_algorithms"):
                continue

            algo_prof = version_prof.signature_algorithms
            hashed = hash(tuple(algo_prof.algorithms))
            if hashed in algo_hash:
                algo_hash[hashed]["versions"].append(str(version))

            else:
                algo_hash[hashed] = {
                    "versions": [str(version)],
                    "algos": algo_prof.algorithms,
                }

        if not algo_hash:
            return

        print(Style.HEADLINE.decorate("Signature algorithms"))
        for algo in algo_hash.values():
            versions = ", ".join(algo["versions"])
            print(f"\n  {Style.BOLD.decorate(versions)}:")

            if not algo["algos"]:
                print("    no signature algorithms supported")

            else:
                print("    signature algorithms:")
                table = utils.Table(indent=6, sep="  ")
                if algo["algos"]:
                    for alg in algo["algos"]:
                        table.row(
                            f"0x{alg.value:04x}",
                            get_style_applied(
                                alg.name, self._style, "signature_schemes", alg.name
                            ),
                        )

                table.dump()

        print()

    def _print_dh_groups(self):
        if not hasattr(self.server_profile, "versions"):
            return

        dh_groups = {}
        for version in self._prof_versions:
            version_prof = self.server_profile.get_version_profile(version)
            dh_prof = getattr(version_prof, "dh_group", None)
            if dh_prof is None:
                continue

            name = getattr(dh_prof, "name", None)
            combined = (name, dh_prof.size)
            hashed = hash(combined)
            if hashed in dh_groups:
                dh_groups[hashed]["versions"].append(str(version))

            else:
                dh_groups[hashed] = {
                    "versions": [str(version)],
                    "combined": combined,
                }

        if dh_groups:
            print(Style.HEADLINE.decorate("DH groups (finite field)"))
            for values in dh_groups.values():
                versions = ", ".join(values["versions"])
                print(f"\n  {Style.BOLD.decorate(versions)}:")
                name, size = values["combined"]
                if name is None:
                    name = "unknown group"
                txt = f"{name} ({size} bits)"
                style = self.style_for_rsa_dh_key_size(size)
                print(f"    {style.decorate(txt)}")

            print()

    def _print_common_features(self, feat_prof):

        if not any(
            hasattr(feat_prof, prop)
            for prop in [
                "ocsp_stapling",
                "ocsp_multi_stapling",
                "heartbeat",
                "downgrade_attack_prevention",
            ]
        ):
            return

        print(f'  {Style.BOLD.decorate("Common features")}')
        table = utils.Table(indent=4, sep="  ")

        ocsp_state = getattr(feat_prof, "ocsp_stapling", None)
        if ocsp_state is not None:
            table.row(
                "OCSP stapling (status_request)",
                get_styled_text(self._style, "ocsp_stapling", ocsp_state.name),
            )

        ocsp_state = getattr(feat_prof, "ocsp_multi_stapling", None)
        if ocsp_state is not None:
            table.row(
                "OCSP multi stapling (status_request_v2)",
                get_styled_text(self._style, "ocsp_multi_stapling", ocsp_state.name),
            )

        hb_state = getattr(feat_prof, "heartbeat", None)
        if hb_state is not None:
            table.row(
                "Heartbeat", get_styled_text(self._style, "heartbeat", hb_state.name)
            )

        fallback = getattr(feat_prof, "downgrade_attack_prevention", None)
        if fallback is not None:
            table.row(
                "Downgrade attack prevention",
                get_styled_text(self._style, "fallback", fallback.name),
            )

        table.dump()
        print()

    def _print_features_tls12(self, feat_prof):
        if not any(
            hasattr(feat_prof, prop)
            for prop in [
                "compression",
                "scsv_renegotiation",
                "encrypt_then_mac",
                "extended_master_secret",
                "insecure_renegotiation",
                "secure_renegotation",
                "session_id",
                "session_ticket",
            ]
        ):
            return

        print(f'  {Style.BOLD.decorate("Features for TLS1.2 and below")}')
        table = utils.Table(indent=4, sep="  ")
        if hasattr(feat_prof, "compression"):
            if (len(feat_prof.compression) == 1) and feat_prof.compression[
                0
            ] is tls.CompressionMethod.NULL:
                compr = tls.ScanState.FALSE

            else:
                compr = tls.ScanState.TRUE

            table.row(
                "compression", get_styled_text(self._style, "compression", compr.name)
            )

        etm = getattr(feat_prof, "encrypt_then_mac", None)
        if etm is not None:
            table.row(
                "encrypt-then-mac",
                get_styled_text(self._style, "encrypt_then_mac", etm.name),
            )

        ems = getattr(feat_prof, "extended_master_secret", None)
        if ems is not None:
            table.row(
                "extended master secret",
                get_styled_text(self._style, "extended_master_secret", ems.name),
            )

        insec_reneg = getattr(feat_prof, "insecure_renegotiation", None)
        if insec_reneg is not None:
            table.row(
                "insecure renegotiation",
                get_styled_text(
                    self._style, "insecure_renegotiation", insec_reneg.name
                ),
            )

        sec_reneg = getattr(feat_prof, "secure_renegotation", None)
        if sec_reneg is not None:
            table.row(
                "secure renegotiation (extension)",
                get_styled_text(self._style, "secure_renegotiation", sec_reneg.name),
            )

        scsv = getattr(feat_prof, "scsv_renegotiation", None)
        if scsv is not None:
            table.row(
                "secure renegotiation (SCSV)",
                get_styled_text(self._style, "scsv_renegotiation", scsv.name),
            )

        session_id = getattr(feat_prof, "session_id", None)
        if session_id is not None:
            table.row(
                "resumption with session_id",
                get_styled_text(self._style, "session_id", session_id.name),
            )

        session_ticket = getattr(feat_prof, "session_ticket", None)
        if session_ticket is not None:
            txt = get_styled_text(self._style, "session_ticket", session_ticket.name)
            life_time = getattr(feat_prof, "session_ticket_lifetime", None)
            if life_time is None:
                add_txt = ""

            else:
                add_txt = f", life time: {feat_prof.session_ticket_lifetime} seconds"

            table.row("resumption with session ticket", f"{txt}{add_txt}")

        table.dump()
        print()

    def _print_features_tls13(self, feat_prof):
        if not any(
            hasattr(feat_prof, prop) for prop in ["resumption_psk", "early_data"]
        ):
            return

        print(f'  {Style.BOLD.decorate("Features for TLS1.3")}')

        table = utils.Table(indent=4, sep="  ")
        resumption_psk = getattr(feat_prof, "resumption_psk", None)
        if resumption_psk is not None:
            txt = get_styled_text(self._style, "resumption_psk", resumption_psk.name)
            life_time = getattr(feat_prof, "psk_lifetime", None)
            if life_time is None:
                add_txt = ""

            else:
                add_txt = f", life time: {feat_prof.psk_lifetime} seconds"

            table.row("resumption with PSK", f"{txt}{add_txt}")

        early_data = getattr(feat_prof, "early_data", None)
        if early_data is not None:
            table.row(
                "early data (0-RTT)",
                get_styled_text(self._style, "early_data", early_data.name),
            )

        table.dump()
        print()

    def _print_grease(self, grease_prof):
        grease = (
            ("version_tolerance", "version"),
            ("cipher_suite_tolerance", "cipher_suite"),
            ("extension_tolerance", "extension"),
            ("group_tolerance", "group"),
            ("sig_algo_tolerance", "sig_algo"),
            ("psk_mode_tolerance", "psk_mode"),
        )

        caption = Style.BOLD.decorate(
            "Server tolerance to unknown values (GREASE, RFC8701)"
        )
        print(f"  {caption}")
        table = utils.Table(indent=4, sep="  ")

        for prof_prop, style_prop in grease:
            val = getattr(grease_prof, prof_prop, tls.ScanState.UNDETERMINED)
            table.row(
                get_dict_value(
                    self._style, "grease", style_prop, "descr", default="???"
                ),
                get_styled_text(self._style, "grease", style_prop, val.name),
            )

        table.dump()
        print()

    def _print_ephemeral_key_reuse(self):
        if not hasattr(self.server_profile.features, "ephemeral_key_reuse"):
            return

        ekr = self.server_profile.features.ephemeral_key_reuse
        print(Style.BOLD.decorate("  Ephemeral key reuse"))
        table = utils.Table(indent=4, sep="  ")
        table.row(
            "DHE key reuse (TLS1.2 or below)",
            get_styled_text(
                self._style, "ephemeral_key_reuse", ekr.tls12_dhe_reuse.name
            ),
        )
        table.row(
            "ECDHE key reuse (TLS1.2 or below)",
            get_styled_text(
                self._style, "ephemeral_key_reuse", ekr.tls12_ecdhe_reuse.name
            ),
        )
        table.row(
            "DHE key reuse (TLS1.3)",
            get_styled_text(
                self._style, "ephemeral_key_reuse", ekr.tls13_dhe_reuse.name
            ),
        )
        table.row(
            "ECDHE key reuse (TLS1.3)",
            get_styled_text(
                self._style, "ephemeral_key_reuse", ekr.tls13_ecdhe_reuse.name
            ),
        )
        table.dump()
        print()

    def _print_features(self):
        feat_prof = getattr(self.server_profile, "features", None)
        if not feat_prof:
            return

        print(Style.HEADLINE.decorate("Features"))
        print()

        self._print_common_features(feat_prof)

        versions = self.server_profile.get_versions()
        wanted = {
            tls.Version.SSL30,
            tls.Version.TLS10,
            tls.Version.TLS11,
            tls.Version.TLS12,
        }
        if wanted.intersection(set(versions)):
            self._print_features_tls12(feat_prof)

        if tls.Version.TLS13 in versions:
            self._print_features_tls13(feat_prof)

        if hasattr(feat_prof, "grease"):
            self._print_grease(feat_prof.grease)

        self._print_ephemeral_key_reuse()

    def _print_cert(self, cert, idx):
        items = [str(getattr(cert, "version", ""))]
        self_signed = getattr(cert, "self_signed", None)
        if self_signed is tls.ScanState.TRUE:
            items.append("self-signed")

        from_trust_store = getattr(cert, "from_trust_store", tls.ScanState.FALSE)
        if from_trust_store is tls.ScanState.TRUE:
            items.append("certificate taken from trust store")

        print(f'  Certificate #{idx}: {", ".join(items)}')
        table = utils.Table(indent=4, sep="  ")

        issues = getattr(cert, "issues", None)
        if issues:
            issue_txt = []
            style = get_style(self._style, "certificate", "issues")
            for issue in issues:
                folded_lines = utils.fold_string(issue, max_length=100)
                issue_txt.append("- " + folded_lines.pop(0))
                issue_txt.extend(["  " + item for item in folded_lines])

            table.row("Issues", style.decorate(issue_txt[0]))
            for line in issue_txt[1:]:
                table.row("", style.decorate(line))

        table.row("Serial number", f"{cert.serial_number_int} (integer)")
        table.row("", f"{pdu.string(cert.serial_number_bytes)} (hex)")
        lines = utils.fold_string(cert.subject, max_length=100, sep=",")
        table.row("Subject", lines.pop(0))
        for line in lines:
            table.row("", line)

        san_ext = get_cert_ext(cert, "SubjectAlternativeName")
        if san_ext is not None:
            sans = " ".join([str(name) for name in san_ext.subj_alt_names])
            lines = utils.fold_string(sans, max_length=80)
            table.row("SubjectAltName (SAN)", lines.pop(0))
            for line in lines:
                table.row("", line)

        if hasattr(cert, "subject_matches"):
            table.row(
                "URI matches",
                get_styled_text(
                    self._style,
                    "certificate",
                    "subject_matches",
                    cert.subject_matches.name,
                ),
            )

        ev = getattr(cert, "extended_validation", tls.ScanState.NA)
        if ev is not tls.ScanState.NA:
            table.row(
                "Extended validation",
                get_styled_text(
                    self._style, "certificate", "extended_validation", ev.name
                ),
            )

        lines = utils.fold_string(cert.issuer, max_length=100, sep=",")
        table.row("Issuer", lines.pop(0))
        for line in lines:
            table.row("", line)

        sig_algo = getattr(cert, "signature_algorithm", None)
        if sig_algo is not None:
            if self_signed is tls.ScanState.TRUE:
                txt = sig_algo.name

            else:
                txt = get_style_applied(
                    sig_algo.name, self._style, "signature_schemes", sig_algo.name
                )

            table.row("Signature algorithm", txt)

        pub_key = getattr(cert, "public_key", None)
        if pub_key is not None:
            key_size = pub_key.key_size
            if pub_key.key_type in [
                tls.SignatureAlgorithm.RSA,
                tls.SignatureAlgorithm.DSA,
            ]:
                style = self.style_for_rsa_dh_key_size(key_size)

            else:
                style = self.style_for_ec_key_size(key_size)

            table.row(
                "Public key",
                f'{pub_key.key_type}, {style.decorate(f"{key_size} bits")}',
            )

        key_usage_ext = get_cert_ext(cert, "KeyUsage")
        if key_usage_ext is not None:
            usage_txt = ", ".join([str(usage) for usage in key_usage_ext.key_usage])
            table.row("Key usage", usage_txt)

        ext_key_usage_ext = get_cert_ext(cert, "ExtendedKeyUsage")
        if ext_key_usage_ext is not None:
            usage_txt = ", ".join(
                [str(usage) for usage in ext_key_usage_ext.extended_key_usage]
            )
            table.row("Extended key usage", usage_txt)

        if hasattr(cert, "not_valid_before"):
            valid = tls.ScanState.TRUE
            valid_from = tls.ScanState.TRUE
            if cert.not_valid_before > self._start_date:
                valid_from = tls.ScanState.FALSE
                valid = tls.ScanState.FALSE

            valid_to = tls.ScanState.TRUE
            if cert.not_valid_after < self._start_date:
                valid_to = tls.ScanState.FALSE
                valid = tls.ScanState.FALSE

            from_txt = get_style_applied(
                cert.not_valid_before,
                self._style,
                "certificate",
                "validity",
                valid_from.name,
                "style",
            )
            to_txt = get_style_applied(
                cert.not_valid_after,
                self._style,
                "certificate",
                "validity",
                valid_to.name,
                "style",
            )
            valid_txt = get_styled_text(
                self._style, "certificate", "validity", valid.name
            )
            table.row(
                "Validity period",
                (
                    f"{from_txt} - {to_txt} ({cert.validity_period_days} days), "
                    f"{valid_txt}"
                ),
            )

        crl_distr = get_cert_ext(cert, "CRLDistributionPoints")
        if crl_distr is not None:
            crls = []
            for distr_schema in crl_distr.distribution_points:
                for gen_name in distr_schema.full_name:
                    if hasattr(gen_name, "uri"):
                        crls.append(gen_name.uri)

            table.row("CRLs", crls.pop(0))
            for crl in crls:
                table.row("", crl)

        crl_status = getattr(cert, "crl_revocation_status", None)
        if crl_status is not None:
            table.row(
                "CRL revocation status",
                get_styled_text(
                    self._style, "certificate", "crl_status", crl_status.name
                ),
            )

        ocsp_status = getattr(cert, "ocsp_revocation_status", None)
        if ocsp_status is not None:
            table.row(
                "OCSP revocation status",
                get_styled_text(
                    self._style, "certificate", "ocsp_status", ocsp_status.name
                ),
            )

            text = []
            must_staple = tls.ScanState.FALSE
            if cert.ocsp_must_staple is tls.ScanState.TRUE:
                text.append("must staple")
                must_staple = tls.ScanState.TRUE

            if cert.ocsp_must_staple_multi is tls.ScanState.TRUE:
                text.append("must multi-staple")
                must_staple = tls.ScanState.TRUE

            txt = get_dict_value(
                self._style,
                "certificate",
                "must_staple",
                must_staple.name,
                "txt",
                default="???",
            )
            if text:
                txt += f" ({', '.join(text)})"

            table.row(
                "OCSP must staple",
                get_style_applied(
                    txt,
                    self._style,
                    "certificate",
                    "must_staple",
                    must_staple.name,
                    "style",
                ),
            )

        if hasattr(cert, "fingerprint_sha1"):
            table.row("Fingerprint SHA1", pdu.string(cert.fingerprint_sha1))

        if hasattr(cert, "fingerprint_sha256"):
            table.row("Fingerprint SHA256", pdu.string(cert.fingerprint_sha256))

        table.dump()
        print()

    def _print_certificates(self):
        cert_chains = getattr(self.server_profile, "cert_chains", None)
        if not cert_chains:
            return

        print(Style.HEADLINE.decorate("Certificate chains"))
        for cert_chain in cert_chains:
            print()
            if hasattr(cert_chain, "successful_validation"):
                valid_txt = get_styled_text(
                    self._style,
                    "cert_chain",
                    "validation",
                    cert_chain.successful_validation.name,
                )

            else:
                valid_txt = ""

            head_line = Style.BOLD.decorate(f"Certificate chain #{cert_chain.id}:")
            print(f"  {head_line} {valid_txt}")
            if hasattr(cert_chain, "issues"):
                style = get_style(self._style, "cert_chain", "issues")
                print("    Issues:")
                for issue in cert_chain.issues:
                    lines = utils.fold_string(issue, max_length=100)
                    txt = "    - " + "\n      ".join(lines)
                    print(style.decorate(txt))

            if hasattr(cert_chain, "root_cert_transmitted"):
                txt = get_styled_text(
                    self._style,
                    "cert_chain",
                    "root_cert_transmitted",
                    cert_chain.root_cert_transmitted.name,
                )
                print("    ", txt)

            for idx, cert in enumerate(cert_chain.cert_chain, start=1):
                self._print_cert(cert, idx)

            root_cert = getattr(cert_chain, "root_certificate", None)
            if root_cert:
                self._print_cert(root_cert, len(cert_chain.cert_chain) + 1)

    def _print_vulnerabilities(self):
        vuln_prof = getattr(self.server_profile, "vulnerabilities", None)
        if not vuln_prof:
            return

        table = utils.Table(indent=2, sep="  ")
        print(Style.HEADLINE.decorate("Vulnerabilities"))
        print()

        beast = getattr(vuln_prof, "beast", None)
        if beast is not None:
            table.row(
                "BEAST (CVE-2011-3389)",
                get_styled_text(self._style, "vulnerabilities", "beast", beast.name),
            )

        ccs = getattr(vuln_prof, "ccs_injection", None)
        if ccs is not None:
            table.row(
                "CCS injection (CVE-2014-0224)",
                get_styled_text(
                    self._style, "vulnerabilities", "ccs_injection", ccs.name
                ),
            )

        crime = getattr(vuln_prof, "crime", None)
        if crime is not None:
            table.row(
                "CRIME (CVE-2012-4929)",
                get_styled_text(self._style, "vulnerabilities", "crime", crime.name),
            )

        freak = getattr(vuln_prof, "freak", None)
        if freak is not None:
            table.row(
                "FREAK (CVE-2015-0204)",
                get_styled_text(self._style, "vulnerabilities", "freak", freak.name),
            )

        hb = getattr(vuln_prof, "heartbleed", None)
        if hb is not None:
            table.row(
                "Heartbleed (CVE-2014-0160)",
                get_styled_text(self._style, "vulnerabilities", "heartbleed", hb.name),
            )

        logjam = getattr(vuln_prof, "logjam", None)
        if logjam is not None:
            table.row(
                "Logjam (CVE-2015-0204)",
                get_styled_text(self._style, "vulnerabilities", "logjam", logjam.name),
            )

        robot = getattr(vuln_prof, "robot", None)
        if robot is not None:
            table.row(
                "ROBOT (CVE-2017-13099, ...)",
                get_styled_text(self._style, "vulnerabilities", "robot", robot.name),
            )

        sweet_32 = getattr(vuln_prof, "sweet_32", None)
        if sweet_32 is not None:
            table.row(
                "Sweet32 (CVE-2016-2183, CVE-2016-6329)",
                get_styled_text(
                    self._style, "vulnerabilities", "sweet_32", sweet_32.name
                ),
            )

        poodle = getattr(vuln_prof, "poodle", None)
        if poodle is not None:
            table.row(
                "POODLE (CVE-2014-3566)",
                get_styled_text(self._style, "vulnerabilities", "poodle", poodle.name),
            )

        tls_poodle = getattr(vuln_prof, "tls_poodle", None)
        if tls_poodle is not None:
            table.row(
                "TLS POODLE",
                get_styled_text(
                    self._style, "vulnerabilities", "tls_poodle", tls_poodle.name
                ),
            )

        lucky_minus_20 = getattr(vuln_prof, "lucky_minus_20", None)
        if lucky_minus_20 is not None:
            table.row(
                "Lucky-Minus-20 (CVE-2016-2107)",
                get_styled_text(
                    self._style,
                    "vulnerabilities",
                    "lucky_minus_20",
                    lucky_minus_20.name,
                ),
            )

        # cbc padding oracle shall be the last vulnerability in the list
        cbc_padding_oracle = getattr(vuln_prof, "cbc_padding_oracle", None)
        if cbc_padding_oracle:
            style_cbc = get_dict_value(
                self._style, "vulnerabilities", "cbc_padding_oracle"
            )
            vulnerable = getattr(cbc_padding_oracle, "vulnerable", None)
            txt = get_dict_value(
                style_cbc, "vulnerable", vulnerable.name, "txt", default="???"
            )
            oracles = getattr(cbc_padding_oracle, "oracles", None)
            if oracles:
                txt += f", number of oracles: {len(oracles)}"

            table.row(
                "CBC padding oracle",
                get_style_applied(
                    txt, style_cbc, "vulnerable", vulnerable.name, "style"
                ),
            )
            accuracy = getattr(cbc_padding_oracle, "accuracy", None)
            table.row(
                "  scan accuracy", get_styled_text(style_cbc, "accuracy", accuracy.name)
            )

        table.dump()
        if cbc_padding_oracle and oracles:
            style_oracle = get_dict_value(style_cbc, "oracle")
            for oracle in oracles:
                print("\n    oracle properties")
                table = utils.Table(indent=6, sep="  ")
                strong = getattr(oracle, "strong", None)
                table.row(
                    "strength", get_styled_text(style_oracle, "strong", strong.name),
                )
                observable = getattr(oracle, "observable", None)
                table.row(
                    "observable",
                    get_styled_text(style_oracle, "observable", observable.name),
                )
                oracle_types = getattr(oracle, "types", None)
                if oracle_types:
                    str_types = []
                    for oracle_type in oracle_types:
                        str_types.append(
                            get_dict_value(
                                style_oracle, "type", oracle_type.name, default="???"
                            )
                        )

                    table.row("oracle type(s)", str_types.pop(0))
                    for line in str_types:
                        table.row("", line)

                cipher_groups = getattr(oracle, "cipher_group", None)
                if cipher_groups:
                    str_group = []
                    max_len = 0
                    for group in cipher_groups:
                        version = getattr(group, "version", None)
                        version_str = version.name if version else "???"
                        cs = getattr(group, "cipher_suite", None)
                        cs_str = cs.name if cs else "???"
                        protocol = getattr(group, "record_protocol", None)
                        protocol_str = get_dict_value(
                            style_oracle,
                            "cipher_group",
                            "record_protocol",
                            protocol.name,
                        )
                        str_group.append((version_str, cs_str, protocol_str))
                        max_len = max(max_len, len(cs_str))
                        # str_group.append(f"  {version_str} {cs_str}   {protocol_str}")

                    txt = "cipher suite groups"
                    for version, cs, prot in str_group:
                        table.row(txt, f"{version} {cs:{max_len}} {prot}")
                        txt = ""

                table.dump()

        print()

    def run(self):
        self.style_file = self.config.get("style")
        self._read_style()
        if self.config.get("progress"):
            sys.stderr.write("\n")

        if self.config.get("format") == "html":
            FontStyle.html = True
            print("<pre>")

        else:
            colorama.init(strip=not self.config.get("color"))

        self._prof_versions = self.server_profile.get_versions()
        self._print_tlsmate()
        self._print_scan_info()
        self._print_host()
        self._print_server_malfunctions()
        self._print_versions()
        if self._prof_versions:
            self._print_cipher_suites()
            self._print_supported_groups()
            self._print_sig_algos()
            self._print_dh_groups()
            self._print_features()
            self._print_certificates()
            self._print_vulnerabilities()

        for callback in self._callbacks:
            callback(self)

        if self.config.get("format") == "html":
            print("</pre>")

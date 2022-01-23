# -*- coding: utf-8 -*-
"""Module scanning for base vulnerabilities

Actually, this is not a scan but rather an evaluation of the server profile.
The following vulnerabilities are treated:

    - BEAST (TLS1.0 enabled)
    - CRIME (compression enabled)
    - Sweet-32 (64-bit block ciphers [IDEA, 3DES])
    - FREAK: RSA export cipher suites
    - LogJam: DHE with 1024 or less bits

"""
# import basic stuff

# import own stuff
import tlsmate.plugin as plg
import tlsmate.tls as tls
import tlsmate.utils as utils

# import other stuff


class ScanBaseVulnerabilities(plg.Worker):
    name = "scan_base_vulnerabilities"
    descr = "scan for base vulnerabilities"
    prio = 40

    def _scan_beast(self):
        beast = False
        cipher_suites = self.server_profile.get_cipher_suites(tls.Version.TLS10)
        if cipher_suites:
            cs = utils.filter_cipher_suites(
                cipher_suites, cipher_type=[tls.CipherType.BLOCK]
            )
            beast = bool(cs)

        self.server_profile.vulnerabilities.beast = tls.ScanState(beast)

    def _scan_crime(self):
        crime = tls.ScanState.FALSE
        if hasattr(self.server_profile, "features"):
            if hasattr(self.server_profile.features, "compression"):
                compr = self.server_profile.features.compression
                null_compr = int(any([x.name == "NULL" for x in compr]))
                crime = tls.ScanState(len(compr) - null_compr)

            else:
                crime = tls.ScanState.UNDETERMINED

        else:
            crime = tls.ScanState.UNDETERMINED

        self.server_profile.vulnerabilities.crime = crime

    def _scan_sweet_32(self):
        prof_values = self.server_profile.get_profile_values(tls.Version.all())
        sweet_32 = tls.ScanState(
            bool(
                utils.filter_cipher_suites(
                    prof_values.cipher_suites,
                    cipher_prim=[
                        tls.CipherPrimitive.IDEA,
                        tls.CipherPrimitive.TRIPPLE_DES,
                    ],
                )
            )
        )
        self.server_profile.vulnerabilities.sweet_32 = sweet_32

    def _scan_freak(self):
        prof_values = self.server_profile.get_profile_values(tls.Version.all())
        freak = tls.ScanState(
            bool(
                utils.filter_cipher_suites(
                    prof_values.cipher_suites,
                    key_algo=[tls.KeyExchangeAlgorithm.RSA_EXPORT],
                )
            )
        )
        self.server_profile.vulnerabilities.freak = freak

    def _scan_logjam(self):
        logjam_na = True
        logjam_512 = False
        logjam_1024_common = False
        logjam_1024_cust = False

        for vers in self.server_profile.get_versions():
            vers_prof = self.server_profile.get_version_profile(vers)
            if hasattr(vers_prof, "dh_group"):
                logjam_na = False
                if vers_prof.dh_group.size <= 512:
                    logjam_512 = True
                    break

                elif vers_prof.dh_group.size <= 1024:
                    if hasattr(vers_prof.dh_group, "name"):
                        logjam_1024_common = True

                    else:
                        logjam_1024_cust = True

        if logjam_512:
            logjam = tls.Logjam.PRIME512

        elif logjam_1024_common:
            logjam = tls.Logjam.PRIME1024_COMMON

        elif logjam_1024_cust:
            logjam = tls.Logjam.PRIME1024_CUSTOMIZED

        elif logjam_na:
            # dh group not found in server profile. Check, if any DH(E) cipher suite
            # is supported by server. If so, it means the DH-param worker was not
            # used.
            cs = self.server_profile.get_profile_values(tls.Version.all()).cipher_suites
            if utils.filter_cipher_suites(
                cs,
                key_algo=[
                    tls.KeyExchangeAlgorithm.DHE_DSS,
                    tls.KeyExchangeAlgorithm.DHE_DSS_EXPORT,
                    tls.KeyExchangeAlgorithm.DHE_RSA,
                    tls.KeyExchangeAlgorithm.DHE_RSA_EXPORT,
                    tls.KeyExchangeAlgorithm.DH_ANON,
                ],
            ):
                logjam = tls.Logjam.UNDETERMINED

            else:
                logjam = tls.Logjam.NA

        else:
            logjam = tls.Logjam.OK

        self.server_profile.vulnerabilities.logjam = logjam

    def run(self):
        self.server_profile.allocate_vulnerabilities()
        self._scan_beast()
        self._scan_crime()
        self._scan_sweet_32()
        self._scan_freak()
        self._scan_logjam()

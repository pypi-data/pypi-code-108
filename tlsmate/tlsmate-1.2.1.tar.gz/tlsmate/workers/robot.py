# -*- coding: utf-8 -*-
"""Module scanning for the ROBOT vulnerability

Refer to CVE-2017-13099, etc.

Padding oracle for RSA-based key transport, refer to https://robotattack.org
"""
# import basic stuff
import math

# import own stuff
import tlsmate.msg as msg
import tlsmate.plugin as plg
import tlsmate.tls as tls
import tlsmate.utils as utils

# import other stuff


def _rsa_encrypt(msg, e, n, mod_bytes):
    return int(pow(msg, e, n)).to_bytes(mod_bytes, byteorder="big")


class ScanRobot(plg.Worker):
    name = "robot"
    descr = "scan for ROBOT vulnerability"
    prio = 41

    def _get_oracle_results(self, with_ccs):
        def cke_pre_serialization(message):
            message.rsa_encrypted_pms = self.enc_pms

        results = []
        for self.enc_pms in self._rsa_encrypted_pms:
            with self.client.create_connection() as conn:
                conn.send(msg.ClientHello)
                conn.wait(msg.ServerHello)
                conn.wait(msg.Certificate)
                conn.wait(msg.CertificateRequest, optional=True)
                conn.wait(msg.ServerHelloDone)
                conn.send(
                    msg.ClientKeyExchange, pre_serialization=cke_pre_serialization
                )
                self.premaster_secret = self.rnd_pms
                if with_ccs:
                    conn.send(msg.ChangeCipherSpec)
                    conn.send(msg.Finished)

                try:
                    rec_msg, rec_bytes = conn.wait_msg_bytes(msg.Any, timeout=1000)
                    results.append(hash(bytes(rec_bytes)))

                except Exception as exc:
                    results.append(hash(str(exc)))

        return results

    def _determine_status(self):
        for send_ccs_finished in [True, False]:
            results = self._get_oracle_results(send_ccs_finished)
            if len(set(results)) == 1:
                continue

            results2 = self._get_oracle_results(send_ccs_finished)
            for res1, res2 in zip(results, results2):
                if res1 != res2:
                    return tls.RobotVulnerability.INCONSITENT_RESULTS

            if results[1] == results[2] == results[3]:
                return tls.RobotVulnerability.WEAK_ORACLE
            return tls.RobotVulnerability.STRONG_ORACLE
        return tls.RobotVulnerability.NOT_VULNERABLE

    def run(self):
        values = self.server_profile.get_profile_values(
            [tls.Version.TLS10, tls.Version.TLS11, tls.Version.TLS12], full_hs=True
        )
        rsa_ciphers = utils.filter_cipher_suites(
            values.cipher_suites, key_algo=[tls.KeyExchangeAlgorithm.RSA]
        )
        if rsa_ciphers:
            self.client.init_profile(profile_values=values)
            self.client.profile.cipher_suites = rsa_ciphers
            with self.client.create_connection() as conn:
                conn.handshake()

            if not conn.handshake_completed:
                status = tls.RobotVulnerability.UNDETERMINED

            else:
                cert = conn.msg.server_certificate.chain.certificates[0]
                pub_nbrs = cert.parsed.public_key().public_numbers()
                modulus_bits = int(math.ceil(math.log(pub_nbrs.n, 2)))
                modulus_bytes = (modulus_bits + 7) // 8
                pad_len = (modulus_bytes - 48 - 3) * 2
                rnd_pad = ("abcd" * (pad_len // 2 + 1))[:pad_len]
                self.rnd_pms = (
                    "aa11223344556677889911223344556677889911223344"
                    "5566778899112233445566778899112233445566778899"
                )
                pms_good_in = int("0002" + rnd_pad + "00" + "0303" + self.rnd_pms, 16)
                # wrong first two bytes
                pms_bad_in1 = int("4117" + rnd_pad + "00" + "0303" + self.rnd_pms, 16)
                # 0x00 on a wrong position, also trigger older JSSE bug
                pms_bad_in2 = int("0002" + rnd_pad + "11" + self.rnd_pms + "0011", 16)
                # no 0x00 in the middle
                pms_bad_in3 = int("0002" + rnd_pad + "11" + "1111" + self.rnd_pms, 16)
                # wrong version number (according to Klima / Pokorny / Rosa paper)
                pms_bad_in4 = int("0002" + rnd_pad + "00" + "0202" + self.rnd_pms, 16)

                self._rsa_encrypted_pms = [
                    _rsa_encrypt(pms, pub_nbrs.e, pub_nbrs.n, modulus_bytes)
                    for pms in [
                        pms_good_in,
                        pms_bad_in1,
                        pms_bad_in2,
                        pms_bad_in3,
                        pms_bad_in4,
                    ]
                ]
                status = self._determine_status()

        else:
            status = tls.RobotVulnerability.NOT_APPLICABLE

        self.server_profile.allocate_vulnerabilities()
        self.server_profile.vulnerabilities.robot = status

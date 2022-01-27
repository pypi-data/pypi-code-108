import base64

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


class SignatureVerifier:
    ROX_CERTIFICATE_BASE64 = 'MIIDWDCCAkACCQDR039HDUMyzTANBgkqhkiG9w0BAQUFADBuMQswCQYDVQQHEwJjYTETMBEGA1UEChMKcm9sbG91dC5pbzERMA8GA1UECxMIc2VjdXJpdHkxFzAVBgNVBAMTDnd3dy5yb2xsb3V0LmlvMR4wHAYJKoZIhvcNAQkBFg9leWFsQHJvbGxvdXQuaW8wHhcNMTQwODE4MDkzNjAyWhcNMjQwODE1MDkzNjAyWjBuMQswCQYDVQQHEwJjYTETMBEGA1UEChMKcm9sbG91dC5pbzERMA8GA1UECxMIc2VjdXJpdHkxFzAVBgNVBAMTDnd3dy5yb2xsb3V0LmlvMR4wHAYJKoZIhvcNAQkBFg9leWFsQHJvbGxvdXQuaW8wggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDq8GMRFLyaQVDEdcHlYm7NnGrAqhLP2E/27W21yTQein7r8FOT/7jJ0PLpcGLw/3zDT5wzIJ3OtFy4HWre2hn7wmt+bI+bbS/9kKrmqkpjAj1+PwnB4lhEad27lolMCuz5purqi209k7q51IMdfq0/Ot7P/Bmp+LBNs2F4jMsPYxZUUYkVTAmPqgnwxuWoJZan/OGNjtj9OGg8eOcOfcyxC4GDR/Yail+kht4I/HHesSXVukqXntsbdgnXKFkX682TuFPc3pd8ly+6N6OSWpbNV8UmEVZygnxWT3vxBT2TWvFexbW52KOFY91wIkjt+IPEMPJBPPDiN9J2nuttvfMpAgMBAAEwDQYJKoZIhvcNAQEFBQADggEBAIXrD6YsIhZa6fYDAR8huP0V3BRwMKjeLGLCXLzvuPaoQGDhn4RJNgz3leNcomIkV/AwneeS9BXgBAcEKjNeLD+nW58RSRnAfxDT5cUtQgIeR6dFmEK05u+8j/cK3VO410xr0taNMbmJfEn07WjfCdcJS3hsGJuVmEUC85KYznbIcafQMGklLYArXYVnR3XKqzxcLohSPX99weujH5wt78Zy3pXxuYCDETwhgcCYCQaZz7mpvtSOub3JQT+Ir5cBSdyI1oPI2dIamUL5+ntTyll/1rbYj83qREw8PKA9Q0KIIgfpggy19TS9zknwOLz44wRdLyT2tFoaiRqHvm6JKaA='

    def verify(self, data, signature_base64):
        certificate_bytes = base64.b64decode(SignatureVerifier.ROX_CERTIFICATE_BASE64)
        cert = x509.load_der_x509_certificate(certificate_bytes, default_backend())
        rsa = cert.public_key()
        data_bytes = data.encode('utf-8')
        signature_bytes = base64.b64decode(signature_base64)
        try:
            rsa.verify(signature_bytes, data_bytes, padding.PKCS1v15(), hashes.SHA256())
        except InvalidSignature:
            return False

        return True

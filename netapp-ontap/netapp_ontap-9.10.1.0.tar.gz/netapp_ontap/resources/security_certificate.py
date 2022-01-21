r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
This API displays security certificate information and manages the certificates in ONTAP.
## Installing certificates in ONTAP
The security certificates GET request retrieves all of the certificates in the cluster.
## Examples
### Retrieving all certificates installed in the cluster with their common-names
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import SecurityCertificate

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(SecurityCertificate.get_collection(fields="common_name")))

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
[
    SecurityCertificate(
        {
            "common_name": "vs0",
            "svm": {"name": "vs0"},
            "uuid": "dad2363b-8ac0-11e8-9058-005056b482fc",
            "_links": {
                "self": {
                    "href": "/api/security/certificates/dad2363b-8ac0-11e8-9058-005056b482fc"
                }
            },
        }
    ),
    SecurityCertificate(
        {
            "common_name": "ROOT",
            "uuid": "1941e048-8ac1-11e8-9058-005056b482fc",
            "_links": {
                "self": {
                    "href": "/api/security/certificates/1941e048-8ac1-11e8-9058-005056b482fc"
                }
            },
        }
    ),
    SecurityCertificate(
        {
            "common_name": "gshancluster-4",
            "uuid": "5a3a77a8-892d-11e8-b7da-005056b482fc",
            "_links": {
                "self": {
                    "href": "/api/security/certificates/5a3a77a8-892d-11e8-b7da-005056b482fc"
                }
            },
        }
    ),
]

```
</div>
</div>

---
### Retrieving all certificates installed at cluster-scope with their common-names
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import SecurityCertificate

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(
        list(SecurityCertificate.get_collection(scope="cluster", fields="common_name"))
    )

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
[
    SecurityCertificate(
        {
            "scope": "cluster",
            "common_name": "ROOT",
            "uuid": "1941e048-8ac1-11e8-9058-005056b482fc",
            "_links": {
                "self": {
                    "href": "/api/security/certificates/1941e048-8ac1-11e8-9058-005056b482fc"
                }
            },
        }
    ),
    SecurityCertificate(
        {
            "scope": "cluster",
            "common_name": "gshancluster-4",
            "uuid": "5a3a77a8-892d-11e8-b7da-005056b482fc",
            "_links": {
                "self": {
                    "href": "/api/security/certificates/5a3a77a8-892d-11e8-b7da-005056b482fc"
                }
            },
        }
    ),
]

```
</div>
</div>

---
### Retrieving all certificates installed on a specific SVM with their common-names
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import SecurityCertificate

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(
        list(
            SecurityCertificate.get_collection(
                fields="common_name", **{"svm.name": "vs0"}
            )
        )
    )

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
[
    SecurityCertificate(
        {
            "common_name": "vs0",
            "svm": {"name": "vs0"},
            "uuid": "dad2363b-8ac0-11e8-9058-005056b482fc",
            "_links": {
                "self": {
                    "href": "/api/security/certificates/dad2363b-8ac0-11e8-9058-005056b482fc"
                }
            },
        }
    )
]

```
</div>
</div>

---
### Retrieving a certificate using its UUID for all fields
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import SecurityCertificate

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = SecurityCertificate(uuid="dad2363b-8ac0-11e8-9058-005056b482fc")
    resource.get(fields="*")
    print(resource)

```
<div class="try_it_out">
<input id="example3_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example3_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example3_result" class="try_it_out_content">
```
SecurityCertificate(
    {
        "hash_function": "sha256",
        "type": "server",
        "expiry_time": "2019-07-18T15:29:14-04:00",
        "scope": "svm",
        "common_name": "vs0",
        "svm": {"uuid": "d817293c-8ac0-11e8-9058-005056b482fc", "name": "vs0"},
        "uuid": "dad2363b-8ac0-11e8-9058-005056b482fc",
        "public_certificate": "-----BEGIN CERTIFICATE-----\nMIIDQjCCAiqgAwIBAgIIFUKNRc+Bz1YwDQYJKoZIhvcNAQELBQAwGzEMMAoGA1UE\nAxMDdnMwMQswCQYDVQQGEwJVUzAeFw0xODA3MTgxOTI5MTRaFw0xOTA3MTgxOTI5\nMTRaMBsxDDAKBgNVBAMTA3ZzMDELMAkGA1UEBhMCVVMwggEiMA0GCSqGSIb3DQEB\nAQUAA4IBDwAwggEKAoIBAQCqFQb27th2ACOmJvWgLh1xRzobSb2ZTQfO561faXQ3\nIbiT+rnRWXetd/s2+iCv91d9LW0NOmP3MN2f3SFbyze3dl7WrnVbjLmYuI9MfOxs\nfmA+Bh6gpap5Yn2YddqoV6rfNGAuUveNLArNl8wODk/mpawpEQ93QSa1Zfg1gnoH\nRFrYqiSYT06X5g6RbUuEl4LTGXspz+plU46Za0i6QyxtvZ4bneibffXN3IigpqI6\nTGUV8R/J3Ps338VxVmSO9ZXBZmvbcJVoysYNICl/oi3fgPZlnBv0tbswqg4FoZO/\nWT+XHGhLep6cr/Aqg7u6C4RfqbCwzB/XFKDIqnmAQkDBAgMBAAGjgYkwgYYwDAYD\nVR0TBAUwAwEB/zALBgNVHQ8EBAMCAQYwHQYDVR0OBBYEFN/AnH8qLxocTtumNHIn\nEN4IFIDBMEoGA1UdIwRDMEGAFN/AnH8qLxocTtumNHInEN4IFIDBoR+kHTAbMQww\nCgYDVQQDEwN2czAxCzAJBgNVBAYTAlVTgggVQo1Fz4HPVjANBgkqhkiG9w0BAQsF\nAAOCAQEAa0pUEepdeQnd2Amwg8UFyxayb8eu3E6dlptvtyp+xtjhIC7Dh95CVXhy\nkJS3Tsu60PGR/b2vc3MZtAUpcL4ceD8XntKPQgBlqoB4bRogCe1TnlGswRXDX5TS\ngMVrRjaWTBF7ikT4UjR05rSxcDGplQRqjnOthqi+yPT+29+8a4Uu6J+3Kdrflj4p\n1nSWpuB9EyxtuCILNqXA2ncH7YKtoeNtChKCchhvPcoTy6Opma6UQn5UMxstkvGT\nVGaN5TlRWv0yiqPXIQblSqXi/uQsuRPcHDu7+KWRFn08USa6QVo2mDs9P7R9dd0K\n9QAsTjTOF9PlAKgNxGoOJl2y0+48AA==\n-----END CERTIFICATE-----\n",
        "ca": "vs0",
        "key_size": 2048,
        "serial_number": "15428D45CF81CF56",
        "_links": {
            "self": {
                "href": "/api/security/certificates/dad2363b-8ac0-11e8-9058-005056b482fc"
            }
        },
    }
)

```
</div>
</div>

### Creating a certificate in a cluster
These certificates can be used to help administrators enable certificate-based authentication and to enable SSL-based communication to the cluster.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import SecurityCertificate

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = SecurityCertificate()
    resource.common_name = "TEST-SERVER"
    resource.type = "server"
    resource.post(hydrate=True)
    print(resource)

```

### Installing a certificate in a cluster
These certificates can be used to help administrators enable certificate-based authentication and to enable-SSL based communication to the cluster.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import SecurityCertificate

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = SecurityCertificate()
    resource.type = "server_ca"
    resource.public_certificate = (
        "-----BEGIN CERTIFICATE-----"
        "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"
        "cGzM7vRX+Bi6hG6H"
        "-----END CERTIFICATE-----"
    )
    resource.post(hydrate=True)
    print(resource)

```

---
### Installing a certificate on a specific SVM
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import SecurityCertificate

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = SecurityCertificate()
    resource.svm = {"name": "vs0"}
    resource.type = "server_ca"
    resource.public_certificate = (
        "-----BEGIN CERTIFICATE-----"
        "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"
        "cGzM7vRX+Bi6hG6H"
        "-----END CERTIFICATE-----"
    )
    resource.post(hydrate=True)
    print(resource)

```

---
### Deleting a certificate using its UUID
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import SecurityCertificate

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = SecurityCertificate(uuid="dad2363b-8ac0-11e8-9058-005056b482fc")
    resource.delete(fields="*")

```

### Signing a new certificate signing request using an existing CA certificate UUID
Once you have created a certificate of type "root_ca", you can use that certificate to act as a local Certificate Authority to sign new certificate signing requests. The following example signs a new certificate signing request using an existing CA certificate UUID. If successful, the API returns a signed certificate.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import SecurityCertificate

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = SecurityCertificate(uuid="253add53-8ac9-11e8-9058-005056b482fc")
    resource.sign(
        body={
            "signing_request": "-----BEGIN CERTIFICATE REQUEST-----\nMIICYTCCAUkCAQAwHDENMAsGA1UEAxMEVEVTVDELMAkGA1UEBhMCVVMwggEiMA0G\nCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQCiBCuVfbYHNdOO7vjRQja4JqL2cHqK\ndrlTj5hz9RVqFKZ7VPh8DSP9LoTbYWsvrTkbuD0Wi715MVQCsbkq/mHos+Y5lfqs\nNP5K92fc6EhBzBDYFgZGFntZYJjEG5MPerIUE7CfVy7o6sjWOlxeY33pjefObyvP\nBcJkBHg6SFJK/TDLvIYJkonLkJEOJoTI6++a3I/1bCMfUeuRtLU9ThWlna1kMMYK\n4T16/Bxgm4bha2U2jtosc0Wltnld/capc+eqRV07WVbMmEOTtop3cv0h3N0S6lbn\nFkd96DXzeGWbSHFHckeCZ9bOHhnVbfEa/efkPLx7ziMC8GtRHHlwbnK7AgMBAAGg\nADANBgkqhkiG9w0BAQsFAAOCAQEAf+rs1i5PHaOSI2HtTM+Hcv/p71yzgoLL+aeU\ntB0V4iuoXdqY8oQeWoPI92ci0K08JuSpu6D0DwCKlstfwuGkAA2b0Wr7ZDRonTUq\nmJ4j3O47MLysW4Db2LbGws/AuDsCIrBJDWHMpHaqsvRbpMx2xQ/V5oagUw5eGGpN\ne4fg/E2k9mGkpxwkUzT7w1RZirpND4xL+XTzpzeZqgalpXug4yjIXlI5hpRESZ9/\nAkGJSCWxI15IZdxxFVXlBcmm6WpJnnboqkcKeXz95GM6Re+oBy9tlgvwvlVd5s8uHX+bycFiZp09Wsm8Ev727MziZ+0II9nxwkDKsdPvam+KLI9hLQ==\n-----END CERTIFICATE REQUEST-----\n",
            "hash_function": "sha256",
        }
    )

```
<div class="try_it_out">
<input id="example8_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example8_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example8_result" class="try_it_out_content">
```
SecurityCertificate(
    {
        "public_certificate": "-----BEGIN CERTIFICATE-----\nMIIDBzCCAe+gAwIBAgIIFUKQpcqeaUAwDQYJKoZIhvcNAQELBQAwHDENMAsGA1UE\nAxMEUkFDWDELMAkGA1UEBhMCVVMwHhcNMTgwNzE4MjAzMTA1WhcNMTkwNzE4MjAz\nMTA1WjAcMQ0wCwYDVQQDEwRURVNUMQswCQYDVQQGEwJVUzCCASIwDQYJKoZIhvcN\nAQEBBQADggEPADCCAQoCggEBAKIEK5V9tgc1047u+NFCNrgmovZweop2uVOPmHP1\nFWoUpntU+HwNI/0uhNthay+tORu4PRaLvXkxVAKxuSr+Yeiz5jmV+qw0/kr3Z9zo\nSEHMENgWBkYWe1lgmMQbkw96shQTsJ9XLujqyNY6XF5jfemN585vK88FwmQEeDpI\nUkr9MMu8hgmSicuQkQ4mhMjr75rcj/VsIx9R65G0tT1OFaWdrWQwxgrhPXr8HGCb\nhuFrZTaO2ixzRaW2eV39xqlz56pFXTtZVsyYQ5O2indy/SHc3RLqVucWR33oNfN4\nZZtIcUdyR4Jn1s4eGdVt8Rr95+Q8vHvOIwLwa1EceXBucrsCAwEAAaNNMEswCQYD\nVR0TBAIwADAdBgNVHQ4EFgQUJMPxjeW1G76TbbD2tXB8dwSpI3MwHwYDVR0jBBgw\nFoAUu5aH0mWR4cFoN9i7k96d2op3sPwwDQYJKoZIhvcNAQELBQADggEBAI5ai+Zi\nFQZUXRTqJCgHsgBThARneVWQYkYpyAXmTR7QeLf1d4ZHL33i4xWCqX3uvW7SFJLe\nZajT2AVmgiDbaWIHtDtvqz1BY78PSgUwPH/IyARTEOBeikp6KdwMPraehDIBMAcc\nANY58wXiTBbsl8UMD6tGecgnzw6sxlMmadGvrfJeJmgY4zert6NNvgtTPhcZQdLS\nE0fGzHS6+3ajCCfEEhPNPeR9D0e5Me81i9EsQGENrnJzTci8rzXPuF4bC3gghrK1\nI1+kmJQ1kLYVUcsntcrIiHmNvtPFJY6stjDgQKS9aDd/THhPpokPtZoCmE6PDxh6\nR+dO6C0hcDKHFzA=\n-----END CERTIFICATE-----\n"
    }
)

```
</div>
</div>

### Generate a new Certificate Signing Request (CSR)
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import SecurityConfig

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = SecurityConfig()
    resource.certificate_signing_request(
        body={
            "algorithm": "rsa",
            "extended_key_usage": ["serverauth"],
            "hash_function": "sha256",
            "key_usage": ["digitalsignature"],
            "security_strength": "112",
            "subject_alternatives": {
                "dns": ["*.example.com", "*.example1.com"],
                "email": ["abc@example.com", "abc@example1.com"],
                "ip": ["10.225.34.223", "10.225.34.224"],
                "uri": ["http://example.com", "http://example1.com"],
            },
            "subject_name": "C=US,O=NTAP,CN=test.domain.com",
        }
    )

```

---
"""

import asyncio
from datetime import datetime
import inspect
from typing import Callable, Iterable, List, Optional, Union

try:
    RECLINE_INSTALLED = False
    import recline
    from recline.arg_types.choices import Choices
    from recline.commands import ClicheCommandError
    from netapp_ontap.resource_table import ResourceTable
    RECLINE_INSTALLED = True
except ImportError:
    pass

from marshmallow import fields, EXCLUDE  # type: ignore

import netapp_ontap
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size
from netapp_ontap import NetAppResponse, HostConnection
from netapp_ontap.validations import enum_validation, len_validation, integer_validation
from netapp_ontap.error import NetAppRestError


__all__ = ["SecurityCertificate", "SecurityCertificateSchema"]
__pdoc__ = {
    "SecurityCertificateSchema.resource": False,
    "SecurityCertificate.security_certificate_show": False,
    "SecurityCertificate.security_certificate_create": False,
    "SecurityCertificate.security_certificate_modify": False,
    "SecurityCertificate.security_certificate_delete": False,
}


class SecurityCertificateSchema(ResourceSchema):
    """The fields of the SecurityCertificate object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the security_certificate. """

    authority_key_identifier = fields.Str(
        data_key="authority_key_identifier",
    )
    r""" Provides the key identifier of the issuing CA certificate that signed the SSL certificate.

Example: 26:1F:C5:53:5B:D7:9E:E2:37:74:F4:F4:06:09:03:3D:EB:41:75:D7 """

    ca = fields.Str(
        data_key="ca",
        validate=len_validation(minimum=1, maximum=256),
    )
    r""" Certificate authority """

    common_name = fields.Str(
        data_key="common_name",
    )
    r""" FQDN or custom common name. Provide on POST when creating a self-signed certificate.

Example: test.domain.com """

    expiry_time = fields.Str(
        data_key="expiry_time",
    )
    r""" Certificate expiration time. Can be provided on POST if creating self-signed certificate. The expiration time range is between 1 day to 10 years. """

    hash_function = fields.Str(
        data_key="hash_function",
        validate=enum_validation(['sha1', 'sha256', 'md5', 'sha224', 'sha384', 'sha512']),
    )
    r""" Hashing function. Can be provided on POST when creating a self-signed certificate. Hash functions md5 and sha1 are not allowed on POST.

Valid choices:

* sha1
* sha256
* md5
* sha224
* sha384
* sha512 """

    intermediate_certificates = fields.List(fields.Str, data_key="intermediate_certificates")
    r""" Chain of intermediate Certificates in PEM format. Only valid in POST when installing a certificate. """

    key_size = Size(
        data_key="key_size",
    )
    r""" Key size of requested Certificate in bits. One of 512, 1024, 1536, 2048, 3072. Can be provided on POST if creating self-signed certificate. Key size of 512 is not allowed on POST. """

    name = fields.Str(
        data_key="name",
    )
    r""" Certificate name. If not provided in POST, a unique name specific to the SVM is automatically generated.

Example: cert1 """

    private_key = fields.Str(
        data_key="private_key",
    )
    r""" Private key Certificate in PEM format. Only valid for create when installing a CA-signed certificate. This is not audited.

Example: -----BEGIN PRIVATE KEY----- MIIBVAIBADANBgkqhkiG9w0BAQEFAASCAT4wggE6AgEAAkEAu1/a8f3G47cZ6pel Hd3aONMNkGJ8vSCH5QjicuDm92VtVwkAACEjIoZSLYlJvPD+odL+lFzVQSmkneW7 VCGqYQIDAQABAkAcfNpg6GCQxoneLOghvlUrRotNZGvqpUOEAvHK3X7AJhz5SU4V an36qvsAt5ghFMVM2iGvGaXbj0dAd+Jg64pxAiEA32Eh9mPtFSmZhTIUMeGcPmPk qIYCEuP8a/ZLmI9s4TsCIQDWvLQuvjSVfwPhi0TFAb5wqAET8X5LBFqtGX5QlUep EwIgFnqM02Gc4wtLoqa2d4qPkYu13+uUW9hLd4XSd6i/OS8CIQDT3elU+Rt+qIwW u0cFrVvNYSV3HNzDfS9N/IoxTagfewIgPvXADe5c2EWbhCUkhN+ZCf38AKewK9TW lQcDy4L+f14= -----END PRIVATE KEY----- """

    public_certificate = fields.Str(
        data_key="public_certificate",
    )
    r""" Public key Certificate in PEM format. If this is not provided in POST, a self-signed certificate is created.

Example: -----BEGIN CERTIFICATE----- MIIBuzCCAWWgAwIBAgIIFTZBrqZwUUMwDQYJKoZIhvcNAQELBQAwHDENMAsGA1UE AxMEVEVTVDELMAkGA1UEBhMCVVMwHhcNMTgwNjA4MTgwOTAxWhcNMTkwNjA4MTgw OTAxWjAcMQ0wCwYDVQQDEwRURVNUMQswCQYDVQQGEwJVUzBcMA0GCSqGSIb3DQEB AQUAA0sAMEgCQQDaPvbqUJJFJ6NNTyK3Yb+ytSjJ9aa3yUmYTD9uMiP+6ycjxHWB e8u9z6yCHsW03ync+dnhE5c5z8wuDAY0fv15AgMBAAGjgYowgYcwDAYDVR0TBAUw AwEB/zALBgNVHQ8EBAMCAQYwHQYDVR0OBBYEFMJ7Ev/o/3+YNzYh5XNlqqjnw4zm MEsGA1UdIwREMEKAFMJ7Ev/o/3+YNzYh5XNlqqjnw4zmoSCkHjAcMQ0wCwYDVQQD EwRURVNUMQswCQYDVQQGEwJVU4IIFTZBrqZwUUMwDQYJKoZIhvcNAQELBQADQQAv DovYeyGNnknjGI+TVNX6nDbyzf7zUPqnri0KuvObEeybrbPW45sgsnT5dyeE/32U 9Yr6lklnkBtVBDTmLnrC -----END CERTIFICATE----- """

    scope = fields.Str(
        data_key="scope",
    )
    r""" The scope field of the security_certificate. """

    serial_number = fields.Str(
        data_key="serial_number",
        validate=len_validation(minimum=1, maximum=40),
    )
    r""" Serial number of certificate. """

    subject_key_identifier = fields.Str(
        data_key="subject_key_identifier",
    )
    r""" Provides the key identifier used to identify the public key in the SSL certificate.

Example: 26:1F:C5:53:5B:D7:9E:E2:37:74:F4:F4:06:09:03:3D:EB:41:75:D8 """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the security_certificate. """

    type = fields.Str(
        data_key="type",
        validate=enum_validation(['client', 'server', 'client_ca', 'server_ca', 'root_ca']),
    )
    r""" Type of Certificate. The following types are supported:

* client - a certificate and its private key used by an SSL client in ONTAP.
* server - a certificate and its private key used by an SSL server in ONTAP.
* client_ca - a Certificate Authority certificate used by an SSL server in ONTAP to verify an SSL client certificate.
* server_ca - a Certificate Authority certificate used by an SSL client in ONTAP to verify an SSL server certificate.
* root_ca - a self-signed certificate used by ONTAP to sign other certificates by acting as a Certificate Authority.


Valid choices:

* client
* server
* client_ca
* server_ca
* root_ca """

    uuid = fields.Str(
        data_key="uuid",
    )
    r""" Unique ID that identifies a certificate. """

    @property
    def resource(self):
        return SecurityCertificate

    gettable_fields = [
        "links",
        "authority_key_identifier",
        "ca",
        "common_name",
        "expiry_time",
        "hash_function",
        "intermediate_certificates",
        "key_size",
        "name",
        "private_key",
        "public_certificate",
        "scope",
        "serial_number",
        "subject_key_identifier",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "type",
        "uuid",
    ]
    """links,authority_key_identifier,ca,common_name,expiry_time,hash_function,intermediate_certificates,key_size,name,private_key,public_certificate,scope,serial_number,subject_key_identifier,svm.links,svm.name,svm.uuid,type,uuid,"""

    patchable_fields = [
        "common_name",
        "expiry_time",
        "hash_function",
        "intermediate_certificates",
        "key_size",
        "name",
        "private_key",
        "public_certificate",
        "scope",
        "svm.name",
        "svm.uuid",
        "type",
    ]
    """common_name,expiry_time,hash_function,intermediate_certificates,key_size,name,private_key,public_certificate,scope,svm.name,svm.uuid,type,"""

    postable_fields = [
        "common_name",
        "expiry_time",
        "hash_function",
        "intermediate_certificates",
        "key_size",
        "name",
        "private_key",
        "public_certificate",
        "scope",
        "svm.name",
        "svm.uuid",
        "type",
    ]
    """common_name,expiry_time,hash_function,intermediate_certificates,key_size,name,private_key,public_certificate,scope,svm.name,svm.uuid,type,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in SecurityCertificate.get_collection(fields=field)]
    return getter

async def _wait_for_job(response: NetAppResponse) -> None:
    """Examine the given response. If it is a job, asynchronously wait for it to
    complete. While polling, prints the current status message of the job.
    """

    if not response.is_job:
        return
    from netapp_ontap.resources import Job
    job = Job(**response.http_response.json()["job"])
    while True:
        job.get(fields="state,message")
        if hasattr(job, "message"):
            print("[%s]: %s" % (job.state, job.message))
        if job.state == "failure":
            raise NetAppRestError("SecurityCertificate modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class SecurityCertificate(Resource):
    """Allows interaction with SecurityCertificate objects on the host"""

    _schema = SecurityCertificateSchema
    _path = "/api/security/certificates"
    _keys = ["uuid"]
    _action_form_data_parameters = { 'file':'file', }

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves security certificates.
### Related ONTAP commands
* `security certificate show`

### Learn more
* [`DOC /security/certificates`](#docs-security-security_certificates)"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="security certificate show")
        def security_certificate_show(
            fields: List[Choices.define(["authority_key_identifier", "ca", "common_name", "expiry_time", "hash_function", "intermediate_certificates", "key_size", "name", "private_key", "public_certificate", "scope", "serial_number", "subject_key_identifier", "type", "uuid", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of SecurityCertificate resources

            Args:
                authority_key_identifier: Provides the key identifier of the issuing CA certificate that signed the SSL certificate.
                ca: Certificate authority
                common_name: FQDN or custom common name. Provide on POST when creating a self-signed certificate.
                expiry_time: Certificate expiration time. Can be provided on POST if creating self-signed certificate. The expiration time range is between 1 day to 10 years.
                hash_function: Hashing function. Can be provided on POST when creating a self-signed certificate. Hash functions md5 and sha1 are not allowed on POST.
                intermediate_certificates: Chain of intermediate Certificates in PEM format. Only valid in POST when installing a certificate.
                key_size: Key size of requested Certificate in bits. One of 512, 1024, 1536, 2048, 3072. Can be provided on POST if creating self-signed certificate. Key size of 512 is not allowed on POST.
                name: Certificate name. If not provided in POST, a unique name specific to the SVM is automatically generated.
                private_key: Private key Certificate in PEM format. Only valid for create when installing a CA-signed certificate. This is not audited.
                public_certificate: Public key Certificate in PEM format. If this is not provided in POST, a self-signed certificate is created.
                scope: 
                serial_number: Serial number of certificate.
                subject_key_identifier: Provides the key identifier used to identify the public key in the SSL certificate.
                type: Type of Certificate. The following types are supported: * client - a certificate and its private key used by an SSL client in ONTAP. * server - a certificate and its private key used by an SSL server in ONTAP. * client_ca - a Certificate Authority certificate used by an SSL server in ONTAP to verify an SSL client certificate. * server_ca - a Certificate Authority certificate used by an SSL client in ONTAP to verify an SSL server certificate. * root_ca - a self-signed certificate used by ONTAP to sign other certificates by acting as a Certificate Authority. 
                uuid: Unique ID that identifies a certificate.
            """

            kwargs = {}
            if authority_key_identifier is not None:
                kwargs["authority_key_identifier"] = authority_key_identifier
            if ca is not None:
                kwargs["ca"] = ca
            if common_name is not None:
                kwargs["common_name"] = common_name
            if expiry_time is not None:
                kwargs["expiry_time"] = expiry_time
            if hash_function is not None:
                kwargs["hash_function"] = hash_function
            if intermediate_certificates is not None:
                kwargs["intermediate_certificates"] = intermediate_certificates
            if key_size is not None:
                kwargs["key_size"] = key_size
            if name is not None:
                kwargs["name"] = name
            if private_key is not None:
                kwargs["private_key"] = private_key
            if public_certificate is not None:
                kwargs["public_certificate"] = public_certificate
            if scope is not None:
                kwargs["scope"] = scope
            if serial_number is not None:
                kwargs["serial_number"] = serial_number
            if subject_key_identifier is not None:
                kwargs["subject_key_identifier"] = subject_key_identifier
            if type is not None:
                kwargs["type"] = type
            if uuid is not None:
                kwargs["uuid"] = uuid
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return SecurityCertificate.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all SecurityCertificate resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)


    @classmethod
    def post_collection(
        cls,
        records: Iterable["SecurityCertificate"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["SecurityCertificate"], NetAppResponse]:
        r"""Creates or installs a certificate.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create or install the certificate.
* `common_name` - Common name of the certificate. Required when creating a certificate.
* `type` - Type of certificate.
* `public_certificate` - Public key certificate in PEM format. Required when installing a certificate.
* `private_key` - Private key certificate in PEM format. Required when installing a CA-signed certificate.
### Recommended optional properties
* `expiry_time` - Certificate expiration time. Specifying an expiration time is recommended when creating a certificate.
* `key_size` - Key size of the certificate in bits. Specifying a strong key size is recommended when creating a certificate.
* `name` - Unique certificate name per SVM. If one is not provided, it is automatically generated.
### Default property values
If not specified in POST, the following default property values are assigned:
* `key_size` - _2048_
* `expiry_time` - _P365DT_
* `hash_function` - _sha256_
### Related ONTAP commands
* `security certificate create`
* `security certificate install`

### Learn more
* [`DOC /security/certificates`](#docs-security-security_certificates)"""
        return super()._post_collection(
            records, *args, hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    post_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post_collection.__doc__)

    @classmethod
    def delete_collection(
        cls,
        *args,
        records: Iterable["SecurityCertificate"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a security certificate.
### Related ONTAP commands
* `security certificate delete`

### Learn more
* [`DOC /security/certificates`](#docs-security-security_certificates)"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves security certificates.
### Related ONTAP commands
* `security certificate show`

### Learn more
* [`DOC /security/certificates`](#docs-security-security_certificates)"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves security certificates.
### Related ONTAP commands
* `security certificate show`

### Learn more
* [`DOC /security/certificates`](#docs-security-security_certificates)"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)

    def post(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Creates or installs a certificate.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create or install the certificate.
* `common_name` - Common name of the certificate. Required when creating a certificate.
* `type` - Type of certificate.
* `public_certificate` - Public key certificate in PEM format. Required when installing a certificate.
* `private_key` - Private key certificate in PEM format. Required when installing a CA-signed certificate.
### Recommended optional properties
* `expiry_time` - Certificate expiration time. Specifying an expiration time is recommended when creating a certificate.
* `key_size` - Key size of the certificate in bits. Specifying a strong key size is recommended when creating a certificate.
* `name` - Unique certificate name per SVM. If one is not provided, it is automatically generated.
### Default property values
If not specified in POST, the following default property values are assigned:
* `key_size` - _2048_
* `expiry_time` - _P365DT_
* `hash_function` - _sha256_
### Related ONTAP commands
* `security certificate create`
* `security certificate install`

### Learn more
* [`DOC /security/certificates`](#docs-security-security_certificates)"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="security certificate create")
        async def security_certificate_create(
        ) -> ResourceTable:
            """Create an instance of a SecurityCertificate resource

            Args:
                links: 
                authority_key_identifier: Provides the key identifier of the issuing CA certificate that signed the SSL certificate.
                ca: Certificate authority
                common_name: FQDN or custom common name. Provide on POST when creating a self-signed certificate.
                expiry_time: Certificate expiration time. Can be provided on POST if creating self-signed certificate. The expiration time range is between 1 day to 10 years.
                hash_function: Hashing function. Can be provided on POST when creating a self-signed certificate. Hash functions md5 and sha1 are not allowed on POST.
                intermediate_certificates: Chain of intermediate Certificates in PEM format. Only valid in POST when installing a certificate.
                key_size: Key size of requested Certificate in bits. One of 512, 1024, 1536, 2048, 3072. Can be provided on POST if creating self-signed certificate. Key size of 512 is not allowed on POST.
                name: Certificate name. If not provided in POST, a unique name specific to the SVM is automatically generated.
                private_key: Private key Certificate in PEM format. Only valid for create when installing a CA-signed certificate. This is not audited.
                public_certificate: Public key Certificate in PEM format. If this is not provided in POST, a self-signed certificate is created.
                scope: 
                serial_number: Serial number of certificate.
                subject_key_identifier: Provides the key identifier used to identify the public key in the SSL certificate.
                svm: 
                type: Type of Certificate. The following types are supported: * client - a certificate and its private key used by an SSL client in ONTAP. * server - a certificate and its private key used by an SSL server in ONTAP. * client_ca - a Certificate Authority certificate used by an SSL server in ONTAP to verify an SSL client certificate. * server_ca - a Certificate Authority certificate used by an SSL client in ONTAP to verify an SSL server certificate. * root_ca - a self-signed certificate used by ONTAP to sign other certificates by acting as a Certificate Authority. 
                uuid: Unique ID that identifies a certificate.
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if authority_key_identifier is not None:
                kwargs["authority_key_identifier"] = authority_key_identifier
            if ca is not None:
                kwargs["ca"] = ca
            if common_name is not None:
                kwargs["common_name"] = common_name
            if expiry_time is not None:
                kwargs["expiry_time"] = expiry_time
            if hash_function is not None:
                kwargs["hash_function"] = hash_function
            if intermediate_certificates is not None:
                kwargs["intermediate_certificates"] = intermediate_certificates
            if key_size is not None:
                kwargs["key_size"] = key_size
            if name is not None:
                kwargs["name"] = name
            if private_key is not None:
                kwargs["private_key"] = private_key
            if public_certificate is not None:
                kwargs["public_certificate"] = public_certificate
            if scope is not None:
                kwargs["scope"] = scope
            if serial_number is not None:
                kwargs["serial_number"] = serial_number
            if subject_key_identifier is not None:
                kwargs["subject_key_identifier"] = subject_key_identifier
            if svm is not None:
                kwargs["svm"] = svm
            if type is not None:
                kwargs["type"] = type
            if uuid is not None:
                kwargs["uuid"] = uuid

            resource = SecurityCertificate(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create SecurityCertificate: %s" % err)
            return [resource]


    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a security certificate.
### Related ONTAP commands
* `security certificate delete`

### Learn more
* [`DOC /security/certificates`](#docs-security-security_certificates)"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="security certificate delete")
        async def security_certificate_delete(
        ) -> None:
            """Delete an instance of a SecurityCertificate resource

            Args:
                authority_key_identifier: Provides the key identifier of the issuing CA certificate that signed the SSL certificate.
                ca: Certificate authority
                common_name: FQDN or custom common name. Provide on POST when creating a self-signed certificate.
                expiry_time: Certificate expiration time. Can be provided on POST if creating self-signed certificate. The expiration time range is between 1 day to 10 years.
                hash_function: Hashing function. Can be provided on POST when creating a self-signed certificate. Hash functions md5 and sha1 are not allowed on POST.
                intermediate_certificates: Chain of intermediate Certificates in PEM format. Only valid in POST when installing a certificate.
                key_size: Key size of requested Certificate in bits. One of 512, 1024, 1536, 2048, 3072. Can be provided on POST if creating self-signed certificate. Key size of 512 is not allowed on POST.
                name: Certificate name. If not provided in POST, a unique name specific to the SVM is automatically generated.
                private_key: Private key Certificate in PEM format. Only valid for create when installing a CA-signed certificate. This is not audited.
                public_certificate: Public key Certificate in PEM format. If this is not provided in POST, a self-signed certificate is created.
                scope: 
                serial_number: Serial number of certificate.
                subject_key_identifier: Provides the key identifier used to identify the public key in the SSL certificate.
                type: Type of Certificate. The following types are supported: * client - a certificate and its private key used by an SSL client in ONTAP. * server - a certificate and its private key used by an SSL server in ONTAP. * client_ca - a Certificate Authority certificate used by an SSL server in ONTAP to verify an SSL client certificate. * server_ca - a Certificate Authority certificate used by an SSL client in ONTAP to verify an SSL server certificate. * root_ca - a self-signed certificate used by ONTAP to sign other certificates by acting as a Certificate Authority. 
                uuid: Unique ID that identifies a certificate.
            """

            kwargs = {}
            if authority_key_identifier is not None:
                kwargs["authority_key_identifier"] = authority_key_identifier
            if ca is not None:
                kwargs["ca"] = ca
            if common_name is not None:
                kwargs["common_name"] = common_name
            if expiry_time is not None:
                kwargs["expiry_time"] = expiry_time
            if hash_function is not None:
                kwargs["hash_function"] = hash_function
            if intermediate_certificates is not None:
                kwargs["intermediate_certificates"] = intermediate_certificates
            if key_size is not None:
                kwargs["key_size"] = key_size
            if name is not None:
                kwargs["name"] = name
            if private_key is not None:
                kwargs["private_key"] = private_key
            if public_certificate is not None:
                kwargs["public_certificate"] = public_certificate
            if scope is not None:
                kwargs["scope"] = scope
            if serial_number is not None:
                kwargs["serial_number"] = serial_number
            if subject_key_identifier is not None:
                kwargs["subject_key_identifier"] = subject_key_identifier
            if type is not None:
                kwargs["type"] = type
            if uuid is not None:
                kwargs["uuid"] = uuid

            if hasattr(SecurityCertificate, "find"):
                resource = SecurityCertificate.find(
                    **kwargs
                )
            else:
                resource = SecurityCertificate()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete SecurityCertificate: %s" % err)

    def sign(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Signs a certificate.
### Required properties
* `signing_request` - Certificate signing request to be signed by the given certificate authority.
### Recommended optional properties
* `expiry_time` - Certificate expiration time. Specifying an expiration time for a signed certificate is recommended.
* `hash_function` - Hashing function. Specifying a strong hashing function is recommended when signing a certificate.
### Default property values
If not specified in POST, the following default property values are assigned:
* `expiry_time` - _P365DT_
* `hash_function` - _sha256_
### Related ONTAP commands
* `security certificate sign`
This API is used to sign a certificate request using a pre-existing self-signed root certificate. The self-signed root certificate acts as a certificate authority within its scope and maintains the records of its signed certificates. <br/>
The root certificate can be created for a given SVM or for the cluster using [`POST security/certificates`].<br/>
"""
        return super()._action(
            "sign", body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    sign.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._action.__doc__)


""""

"""

def extension_metadata():
  return {
      "primary_extension": True,
      "priority": 100,
      "setups": {
          "CTA": "dips://dcta-servers02.pic.es:9135/Configuration/Server",
          "CTA-cert": "dips://ccdcta-cert.in2p3.fr:9135/Configuration/Server",
      },
      "default_setup": "CTA",
  }


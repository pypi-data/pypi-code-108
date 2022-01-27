class AD_Config():

    inited = False

    ad_login = False
    ad_address = "ldap://127.0.0.1:389"
    base_dn = "ou=User,dc=ad,dc=local"
    ad_group = "allowed_to_login"
    ad_suffix ="@ad.local"

    def __init__(self,ad_login = False, ad_address = "ldap://127.0.0.1:389", base_dn = "ou=User,dc=ad,dc=local", ad_group = "allowed_to_login", ad_suffix ="@ad.local"):
        if not AD_Config.inited:
            AD_Config.login = ad_login
            AD_Config.address = ad_address
            AD_Config.base_dn = base_dn
            AD_Config.group = ad_group
            AD_Config.suffix = ad_suffix
        AD_Config.inited = True

    def __str__(self):
        return f"""
===============AD-Config===============

    ad_login:   {self.login}
    ad_address: {self.address}
    base_dn:    {self.base_dn}
    ad_group:   {self.group}
    ad_suffix:  {self.suffix}

=======================================
        """
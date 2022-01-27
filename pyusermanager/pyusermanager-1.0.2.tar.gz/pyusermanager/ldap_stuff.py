import ldap

from .config_class import LoginConfig
from .ad_config_class import AD_Config


def authenticate(username, password):
    conn = ldap.initialize(AD_Config.address)
    conn.protocol_version = 3
    conn.set_option(ldap.OPT_REFERRALS, 0)

    #add ad suffix if it does not exist!
    if not username.endswith(AD_Config.suffix):
        username = f"{username}{AD_Config.suffix}"
    conn.simple_bind_s(username, password)
    return conn
    

def get_ldap_groups(username,password):
       
    ldap_c = authenticate(username,password)
    userfilter = f"(&(objectClass=user)(sAMAccountName={username}))"
    userresults = ldap_c.search_s(AD_Config.base_dn,ldap.SCOPE_SUBTREE,userfilter, None)[0][1]["memberOf"]
    groups = []
    for group in userresults:
        group = group.decode("utf-8")
        group = group[group.index("CN=")+3:group.index(",")]
        groups.append(group)
    return groups

def check_group(group_name,username,password):
    try:
        groups = get_ldap_groups(username,password)
        if group_name in groups:
            return True
        else:
            return False
    except Exception as err:
        if LoginConfig.debug_output:
            print(err)
        return False

#if __name__ == "__main__":
#    print(get_ldap_groups(sys.argv[1],sys.argv[2]))


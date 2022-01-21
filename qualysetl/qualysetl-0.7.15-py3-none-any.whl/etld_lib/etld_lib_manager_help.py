
def api_manager_usage():
    usage = '''
        qetl_manage_user [-h] -p PARENT -c CHILD [-t] [-u] [-n] [-r] [-y] [-e]

Examples of usage:
  1) Create New User    - qetl_manage_user -p /usr/local/qetl -c qualys_user01 -t
  2) Report User        - qetl_manage_user -p /usr/local/qetl -c qualys_user01 -r
  3) Test User          - qetl_manage_user -p /usr/local/qetl -c qualys_user01 -t
  4) Credentials update - qetl_manage_user -p /usr/local/qetl -c qualys_user01 -u
  4) Execute ETL Job    - qetl_manage_user -p /usr/local/qetl -c qualys_user01 -e etl_kb_main

Description: Manage your qetl users.
    Key Points:
      - There is one directory for each qualys user.
      - The parent directory is the qetl root directory for your users.  Ex. /usr/local/qetl 
      - The child directory is your qetl user that you want to use.  
        ex. qualys_user_01 located under 
      - This command is the user interface to the ETL system.
    
    Example Uses of qetl_manage_user: 
        1) [-n] Create New User, generating application directories.
        2) [-t] Test New User
        3) [-y] Update Credentials (username, password, api_fqdn_server) 
        4) [-r] Report of Application Directory and Files 
        5) [-e] Execute ETL Job.  Ex. -e etl_kb  
                See bin directory in report [-r] for options.

        Execute qetl_manage_user -h for details

    Example User Directory Structure: 
        User Directory /usr/local/qetl/qualys_user_01/qetl_home
           1) /usr/local/qetl: Parent dir for all your users
           2) /usr/local/qetl/qualys_user_01: Child dir for
              single qualys user
           3) /usr/local/qetl/qualys_user_01/qetl_home: 
              Application cred,config,data,log directories
    
    In the example above, qetl_home directories are generated

    The qetl_home directory is where the user programs for a single
    qualys userid live and they are generated through this command.
    For example: Directory /usr/local/qetl/qualys_user_01 contains: 
         1) qetl_home/config
         2) qetl_home/data
         3) qetl_home/log
         4) qetl_home/cred
                 
    Examples:
       1) ETL the KnowledgeBase data files:
          /usr/local/qetl/qualys_user_01/qetl_home/data/kb.*
       2) ETL the Host List data files:
          /usr/local/qetl/qualys_user_01/qetl_home/data/host_list.*
    
    See github documentation for more details
    usage: qetl_manage_user [-h] -p PARENT -c CHILD [-t] [-u] [-n] [-r] [-y] [-e]
    '''
    return usage



from omfit_classes import unix_os as os
import signal

from omfit_classes.utils_base import *

os.environ['OMFIT_SETUP'] = '1'

# This import of matplotlib at the beginning is to make sure that later imports
# use the correct backend (TkAgg), and don't fail because they try to use
# the macosx backend, which might be the default for a fresh installation on Mac
# OSX
try:
    import matplotlib

    matplotlib.use('TkAgg')
except Exception:
    pass
sshDir = f"{os.environ['HOME']}{os.sep}.ssh{os.sep}"
privateKey = f'{sshDir}id_dsa'
if not os.path.exists(privateKey):
    privateKey = f'{sshDir}id_rsa'
publicKey = privateKey + '.pub'
privateKey_name = os.path.basename(privateKey)
publicKey_name = os.path.basename(publicKey)

# -----------------------------------------------
def setup_dependencies():
    # get the installation dependencies from the install/requirements.txt file
    pipdep = {}
    pipdep['ttk'] = {'pip': 'pyttk'}
    pipdep['dateutil'] = {'pip': 'python-dateutil'}
    pipdep['yaml'] = {'pip': 'pyyaml'}
    with open(os.path.split(__file__)[0] + '/../install/requirements.txt', 'r') as f:
        for line in f.readlines():
            entry = line.strip().split('#')[0].strip().split('>=')[0].split('==')[0]
            if entry and entry not in list(pipdep.keys()) and entry not in [x['pip'] for x in list(pipdep.values())]:
                pipdep[entry] = {'pip': entry}
                tmp = line.strip().split('#')[1]
                if len(tmp):
                    pipdep[entry].update(eval(tmp))

    dependencies = sorted(list(pipdep.keys()), key=lambda x: str(x).lower())

    install_command = []
    for mod_import in dependencies:
        print(mod_import)
        try:
            __import__(mod_import.replace('-', '_'))
            print(f'ok - Module {mod_import} is already installed')
        except Exception as _excp:
            action = 'working properly'
            if isinstance(_excp, ImportError):
                action = 'installed'
            if pipdep[mod_import].get('optional', ''):
                print(f"NO - Module {mod_import} is NOT {action}  <------ (OPTIONAL for {pipdep[mod_import]['optional']}")
            else:
                print(f'NO - Module {mod_import} is NOT {action}  <------ (REQUIRED)')
            if isinstance(_excp, ImportError) and mod_import in pipdep:
                install_command.append(f"pip install {pipdep[mod_import]['pip']}")
            else:
                install_command.append(f'--> Check {mod_import} installation by hand:{repr(_excp)}')

    if len(install_command):
        print('')
        print('You can attempt to install the  missing OMFIT dependencies by typing in a terminal:\n')
        print('\n'.join(['   ' + k for k in sorted(install_command)]) + '\n')
        if platform.system() == 'Darwin':
            print(
                'For OSX, consider using MacPorts and running the script: '
                + os.path.abspath(os.sep.join([os.path.split(__file__)[0], '..', 'install', 'ports', 'install.sh']))
            )
        else:
            print('If you have root privileges consider using your distribution package manager to install Python packages')
        print('Alternatively, you can use the Anaconda Python distribution: https://www.continuum.io/downloads')


def generate_private_public_key_pairs():
    child = subprocess.Popen(
        'ssh -o StrictHostKeyChecking=no -q -V',
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        close_fds=True,
    )
    while child.poll() is None:
        pass

    if os.path.exists(privateKey) and os.path.exists(publicKey):
        print('SSH keys already exists.')
        print('')
        print('To change your private key password type in a terminal:')
        print(f'ssh-keygen -p -f {privateKey}')
    else:
        print('SSH keys do not exist! Generating...')
        m_form = ''
        import platform

        if platform.system() == 'Darwin':
            m_form = '-m PEM'
        child = subprocess.Popen(f'ssh-keygen -b 4096 {m_form} -f {privateKey}', shell=True)
        while child.poll() is None:
            pass


def __setup_authorization__(ssh_string, ssh_t_string=''):
    username, server, port = setup_ssh_tunnel(ssh_string, ssh_t_string, forceRemote=True)
    if len(ssh_t_string):
        ssh_t_string = ' via ' + ssh_t_string

    # keep doing this until it takes less than 2 seconds (a good indicator for the connection being passwordless)
    print('If prompted, enter the password you use to ssh to the server')
    t0 = time.time()
    time.sleep(1)  # avoid one connection after the other
    connect_and_setup_authorized_keys = f'\\cat {publicKey} | ssh -o StrictHostKeyChecking=no -q {username}@{server} -p {port}'
    connect_and_setup_authorized_keys += (
        r" 'mkdir -p .ssh ; chmod 700 .ssh; touch .ssh/authorized_keys; cat >> .ssh/authorized_keys ; chmod 600 .ssh/authorized_keys'"
    )
    child = subprocess.Popen(connect_and_setup_authorized_keys, shell=True)
    while child.poll() is None:
        pass
    if child.poll():
        print('Error 1.' + str(child.poll()) + ': Could not reach the server ' + ssh_string + ssh_t_string)
        return

    OMFITtmptmp = os.environ['HOME'] + os.sep + 'OMFITtmptmp'
    if os.path.exists(OMFITtmptmp):
        os.remove(OMFITtmptmp)

    # now that I have seamless access I can do some cleanup if necessary
    time.sleep(1)  # avoid one connection after the other
    child = subprocess.Popen(
        f'scp -o StrictHostKeyChecking=no -q -P {port} {username}@{server}:.ssh/authorized_keys {OMFITtmptmp}', shell=True
    )
    while child.poll() is None:
        pass
    if child.poll():
        if os.path.exists(OMFITtmptmp):
            os.remove(OMFITtmptmp)
        print(f'Error 2.{child.poll()}: Could not reach the server {ssh_string}{ssh_t_string}')
        return

    # read the authorized_keys and remove duplicates and empty lines
    if os.path.exists(OMFITtmptmp):
        with open(OMFITtmptmp, 'r') as f:
            authkeys = set([_f for _f in f.readlines() if _f])
        with open(OMFITtmptmp, "w+") as f:
            f.writelines(authkeys)

        # upload the cleaned authorized_keys file
        time.sleep(1)  # avoid one connection after the other
        child = subprocess.Popen(
            f'scp -o StrictHostKeyChecking=no -q -P {port} {OMFITtmptmp} {username}@{server}:.ssh/authorized_keys', shell=True
        )
        while child.poll() is None:
            pass
        if child.poll():
            if os.path.exists(OMFITtmptmp):
                os.remove(OMFITtmptmp)
            print(f'Error 3.{child.poll()}: Could not reach the server {ssh_string}{ssh_t_string}')
            return

        # remove temporary file
        os.remove(OMFITtmptmp)
        print('Done!')

    else:
        print(f'Error 4: Could not find local temporary file: {OMFITtmptmp}')


def __copy_keys__(ssh_string):
    username, password, server, port = parse_server(ssh_string)

    # copy the private and public keys from the server
    time.sleep(1)  # avoid one connection after the other
    cp_command = f'scp -o StrictHostKeyChecking=no -q -P {port} {username}@{server}:.ssh/{privateKey_name} {username}@{server}:.ssh/{publicKey_name} .'
    child = subprocess.Popen(cp_command, shell=True)
    while child.poll() is None:
        pass
    if child.poll():
        print(f'Error 5.{child.poll()}: Could not reach the server {ssh_string}')


def __setup_keys__(ssh_string):
    username, password, server, port = parse_server(ssh_string)

    # copy the private and public keys to the server
    time.sleep(1)  # avoid one connection after the other
    cp_command = f'scp -o StrictHostKeyChecking=no -q -P {port} {privateKey} {publicKey} {username}@{server}:.ssh/'
    child = subprocess.Popen(cp_command, shell=True)
    while child.poll() is None:
        pass
    if child.poll():
        print(f'Error 5.{child.poll()}: Could not reach the server {ssh_string}')


def setup_authorization():
    print(f'    -= Your PUBLIC key {publicKey} will be appended to the ~/.ssh/authorized_keys file of the server =-')
    print('    Type a comma separated list of servers (leave blank to skip)')
    print(f"    e.g. {os.environ['USER']}@iris.gat.com:22")
    a = input('>> ')
    a = [_f for _f in a.split(',') if _f]
    if len(a):
        for ssh_string in a:
            __setup_authorization__(ssh_string)
    else:
        print('Skipped!')


def copy_keys_to_server():
    print(f'    -= Your local PRIVATE key {privateKey} will replace the existing ~/.ssh/{privateKey_name} on the server =-')
    print(f'    -= Your local PUBLIC key {publicKey} will replace the existing ~/.ssh/{publicKey_name} on the server =-')
    print('    Type a comma separated list of servers to which to copy the keys:')
    print(f"    e.g. {os.environ['USER']}@iris.gat.com:22 (leave blank to skip)")
    a = input('>> ')
    if len(a):
        for ssh_string in a.split(','):
            __setup_authorization__(ssh_string)
            __setup_keys__(ssh_string)
    else:
        print('Skipped!')


def copy_keys_from_server():
    print(f'    -= Your PRIVATE key {privateKey_name} on the server will replace {privateKey} locally =-')
    print(f'    -= Your PUBLIC key {publicKey_name} on the server will replace {publicKey} locally =-')
    print('    Type the name of the server from which to copy your keys:')
    print(f"    e.g. {os.environ['USER']}@iris.gat.com:22 (leave blank to skip)")
    a = input('>> ')
    if len(a):
        for ssh_string in a.split(','):
            __setup_authorization__(ssh_string)
            __copy_keys__(ssh_string)
    else:
        print('Skipped!')


def setup_authorization_tunnel():
    print('    -= This will setup an SSH tunnel =-')
    print('    Type a comma separated list of tunnels behind which your servers exist:')
    print(f"    e.g. {os.environ['USER']}@cybele.gat.com:2039 (leave blank to skip)")
    a = input('>> ')
    a = [_f for _f in a.split(',') if _f]
    if len(a):
        for ssh_t_string in a:
            print('    -= Your PUBLIC key will be appended to their ~/.ssh/authorized_keys file =-')
            print(f'    Type a comma separated list of servers behind the tunnel {ssh_t_string}')
            print(f"    e.g. {os.environ['USER']}@iris.gat.com:22 (leave blank to skip)")
            b = input('>> ')
            b = [_f for _f in b.split(',') if _f]
            if len(b):
                for ssh_string in b:
                    __setup_authorization__(ssh_string, ssh_t_string)
            else:
                print('Skipped!')
    else:
        print('Skipped!')


def signalHandler(signal=None, frame=None):
    print('')
    sys.exit()


for k in range(1, 9):
    signal.signal(k, signalHandler)

# -----------------------------------------------
old_dir = os.getcwd()
if not os.path.exists(sshDir):
    os.makedirs(sshDir)
os.chdir(sshDir)

a = ''
while a.lower() not in ['q', 'quit']:
    print(
        """
############################################
#           OMFIT helper setup             #
############################################

    SERVERS ARE DIRECTLY REACHABLE
[host]  <-->  (Internet/Lan)  <-->  [server]

  SERVERS ARE NOT DIRECTLY REACHABLE
[host]                              [server]
   |    ==========================    |
   +--->--->---->-tunnel--->--->--->--+
        ==========================

You must avoid having to enter a password
when you connect to tunnels/servers. You can
do this either by not using one or by setting
up an ssh-agent on this host and on your tunnels.

1: Generate private/public key pairs
2: Authorize access to directly reachable servers
3: Copy private/public keys to servers
4: Authorize access to servers behind tunnels
5: Copy private/public keys from server
--
6: Check python dependencies for OMFIT
--
Q: Quit
############################################
    """
    )
    a = input('>> ')

    if a.lower() == '1':
        generate_private_public_key_pairs()
    elif a.lower() == '2':
        setup_authorization()
    elif a.lower() == '3':
        copy_keys_to_server()
    elif a.lower() == '4':
        print('    NOTE: tunnels require your private key to be copied to the tunneling server')
        print('          Make sure to copy your keys [step 3] to the tunneling server!')
        setup_authorization_tunnel()
    elif a.lower() == '5':
        copy_keys_from_server()
    elif a.lower() == '6':
        setup_dependencies()

    if a.lower() in ['1', '2', '3', '4', '5', '6']:
        print('')
        input('Press <enter> to return to the main menu...')

os.chdir(old_dir)

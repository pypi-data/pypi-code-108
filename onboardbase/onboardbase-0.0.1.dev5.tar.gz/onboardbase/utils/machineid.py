import os
import re
import subprocess
import platform
from Crypto.Hash import SHA256


class MachineID:

  system = platform.system()

  win32RegBinPath = { 'native': '%windir%\\System32',
        'mixed': '%windir%\\sysnative\\cmd.exe /c %windir%\\System32',
        '': ''}
  
  def isWindowsProcessMixedOrNativeArchitecture():
    if platform.system() != 'win32':
      return ''
    if platform.architecture() == 'ia32' and 'PROCESSOR_ARCHITEW6432' in os.environ:
      return 'mixed'
    return 'native'
  
  guid = {'darwin': 'ioreg -rd1 -c IOPlatformExpertDevice', 
          'win32': '%s\\REG.exe '%(win32RegBinPath[isWindowsProcessMixedOrNativeArchitecture()]) + 'QUERY HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Cryptography ' + '/v MachineGuid',
          'linux': '( cat /var/lib/dbus/machine-id /etc/machine-id 2> /dev/null || hostname ) | head -n 1 || :',
          'freebsd': 'kenv -q smbios.system.uuid || sysctl -n kern.hostuuid'}

  def hash(self, guid):
    return SHA256.new(data=guid.encode()).hexdigest()

  def expose(self, result):
    regex = r"\=|\s+|\""
    subst = ""
    system = self.system.lower()
    if(system == 'darwin'):   
      formattedResult = result.split('IOPlatformUUID')[1].split('\n')[0]
      return re.sub(regex, subst, formattedResult, 0, re.IGNORECASE).lower()
    elif(system == 'win32'):
      formattedResult = str(result).split('REG_SZ')[1]
      return re.sub(regex, subst, formattedResult, 0, re.IGNORECASE).lower()
    elif(system == 'linux'):
      formattedResult = str(result)
      return re.sub(regex, subst, formattedResult, 0, re.IGNORECASE).lower()
    elif(system == 'freebsd'):
      formattedResult = str(result)
      return re.sub(regex, subst, formattedResult, 0, re.IGNORECASE).lower()
    else:
      raise Exception('Unsupported platform: %s'%(system))
    
  def getMachineId(self, original = False):
    process = subprocess.Popen(self.guid[self.system.lower()].split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    if error:
      raise Exception('Error while obtaining machine id %s'%(error))
    id = self.expose(output.decode())
    return (self.hash(id), id) [original]
    
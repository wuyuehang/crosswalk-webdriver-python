__all__ = ["AdbImpl"]

import subprocess
import re
import time
from adb import Adb
from status import *
from base.thread_wrap import ExecuteGetResponse
from base.log import VLOG

class AdbImpl(Adb):
    
  def GetDevices(self, devices):
    devices[:] = []
    p = subprocess.Popen(['adb', 'devices'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (res, errorMsg) = p.communicate()
    if errorMsg:
      return Status(kUnknownError, "Falied to get devices ")
    res = res.split('\n')
    # usually we target on only one device
    if len(res) == 4:
      res = res[1]
      devices.append(res.split('\t')[0])
      return Status(kOk)
    # maybe more than one devices
    elif len(res) > 4:
      res = res[1:-2]
      for item in res:
        devices.append(item.split('\t')[0])
      return Status(kOk)
    else:
      return Status(kUnknownError, "Falied to get devices ")
       
  def ForwardPort(self, device_serial, local_port, remote_abstract):
    #VLOG(0, "adb_impl ForwardPort(serial:%s, local_port:%s, remote_abstract:%s)" % (device_serial, local_port, remote_abstract)) 
    (status, res) = self.ExecuteCommand("adb -s " + device_serial + " forward tcp:" + local_port + \
                 " localabstract:" + remote_abstract + "_devtools_remote")
    if not status.IsOk():
      return Status(kUnknownError, "Failed to forward ports to device " + device_serial + ": " + res)
    return status

  def SetCommandLineFile(self, device_serial, command_line_file, exec_name, args):
    return Status(kOk)
    
  def CheckAppInstalled(self, device_serial, package):
    #VLOG(0, "adb_impl CheckAppInstalled(device_serial:%s, package:%s)" % (device_serial, package))
    (status, res) = self.ExecuteCommand("adb -s " + device_serial + " shell pm path " + package)
    if not status.IsOk():
      return status
    if res.find("package") == -1:
      return Status(kUnknownError, package + " is not installed on device " + device_serial)
    return Status(kOk)

  def ClearAppData(self, device_serial, package):
    #VLOG(0, "adb_impl CheckAppInstalled(device_serial:%s, package:%s)" % (device_serial, package))
    (status, res) = self.ExecuteCommand("adb -s " + device_serial + " shell pm clear " + package)
    if not status.IsOk():
      return status
    if res.find("Success") == -1:
      return Status(kUnknownError, "Failed to clear data for " + package + ": " + res)
    return Status(kOk)

  def SetDebugApp(self, device_serial="", package=""):
    #VLOG(0, "adb_impl SetDebugApp(device_serial:%s, package:%s)" % (device_serial, package))
    (status, res) = self.ExecuteCommand("adb -s " + device_serial + " shell am set-debug-app --persistent " + package)
    if not status.IsOk():
      return status
    return Status(kOk)

  def Launch(self, device_serial, package, activity):
    #VLOG(0, "adb_impl Launch(device_serial:%s, package:%s, activity:%s)" % (device_serial, package, activity))
    (status, res) = self.ExecuteCommand("adb -s " + device_serial + " shell am start -W -n " + package + "/" + activity + " -d data:,")
    if not status.IsOk():
      return status
    if res.find("Complete") == -1:
      return Status(kUnknownError, "Failed to start " + package + " on device " + device_serial + ": " + res)
    return Status(kOk)

  def ForceStop(self, device_serial, package):
    #VLOG(0, "adb_impl ForceStop(device_serial:%s, package:%s)" % (device_serial, package))
    (status, res) = self.ExecuteCommand("adb -s " + device_serial + " shell am force-stop " + package)
    if not status.IsOk():
      return status
    return Status(kOk)
        
  """ return status and pid<string> """
  def GetPidByName(self, device_serial, process_name):
    pid = ""
    (status, res) = self.ExecuteCommand("adb -s " + device_serial + " shell ps")
    if not status.IsOk():
      return status, pid
    patt = r'\w+\s*(\d+)\s*\d+\s*\d+\s*\d+\s*\w+\s*\w+\s*\w\s*' + process_name
    matchObj = re.search(patt, res)
    if not matchObj:
      return Status(kUnknownError, "Failed to get PID for the following process: " + process_name), pid
    pid = matchObj.groups()[0]
    #VLOG(0, "adb_impl GetPidByName(device_serial:%s, process_name:%s, pid:%s)" % (device_serial, process_name, pid))
    return Status(kOk), pid

  """ return status and response<string> """
  def ExecuteCommand(self, command=""):
    res = ""
    #VLOG(1, "Sending adb command: " + command)
    if command.find("ps auxww") != -1:
      time.sleep(1)  
    delta_time = 30
    if command.find("xwalk-launcher") != -1:
      delta_time = 3
    cmd_runner = ExecuteGetResponse(command, delta_time)
    status, res = cmd_runner.GetResponse()
    if status.IsOk():
      #VLOG(1, "Received adb response: " + res)
      pass
    return status, res

if __name__ == "__main__":
  adb_test = AdbImpl()
  devices = []
  status = Status(kOk)
  status = adb_test.GetDevices(devices)
  print ">>>>>>>> GetDevices : %s" % str(devices)

  status = adb_test.CheckAppInstalled(devices[0], "org.xwalk.simple")
  print ">>>>>>>> CheckAppInstalled : %s" % status.Message()

  status = adb_test.SetDebugApp(devices[0], "org.xwalk.simple")
  print ">>>>>>>> SetDebugApp : %s" % status.Message()

  status = adb_test.Launch(devices[0], "org.xwalk.simple", ".simpleActivity")
  print ">>>>>>>> Launch : %s" % status.Message()

  status, pid = adb_test.GetPidByName(devices[0], "org.xwalk.simple")
  print ">>>>>>>> GetPidByName : %s, pid : %s" % (status.Message(), pid)

  status = adb_test.ForwardPort(devices[0], "8899", "org.xwalk.simple")
  print ">>>>>>>> ForwardPort : %s" % status.Message()

  time.sleep(5)
  status = adb_test.ForceStop(devices[0], "org.xwalk.simple")
  print ">>>>>>>> ForceStop : %s" % status.Message()

  status = adb_test.ClearAppData(devices[0], "org.xwalk.simple")
  print ">>>>>>>> ClearAppData : %s" % status.Message()
    

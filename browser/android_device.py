__all__ = ["AndroidDevice"]

from adb_impl import AdbImpl
from status import *
from base.log import VLOG

class AndroidDevice(object):

  def __init__(self, device_serial="", adb=AdbImpl(), release_callback=None):
    self.device_serial = device_serial
    self.release_callback = release_callback
    self.xdb = adb
    self.active_package = ""

  def __del__(self):
    if callable(self.release_callback):
      self.release_callback(self.device_serial)
    return

  def ForwardDevtoolsPort(self, package="", process="", device_socket="", port=""):
    if not device_socket:
      # Assunme this is a WebView app.
      if not process:
        status, pid = self.xdb.GetPidByName(self.device_serial, package)
      else:
        status, pid = self.xdb.GetPidByName(self.device_serial, process)
      if status.IsError():
        if not process:
          status.AddDetails("process name must be specified if not equal to package name")
        return status
    VLOG(0, "Devtools port: " + port)
    return self.xdb.ForwardPort(self.device_serial, port, package)
         
  def SetUp(self, package, activity, process, args, use_running_app, port):
    if self.active_package:
      return Status(kUnknownError, self.active_package + " was launched and has not been quit")
    status = self.xdb.CheckAppInstalled(self.device_serial, package)
    if status.IsError():
      return status
    known_activity = ""
    command_line_file = ""
    device_socket = ""
    exec_name = ""
    if not use_running_app:
      status = self.xdb.ClearAppData(self.device_serial, package)
      if status.IsError():
        return status
      if known_activity:
        if activity or process:
          return Status(kUnknownError, "known package " + package + \
                      " does not accept activity/process")
        elif not activity:
          return Status(kUnknownError, "WebView apps require activity name")
      if command_line_file:
        status = self.xdb.SetCommandLineFile(self.device_serial, \
                        exec_name, args)
        if status.IsError():
          return status
      if known_activity:
        status = self.xdb.Launch(self.device_serial, package, known_activity)
      else:
        status = self.xdb.Launch(self.device_serial, package, activity)
      if status.IsError():
        return status
      self.active_package = package
    self.ForwardDevtoolsPort(package, process, device_socket, port)
    return status

  def TearDown(self):
    if self.active_package:
      status = self.xdb.ForceStop(self.device_serial, self.active_package)
      if status.IsError():
        return status
      self.active_package = ""
    return Status(kOk)
   
if __name__ == "__main__":
  import time
  test = AndroidDevice("emulator-5554", AdbImpl(), None)
  status = Status(kOk)
  test.SetUp("org.xwalk.simple", ".simpleActivity", "", "", False, "8899")
  print ">>>>>>>>> SetUp : %s" % status.Message()
  time.sleep(5)
  test.TearDown()
  print ">>>>>>>>> TearDown : %s" % status.Message()


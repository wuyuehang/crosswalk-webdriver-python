import BaseHTTPServer
import re
import time
import threading
import json
import yaml
import os
from browser.device_manager import DeviceManager
from browser.adb_impl import AdbImpl
from browser.sdb_impl import SdbImpl
from browser.status import *
from command.init_session_commands import *
from command.window_commands import ExecuteWindowCommand
from command.command_mapping import SessionCommandMapping
from command.command_mapping import WindowCommandMapping
from misc.session import Session
from base.bind import Bind
from base.log import VLOG
from base.thread_wrap import ThreadWrap
from net.port_server import PortManager
from net.http_error_code import *
from net.websocket_factory import WebsocketFactory

def fake_quit_func():
  return Status(kOk)

# inner complement of Http request handler
class XwalkHttpHandler(BaseHTTPServer.BaseHTTPRequestHandler):

  def __init__(self, port, url_base, target, port_server, *args):
    self.port_ = port
    self.url_base_ = url_base
    self.port_server_ = port_server
    self.socket_factory_ = WebsocketFactory()
    self.port_manager_ = PortManager(12000, 13000)
    # determine type of device_manager according to device_os, so whenever meet
    # judge logic, you can call isinstance(device_manager.xdb_, AdbImpl)
    if target == "android":
      self.device_manager_ = DeviceManager(AdbImpl())
    else:
      self.device_manager_ = DeviceManager(SdbImpl())
    BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, *args)

  def PrepareResponse(self, trimmed_path, status, value, session_id):
    response = self.PrepareResponseHelper(trimmed_path, status, value, session_id)
    VLOG(0, "SendTo Sele: " + str(response))
    self.send_response(response["code"])
    for header_item in response["headers"]:
      self.send_header(header_item[0], header_item[1])
    self.end_headers()
    self.wfile.write(response["body"])
    return Status(kOk)

  def PrepareResponseHelper(self, trimmed_path, status, value, session_id):
    if status.Code() == kUnknownCommand:
      response = {"code": HTTP_NOT_IMPLEMENTED, 
                  "headers": [["", ""],], 
                  "body": "unimplemented command: " + trimmed_path}
      return response
    if trimmed_path == "/status" and status.IsOk():
      response = {}
      response["code"] = HTTP_OK
      response["headers"] = [["Content-Type", "application; charset=utf-8"],]
      response["body"] = value
      return response
    if trimmed_path == "/session" and status.IsOk():
    # Creating a session involves a HTTP request to /session, which is
    # supposed to redirect to /session/:sessionId, which returns the
    # session info.
      body_params = {}
      body_params["status"] = status.Code()
      body_params["sessionId"] = session_id
      body_params["value"] = value
      response = {"code": HTTP_OK, 
                  "headers": [["Content-Location", self.url_base_ + "session/" + session_id],],
                  "body": json.dumps(body_params)}
      return response
    elif status.IsError():
      full_status = status
      full_status.AddDetails("Driver info: xwalkdriver=" + kXwalkDriverVersion + \
                             ",platform=" + os.uname()[0] + " " + os.uname()[2] + " " + os.uname()[-1])
      value.clear()
      value.update({"message": full_status.Message()})
    body_params = {}
    body_params["status"] = status.Code()
    body_params["value"] = value.get("value", value)
    body_params["sessionId"] = session_id
    body_params_str = json.dumps(body_params)
    response = {}
    response["code"] = HTTP_OK
    response["headers"] = [["Content-Type", "application; charset=utf-8"],]
    response["body"] = body_params_str
    return response

  def ExecuteCreateSession(self):
    # init session command, capabilities is located in content
    matchObj = re.match(r'/session$', self.path)
    if matchObj:
      params = {}
      varLen = int(self.headers['Content-Length'])
      content = self.rfile.read(varLen)
      #params = json.loads(content)
      # we focus on ascii not unicode
      params = yaml.load(content)
      # Create a new session
      new_id = GenerateId()
      #VLOG(0, "generate session id in webdriver:" + new_id)
      session = Session(new_id)
      condition = threading.Condition()
      threadwrap = ThreadWrap(condition, new_id, session)
      response_sele_cmd = Bind(self.PrepareResponse, ["/session", threadwrap.status, threadwrap.value, new_id])
      response_sele_cmd.is_send_func_ = True
      # prepare init session command
      bound_params = InitSessionParams(self.socket_factory_, \
                                       self.device_manager_, \
                                       self.port_server_, \
                                       self.port_manager_)
      init_session_cmd = Bind(ExecuteInitSession, [bound_params, session, params, threadwrap.value])
      threadwrap.PostTask(init_session_cmd)
      threadwrap.PostTask(response_sele_cmd)
      # run the new thread
      try:
        threadwrap.start()
      except:
        response_sele_cmd = Bind(self.PrepareResponse, ["/session", Status(kUnknownError, "failed to start a thread for the new session"), {}, ""])
        response_sele_cmd.Run()
        return Status(kUnknownError, "failed to start a thread for new session")
      # use condition lock to make sure current thread blocks until the child-thread finishes execute send function
      condition.acquire()
      threadwrap.is_ready = True
      #VLOG(0, "parents run first")
      condition.wait()
      condition.release()
      VLOG(0, "init session finish")
    return Status(kOk)

  def ExecuteDeleteSession(self):
    matchObj = re.match(r'/session/([a-f0-9]+)$', self.path)
    if matchObj:
      target_session_id = matchObj.groups()[0]
      target_threadwrap = None
      # hit the target threadwrap
      for item in threading.enumerate():
        if item.name == target_session_id:
          target_threadwrap = item
          break
      if target_threadwrap == None:
        VLOG(3, "no such session")
        return Status(kUnknownError)
      # quit relative xwalk impl
      quit_session_cmd = Bind(ExecuteQuit, [False, target_threadwrap.session, {}, {}])
      # send response
      response_sele_cmd = Bind(self.PrepareResponse, [self.path, Status(kOk), {}, target_session_id])
      response_sele_cmd.is_send_func_ = True
      # quit thread
      quit_thread_cmd = Bind(fake_quit_func)
      quit_thread_cmd.is_quit_func_ = True
      target_threadwrap.PostTask(quit_session_cmd)
      target_threadwrap.PostTask(response_sele_cmd)
      # use condition lock to make sure current thread blocks until the child-thread finishes execute send function
      target_threadwrap.condition.acquire()
      target_threadwrap.condition.wait()
      target_threadwrap.condition.release()
      target_threadwrap.PostTask(quit_thread_cmd)
      VLOG(0, "finish quit command")
    return Status(kOk)

  def SessionCommandHandler(self):
    execute_cmd = None
    # parse what kind of session command
    for key, value in SessionCommandMapping.iteritems():
      matchObj = re.match(key, self.path)
      if matchObj:
        execute_cmd = SessionCommandMapping[key].get(self.command, None)
        # ensure the command is valid
        if execute_cmd != None:
          # handle /status and /sessions
          if self.path == '/status':
            value = {}
            execute_cmd.Update([value])
            execute_cmd.Run()
            return self.PrepareResponse(self.path, Status(kOk), value, "ignore")
          elif self.path == '/sessions':
            return
          else: 
            target_session_id = matchObj.groups()[0]
          break
    # ignore invalid command
    if execute_cmd == None:
      return Status(kUnknownCommand, "invalid or unimplement session command from selenium")
    # handle command
    # hit the target thread
    for item in threading.enumerate():
      if item.name == target_session_id:
        target_threadwrap = item
        break
    if target_threadwrap == None:
      VLOG(3, "no such session")
      return Status(kNoSuchSession)
    # extract the params from selenium
    params = {}
    try:
      varLen = int(self.headers['Content-Length'])
    except:
      # in case of no such header option
      varLen = 0
    if varLen:
      content = self.rfile.read(varLen)
      #params = json.loads(content)
      params = yaml.load(content)
    # dynamic reset parameters of session command
    execute_cmd.Update([target_threadwrap.session, params, target_threadwrap.value])
    # prepare response to selenium command
    response_sele_cmd = Bind(self.PrepareResponse, [self.path, target_threadwrap.status, target_threadwrap.value, target_session_id])
    response_sele_cmd.is_send_func_ = True
    target_threadwrap.PostTask(execute_cmd)
    target_threadwrap.PostTask(response_sele_cmd)
    # use condition lock to make sure current thread blocks until the child-thread finishes execute send function
    target_threadwrap.condition.acquire()
    target_threadwrap.condition.wait()
    target_threadwrap.condition.release()
    return Status(kOk)
    
  def WindowCommandHandler(self):
    execute_cmd = None
    # parse what kind of session command
    for key, value in WindowCommandMapping.iteritems():
      matchObj = re.match(key, self.path)
      if matchObj:
        execute_cmd = WindowCommandMapping[key].get(self.command, None)
        # ensure the command is valid
        if execute_cmd != None:
          target_session_id = matchObj.groups()[0]
          break
    # ignore invalid command
    if execute_cmd == None:
      return Status(kUnknownCommand, "invalid or unimplement window command from selenium")
    # handle command
    # hit the target thread
    for item in threading.enumerate():
      if item.name == target_session_id:
        target_threadwrap = item
        break
    if target_threadwrap == None:
      VLOG(3, "no such session")
      return Status(kNoSuchSession)
    # extract the params from selenium
    params = {}
    try:
      varLen = int(self.headers['Content-Length'])
    except:
      # in case of no such header option
      varLen = 0
    if varLen:
      content = self.rfile.read(varLen)
      #params = json.loads(content)
      params = yaml.load(content)
    # make up window command
    window_cmd = Bind(ExecuteWindowCommand, [execute_cmd, target_threadwrap.session, params, target_threadwrap.value])
    # prepare response to selenium command
    response_sele_cmd = Bind(self.PrepareResponse, [self.path, Status(kOk), target_threadwrap.value, target_session_id])
    response_sele_cmd.is_send_func_ = True
    target_threadwrap.PostTask(window_cmd)
    target_threadwrap.PostTask(response_sele_cmd)
    # use condition lock to make sure current thread blocks until the child-thread finishes execute send function
    target_threadwrap.condition.acquire()
    target_threadwrap.condition.wait()
    target_threadwrap.condition.release()
    return Status(kOk)

  def do_POST(self):
    VLOG(1, "%s : %s" % (self.command, self.path))
    if re.match(r'/session$', self.path):
      return self.ExecuteCreateSession()
    else:
      self.SessionCommandHandler()
      self.WindowCommandHandler()
    
  def do_GET(self):
    VLOG(1, "%s : %s" % (self.command, self.path))
    self.SessionCommandHandler()
    self.WindowCommandHandler()
        
  def do_DELETE(self):
    VLOG(1, "%s : %s" % (self.command, self.path))
    if re.match(r'/session/([a-f0-9]+)$', self.path):
      self.ExecuteDeleteSession()
    else:
      self.SessionCommandHandler()
      self.WindowCommandHandler()

""" interface of XwalkHttpHandler for extending BaseHTTPRequestHandler """
def XwalkHttpHandlerWrapper(port, url_base, target, port_server):
  return lambda *args: XwalkHttpHandler(port, url_base, target, port_server, *args)


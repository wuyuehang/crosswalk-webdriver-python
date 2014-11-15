__all__ = ["ExecuteGetSessionCapabilities", \
           "ExecuteImplicitlyWait", \
           "ExecuteSetTimeout", \
           "ExecuteSetScriptTimeout", \
           "ExecuteGetCurrentWindowHandle"]

from browser.status import *
from browser.web_view_impl import WebViewImpl
from base.log import VLOG

kWindowHandlePrefix = "CDwindow-"

def _WebViewIdToWindowHandle(web_view_id):
  return kWindowHandlePrefix + web_view_id

def ExecuteGetSessionCapabilities(session, params, value):
  value.clear()
  value.update(session.capabilities)
  return Status(kOk)

def ExecuteImplicitlyWait(session, params, value):
  ms = params.get("ms", -1.0)
  if type(ms) != float or ms < 0.0:
    return Status(kUnknownError, "'ms' must be a non-negative number")
  session.implicit_wait = int(ms)
  return Status(kOk)

def ExecuteSetTimeout(session, params, value):
  ms_double = params.get("ms")
  if type(ms_double) != float:
    return Status(kUnknownError, "'ms' must be a double")
  typer = params.get("type")
  if type(typer) != str:
    return Status(kUnknownError, "'type' must be a string")
  timeout = int(ms_double)
  # TODO(wyh): implicit and script timeout should be cleared
  # if negative timeout is specified.
  if typer == "implicit":
    session.implicit_wait = timeout
  elif typer == "script":
    session.script_timeout = timeout
  elif typer == "page load":
    session.page_load_timeout = session.kDefaultPageLoadTimeout if timeout < 0 else timeout
  else:
    return Status(kUnknownError, "unknown type of timeout:" + typer)
  return Status(kOk)

def ExecuteSetScriptTimeout(session, params, value):
  ms = params.get("ms", -1.0)
  if type(ms) != float or ms < 0.0:
    return Status(kUnknownError, "'ms' must be a non-negative number")
  session.script_timeout = int(ms)
  return Status(kOk)

def ExecuteGetCurrentWindowHandle(session, params, value):
  #web_view = WebViewImpl("fake", 0, None)
  #status = session.GetTargetWindow(web_view)
  web_view_ids = []
  status = session.xwalk.GetWebViewIds(web_view_ids)
  print "in cur %d" % len(web_view_ids)
  if status.IsError():
    return status
  value.clear()
  #value.update({"value": _WebViewIdToWindowHandle(web_view.GetId())})
  value.update({"value": _WebViewIdToWindowHandle(web_view_ids[0])})
  return Status(kOk)


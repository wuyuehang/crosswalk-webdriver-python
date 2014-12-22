__all__ = ["ExecuteWindowCommand", \
           "ExecuteGetTitle", \
           "ExecuteRefresh", \
           "ExecuteGetCurrentUrl", \
           "ExecuteGetPageSource", \
           "ExecuteIsBrowserOnline", \
           "ExecuteGet", \
           "ExecuteGoBack", \
           "ExecuteGoForward", \
           "ExecuteFindElement", \
           "ExecuteFindElements", \
           "ExecuteExecuteScript", \
           "ExecuteExecuteAsyncScript", \
           "ExecuteScreenshot"]

from browser.web_view_impl import WebViewImpl
from browser.status import *
from base.log import VLOG
from command.element_util import FindElement

# return status and url<string>
def _GetUrl(web_view, frame):
  value = {}
  args = []
  status = web_view.CallFunction(frame, "function() { return document.URL; }", args, value)
  if status.IsError():
    return (status, "")
  if type(value["value"]) != str:
    return (Status(kUnknownError, "javascript failed to return the url"), "")
  return (Status(kOk), value)

def ExecuteWindowCommand(command, session, params, value):
  web_view = WebViewImpl("fake_id", 0, None)
  # update web_view
  status = session.GetTargetWindow(web_view)
  if status.IsError():
    return status

  status = web_view.ConnectIfNecessary()
  if status.IsError():
    return status

  status = web_view.HandleReceivedEvents()
  if status.IsError():
    return status

  if web_view.GetJavaScriptDialogManager().IsDialogOpen():
    return Status(kUnexpectedAlertOpen)

  nav_status = Status(kOk)
  for attempt in range(2):
    if attempt == 1:
      if status.Code() == kNoSuchExecutionContext:
        # Switch to main frame and retry command if subframe no longer exists.
        session.SwitchToTopFrame()
      else:
        break
    nav_status = web_view.WaitForPendingNavigations(session.GetCurrentFrameId(), session.page_load_timeout, True)
    if nav_status.IsError():
      return nav_status
    print "before cmd run status %s" % nav_status.Message()
    command.Update([session, web_view, params, value])
    status = command.Run()
  print "after 1st WaitForPendingNavigations status %s" % nav_status.Message()
  nav_status = web_view.WaitForPendingNavigations(session.GetCurrentFrameId(), session.page_load_timeout, True)
  print "after 2nd WaitForPendingNavigations status %s" % nav_status.Message()

  if status.IsOk() and nav_status.IsError() and nav_status.Code() != kUnexpectedAlertOpen:
    return nav_status
  if status.Code() == kUnexpectedAlertOpen:
    return Status(kOk)
  return status

def ExecuteGetTitle(session, web_view, params, value):
  kGetTitleScript = "function() {"\
                    "  if (document.title)"\
                    "    return document.title;"\
                    "  else"\
                    "    return document.URL;"\
                    "}"
  args = []
  return web_view.CallFunction("", kGetTitleScript, args, value)

def ExecuteRefresh(session, web_view, params, value):
  return web_view.Reload()

def ExecuteGetCurrentUrl(session, web_view, params, value):
  (status, url) = _GetUrl(web_view, session.GetCurrentFrameId())
  if status.IsError():
    return status
  value.clear()
  value.update(url)   
  return Status(kOk)

def ExecuteGetPageSource(session, web_view, params, value):
  kGetPageSource = \
      "function() {"\
      "  return new XMLSerializer().serializeToString(document);"\
      "}"
  return web_view.CallFunction(session.GetCurrentFrameId(), kGetPageSource, [], value)

def ExecuteIsBrowserOnline(session, web_view, params, value):
  return web_view.EvaluateScript(session.GetCurrentFrameId(), "navigator.onLine", value)

def ExecuteGet(session, web_view, params, value):
  url = params.get("url", None)
  if type(url) != str:
    return Status(kUnknownError, "'url' must be a string")
  return web_view.Load(url)

def ExecuteGoBack(session, web_view, params, value):
  return web_view.EvaluateScript("", "window.history.back();", value)

def ExecuteGoForward(session, web_view, params, value):
  return web_view.EvaluateScript("", "window.history.forward();", value)

def ExecuteFindElement(session, web_view, params, value):
  interval_ms = 50
  return FindElement(interval_ms, True, "", session, web_view, params, value)

def ExecuteFindElements(session, web_view, params, value):
  interval_ms = 50
  return FindElement(interval_ms, False, "", session, web_view, params, value)

def ExecuteExecuteScript(session, web_view, params, value):
  script = params.get("script")
  if type(script) != str:
    return Status(kUnknownError, "'script' must be a string")
  if script == ":takeHeapSnapshot":
    #TODO:
    #return web_view->TakeHeapSnapshot(value);
    pass
  else:
    args = params.get("args")
    if type(args) != list:
      return Status(kUnknownError, "'args' must be a list")
    return web_view.CallFunction(session.GetCurrentFrameId(), "function(){" + script + "}", args, value)

def ExecuteExecuteAsyncScript(session, web_view, params, value):
  script = params.get("script")
  if type(script) != str:
    return Status(kUnknownError, "'script' must be a string")
  args = params.get("args")
  if type(args) != list:
    return Status(kUnknownError, "'args' must be a list")
  return web_view.CallUserAsyncFunction(session.GetCurrentFrameId(), "function(){" + script + "}", args, session.script_timeout, value)

def ExecuteScreenshot(session, web_view, params, value):
  status = session.xwalk.ActivateWebView(web_view.GetId())
  if status.IsError():
    print "The Crosswalk WebView Activate Status is %s" % status.Message()

  (status, screenshot) = web_view.CaptureScreenshot()
  if status.IsError():
    return status
  
  value.clear()
  value.update({"value": screenshot})
  return Status(kOk)


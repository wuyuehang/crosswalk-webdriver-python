__all__ = ["ExecuteElementCommand", \
           "ExecuteFindChildElement", \
           "ExecuteFindChildElements", \
           "ExecuteGetElementText", \
           "ExecuteGetElementTagName", \
           "ExecuteIsElementSelected", \
           "ExecuteIsElementEnabled", \
           "ExecuteIsElementDisplayed"]

from element_util import *
from browser.status import *
from browser.web_view_impl import WebViewImpl
from third_party.atoms import *

def ExecuteElementCommand(command, element_id, session, params, value):
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
    command.Update([session, web_view, element_id, params, value])
    status = command.Run()
  print "after 1st WaitForPendingNavigations status %s" % nav_status.Message()
  nav_status = web_view.WaitForPendingNavigations(session.GetCurrentFrameId(), session.page_load_timeout, True)
  print "after 2nd WaitForPendingNavigations status %s" % nav_status.Message()

  if status.IsOk() and nav_status.IsError() and nav_status.Code() != kUnexpectedAlertOpen:
    return nav_status
  if status.Code() == kUnexpectedAlertOpen:
    return Status(kOk)
  return status

def ExecuteFindChildElement(session, web_view, element_id, params, value):
  interval_ms = 50
  return FindElement(interval_ms, True, element_id, session, web_view, params, value)

def ExecuteFindChildElements(session, web_view, element_id, params, value):
  interval_ms = 50
  return FindElement(interval_ms, False, element_id, session, web_view, params, value)

def ExecuteGetElementText(session, web_view, element_id, params, value):
  args = []
  args.append(CreateElement(element_id))
  return web_view.CallFunction(session.GetCurrentFrameId(), GET_TEXT, args, value)
  
def ExecuteGetElementTagName(session, web_view, element_id, params, value):
  args = []
  args.append(CreateElement(element_id))
  return web_view.CallFunction(session.GetCurrentFrameId(), "function(elem) { return elem.tagName.toLowerCase(); }", args, value)

def ExecuteIsElementSelected(session, web_view, element_id, params, value):
  args = []
  args.append(CreateElement(element_id))
  return web_view.CallFunction(session.GetCurrentFrameId(), IS_SELECTED, args, value)

def ExecuteIsElementEnabled(session, web_view, element_id, params, value):
  args = []
  args.append(CreateElement(element_id))
  return web_view.CallFunction(session.GetCurrentFrameId(), IS_ENABLED, args, value)

def ExecuteIsElementDisplayed(session, web_view, element_id, params, value):
  args = []
  args.append(CreateElement(element_id))
  return web_view.CallFunction(session.GetCurrentFrameId(), IS_DISPLAYED, args, value)




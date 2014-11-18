__all__ = ["FindElement", \
           "CreateElement", \
           "IsElementEnabled", \
           "IsOptionElementSelected", \
           "IsElementDisplayed", \
           "GetElementSize", \
           "IsOptionElementTogglable"]

import time
from misc.basic_types import WebPoint
from misc.basic_types import WebSize
from misc.basic_types import WebRect
from third_party.atoms import *
from browser.status import *
from browser.js import *

kElementKey = "ELEMENT"

def ParseFromValue(value, target):
  if type(value) != dict:
    return False
  # target is WebPoint
  if isinstance(target, WebPoint):
    x = value.get("x")
    y = value.get("y")
    if type(x) != float or type(y) != float:
      return False
    target.x = int(x)
    target.y = int(y)
    return True
  # target is WebSize
  if isinstance(target, WebSize):
    width = value.get("width")
    height = value.get("height")
    if type(width) != float or type(height) != float:
      return False
    target.width = int(width)
    target.height = int(height)
    return True
  # target is WebRect
  if isinstance(target, WebRect):
    x = value.get("left")
    y = value.get("right")
    width = value.get("width")
    height = value.get("height")
    if type(x) != float or type(y) != float or type(width) != float or type(height) != float:
      return False
    target.origin.x = int(x)
    target.origin.y = int(y)
    target.size.width = int(width)
    target.size.height = int(height)
    return True
  
def CreateValueFrom(target):
  dict_value = {}
  # create value from WebPoint
  if isinstance(target, WebPoint):
    dict_value["x"] = target.x
    dict_value["y"] = target.y
  # create value from WebSize
  if isinstance(target, WebSize):
    dict_value["width"] = target.width
    dict_value["height"] = target.height
    return dict_value
  # create value from WebRect 
  if isinstance(target, WebRect):
    dict_value["left"] = target.X()
    dict_value["right"] = target.Y()
    dict_value["width"] = target.Width()
    dict_value["height"] = target.Height()
    return dict_value

def CreateElement(element_id):
  element = {}
  element[kElementKey] = element_id
  return element

def CallAtomsJs(frame, web_view, atom_function, args, result):
  return web_view.CallFunction(frame, atom_function, args, result)

def VerifyElementClickable(frame, web_view, element_id, location):
  args = []
  args.append(CreateElement(element_id))
  args.append(CreateValueFrom(location))
  result = {}
  status = CallAtomsJs(frame, web_view, IS_ELEMENT_CLICKABLE, args, result)
  if status.IsError():
    return status
  is_clickable = False
  is_clickable = result.get("clickable")
  if type(is_clickable) != bool:
    return Status(kUnknownError, "failed to parse value of IS_ELEMENT_CLICKABLE")
  if not is_clickable:
    message = result.get("message")
    if type(message) != str:
      message = "element is not clickable"
    return Status(kUnknownError, message)
  return Status(kOk)

def FindElement(interval_ms, only_one, root_element_id, session, web_view, params, value):
  strategy = params.get("using")
  if type(strategy) != str:
    return Status(kUnknownError, "'using' must be a string")
  target = params.get("value")
  if type(target) != str:
    return Status(kUnknownError, "'value' must be a string")

  script = FIND_ELEMENT if only_one else FIND_ELEMENTS
  locator = {}
  locator[strategy] = target
  arguments = []
  arguments.append(locator)
  if root_element_id:
    arguments.append(CreateElement(root_element_id))

  start_time = time.time()
  while True: 
    temp = {}
    status = web_view.CallFunction(session.GetCurrentFrameId(), script, arguments, temp)
    if status.IsError():
      return status
    # no matter what kind of result, it will packed in {"value": RemoteObject} format
    # RemoteObject can be JSON type
    if temp != {}:
      if only_one:
        value.clear()
        value.update(temp)
        return Status(kOk)
      else:
        if type(temp["value"]) != list:
          return Status(kUnknownError, "script returns unexpected result")
        if len(temp["value"]) > 0:
          value.clear()
          value.update(temp)
          return Status(kOk)

    if ((time.time() - start_time) >= session.implicit_wait):
      if only_one:
        return Status(kNoSuchElement)
      else:
        value.update({"value": []})
        return Status(kOk)

    time.sleep(float(interval_ms)/1000)
  return Status(kUnknownError)

# return status and is_enabled<bool>
def IsElementEnabled(session, web_view, element_id):
  is_enabled = False
  args = []
  args.append(CreateElement(element_id))
  result = {}
  status = CallAtomsJs(session.GetCurrentFrameId(), web_view, IS_ENABLED, args, result)
  if status.IsError():
    return (status, is_enabled)
  # we packed everything in key "value", remember?
  is_enabled = result["value"]
  if type(is_enabled) != bool:
    return (Status(kUnknownError, "IS_ENABLED should return a boolean value"), False)
  return (Status(kOk), is_enabled)

# return status and is_selected<bool>
def IsOptionElementSelected(session, web_view, element_id):
  is_selected = False
  args = []
  args.append(CreateElement(element_id))
  result = {}
  status = CallAtomsJs(session.GetCurrentFrameId(), web_view, IS_SELECTED, args, result)
  if status.IsError():
    return (status, is_selected)
  # we packed everything in key "value", remember?
  is_selected = result["value"]
  if type(is_selected) != bool:
    return (Status(kUnknownError, "IS_SELECTED should return a boolean value"), False)
  return (Status(kOk), is_selected)

def GetElementSize(session, web_view, element_id, size):
  args = []
  args.append(CreateElement(element_id))
  result = {}
  status = CallAtomsJs(session.GetCurrentFrameId(), web_view, GET_SIZE, args, result)
  if status.IsError():
    return status
  # we packed everything in key "value", remember?
  if not ParseFromValue(result["value"], size):
    return Status(kUnknownError, "failed to parse value of GET_SIZE")
  return Status(kOk)

# return status and is_displayed<bool>
def IsElementDisplayed(session, web_view, element_id, ignore_opacity):
  is_displayed = False
  args = []
  args.append(CreateElement(element_id))
  args.append(ignore_opacity)
  result = {}
  status = CallAtomsJs(session.GetCurrentFrameId(), web_view, IS_DISPLAYED, args, result)
  if status.IsError():
    return (status, is_displayed)
  # we packed everything in key "value", remember?
  is_displayed = result["value"] 
  if type(is_displayed) != bool:
    return (Status(kUnknownError, "IS_DISPLAYED should return a boolean value"), False)
  return (Status(kOk), is_displayed)

# return status and is_togglable<bool>
def IsOptionElementTogglable(session, web_view, element_id):
  is_togglable = False
  args = []
  args.append(CreateElement(element_id))
  result = {}
  status = web_view.CallFunction(session.GetCurrentFrameId(), kIsOptionElementToggleableScript, args, result)
  if status.IsError():
    return (status, is_togglable)
  # we packed everything in key "value", remember?
  is_togglable = result["value"]
  if type(is_togglable) != bool:
    return (Status(kUnknownError, "failed check if option togglable or not"), False)
  return (Status(kOk), is_togglable)

def SetOptionElementSelected(session, web_view, element_id, selected):
  # TODO(wyh): need to fix throwing error if an alert is triggered.
  args = []
  args.append(CreateElement(element_id))
  args.append(selected)
  return CallAtomsJs(session.GetCurrentFrameId(), web_view, CLICK, args, {})

def GetActiveElement(session, web_view, value):
  return web_view.CallFunction(session.GetCurrentFrameId(), "function() { return document.activeElement || document.body }", [], value)

def GetElementAttribute(session, web_view, element_id, attribute_name, value):
  args = []
  args.append(CreateElement(element_id))
  args.append(attribute_name)
  return CallAtomsJs(session.GetCurrentFrameId(), web_view, GET_ATTRIBUTE, args, value)

# return status and name<string>
def GetElementTagName(session, web_view, element_id):
  name = ""
  args = []
  args.append(CreateElement(element_id))
  result = {}
  status = web_view.CallFunction(session.GetCurrentFrameId(), "function(elem) { return elem.tagName.toLowerCase(); }", args, result)
  if status.IsError():
    return (status, name)
  # we packed everything in key "value", remember?
  name = result["value"]
  if type(name) != str:
    return (Status(kUnknownError, "failed to get element tag name"), "")
  return (Status(kOk), name)

# return status and is_focused<bool>
def IsElementFocused(session, web_view, element_id):
  is_focused = False
  result = {}
  status = GetActiveElement(session, web_view, result)
  if status.IsError():
    return (status, is_focused)
  element_dict = CreateElement(element_id)
  # we packed everything in key "value", remember?
  is_focused = (result["value"] == element_dict)
  return (Status(kOk), is_focused)

def GetElementAttribute(session, web_view, element_id, attribute_name, value):
  args = []
  args.append(CreateElement(element_id))
  args.append(attribute_name)
  return CallAtomsJs(session.GetCurrentFrameId(), web_view, GET_ATTRIBUTE, args, value)

def ToggleOptionElement(session, web_view, element_id):
  is_selected = False
  (status, is_selected) = IsOptionElementSelected(session, web_view, element_id)
  if status.IsError():
    return status
  return SetOptionElementSelected(session, web_view, element_id, not is_selected)

def GetElementRegion(session, web_view, element_id, rect):
  args = []
  args.append(CreateElement(element_id))
  result = {}
  status = web_view.CallFunction(session.GetCurrentFrameId(), kGetElementRegionScript, args, result)
  if status.IsError():
    return status
  if not ParseFromValue(result["value"], rect):
    return Status(kUnknownError, "failed to parse value of getElementRegion")
  return Status(kOk)

def GetElementEffectiveStyle(frame, web_view, element_id, sproperty, value):
  args = []
  args.append(CreateElement(element_id))
  args.append(sproperty)
  result = {}
  status = web_view.CallFunction(frame, GET_EFFECTIVE_STYLE, args, result)
  if status.IsError():
    return status
  if type(result["value"]) != str:
    return Status(kUnknownError, "failed to parse value of GET_EFFECTIVE_STYLE")
  value.clear()
  value.update(result)
  return Status(kOk)


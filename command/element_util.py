__all__ = ["FindElement"]

import time
from misc.basic_types import WebPoint
from misc.basic_types import WebSize
from misc.basic_types import WebRect
from third_party.atoms import *
from browser.status import *

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


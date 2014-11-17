from element_util import *

__all__ = ["ExecuteFindChildElement", \
           "ExecuteFindChildElements"]
"""
def ExecuteElementCommand(command, session, web_view, params, value):
  sid = 
  if (params.GetString("id", &id) || params.GetString("element", &id))
    return command.Run(session, web_view, id, params, value);
  return Status(kUnknownError, "element identifier must be a string");
}
"""
def ExecuteFindChildElement(session, web_view, element_id, params, value):
  interval_ms = 50
  return FindElement(interval_ms, True, element_id, session, web_view, params, value)

def ExecuteFindChildElements(session, web_view, element_id, params, value):
  interval_ms = 50
  return FindElement(interval_ms, False, element_id, session, web_view, params, value)


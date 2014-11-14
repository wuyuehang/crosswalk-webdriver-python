__all__ = ["ExecuteGetSessionCapabilities", \
           "ExecuteImplicitlyWait"]

from browser.status import *
from base.log import VLOG

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


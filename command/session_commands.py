__all__ = ["ExecuteGetSessionCapabilities"]

from browser.status import *
from base.log import VLOG

def ExecuteGetSessionCapabilities(session, params, value):
  value.clear()
  value.update(session.capabilities)
  return Status(kOk)


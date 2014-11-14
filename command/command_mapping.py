__all__ = ["SessionCommandMapping"]

from base.bind import Bind
from window_commands import *
from session_commands import *
from init_session_commands import ExecuteGetStatus


SessionCommandMapping = {r'/status$': {'GET': Bind(ExecuteGetStatus)},
                         r'/session/([a-f0-9]+)$': {'GET': Bind(ExecuteGetSessionCapabilities)}}

WindowCommandMapping = {r'/session/([a-f0-9]+)/title$': {'GET': Bind(ExecuteGetTitle)},
                        r'/session/([a-f0-9]+)/refresh$': {'POST': Bind(ExecuteRefresh)},
                        r'/session/([a-f0-9]+)/url$': {'GET': Bind(ExecuteGetCurrentUrl),
                                                       'POST': Bind(ExecuteGet)},
                        r'/session/([a-f0-9]+)/source$': {'GET': Bind(ExecuteGetPageSource)},
                        r'/session/([a-f0-9]+)/browser_connection$': {'GET': Bind(ExecuteIsBrowserOnline)},
                        r'/session/([a-f0-9]+)/back$': {'POST': Bind(ExecuteGoBack)},
                        r'/session/([a-f0-9]+)/forward$': {'POST': Bind(ExecuteGoForward)}}


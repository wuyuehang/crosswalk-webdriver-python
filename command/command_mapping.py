__all__ = ["SessionCommandMapping"]

from base.bind import Bind
from window_commands import *
from session_commands import *
from alert_commands import *
from element_commands import *
from init_session_commands import ExecuteGetStatus

# session commands map
SessionCommandMapping = {r'/status$': {'GET': Bind(ExecuteGetStatus)},
                         r'/session/([a-f0-9]+)$': {'GET': Bind(ExecuteGetSessionCapabilities)},
                         r'/session/([a-f0-9]+)/timeouts/implicit_wait$': {'POST': Bind(ExecuteImplicitlyWait)},
                         r'/session/([a-f0-9]+)/timeouts$': {'POST': Bind(ExecuteSetTimeout)},
                         r'/session/([a-f0-9]+)/timeouts/async_script$': {'POST': Bind(ExecuteSetScriptTimeout)},
                         r'/session/([a-f0-9]+)/window_handle$': {'GET': Bind(ExecuteGetCurrentWindowHandle)}}

# window commands map
WindowCommandMapping = {r'/session/([a-f0-9]+)/title$': {'GET': Bind(ExecuteGetTitle)},
                        r'/session/([a-f0-9]+)/refresh$': {'POST': Bind(ExecuteRefresh)},
                        r'/session/([a-f0-9]+)/url$': {'GET': Bind(ExecuteGetCurrentUrl),
                                                       'POST': Bind(ExecuteGet)},
                        r'/session/([a-f0-9]+)/source$': {'GET': Bind(ExecuteGetPageSource)},
                        r'/session/([a-f0-9]+)/browser_connection$': {'GET': Bind(ExecuteIsBrowserOnline)},
                        r'/session/([a-f0-9]+)/back$': {'POST': Bind(ExecuteGoBack)},
                        r'/session/([a-f0-9]+)/forward$': {'POST': Bind(ExecuteGoForward)},
                        r'/session/([a-f0-9]+)/element$': {'POST': Bind(ExecuteFindElement)},
                        r'/session/([a-f0-9]+)/elements$': {'POST': Bind(ExecuteFindElements)}}

# alert commands map
AlertCommandMapping = {r'/session/([a-f0-9]+)/accept_alert$': {'POST': Bind(ExecuteAcceptAlert)}}

# element commands map
ElementCommandMapping = {r'/session/([a-f0-9]+)/element/([.\-0-9]+)/text$': {'GET': Bind(ExecuteGetElementText)},
                         r'/session/([a-f0-9]+)/element/([.\-0-9]+)/name$': {'GET': Bind(ExecuteGetElementTagName)},
                         r'/session/([a-f0-9]+)/element/([.\-0-9]+)/selected$': {'GET': Bind(ExecuteIsElementSelected)},
                         r'/session/([a-f0-9]+)/element/([.\-0-9]+)/enabled$': {'GET': Bind(ExecuteIsElementEnabled)},
                         r'/session/([a-f0-9]+)/element/([.\-0-9]+)/displayed$': {'GET': Bind(ExecuteIsElementDisplayed)}}



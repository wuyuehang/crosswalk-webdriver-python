
from browser.status import *
from browser.ui_events import *
from keyboard_codes_posix import *
"""
class ModifierMaskAndKeyCode(object):

  def __init__(self, mask, key_code):
    self.mask = mask
    self.key_code = key_code

  def Update(self, other):
    self.mask = other.mask
    self.key_code = other.key_code
    return

kModifiers = [ModifierMaskAndKeyCode(kShiftKeyModifierMask, VKEY_SHIFT),
              ModifierMaskAndKeyCode(kControlKeyModifierMask, VKEY_CONTROL),
              ModifierMaskAndKeyCode(kAltKeyModifierMask, VKEY_MENU)]

# TODO(wyh): Use this in KeyMap.
# Ordered list of all the key codes corresponding to special WebDriver keys.
# These WebDriver keys are defined in the Unicode Private Use Area.
# http://code.google.com/p/selenium/wiki/JsonWireProtocol#/session/:sessionId/element/:id/value
kSpecialWebDriverKeys = [
    VKEY_UNKNOWN,
    VKEY_UNKNOWN,
    VKEY_HELP,
    VKEY_BACK,
    VKEY_TAB,
    VKEY_CLEAR,
    VKEY_RETURN,
    VKEY_RETURN,
    VKEY_SHIFT,
    VKEY_CONTROL,
    VKEY_MENU,
    VKEY_PAUSE,
    VKEY_ESCAPE,
    VKEY_SPACE,
    VKEY_PRIOR,    # page up
    VKEY_NEXT,     # page down
    VKEY_END,
    VKEY_HOME,
    VKEY_LEFT,
    VKEY_UP,
    VKEY_RIGHT,
    VKEY_DOWN,
    VKEY_INSERT,
    VKEY_DELETE,
    VKEY_OEM_1,     # semicolon
    VKEY_OEM_PLUS,  # equals
    VKEY_NUMPAD0,
    VKEY_NUMPAD1,
    VKEY_NUMPAD2,
    VKEY_NUMPAD3,
    VKEY_NUMPAD4,
    VKEY_NUMPAD5,
    VKEY_NUMPAD6,
    VKEY_NUMPAD7,
    VKEY_NUMPAD8,
    VKEY_NUMPAD9,
    VKEY_MULTIPLY,
    VKEY_ADD,
    VKEY_OEM_COMMA,
    VKEY_SUBTRACT,
    VKEY_DECIMAL,
    VKEY_DIVIDE,
    VKEY_UNKNOWN,
    VKEY_UNKNOWN,
    VKEY_UNKNOWN,
    VKEY_UNKNOWN,
    VKEY_UNKNOWN,
    VKEY_UNKNOWN,
    VKEY_UNKNOWN,
    VKEY_F1,
    VKEY_F2,
    VKEY_F3,
    VKEY_F4,
    VKEY_F5,
    VKEY_F6,
    VKEY_F7,
    VKEY_F8,
    VKEY_F9,
    VKEY_F10,
    VKEY_F11,
    VKEY_F12]

kWebDriverNullKey = 0xE000
kWebDriverShiftKey = 0xE008
kWebDriverControlKey = 0xE009
kWebDriverAltKey = 0xE00A
kWebDriverCommandKey = 0xE03D

# Returns whether the given key code has a corresponding printable char.
# Notice: The given key code should be a special WebDriver key code.
def IsSpecialKeyPrintable(key_code):
  return (key_code == VKEY_TAB or key_code == VKEY_SPACE or \
      key_code == VKEY_OEM_1 or key_code == VKEY_OEM_PLUS or \
      key_code == VKEY_OEM_COMMA or \
      (key_code >= VKEY_NUMPAD0 and key_code <= VKEY_DIVIDE))

# Returns whether the given key is a WebDriver key modifier.
def IsModifierKey(key):
  if (key == kWebDriverShiftKey or key == kWebDriverControlKey or \
      key == kWebDriverAltKey or key == kWebDriverCommandKey):
    return True
  else:
    return False

# Gets the key code associated with |key|, if it is a special WebDriver key.
# Returns whether |key| is a special WebDriver key. If true, |key_code| will
# be set.
# return bool and key_code<int>
def KeyCodeFromSpecialWebDriverKey(key) {
  # base::char16
  index = key - 0xE000
  is_special_key = (index >= 0 and index < len(kSpecialWebDriverKeys))
  if is_special_key:
    return (is_special_key, kSpecialWebDriverKeys[index])
  return (is_special_key, -1)

# Gets the key code associated with |key_utf16|, if it is a special shorthand
# key. Shorthand keys are common text equivalents for keys, such as the newline
# character, which is shorthand for the return key. Returns whether |key| is
# a shorthand key. If true, |key_code| will be set and |client_should_skip|
# will be set to whether the key should be skipped.
# return bool and key_code<int> and client_should_skip<bool>
def KeyCodeFromShorthandKey(base::char16 key_utf16,
                             ui::KeyboardCode* key_code,
                             bool* client_should_skip) {
  base::string16 key_str_utf16;
  key_str_utf16.push_back(key_utf16);
  std::string key_str_utf8 = base::UTF16ToUTF8(key_str_utf16);
  if (key_str_utf8.length() != 1)
    return false;
  bool should_skip = false;
  char key = key_str_utf8[0];
  if (key == '\n') {
    *key_code = ui::VKEY_RETURN;
  } else if (key == '\t') {
    *key_code = ui::VKEY_TAB;
  } else if (key == '\b') {
    *key_code = ui::VKEY_BACK;
  } else if (key == ' ') {
    *key_code = ui::VKEY_SPACE;
  } else if (key == '\r') {
    *key_code = ui::VKEY_UNKNOWN;
    should_skip = true;
  } else {
    return false;
  }
  *client_should_skip = should_skip;
  return true;
}

# Convenience functions for creating |KeyEvent|s. Used by unittests.          
KeyEvent CreateKeyDownEvent(ui::KeyboardCode key_code, int modifiers);         
KeyEvent CreateKeyUpEvent(ui::KeyboardCode key_code, int modifiers);           
KeyEvent CreateCharEvent(const std::string& unmodified_text,                   
                         const std::string& modified_text,                     
                         int modifiers);                                       
                                                                               
# Converts keys into appropriate |KeyEvent|s. This will do a best effort      
# conversion. However, if the input is invalid it will return a status with   
# an error message. If |release_modifiers| is true, all modifiers would be    
# depressed. |modifiers| acts both an input and an output, however, only when 
# the conversion process is successful will |modifiers| be changed.           
Status ConvertKeysToKeyEvents(const base::string16& keys,                      
                              bool release_modifiers,                                                                                                         
                              int* modifiers,                                  
                              std::list<KeyEvent>* key_events);
"""

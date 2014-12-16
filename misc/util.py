"""
# return status and sticky_modifiers<int>
def SendKeysOnWindow(web_view, key_list, release_modifiers):
    int* sticky_modifiers) {
  base::string16 keys;
  Status status = FlattenStringArray(key_list, &keys);
  if (status.IsError())
    return status;
  std::list<KeyEvent> events;
  int sticky_modifiers_tmp = *sticky_modifiers;
  status = ConvertKeysToKeyEvents(
      keys, release_modifiers, &sticky_modifiers_tmp, &events);
  if (status.IsError())
    return status;
  status = web_view->DispatchKeyEvents(events);
  if (status.IsOk())
    *sticky_modifiers = sticky_modifiers_tmp;
  return status;
}
"""

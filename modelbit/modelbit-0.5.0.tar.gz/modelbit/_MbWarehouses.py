class _MbWarehouses:
  _mbMain = None
  _warehouses = []
  
  def __init__(self, mbMain):
    self._mbMain = mbMain
    resp = self._mbMain._getJsonOrPrintError("jupyter/v1/warehouses/list")
    if resp:
      self._warehouses = resp["warehouses"]
  
  def _repr_markdown_(self):
    return self._makeWarehousesMkTable()

  def _makeWarehousesMkTable(self):
    import timeago, datetime
    if len(self._warehouses) == 0: return ""
    formatStr = "| Name | Type | Connected | Deploy Status | \n" + \
      "|:-|:-|:-|:-|\n"
    for w in self._warehouses:
      connectedAgo = timeago.format(datetime.datetime.fromtimestamp(w["createdAtMs"]/1000), datetime.datetime.now())
      formatStr += f'| { w["displayName"] } | { w["type"] } | { connectedAgo } | { w["deployStatusPretty"] } | \n'
    return formatStr

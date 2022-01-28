re_number_scale_list = [
    "-*\d{1,7}[ ]*",
    "-*\d{1,7}[\.,]\d{1,7}[ ]*",
    "\d{1,7}[\.,\-x]\d{1,7}[ ]*",
    "\d{1,3}[\.,]\d{3}[\.,]\d{1,5}[ ]*",
    "\d{1,3}[\.,]\d{3}[\.,]\d{1,3}[\.,]\d{1,5}[ ]",
]
re_number_scale_list = [
    item + "(s|h|p|gram|g|kg|mg|hz|cm|mm|m|km|mb|gb|tb|l|m3|m2|ha|km2|km3|kw|w|kWh|kwh|v|%|usd|vnd|đ|euro|cent|kb|%|$|euro|s|m|nm|g|ampe|mol|cd|n|pa|atm|đ|ha|h|kb|s|ml|l|gb|mb|kb|kg|mg|m3|km3|dm3|cc|cm3|m2|km2|dm2|cm2|mm2|km|dm|cm|mm|nm|mph|ft|kn|nm|gn|mn|kn|mn|j|kj|mj|gj|mw|kw|w|wh|mwh|kwh|mev|ev|cal|kcal|oc|of|ok|dp|wb|diop|bq|db|min|sec|mmhg|ma|rad|hz|lb|oz|gal|inch|vnđ|vnd|rm|rub|vg|ph|s2)"
    for item in re_number_scale_list]

class StockItem:
	item_id: int
	product_id: int
	stock_id: int
	qty: int
	is_in_stock: bool
	is_qty_decimal: bool
	show_default_notification_message: bool
	use_config_min_qty: bool
	min_qty: int
	use_config_min_sale_qty: int
	min_sale_qty: int
	use_config_max_sale_qty: bool
	max_sale_qty: int
	use_config_backorders: bool
	backorders: int
	use_config_notify_stock_qty: bool
	notify_stock_qty: int
	use_config_qty_increments: bool
	qty_increments: int
	use_config_enable_qty_inc: bool
	enable_qty_increments: bool
	use_config_manage_stock: bool
	manage_stock: bool
	low_stock_date: str
	is_decimal_divided: bool
	stock_status_changed_auto: int

	def __init__(self, item_id: int,
						qty: int,
						is_in_stock: bool,
						is_qty_decimal: bool,
						show_default_notification_message: bool,
						use_config_min_qty: bool,
						min_qty: int,
						use_config_min_sale_qty: int,
						min_sale_qty: int,
						use_config_max_sale_qty: bool,
						max_sale_qty: int,
						use_config_backorders: bool,
						backorders: int,
						use_config_notify_stock_qty: bool,
						notify_stock_qty: int,
						use_config_qty_increments: bool,
						qty_increments: int,
						use_config_enable_qty_inc: bool,
						enable_qty_increments: bool,
						use_config_manage_stock: bool,
						manage_stock: bool,
						low_stock_date: str,
						is_decimal_divided: bool,
						stock_status_changed_auto: int,
						product_id: int = None,
						stock_id: int = None) -> None:
		self.item_id = item_id
		self.qty = qty
		self.is_in_stock = is_in_stock
		self.is_qty_decimal = is_qty_decimal
		self.show_default_notification_message = show_default_notification_message
		self.use_config_min_qty = use_config_min_qty
		self.min_qty = min_qty
		self.use_config_min_sale_qty = use_config_min_sale_qty
		self.min_sale_qty = min_sale_qty
		self.use_config_max_sale_qty = use_config_max_sale_qty
		self.max_sale_qty = max_sale_qty
		self.use_config_backorders = use_config_backorders
		self.backorders = backorders
		self.use_config_notify_stock_qty = use_config_notify_stock_qty
		self.notify_stock_qty = notify_stock_qty
		self.use_config_qty_increments = use_config_qty_increments
		self.qty_increments = qty_increments
		self.use_config_enable_qty_inc = use_config_enable_qty_inc
		self.enable_qty_increments = enable_qty_increments
		self.use_config_manage_stock = use_config_manage_stock
		self.manage_stock = manage_stock
		self.low_stock_date = low_stock_date
		self.is_decimal_divided = is_decimal_divided
		self.stock_status_changed_auto = stock_status_changed_auto

		if stock_id:
			self.stock_id = stock_id
		if product_id:
			self.product_id = product_id


class ItauPowerInventory:
	stock_item: StockItem

	def __init__(self, stock_item: StockItem) -> None:
		self.stock_item = stock_item

from controllers.order_controller.order_handler import CreateOrderHandler
from controllers.order_controller.fetch_order_handler import FetchOrderStatusHandler

order_routes = [
    (r"/create_order", CreateOrderHandler),
    (r"/fetch_order/(.*)", FetchOrderStatusHandler )
]
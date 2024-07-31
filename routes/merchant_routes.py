from controllers.merchant_controller import merchant_signup_handler
from controllers.merchant_controller import merchant_signin_handler
merchant_routes = [

    (r"/merchant_signup",merchant_signup_handler.MerchantSignupHandler),
    (r"/merchant_signin",merchant_signin_handler.MerchantLoginHandler)
]
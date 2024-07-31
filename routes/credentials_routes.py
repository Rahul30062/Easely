from controllers.merchant_controller.merchant_credentials_handler import CredentialsHandler

credentials_routes = [
    (r"/post_credentials", CredentialsHandler),
]



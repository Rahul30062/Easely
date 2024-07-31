import requests
import time
import tornado.web
from sqlalchemy.future import select
from utils.auth import verify_token
from utils.order_id_generate import generate_order_id
from db_init import AsyncSessionLocal
from models.orders_model import Order
from models.transaction_model import Transaction
from models.credentials_model import Credential

class CreateOrderHandler(tornado.web.RequestHandler):
    async def post(self):
        start = time.time()
        token = self.request.headers.get("Authorization")
        if not token:
            self.set_status(401)
            self.write({"error": "Authorization token is missing"})
            return

        if token.startswith("Bearer "):
            token = token[7:]

        try:
            payload = verify_token(token)
            merchant_id = payload.get("id")
        except Exception as e:
            self.set_status(401)
            self.write({"error": str(e)})
            return

        data = tornado.escape.json_decode(self.request.body)
        amount = data.get("amount")  
        currency = data.get("currency")

        if not all([amount, currency, merchant_id]):
            self.set_status(400)
            self.write({"error": "Missing required fields"})
            return

        nimbbl_order_id = generate_order_id()

        async with AsyncSessionLocal() as session:
            async with session.begin():
                result = await session.execute(select(Credential).filter_by(merchant_id=merchant_id))
                credentials = result.scalar_one_or_none()

                if not credentials:
                    self.set_status(500)
                    self.write({"error": "Razorpay credentials not found"})
                    return

                try:
                    response = requests.post(
                        "https://api.razorpay.com/v1/orders",
                        auth=(credentials.access_key, credentials.secret_key),
                        json={
                            "amount": amount,
                            "currency": currency,
                            "receipt": nimbbl_order_id
                        }
                    )
                    response.raise_for_status()
                    razorpay_order = response.json()
                    razorpay_order_id = razorpay_order['id']
                except requests.RequestException as e:
                    self.set_status(500)
                    self.write({"error": "Failed to create order with Razorpay", "details": str(e)})
                    return

                order = Order(
                    order_id=nimbbl_order_id,
                    amount=amount,
                    currency=currency,
                    status='pending',
                    merchant_id=merchant_id
                )
                session.add(order)

                transaction = Transaction(
                    psp="Razorpay",
                    razorpay_order_id=razorpay_order_id,
                    status='pending',
                    order_id=order.order_id
                )
                session.add(transaction)

            await session.commit()

            self.write({
                "message": "Order created successfully",
                "nimbbl_order_id": nimbbl_order_id,
            })
            end=time.time()
            print((end-start)*10**3,"ms") 

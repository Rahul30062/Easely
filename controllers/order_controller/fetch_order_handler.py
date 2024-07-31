import requests
import tornado.web
from sqlalchemy.future import select
from db_init import AsyncSessionLocal
from models.transaction_model import Transaction
from models.credentials_model import Credential
from utils.auth import verify_token

class FetchOrderStatusHandler(tornado.web.RequestHandler):
    async def get(self, order_id):
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

        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Transaction).filter_by(order_id=order_id))
            transaction = result.scalar_one_or_none()

            if not transaction:
                self.set_status(404)
                self.write({"error": "Transaction not found"})
                return

            result = await session.execute(select(Credential).filter_by(merchant_id=merchant_id))
            credentials = result.scalar_one_or_none()

            if not credentials:
                self.set_status(500)
                self.write({"error": "Razorpay credentials not found"})
                return

            try:
                response = requests.get(
                    f"https://api.razorpay.com/v1/orders/{transaction.razorpay_order_id}",
                    auth=(credentials.access_key, credentials.secret_key)
                )
                razorpay_order = response.json()
                print(razorpay_order)
                order_status = razorpay_order.get('status', 'unknown')
            except requests.RequestException as e:
                self.set_status(500)
                self.write({"error": "Failed to fetch order status from Razorpay", "details": str(e)})
                return

            self.write({
                "razorpay_order_id": transaction.razorpay_order_id,
                "status": order_status
            })

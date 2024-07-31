import tornado.web
from sqlalchemy.future import select
from db_init import AsyncSessionLocal
from models.credentials_model import Credential
from utils.auth import verify_token

''' this script is for handling credentials of merchant.
    every credentials is mapped one - one with merchant.
'''
class CredentialsHandler(tornado.web.RequestHandler):
    async def post(self):
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
        access_key = data.get("razorpay_access_key")
        secret_key = data.get("razorpay_secret_key")

        if not all([access_key, secret_key, merchant_id]):
            self.set_status(400)
            self.write({"error": "Missing required fields"})
            return

        async with AsyncSessionLocal() as session:
            async with session.begin():
                result = await session.execute(select(Credential).filter_by(merchant_id=merchant_id))
                existing_credentials = result.scalar_one_or_none()

                if existing_credentials:
                    existing_credentials.access_key = access_key
                    existing_credentials.secret_key = secret_key
                else:
                    new_credentials = Credential(
                        access_key=access_key,
                        secret_key=secret_key,
                        merchant_id=merchant_id
                    )
                    session.add(new_credentials)
                await session.commit()
                self.write({"message": "Credentials posted successfully"})

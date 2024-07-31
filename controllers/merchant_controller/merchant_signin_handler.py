import json
import bcrypt
from tornado.web import RequestHandler
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from models.merchant_model import Merchant
from utils.auth import create_access_token 
from db_init import AsyncSessionLocal

''' this script is for handling authentication of merchant.
    after authenticating the merchant, a token is received storing a merchant_id,
    as it will be useful when hitting the different api endpoints.
'''

class MerchantLoginHandler(RequestHandler):

    async def post(self):
        try:
            login_details = json.loads(self.request.body)
            
            email = login_details.get("email")
            password = login_details.get("password")
            
            if not (email and password):
                self.set_status(400)
                self.write({"message": "Missing required fields"})
                return

            async with AsyncSessionLocal() as session:
                async with session.begin():
                    result = await session.execute(select(Merchant).filter_by(merchant_email=email))
                    merchant = result.scalar_one_or_none()
                    
                    
                    if not merchant:
                        self.set_status(401)
                        self.write({"message": "Invalid email."})
                        return

                    if not bcrypt.checkpw(password.encode('utf-8'), merchant.merchant_password.encode('utf-8')):
                        self.set_status(401)
                        self.write({"message": "Invalid password"})
                        return
                    merchant_id = merchant.id
                    token_data = {"id": merchant_id}
                    token = create_access_token(token_data)
                    
                    self.set_status(200)
                    self.write({"message": "Login successful", "token": token})

        except json.JSONDecodeError:
            self.set_status(400)
            self.write({"message": "Invalid JSON"})
        except SQLAlchemyError as e:
            self.set_status(500)
            self.write({"message": f"Database error: {e}"})
        except Exception as e:
            self.set_status(500)
            self.write({"message": f"Internal server error: {e}"})
    
import json
import bcrypt
from tornado.web import RequestHandler
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from db_init import AsyncSessionLocal
from models.merchant_model import Merchant

''' this script is for handling signup of merchant.
    here the password of merchant is bcrypted with help of bcrypt.io
'''

class MerchantSignupHandler(RequestHandler):

    async def post(self):
        try:
            merchant_details = json.loads(self.request.body)
            
            merchant_name = merchant_details.get("merchant_name")
            merchant_email = merchant_details.get("merchant_email")
            merchant_password = merchant_details.get("merchant_password")
            merchant_repassword = merchant_details.get("merchant_repass")
            
            if not (merchant_name and merchant_email and merchant_password and merchant_repassword):
                self.set_status(400)
                self.write({"message": "Missing required fields"})
                return

            if merchant_password != merchant_repassword:
                self.set_status(400)
                self.write({"message": "Passwords do not match"})
                return
            
            async with AsyncSessionLocal() as session:
                async with session.begin():
                    result = await session.execute(select(Merchant).filter_by(merchant_email=merchant_email))
                    existing_merchant = result.scalar_one_or_none()
                    
                    if existing_merchant:
                        self.set_status(409)
                        self.write({"message": "Merchant with this email already exists"})
                        return

                    hashed_password = bcrypt.hashpw(merchant_password.encode('utf-8'), bcrypt.gensalt())
                    new_merchant = Merchant(
                        merchant_name = merchant_name,
                        merchant_email = merchant_email,
                        merchant_password = hashed_password.decode("utf-8"),
                       
                    )
                    
                    session.add(new_merchant)
                    await session.commit()
                    
                    self.set_status(201)
                    self.write({"message": "Merchant created successfully"})

        except json.JSONDecodeError:
            self.set_status(400)
            self.write({"message": "Invalid JSON"})
        except SQLAlchemyError as e:
            self.set_status(500)
            self.write({"message": f"Database error: {e}"})
        except Exception as e:
            self.set_status(500)
            self.write({"message": f"Internal server error: {e}"})

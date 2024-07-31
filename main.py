import tornado.web
from tornado.ioloop import IOLoop
from db_init import Base, engine
from models.credentials_model import Credential 
from models.merchant_model import Merchant
from routes.merchant_routes import merchant_routes
from routes.credentials_routes import credentials_routes
from routes.order_routes import order_routes

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

def main():
    routes = merchant_routes+credentials_routes+order_routes
    app = tornado.web.Application(routes)
    app.listen(8080)
    print("Async server started on port 8080")
    
    loop = IOLoop.current()
    loop.run_sync(create_tables)  
    
    loop.start()

if __name__ == "__main__":
    main()

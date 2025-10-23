from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import customers, vegetables, orders

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],    
)

app.include_router(customers.router, 
                   prefix='/api/v1/customers', 
                   tags=['customers']
                    )


app.include_router(vegetables.router, 
                   prefix='/api/v1/vegetables', 
                   tags=['vegetables']
                   )

app.include_router(orders.router, 
                   prefix='/api/v1/orders', 
                   tags=['orders']
                   )
                   
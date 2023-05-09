from fastapi import FastAPI
from routes import auth, contact

app = FastAPI()

app.include_router(auth.router, prefix='/api')
app.include_router(contact.router, prefix='/api')

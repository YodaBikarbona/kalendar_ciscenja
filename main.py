from api.app import app
from api.base.database_connector import initialize_database

from api.user.controller.register_controller import router as register_router
from api.user.controller.login_controller import router as login_router
from api.calendar.controller.calendar_controller import router as calendar_router
from api.apartment.controller.apartment_controler import router as apartment_router

app.include_router(register_router)
app.include_router(login_router)
app.include_router(calendar_router)
app.include_router(apartment_router)

initialize_database()

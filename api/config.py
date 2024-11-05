from pydantic.v1 import (
    BaseSettings,
    validator,
)


class Settings(BaseSettings):
    debug: bool = False

    route: str = '/api/v1'
    description: str = 'RestAPI Service'

    server_type: str

    # Database parameters
    driver_name: str = 'postgresql://'
    database_type: str = 'postgresql'
    username: str
    password: str
    host: str
    port: str
    database: str

    # JWT secret
    jwt_access_secret_key: str
    jwt_refresh_secret_key: str

    @validator('server_type')
    def validate_server_type(cls, value):
        if value not in {'test', 'dev', 'prod', 'local'}:
            raise ValueError('The server_type must be one of: test, dev, prod, local')
        return value


settings = Settings()

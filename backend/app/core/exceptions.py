from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

class BeaconAPIException(Exception):
    """Base exception for BeaconAI API errors"""
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail

class ResourceNotFoundException(BeaconAPIException):
    """Exception for resource not found errors"""
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=404, detail=detail)

class DatabaseException(BeaconAPIException):
    """Exception for database errors"""
    def __init__(self, detail: str = "Database error occurred"):
        super().__init__(status_code=500, detail=detail)

# Exception handlers
async def beacon_api_exception_handler(request: Request, exc: BeaconAPIException):
    """Handler for BeaconAPIException"""
    logger.error(f"API Exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler for validation errors"""
    errors = exc.errors()
    error_messages = []
    
    for error in errors:
        error_messages.append({
            "loc": error.get("loc", []),
            "msg": error.get("msg", ""),
            "type": error.get("type", "")
        })
    
    logger.error(f"Validation error: {error_messages}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Invalid request parameters",
            "errors": error_messages
        }
    )

async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handler for SQLAlchemy errors"""
    logger.error(f"Database error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Database error occurred"}
    )

async def generic_exception_handler(request: Request, exc: Exception):
    """Handler for unhandled exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred"}
    )

def register_exception_handlers(app: FastAPI):
    """Register all exception handlers with the app"""
    app.add_exception_handler(BeaconAPIException, beacon_api_exception_handler)
    app.add_exception_handler(ResourceNotFoundException, beacon_api_exception_handler)
    app.add_exception_handler(DatabaseException, beacon_api_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler) 
from fastapi import HTTPException, status


class EntityNotFoundHTTPException(HTTPException):
    def __init__(self, entity_name: str, entity_id: str = None):
        detail = f"{entity_name} nao encontrado"
        if entity_id:
            detail += f" com id: {entity_id}"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class EntityAlreadyExistsHTTPException(HTTPException):
    def __init__(self, entity_name: str, field: str = None, value: str = None):
        detail = f"{entity_name} ja existe"
        if field and value:
            detail += f" com {field}: {value}"
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class EntityValidationHTTPException(HTTPException):
    def __init__(self, entity_name: str, message: str = None):
        detail = f"{entity_name} invalido"
        if message:
            detail += f": {message}"
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST, detail=detail
            )


class EntityProcessingHTTPException(HTTPException):
    def __init__(self, entity_name: str, operation: str = None):
        detail = f"Erro ao processar {entity_name}"
        if operation:
            detail += f" durante {operation}"
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail
            )


class EntityForbiddenHTTPException(HTTPException):
    def __init__(self, entity_name: str, action: str = None):
        detail = f"Acesso negado ao {entity_name}"
        if action:
            detail += f" para acao: {action}"
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

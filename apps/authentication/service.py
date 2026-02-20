import uuid
from http import HTTPStatus
from django.http import JsonResponse
from ninja.errors import HttpError

from apps.authentication.schema import LoginSchemaInput
from apps.users.repository import UserRepository
from utils.jwt import generate_jwt_token

repo = UserRepository()

class AuthenticationService:
    def auth_login(self, request, input_schema: LoginSchemaInput) -> JsonResponse:
        # 1) Busca no seu repositório (tabela "users")
        user = repo.get_user_by_email(input_schema.email)
        if not user:
            raise HttpError(HTTPStatus.NOT_FOUND, "Usuário não cadastrado no sistema")

        # 2) Verifica senha usando seu VO Password (hash já está no user.password)
        if not user.password.verify(input_schema.password):
            raise HttpError(HTTPStatus.UNAUTHORIZED, "Senha incorreta, verifique e tente novamente")

        # 3) Gera JWT com os claims esperados (user_id, email)
        #    (Shim simples para reutilizar generate_jwt_token sem alterar utils/jwt.py)
        class _ClaimsUser:
            def __init__(self, id, email):
                self.id = id
                self.email = email

        token = generate_jwt_token(_ClaimsUser(user.id, user.email.value))

        return JsonResponse(data={"access_token": token}, status=HTTPStatus.OK)

    def get_me(self, user_id: uuid.UUID):
        user = repo.get_user_by_id(user_id)
        if not user:
            raise HttpError(HTTPStatus.NOT_FOUND, "Usuário não encontrado")
        return user

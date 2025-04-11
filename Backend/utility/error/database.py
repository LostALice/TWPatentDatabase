# Code by AkinoAlice@TyrantRey


class AuthorizationError(Exception): ...


class RoleError(AuthorizationError): ...


class RoleIDNotFoundError(RoleError): ...

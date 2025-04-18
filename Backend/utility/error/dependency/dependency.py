# Code by AkinoAlice@TyrantRey


class JWTPayloadError(Exception): ...


class InvalidAlgorithmError(JWTPayloadError): ...


class InvalidJWTExpireTimeFormatError(JWTPayloadError): ...


class InvalidUnsupportedJWTExpireTimeError(JWTPayloadError): ...


class RefreshTokenExpiryError(JWTPayloadError): ...

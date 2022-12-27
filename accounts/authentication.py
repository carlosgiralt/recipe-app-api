from rest_framework import authentication


class TokenAuthentication(authentication.TokenAuthentication):
    def get_model(self):
        from .models import Token

        return Token

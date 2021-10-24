from django.contrib.auth.backends import ModelBackend
import re
from django.contrib.auth.models import User


class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = User.objects.get(username=username)
        v_code = False
        if 'verify_code' in request.data:
            v_code = request.data["verify_code"]

        print("verify code is " + str(v_code))
        print("user is " + user.username)
        print("user password is "+ password)

        if v_code:
            if user:
                # check validate code here
                return user
            else:
                return None
        else:
            if user.check_password(password):
                return user
            else:
                return None



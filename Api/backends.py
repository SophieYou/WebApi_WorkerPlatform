

from django.contrib.auth.backends import ModelBackend
import re
from django.contrib.auth.models import User
import datetime

from Api import models


class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = User.objects.get(username=username)
        v_code = False
        try:
            if 'verify_code' in request.data:
                v_code = request.data["verify_code"]
        except:
            pass

        print("verify code is " + str(v_code))
        print("user is " + user.username)
        print("user password is " + password)

        if v_code:
            if user:
                # check validate code here
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M");
                print(str(now))
                now_1 = datetime.datetime.now() + datetime.timedelta(minutes=-5)
                print(str(now_1))
                vi = models.VerifyCodeInfo.objects.filter(tel_or_email=username, verifycode=password, created_on__gte=now_1)
                print(vi)
                if vi.exists():
                    return user
                else:
                    return None
            else:
                return None
        else:
            if user.check_password(password):
                return user
            else:
                return None



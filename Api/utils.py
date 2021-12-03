from . import models
import random

# global function
class ClassWithGlobalFunction:

    def get_userid(user):
        if user.id is not None:
            try:
                p_user = models.UserProfile.objects.get(user_auth=user.id)
                print('user auth id: ' + str(user.id))
                print('user profile id: ' + str(p_user.user_id))
                return p_user.user_id
            except:
                return None
        else:
            return None

    def get_companyid(user):
        if user.id is not None:
            try:
                p_comp = models.CompanyInfo.objects.get(user_auth=user.id)
                print('user auth id: ' + str(user.id))
                print('company info id: ' + str(p_comp.company_id))
                return p_comp.company_id
            except:
                return None
        else:
            return None



    # random number
    def get_random_num(num):
        str = ""
        for i in range(num):
            ch = chr(random.randrange(ord('0'),ord('9')+1))
            str += ch

        print ('random num is: '+str)
        return str

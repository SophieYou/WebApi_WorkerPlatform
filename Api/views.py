#  from django.shortcuts import render
import ast
import datetime
import hashlib
import mimetypes
import os

from aliyunsdkcore.request import CommonRequest
from django.core.files.storage import default_storage
from django.db.models import Q
from django.forms import model_to_dict
from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.views import APIView

from . import serializer
from . import models
from .utils import ClassWithGlobalFunction
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework import pagination
import logging

# send SMS
from aliyunsdkcore.client import AcsClient

import smtplib
from email.mime.text import MIMEText
from email.header import Header

# get a looger object
logger = logging.getLogger(__name__)


# override the token view
class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        login_type = 'backend'

        try:
            if 'login_type' in request.data:
                login_type = request.data['login_type']
        except Exception as e:
            logger.error(e)
            pass

        logger.info("current login type: " + login_type)

        m_serializer = self.serializer_class(data=request.data, context={'request': request})
        m_serializer.is_valid(raise_exception=True)
        user = m_serializer.validated_data['user']

        Token.objects.filter(user=user).delete()
        token = Token.objects.create(user=user)
        token.save()

        if login_type == 'worker':
            u_id = ClassWithGlobalFunction.get_userid(user)
            return Response({
                'token': token.key,
                'user_id': u_id
            })
        elif login_type == 'company':
            c_id = ClassWithGlobalFunction.get_companyid(user)
            return Response({
                'token': token.key,
                'comp_id': c_id
            })
        else:
            return Response({
                'token': token.key
            })


# SMS sender
class SMSSender(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        m_tel = request.query_params['tel']
        logger.info("send SMS to: "+m_tel)

        client = AcsClient(
            os.environ.get('SMS_AccessKey'),
            os.environ.get('SMS_AccessSecret'),
            "cn-hangzhou"
        );

        m_code = ClassWithGlobalFunction.get_random_num(6)
        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain('dysmsapi.ap-southeast-1.aliyuncs.com')
        request.set_method('POST')
        request.set_protocol_type('https')  # https | http
        request.set_version('2018-05-01')
        request.set_action_name('SendMessageToGlobe')

        request.add_query_param('RegionId', "cn-hangzhou")
        request.add_query_param('To', m_tel)
        request.add_query_param('Message', "登录验证码 " + m_code + "， 有效期为60秒。请勿将验证码告知他人。")
        request.add_query_param('From', "HKC Career")

        response = client.do_action_with_exception(request)

        logger.info(str(response, encoding='utf-8'))

        response = ast.literal_eval(response.decode('utf-8'))

        if response['ResponseCode'] == 'OK':
            models.VerifyCodeInfo.objects.filter(tel_or_email=m_tel).delete()
            try:
                vi = models.VerifyCodeInfo.objects.create(tel_or_email=m_tel, verifycode=m_code)
                vi.save()
                logger.info("save SMS code to DB!")
            except Exception as e:
                logger.error("save SMS code to DB error; tel: "+m_tel + "; code: "+m_code)
                logger.error(str(e))
                return Response({
                    "ResponseCode": "Error",
                    "ResponseDescription": str(e),
                    "From": response['From'],
                    "To": response['To']
                })

        # return HttpResponse(str(response,encoding='utf-8'), content_type='application/json')
        return Response({
            "ResponseCode": response['ResponseCode'],
            "ResponseDescription": response['ResponseDescription'],
            "From": response['From'],
            "To": response['To']
        })


# SMS OR Email check
class SenderCheck(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        m_time = -1
        m_tel = request.query_params['tel_or_email']
        m_code = request.query_params['code']
        m_type = request.query_params['type']
        if m_type == 'email':
            m_time = -5

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M");
        now_1 = datetime.datetime.now() + datetime.timedelta(minutes=m_time)

        logger.info(
            "sender check type is : " + m_type + "; from: " + m_tel + "; the verify code is: " + m_code +
            "; date is " + str(now))

        vi = models.VerifyCodeInfo.objects.filter(tel_or_email=m_tel, verifycode=m_code, created_on__gte=now_1)


        if vi.exists():
            logger.info("sender check successfully!")
            return Response({
                "ResponseCode": 'OK'
            })
        else:
            logger.info("sender check fail! tel or email is "+m_tel+"; code is "+m_code+"; date is "+ str(now))
            return Response({
                "ResponseCode": 'Fail'
            })


# Email sender
class EmailSender(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        receiver = request.query_params['email']
        logger.info("Send email check to: "+receiver)

        sender = os.environ.get('Email_Sender')
        m_code = ClassWithGlobalFunction.get_random_num(6)

        message = MIMEText('郵箱驗證碼：' + str(m_code) + '; 請在5分鐘內輸入，認證郵箱！', 'plain', 'utf-8')
        message['From'] = Header("HK Construction Career", 'utf-8')  # 发送者
        message['To'] = Header(receiver, 'utf-8')  # 接收者

        subject = 'HK Construction Career 驗證碼'
        message['Subject'] = Header(subject, 'utf-8')

        mail_host = "smtp.gmail.com"  # 设置服务器
        mail_user = os.environ.get('Email_Sender')  # 用户名
        mail_pass = os.environ.get('Email_PWD')  # 口令

        try:
            smtpObj = smtplib.SMTP(mail_host, 587)
            # smtpObj.connect(mail_host, 587)  # 25 为 SMTP 端口号
            smtpObj.ehlo()
            smtpObj.starttls()
            smtpObj.login(mail_user, mail_pass)
            smtpObj.sendmail(sender, receiver, message.as_string())
            logger.info("Send email check successfully!")

            try:
                models.VerifyCodeInfo.objects.filter(tel_or_email=receiver).delete()
                vi = models.VerifyCodeInfo.objects.create(tel_or_email=receiver, verifycode=m_code)
                vi.save()
                logger.info("Save email code to DB!")
                return Response({
                    "ResponseCode": 'OK',
                    "ResponseDescription": 'Send email Successfully!'
                })
            except Exception as e:
                logger.error("save email code to DB error; email: " + str(receiver) + "; code: " + str(m_code))
                logger.error(str(e))
                return Response({
                    "ResponseCode": 'Fail',
                    "ResponseDescription": 'Error: save email code to DB error!'
                })

        except smtplib.SMTPException as e:
            logger.error("send email check error; email: " + str(receiver))
            logger.error(str(e))
            return Response({
                "ResponseCode": 'Fail',
                "ResponseDescription": 'Error: Cannot send email!'
            })


# create: new user
class RegisterUserViewSet(viewsets.ModelViewSet):
    queryset = models.UserProfile.objects.all().order_by('user_id')
    serializer_class = serializer.UserRegisterSerializer
    permission_classes = (permissions.AllowAny,)

    # create a new user(register)
    def create(self, request, *args, **kwargs):
        u_tel = request.data["user_tel"]
        logger.info('register tel: ' + str(u_tel))

        u_pwd = None
        u_check = False
        try:
            u_pwd = request.data["user_pwd"]
            logger.info('register password: ' + str(u_pwd))
        except Exception as e:
            logger.info(e)
            logger.info('register without password')
            pass

        try:
            u_check = request.data["check"]
            logger.info('check telephone before register')
        except Exception as e:
            logger.info(e)
            pass

        user = self.queryset.filter(user_tel=u_tel)

        if user.exists():
            logger.info('Fail: This telephone has been registered')
            return Response({'Fail: This telephone has been registered'}, status=status.HTTP_302_FOUND)
        elif u_check:
            logger.info('Check: This telephone has not been registered')
            return Response({'This telephone has not been registered'}, status=status.HTTP_200_OK)
        else:
            u_user = models.User.objects.create(username=u_tel)
            if u_pwd and u_user:
                u_user.set_password(u_pwd)
                u_user.save()
            logger.info('Create an auth user, auth user id is '+str(u_user.id))
            request.data["user_auth"] = u_user.id
            m_serializer = self.get_serializer(data=request.data)
            m_serializer.is_valid(raise_exception=True)
            self.perform_create(m_serializer)
            headers = self.get_success_headers(m_serializer.data)
            logger.info("register user successfully! tel is: "+str(u_tel))
            return Response(m_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


# list/retrieve: user profile
# update: user profile (include set password)
class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = models.UserProfile.objects.all().order_by('user_id')
    filterset_fields = ('user_id', 'user_tel')
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        print(self.action)
        if self.action == 'list' or self.action == 'retrieve':
            # get
            return serializer.UserProfileSerializer
        else:
            # patch
            return serializer.UserUpdateSerializer


# list: all job type detail
class JobtypeDetailViewSet(viewsets.ModelViewSet):
    queryset = models.JobtypeDetail.objects.all().order_by('jobtype_upper')
    serializer_class = serializer.JobtypeDetailSerializer
    permission_classes = (permissions.AllowAny,)
    pagination.PageNumberPagination.page_size = 1000


# list: news info
class NewsInfoViewSet(viewsets.ModelViewSet):
    queryset = models.NewsInfo.objects.all().order_by('-post_date')
    serializer_class = serializer.NewsInfoListSerializer
    permission_classes = (permissions.AllowAny,)

    def get_serializer_class(self):
        if self.action == 'list':
            return serializer.NewsInfoListSerializer
        else:
            return serializer.NewsInfoSerializer

    def get_queryset(self):
        topnum = self.request.query_params.get('topnum')
        if topnum:
            # list top num news list
            self.queryset = models.NewsInfo.objects.all().order_by('-post_date')[:int(topnum)]

        return self.queryset


# list: job info
class JobInfoViewSet(viewsets.ModelViewSet):
    queryset = models.JobInfo.objects.filter(job_status='1').order_by('-post_date')
    permission_classes = (permissions.AllowAny,)

    # serializer_class = serializer.JobInfoListSerializer

    def get_serializer_class(self):
        print(self.action)
        if self.action == 'list':
            return serializer.JobInfoListSerializer
        else:
            return serializer.JobInfoDetailSerializer


# list: search job info
class JobSearchViewSet(viewsets.ModelViewSet):
    # queryset = models.JobInfo.objects.filter(job_status='1').order_by('-post_date')
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializer.JobInfoListSerializer

    def get_queryset(self):
        job_comp_name = None
        jobtype_id = None
        region_id = None
        salary_type = None
        salary_upper = None
        salary_lower = None
        if 'job_comp_name' in self.request.query_params:
            job_comp_name = self.request.query_params["job_comp_name"]

        if 'jobtype_id' in self.request.query_params:
            jobtype_id = self.request.query_params['jobtype_id']
            if '[' and ']' in jobtype_id:
                jobtype_id = eval(jobtype_id)

        if 'region_id' in self.request.query_params:
            region_id = self.request.query_params['region_id']
            if '[' and ']' in region_id:
                region_id = eval(region_id)

        if 'salary_type' in self.request.query_params:
            salary_type = self.request.query_params['salary_type']

        if 'salary_upper' in self.request.query_params:
            salary_upper = self.request.query_params['salary_upper']

        if 'salary_lower' in self.request.query_params:
            salary_lower = self.request.query_params['salary_lower']

        m_filter = Q()
        and_filter = Q()
        and_filter.connector = 'AND'
        and_filter.children.append(('job_status', '1'))
        or_filter = Q()
        or_filter.connector = 'OR'

        if job_comp_name:
            print('job/company name: ', job_comp_name)
            or_filter.children.append(('job_name__contains', job_comp_name))
            company_id = models.CompanyInfo.objects.filter(company_name__contains=job_comp_name).values_list(
                'company_id', flat=True)
            if company_id:
                print('company id list: ', company_id)
                or_filter.children.append(('company_id__in', company_id))

        if jobtype_id:
            print('jobtype id: ', jobtype_id)
            and_filter.children.append(('jobtype_id__in', jobtype_id))
        if region_id:
            print('region id: ', region_id)
            and_filter.children.append(('region_id__in', region_id))
        if salary_type:
            print('salary type: ', salary_type)
            and_filter.children.append(('salary_type', salary_type))
        if salary_lower:
            print('salary lower: ', salary_lower)
            and_filter.children.append(('salary_upper__gte', salary_lower))
        if salary_upper:
            print('salary upper: ', salary_upper)
            and_filter.children.append(('salary_lower__lte', salary_upper))

        m_filter.add(and_filter, 'AND')
        if or_filter:
            m_filter.add(or_filter, 'AND')
        queryset = models.JobInfo.objects.filter(m_filter).order_by('-post_date')
        return queryset

# list: all region
class RegionInfoViewSet(viewsets.ModelViewSet):
    queryset = models.RegionInfo.objects.all().order_by('region_upper')
    serializer_class = serializer.RegionInfoSerializer
    permission_classes = (permissions.AllowAny,)
    pagination.PageNumberPagination.page_size = 1000


# list: all salary
class SalaryListViewSet(viewsets.ModelViewSet):
    queryset = models.SalaryList.objects.all().order_by('salary_type', 'salary_lower')
    serializer_class = serializer.SalaryListSerializer
    permission_classes = (permissions.AllowAny,)
    pagination.PageNumberPagination.page_size = 1000


# list: all benefit
class BenefitListViewSet(viewsets.ModelViewSet):
    queryset = models.BenefitList.objects.all()
    serializer_class = serializer.BenefitListSerializer
    permission_classes = (permissions.AllowAny,)


# list: all applied job
# create or update applied job
class JobApplyViewSet(viewsets.ModelViewSet):
    filterset_fields = ('job_id', 'user_id')
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        if self.action == 'list' or self.action == 'retrieve':
            u_id = ClassWithGlobalFunction.get_userid(self.request.user)
            return models.JobApply.objects.filter(user_id=u_id).order_by('-created_on')
        else:
            return models.JobApply.objects.all().order_by('-created_on')

    def get_serializer_class(self):
        print(self.action)
        if self.action == 'list' or self.action == 'retrieve':
            return serializer.JobApplyListSerializer
        else:
            return serializer.JobApplyUpdateSerializer

    # create applied job
    def create(self, request, *args, **kwargs):
        u_id = ClassWithGlobalFunction.get_userid(self.request.user)
        a_job = models.JobApply.objects.filter(user_id=u_id, job_id=request.data["job_id"])
        if a_job.exists():
            return Response({'Fail: This job has been applied'}, status=status.HTTP_302_FOUND)
        else:
            request.data['user_id'] = u_id
            m_serializer = self.get_serializer(data=request.data)
            m_serializer.is_valid(raise_exception=True)
            self.perform_create(m_serializer)
            headers = self.get_success_headers(m_serializer.data)
            return Response(m_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


# list: all favor job
# create or update favor job
class JobFavorViewSet(viewsets.ModelViewSet):
    filterset_fields = ('job_id', 'user_id')
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        u_id = ClassWithGlobalFunction.get_userid(self.request.user)
        return models.JobFavor.objects.filter(user_id=u_id, is_deleted=False).order_by('-created_on')

    def get_serializer_class(self):
        print(self.action)
        if self.action == 'list' or self.action == 'retrieve':
            return serializer.JobFavorListSerializer
        else:
            return serializer.JobFavorUpdateSerializer

    # create favor job
    def create(self, request, *args, **kwargs):
        u_id = ClassWithGlobalFunction.get_userid(self.request.user)
        a_job = models.JobFavor.objects.filter(user_id=u_id, job_id=request.data["job_id"]).values()

        if a_job.exists():
            a_obj = models.JobFavor.objects.get(id=a_job[0]['id'])
            a_obj.is_deleted = False
            a_obj.created_on = datetime.datetime.now()
            a_obj.save()

            dict_obj = model_to_dict(a_obj)
            m_serializer = self.get_serializer(data=dict_obj)
            m_serializer.is_valid(raise_exception=True)

            headers = self.get_success_headers(m_serializer.data)
            return Response(m_serializer.data, status=status.HTTP_200_OK, headers=headers)

        else:
            request.data['user_id'] = u_id
            m_serializer = self.get_serializer(data=request.data)
            m_serializer.is_valid(raise_exception=True)
            self.perform_create(m_serializer)
            headers = self.get_success_headers(m_serializer.data)
            return Response(m_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


# list/retrieve: company info
# update: company profile (include set password)
class CompanyInfoViewSet(viewsets.ModelViewSet):
    filterset_fields = ('contact_tel', 'contact_email', 'company_id')
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        c_id = ClassWithGlobalFunction.get_companyid(self.request.user)
        return models.CompanyInfo.objects.filter(company_id=c_id)

    def get_serializer_class(self):
        print(self.action)
        if self.action == 'list' or self.action == 'retrieve':
            # get
            return serializer.CompanyInfoSerializer
        else:
            # patch
            return serializer.CompanyUpdateSerializer


# create: new company
class RegisterCompanyViewSet(viewsets.ModelViewSet):
    queryset = models.CompanyInfo.objects.all().order_by('company_id')
    serializer_class = serializer.CompanyInfoSerializer
    permission_classes = (permissions.AllowAny,)

    # create a new company(register)
    def create(self, request, *args, **kwargs):
        c_tel = request.data["contact_tel"]
        c_email = request.data["contact_email"]
        c_pwd = request.data["company_pwd"]
        comp = self.queryset.filter(contact_tel=c_tel) | self.queryset.filter(contact_email=c_email)
        print(comp)
        if comp.exists():
            return Response({'This company (telephone or email) has been registered'}, status=status.HTTP_302_FOUND)
        else:
            c_user = models.User.objects.create(username=c_email)
            c_user.set_password(c_pwd)
            c_user.save()
            request.data["user_auth"] = c_user.id
            m_serializer = self.get_serializer(data=request.data)
            m_serializer.is_valid(raise_exception=True)
            self.perform_create(m_serializer)
            headers = self.get_success_headers(m_serializer.data)
            return Response(m_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


# list: training info list
class TrainingInfoListViewSet(viewsets.ModelViewSet):
    queryset = models.TrainingInfo.objects.all().order_by('-updated_on')
    serializer_class = serializer.TrainingInfoListSerializer
    permission_classes = (permissions.AllowAny,)


# create a search info
class SearchInfoViewSet(viewsets.ModelViewSet):
    queryset = models.SearchInfo.objects.all().order_by('-created_on')
    serializer_class = serializer.SearchInfoSerializer
    permission_classes = (permissions.AllowAny,)


# list: course info list
class CourseInfoListViewSet(viewsets.ModelViewSet):
    queryset = models.CourseInfo.objects.all().order_by('-updated_on')
    permission_classes = (permissions.AllowAny,)

    def get_serializer_class(self):
        print(self.action)
        if self.action == 'list':
            # list
            return serializer.CourseInfoListSerializer
        else:
            # detail
            return serializer.CourseDetailSerializer


# list: course info search list
class CourseInfoSearchViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializer.CourseInfoListSerializer

    def get_queryset(self):
        ctype_id = None
        course_title = None
        course_form = None

        if 'ctype_id' in self.request.query_params:
            ctype_id = self.request.query_params["ctype_id"]
        if 'course_title' in self.request.query_params:
            course_title = self.request.query_params["course_title"]
        if 'course_form' in self.request.query_params:
            course_form = self.request.query_params["course_form"]

        and_filter = Q()
        and_filter.connector = 'AND'

        if ctype_id:
            print('course type id is : ', ctype_id)
            and_filter.children.append(('ctype_id', ctype_id))

        if course_title:
            print('course title contains: ', course_title)
            and_filter.children.append(('course_title__contains', course_title))

        if course_form:
            print('course form is: ', course_form)
            and_filter.children.append(('course_form', course_form))

        if and_filter is None:
            queryset = models.CourseInfo.objects.all().order_by('-updated_on')
        else:
            queryset = models.CourseInfo.objects.filter(and_filter).order_by('-updated_on')
        return queryset


# list: course type list
class CourseTypeListViewSet(viewsets.ModelViewSet):
    queryset = models.CourseType.objects.all().order_by('ctype_desc')
    serializer_class = serializer.CourseTypeListSerializer
    permission_classes = (permissions.AllowAny,)


# list: job vacancy list
class JobVacancyViewSet(viewsets.ModelViewSet):
    # queryset = models.JobVacancyInfo.objects.all().order_by('updated_on')
    filterset_fields = ('vacancy_id', 'user_id')
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        u_id = ClassWithGlobalFunction.get_userid(self.request.user)
        return models.JobVacancyInfo.objects.filter(user_id=u_id).order_by('-updated_on')

    # serializer_class = serializer.JobVacancyInfoSerializer
    def get_serializer_class(self):
        print(self.action)
        if self.action == 'list':
            # list
            return serializer.JobVacancyInfoSerializer
        elif self.action == 'retrieve':
            # detail
            return serializer.JobVacancyDetailSerializer
        else:
            # create or update
            return serializer.JobVacancyNewSerializer

    # create new vacancy
    def create(self, request, *args, **kwargs):
        u_id = ClassWithGlobalFunction.get_userid(self.request.user)
        request.data["user_id"] = u_id
        m_serializer = self.get_serializer(data=request.data)
        m_serializer.is_valid(raise_exception=True)
        self.perform_create(m_serializer)
        headers = self.get_success_headers(m_serializer.data)
        return Response(m_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


# list: job info by company
class JobInfoCompanyViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        c_id = ClassWithGlobalFunction.get_companyid(self.request.user)
        return models.JobInfo.objects.filter(company_id=c_id).order_by('-updated_on')

    def get_serializer_class(self):
        print(self.action)
        if self.action == 'list':
            return serializer.JobInfoCompanySerializer
        elif self.action == 'retrieve':
            return serializer.JobInfoDetailCompanySerializer
        else:
            return serializer.JobInfoNewSerializer


# list: user who applied the job by company
class UserAppliedJobViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    filterset_fields = ('job_id', 'apply_status')

    def get_queryset(self):
        c_id = ClassWithGlobalFunction.get_companyid(self.request.user)
        qy = models.JobInfo.objects.filter(company_id=c_id).values_list('job_id')
        return models.JobApply.objects.filter(job_id__in=qy).order_by('-created_on')

    def get_serializer_class(self):
        print(self.action)
        if self.action == 'list':
            return serializer.UserAppliedJobListSerializer
        elif self.action == 'retrieve':
            return serializer.UserAppliedJobDetailSerializer
        else:
            return serializer.JobApplyUpdateSerializer


# list: company search job info
class CompanyJobSearchViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializer.JobInfoCompanySerializer

    def get_queryset(self):
        job_name = None
        jobtype_id = None
        region_id = None
        job_status = None
        c_id = ClassWithGlobalFunction.get_companyid(self.request.user)
        print(self.request.query_params)
        if 'job_name' in self.request.query_params:
            job_name = self.request.query_params["job_name"]

        if 'jobtype_id' in self.request.query_params:
            jobtype_id = self.request.query_params['jobtype_id']
            if '[' and ']' in jobtype_id:
                jobtype_id = eval(jobtype_id)

            print(jobtype_id)

        if 'region_id' in self.request.query_params:
            region_id = self.request.query_params['region_id']
            if '[' and ']' in region_id:
                region_id = eval(region_id)
            print(region_id)

        if 'job_status' in self.request.query_params:
            job_status = self.request.query_params['job_status']
            if '[' and ']' in job_status:
                job_status = eval(job_status)
            print(job_status)

        and_filter = Q()
        and_filter.connector = 'AND'
        and_filter.children.append(('company_id', c_id))

        if job_name:
            print('job name: ', job_name)
            and_filter.children.append(('job_name__contains', job_name))
        if jobtype_id:
            print('jobtype id: ', jobtype_id)
            and_filter.children.append(('jobtype_id__in', jobtype_id))
        if region_id:
            print('region id: ', region_id)
            and_filter.children.append(('region_id__in', region_id))
        if job_status:
            print('job status: ', job_status)
            and_filter.children.append(('job_status__in', job_status))

        queryset = models.JobInfo.objects.filter(and_filter).order_by('-post_date')
        return queryset


# list: search user who applied the job by company
class UserAppliedJobSearchViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializer.UserAppliedJobListSerializer

    def get_queryset(self):
        job_name = None
        jobtype_id = None
        apply_status = None
        c_id = ClassWithGlobalFunction.get_companyid(self.request.user)

        if 'job_name' in self.request.query_params:
            job_name = self.request.query_params["job_name"]

        if 'jobtype_id' in self.request.query_params:
            jobtype_id = self.request.query_params['jobtype_id']
            if '[' and ']' in jobtype_id:
                jobtype_id = eval(jobtype_id)

        if 'apply_status' in self.request.query_params:
            apply_status = self.request.query_params['apply_status']

        and_filter = Q()
        and_filter.connector = 'AND'
        and_filter.children.append(('company_id', c_id))

        if job_name:
            print('job name: ', job_name)
            and_filter.children.append(('job_name__contains', job_name))
        if jobtype_id:
            print('jobtype id: ', jobtype_id)
            and_filter.children.append(('jobtype_id__in', jobtype_id))

        print(and_filter)
        qy = models.JobInfo.objects.filter(and_filter).values_list('job_id')
        print(qy)

        and_filter = Q()
        and_filter.connector = 'AND'
        and_filter.children.append(('job_id__in', qy))

        if apply_status:
            print('apply status: ', apply_status)
            and_filter.children.append(('apply_status', apply_status))

        queryset = models.JobApply.objects.filter(and_filter).order_by('-created_on')
        return queryset


# open image
def get_file(file_name):
    resp = HttpResponse()
    f = None
    try:
        print(file_name)
        logger.info('open file: ' + file_name)
        f = default_storage.open(file_name, 'rb+')
    except Exception as e:
        logger.error('error in open file '+ file_name+';error: '+ str(e))
        return resp

    content_type, _ = mimetypes.guess_type(file_name)
    if content_type is None:
        content_type = "application/octet-stream"

    md5 = hashlib.md5()
    resp["content-type"] = content_type
    for c in f.chunks():
        resp.write(c)
        md5.update(c)
    f.close()
    resp["ETag"] = f'"{md5.hexdigest()}"'
    try:
        resp["Last-Modified"] = default_storage.get_modified_time(file_name).strftime('%a, %d %b %Y %H:%M:%S GMT')
    except Exception as e:
        logger.error('error when storage file '+file_name+';error is :'+str(e))
        pass
    return resp


def get_media(request, file_name):
    resp = get_file(file_name)
    return resp

#  from django.shortcuts import render

from django.db.models import Count, Q
from django.http import JsonResponse, HttpResponse
from rest_framework import viewsets, status, views
from rest_framework.response import Response
from rest_framework import permissions

from . import serializer
from . import models
from .utils import ClassWithGlobalFunction
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

from django_filters.rest_framework import DjangoFilterBackend


# override the token view

class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        login_type = 'backend'
        if 'login_type' in request.data:
            login_type = request.data['login_type']

        print("login type: " + login_type)
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
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



# create: new user
class RegisterUserViewSet(viewsets.ModelViewSet):
    queryset = models.UserProfile.objects.all().order_by('user_id')
    serializer_class = serializer.UserRegisterSerializer
    permission_classes = (permissions.AllowAny,)

    # create a new user(register)
    def create(self, request, *args, **kwargs):
        u_tel = request.data["user_tel"]
        print('register tel: ' + u_tel)
        u_pwd = None
        try:
            u_pwd = request.data["user_pwd"]
            print('register password: ' + u_pwd)
        except:
            pass
        user = self.queryset.filter(user_tel=u_tel)

        if user.exists():
            return Response({'Fail: This telephone has been registered'}, status=status.HTTP_302_FOUND)
        else:
            u_user = models.User.objects.create(username=u_tel)
            if u_pwd and u_user:
                u_user.set_password(u_pwd)
                u_user.save()

            request.data["user_auth"] = u_user.id
            m_serializer = self.get_serializer(data=request.data)
            m_serializer.is_valid(raise_exception=True)
            self.perform_create(m_serializer)
            headers = self.get_success_headers(m_serializer.data)
            return Response(m_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


# list/retrieve: user profile
# update: user profile (include set password)
class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = models.UserProfile.objects.all().order_by('user_id')
    # serializer_class = serializer.UserProfileSerializer
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


# list: news info
class NewsInfoViewSet(viewsets.ModelViewSet):
    queryset = models.NewsInfo.objects.all().order_by('-post_date')
    serializer_class = serializer.NewsInfoListSerializer
    permission_classes = (permissions.AllowAny,)

    def get_serializer_class(self):
        print(self.action)
        if self.action == 'list':
            return serializer.NewsInfoListSerializer
        else:
            return serializer.NewsInfoSerializer

    def get_queryset(self):
        topnum = self.request.query_params.get('topnum')
        print(topnum)
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
        if 'job_comp_name' in self.request.data:
            job_comp_name = self.request.data["job_comp_name"]

        if 'jobtype_id' in self.request.data:
            jobtype_id = self.request.data['jobtype_id']

        if 'region_id' in self.request.data:
            region_id = self.request.data['region_id']

        if 'salary_type' in self.request.data:
            salary_type = self.request.data['salary_type']

        if 'salary_upper' in self.request.data:
            salary_upper = self.request.data['salary_upper']

        if 'salary_lower' in self.request.data:
            salary_lower = self.request.data['salary_lower']

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


# list: all salary
class SalaryListViewSet(viewsets.ModelViewSet):
    queryset = models.SalaryList.objects.all().order_by('salary_type', 'salary_lower')
    serializer_class = serializer.SalaryListSerializer
    permission_classes = (permissions.AllowAny,)


# list: all benefit
class BenefitListViewSet(viewsets.ModelViewSet):
    queryset = models.BenefitList.objects.all()
    serializer_class = serializer.BenefitListSerializer
    permission_classes = (permissions.AllowAny,)


# list: all applied job
# create or update applied job
class JobApplyViewSet(viewsets.ModelViewSet):
    # queryset = models.JobApply.objects.all().order_by('-created_on')
    # serializer_class = serializer.JobApplyListSerializer
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
    # queryset = models.JobFavor.objects.all().filter(is_deleted=False).order_by('-created_on')
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
        a_job = models.JobFavor.objects.filter(user_id=u_id, job_id=request.data["job_id"])
        print(a_job)
        if a_job.exists():
            return Response({'Fail: This job has been added to favoriate'}, status=status.HTTP_302_FOUND)
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
    queryset = models.CompanyInfo.objects.all().order_by('company_id')
    filterset_fields = ('contact_tel', 'contact_email', 'company_id')
    permission_classes = (permissions.IsAuthenticated,)

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
        comp = self.queryset.filter(contact_tel=c_tel) \
               | self.queryset.filter(contact_email=c_email)
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

        if 'job_name' in self.request.data:
            job_name = self.request.data["job_name"]

        if 'jobtype_id' in self.request.data:
            jobtype_id = self.request.data['jobtype_id']

        if 'region_id' in self.request.data:
            region_id = self.request.data['region_id']

        if 'job_status' in self.request.data:
            job_status = self.request.data['job_status']

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
            and_filter.children.append(('job_status', job_status))

        queryset = models.JobInfo.objects.filter(and_filter).order_by('-post_date')
        return queryset


# list: search user who applied the job by company
class UserAppliedJobSearchViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializer.UserAppliedJobListSerializer

    def get_queryset(self):
        job_name = None
        jobtype_id = None
        c_id = ClassWithGlobalFunction.get_companyid(self.request.user)


        if 'job_name' in self.request.data:
            job_name = self.request.data["job_name"]

        if 'jobtype_id' in self.request.data:
            jobtype_id = self.request.data['jobtype_id']

        and_filter = Q()
        and_filter.connector = 'AND'
        and_filter.children.append(('company_id', c_id))

        if job_name:
            print('job name: ', job_name)
            and_filter.children.append(('job_name__contains', job_name))
        if jobtype_id:
            print('jobtype id: ', jobtype_id)
            and_filter.children.append(('jobtype_id__in', jobtype_id))

        qy = models.JobInfo.objects.filter(and_filter).values_list('job_id')

        queryset = models.JobApply.objects.filter(job_id__in=qy).order_by('-created_on')
        return queryset
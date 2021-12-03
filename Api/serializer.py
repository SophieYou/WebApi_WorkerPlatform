from rest_framework import serializers, status
from rest_framework.response import Response
from . import models
from .utils import ClassWithGlobalFunction
from django.contrib.auth.models import Group


# list: job type detail
class JobtypeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.JobtypeDetail
        fields = ('jobtype_id', 'jobtype_desc', 'jobtype_upper')


# list: user job type id + job detail
class UserJobtypeSerializer(serializers.ModelSerializer):
    jobtype_id = JobtypeDetailSerializer()

    class Meta:
        model = models.UserJobtype
        fields = ('jobtype_id',)


# retrieve: user profile + user job type
class UserProfileSerializer(serializers.ModelSerializer):
    jobtype = UserJobtypeSerializer(many=True)

    class Meta:
        model = models.UserProfile
        fields = '__all__'
        extra_fields = 'jobtype'


# create: user profile
class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserProfile
        fields = '__all__'


# update: user profile
class UserUpdateSerializer(serializers.ModelSerializer):
    u_jobtype = serializers.ListSerializer(child=serializers.IntegerField(), required=False)
    user_pwd = serializers.CharField(required=False)

    class Meta:
        model = models.UserProfile
        fields = '__all__'
        extra_fields = 'u_jobtype'

    def update(self, instance, validated_data):
        n_request = self.context.get('request', None)
        if 'u_jobtype' in validated_data:
            jobtype_data = validated_data.pop('u_jobtype')
            # update user job type
            models.UserJobtype.objects.filter(user_id=instance).delete()
            for jt in jobtype_data:
                print(str(jt))
                ins = models.UserJobtype.objects.create(
                    user_id=instance,
                    jobtype_id=models.JobtypeDetail(jobtype_id=jt)
                )

        if 'user_pwd' in validated_data:
            # update password
            u_pwd = validated_data.pop('user_pwd')
            print(u_pwd)
            n_user = n_request.user
            print(n_user)
            if n_user:
                n_user.set_password(u_pwd)
                n_user.save()
            else:
                return Response({'Change password Failed'}, status=status.HTTP_304_NOT_MODIFIED)

        # update user profile
        return super().update(instance, validated_data)


# list: region info
class RegionInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RegionInfo
        fields = '__all__'


# retrieve news info
class NewsInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.NewsInfo
        fields = '__all__'


# list news info
class NewsInfoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.NewsInfo
        fields = ('news_id', 'news_title', 'news_overview', 'post_date', 'url_cover')


# list company info
class CompanyInfoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CompanyInfo
        fields = ('company_id', 'company_name', 'url_logo')


# retrieve company detail text info
class CompanyTextSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CompanyInfo
        fields = ('company_id', 'company_name', 'url_logo', 'company_detail')


# retrieve company info
class CompanyInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CompanyInfo
        fields = '__all__'


# update company info
class CompanyUpdateSerializer(serializers.ModelSerializer):
    company_pwd = serializers.CharField(required=False)

    class Meta:
        model = models.CompanyInfo
        fields = '__all__'

    def update(self, instance, validated_data):
        n_request = self.context.get('request', None)
        print(validated_data)
        if 'company_pwd' in validated_data:
            # update password
            c_pwd = validated_data.pop('company_pwd')
            print('new company password: ' + c_pwd)
            c_user = n_request.user
            if c_user:
                c_user.set_password(c_pwd)
                c_user.save()
            else:
                return Response({'Change password Failed'}, status=status.HTTP_304_NOT_MODIFIED)

        # update user profile
        return super().update(instance, validated_data)


# refer job overview info
class JobOverviewSerializer(serializers.ModelSerializer):
    company_id = CompanyInfoListSerializer()
    jobtype_id = JobtypeDetailSerializer()
    region_id = RegionInfoSerializer()

    class Meta:
        model = models.JobInfo
        fields = ('job_id', 'company_id', 'jobtype_id', 'region_id', 'job_name', 'post_date')


# create job apply
class JobApplyUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.JobApply
        fields = '__all__'


class UserOverviewSerialize(serializers.ModelSerializer):

    class Meta:
        model = models.UserProfile
        fields = ('user_id', 'user_name', 'user_sex', 'user_year', 'work_year')


class JobNameSerializer(serializers.ModelSerializer):
    jobtype_id = JobtypeDetailSerializer()
    class Meta:
        model = models.JobInfo
        fields = ('job_id','company_id', 'jobtype_id', 'job_name', 'job_status', 'post_date')


# list job user applied info
class UserAppliedJobListSerializer(serializers.ModelSerializer):
    user_id = UserOverviewSerialize()
    job_id = JobNameSerializer()

    class Meta:
        model = models.JobApply
        fields = ('id', 'job_id', 'user_id', 'apply_status', 'created_on')


# list job applied info
class JobApplyListSerializer(JobApplyUpdateSerializer):
    job_id = JobOverviewSerializer()


# create job favorite
class JobFavorUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.JobFavor
        fields = '__all__'


# list job applied info
class JobFavorListSerializer(serializers.ModelSerializer):
    job_id = JobOverviewSerializer()
    is_applied = serializers.SerializerMethodField()

    class Meta:
        model = models.JobFavor
        fields = '__all__'
        extras_fields = 'is_applied'

    def get_is_applied(self, obj):
        # request_object = self.context['request']
        # u_id = request_object.query_params.get('user_id')
        u_id = ClassWithGlobalFunction.get_userid(self.context['request'].user)
        if u_id is not None:
            qy = models.JobApply.objects.filter(user_id=u_id, job_id=obj.job_id)
            if qy:
                return True
        return False


# list job info
class JobInfoListSerializer(serializers.ModelSerializer):
    company_id = CompanyInfoListSerializer()
    jobtype_id = JobtypeDetailSerializer()
    region_id = RegionInfoSerializer()
    is_applied = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = models.JobInfo
        fields = ('job_id', 'company_id', 'jobtype_id', 'region_id', 'job_name',
                  'salary_type', 'salary_upper', 'salary_lower', 'post_date', 'is_applied', 'is_favorite')

    def get_is_applied(self, obj):
        # request_object = self.context['request']
        # u_id = request_object.query_params.get('user_id')
        u_id = ClassWithGlobalFunction.get_userid(self.context['request'].user)
        if u_id is not None:
            qy = models.JobApply.objects.filter(user_id=u_id, job_id=obj.job_id)
            if qy:
                return True
        return False

    def get_is_favorite(self, obj):
        u_id = ClassWithGlobalFunction.get_userid(self.context['request'].user)
        if u_id is not None:
            qy = models.JobFavor.objects.filter(user_id=u_id, job_id=obj.job_id, is_deleted=False)
            if qy:
                return True
        return False


# retrieve job info detail
class JobInfoDetailSerializer(JobInfoListSerializer):
    company_id = CompanyTextSerializer()

    class Meta:
        model = models.JobInfo
        fields = '__all__'
        extra_fields = ('is_applied', 'is_favorite')


class JobInfoNewSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.JobInfo
        fields = '__all__'


# list job info by company
class JobInfoCompanySerializer(serializers.ModelSerializer):
    jobtype_id = JobtypeDetailSerializer()
    region_id = RegionInfoSerializer()
    applied_num = serializers.SerializerMethodField()

    class Meta:
        model = models.JobInfo
        fields = ('job_id', 'jobtype_id', 'region_id', 'job_name',
                  'job_duty', 'post_date', 'end_date', 'job_status', 'applied_num')

    def get_applied_num(self, obj):
        a_num = models.JobApply.objects.filter(job_id=obj.job_id).count()
        return a_num


# retrieve company job info detail
class JobInfoDetailCompanySerializer(JobInfoCompanySerializer):

    class Meta:
        model = models.JobInfo
        fields = '__all__'
        extra_fields = ('applied_num')


# list job user applied detail info
class UserAppliedJobDetailSerializer(serializers.ModelSerializer):
    user_id = UserProfileSerializer()
    job_id = JobInfoDetailCompanySerializer()

    class Meta:
        model = models.JobApply
        fields = '__all__'

# list salary info
class SalaryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SalaryList
        fields = '__all__'


# list benefit list info
class BenefitListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BenefitList
        fields = '__all__'


# list training info list
class TrainingInfoListSerializer(serializers.ModelSerializer):
    region_id = RegionInfoSerializer()

    class Meta:
        model = models.TrainingInfo
        fields = '__all__'


# create a search info
class SearchInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SearchInfo
        fields = '__all__'


# list course type
class CourseTypeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CourseType
        fields = '__all__'


# list course info
class CourseInfoListSerializer(serializers.ModelSerializer):
    ctype_id = CourseTypeListSerializer()
    course_overview = serializers.SerializerMethodField()

    class Meta:
        model = models.CourseInfo
        fields = ('course_id', 'ctype_id', 'course_title', 'course_form', 'course_overview', 'updated_on')

    def get_course_overview(self, obj):
        # print(obj.course_detail)
        return obj.course_detail[0:40]


# retrieve course info
class CourseDetailSerializer(serializers.ModelSerializer):
    ctype_id = CourseTypeListSerializer()

    class Meta:
        model = models.CourseInfo
        fields = '__all__'


# create vacancy job
class JobVacancyNewSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.JobVacancyInfo
        fields = '__all__'


# list vacancy job list
class JobVacancyInfoSerializer(serializers.ModelSerializer):
    jobtype_id = JobtypeDetailSerializer()
    region_id = RegionInfoSerializer()
    match_num = serializers.SerializerMethodField()

    class Meta:
        model = models.JobVacancyInfo
        fields = '__all__'

    def get_match_num(self, obj):
        m_num = obj.match_num
        if obj.vacancy_status == '0':
            m_num = models.JobInfo.objects.filter(
                job_status='1',
                jobtype_id=obj.jobtype_id,
                region_id=obj.region_id,
                salary_type=obj.salary_type,
                salary_lower__lte=obj.salary_upper,
                salary_upper__gte=obj.salary_lower
            ).count()

        return m_num


# retrieve vacancy detail job
class JobVacancyDetailSerializer(serializers.ModelSerializer):
    jobtype_id = JobtypeDetailSerializer()
    region_id = RegionInfoSerializer()
    match_num = serializers.SerializerMethodField()

    class Meta:
        model = models.JobVacancyInfo
        fields = '__all__'

    def get_match_num(self, obj):
        m_num = models.JobInfo.objects.filter(
            job_status='1',
            jobtype_id=obj.jobtype_id,
            region_id=obj.region_id,
            salary_type=obj.salary_type,
            salary_lower__lte=obj.salary_upper,
            salary_upper__gte=obj.salary_lower)
        print(m_num)
        return JobInfoListSerializer(m_num, many=True, context={'request': self.context['request']}).data





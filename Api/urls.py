from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()

router.register(r'registeruser', views.RegisterUserViewSet)
router.register(r'registercompany', views.RegisterCompanyViewSet)
router.register(r'userprofile', views.UserProfileViewSet)
router.register(r'jobtypedetail', views.JobtypeDetailViewSet)
router.register(r'newsinfo', views.NewsInfoViewSet)
router.register(r'jobinfo', views.JobInfoViewSet)
router.register(r'jobsearch', views.JobSearchViewSet, basename='JobInfo')
router.register(r'companyjobsearch', views.CompanyJobSearchViewSet, basename='JobInfo')
router.register(r'userappliedsearch', views.UserAppliedJobSearchViewSet, basename='JobApply')
router.register(r'regioninfo', views.RegionInfoViewSet)
router.register(r'salarylist', views.SalaryListViewSet)
router.register(r'benefitlist', views.BenefitListViewSet)
router.register(r'jobapply', views.JobApplyViewSet, basename='JobApply')
router.register(r'jobfavor', views.JobFavorViewSet, basename='JobFavor')
router.register(r'companyinfo', views.CompanyInfoViewSet, basename='CompanyInfo')
router.register(r'jobinfocompany', views.JobInfoCompanyViewSet, basename='JobInfo')
router.register(r'userapplied', views.UserAppliedJobViewSet, basename='JobApply')
router.register(r'traininglist', views.TrainingInfoListViewSet)
router.register(r'searchinfo', views.SearchInfoViewSet)
router.register(r'courseinfo', views.CourseInfoListViewSet)
router.register(r'courseinfosearch', views.CourseInfoSearchViewSet, basename='CourseInfo')
router.register(r'coursetype', views.CourseTypeListViewSet)
router.register(r'jobvacancy', views.JobVacancyViewSet, basename='JobVacancyInfo')
# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api-token-auth/', views.CustomAuthToken.as_view()),
    path('smssender/', views.SMSSender.as_view()),
    path('smssendercheck/', views.SenderCheck.as_view()),
    path('emailsender/', views.EmailSender.as_view()),
    path('media/<path:file_name>', views.get_media)


]

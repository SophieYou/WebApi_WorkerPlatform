from rest_framework import serializers
from . import models
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
        fields = ('url', 'user_id', 'user_name', 'jobtype', 'user_tel', 'user_year', 'user_sex',
                  'safecard_date', 'regcard_date', 'work_year', 'lan_en', 'lan_cantonese', 'lan_mandarin',
                  'user_pwd')


# create/update: user profile
class UserUpdateSerializer(UserProfileSerializer):
    u_jobtype = serializers.ListSerializer(child=serializers.IntegerField(), required=False)

    class Meta:
        model = models.UserProfile
        fields = ('url', 'user_id', 'user_name', 'u_jobtype', 'user_tel', 'user_year', 'user_sex',
                  'safecard_date', 'regcard_date', 'work_year', 'lan_en', 'lan_cantonese', 'lan_mandarin',
                  'user_pwd')

    '''
    def create(self, validated_data):
        jobtype_data = validated_data.pop('jobtype')
        userprofile = models.UserProfile.objects.create(**validated_data)
        print(jobtype_data)
        return userprofile
    '''
    def update(self, instance, validated_data):
        if 'u_jobtype' in validated_data:
            jobtype_data = validated_data.pop('u_jobtype')
            # update user job type
            models.UserJobtype.objects.filter(user_id=instance).delete()
            for jt in jobtype_data:
                print(str(jt))
                models.UserJobtype.objects.create(
                    user_id=instance,
                    jobtype_id=models.JobtypeDetail(jobtype_id=jt)
                )

        # update user profile
        instance.save()
        return instance



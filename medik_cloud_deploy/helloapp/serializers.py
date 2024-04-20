from rest_framework import serializers

from django.conf import settings

from helloapp.models import MedApplicant


class RegisterSerializer(serializers.Serializer):
    password2 = serializers.CharField(style={'input_type': 'password'},write_only=True)

    class Meta:
        model = MedApplicant
        fields = ('email', 'username', 'password', 'password2')
        extra_kwargs = {'password': {'write_only': True}}

    def save(self, **kwargs):
        user = MedApplicant(email=self.validated_data['email'], student_name=self.validated_data['student_name'])

        password = self.validated_data['password']
        password2 = self.validated_data['password2']

        if password != password2:
            raise serializers.ValidationError({
                'password': 'Passwords do not match'
            })

        user.set_password(password)
        user.save()

        return user


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedApplicant
        fields = ['id', 'username', 'email']

from rest_framework import serializers

from django.conf import settings

from helloapp.models import MedApplicant


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()  
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = MedApplicant
        fields = ('email', 'username', 'password', 'password2')
        extra_kwargs = {'password': {'write_only': True}}

    def save(self, **kwargs):
        if self.validated_data['password'] != self.validated_data['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match"})

        user = MedApplicant(email=self.validated_data['email'], username=self.validated_data['username'])
        user.set_password(self.validated_data['password'])
        user.save()

        return user

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedApplicant
        fields = ['id', 'username', 'email']

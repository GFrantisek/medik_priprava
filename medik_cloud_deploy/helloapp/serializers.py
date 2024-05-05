from rest_framework import serializers

from django.conf import settings

from helloapp.models import MedApplicant, StudentAnswers, StudentTests


class StudentAnswersSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAnswers
        fields = ['question', 'selected_answer', 'is_correct']


class StudentTestsSerializer(serializers.ModelSerializer):
    answers = StudentAnswersSerializer(many=True)

    class Meta:
        model = StudentTests
        fields = ['test_id', 'test_template_id', 'test_date', 'score', 'total_possible_score', 'answers']


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

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class MedApplicantManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError('Email is required')
        if not username:
            raise ValueError('Username is required')

        user = self.model(email=self.normalize_email(email), username=username)

        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password
        )

        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class MedApplicant(AbstractBaseUser):
    class Meta:
        db_table = 'medapplicants'

    email = models.EmailField(max_length=60, unique=True)
    username = models.CharField(max_length=255, unique=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username',)

    objects = MedApplicantManager()

    def __str__(self) -> str:
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True


class MedTestTemplate(models.Model):
    test_template_id = models.AutoField(primary_key=True)
    template_name = models.TextField()
    template_description = models.TextField()

    class Meta:
        db_table = 'med_test_templates'


class MedQuestions(models.Model):
    question_id = models.AutoField(primary_key=True)
    question_text = models.TextField()
    question_image = models.TextField(null=True, blank=True)
    question_category = models.CharField(max_length=255)

    class Meta:
        db_table = 'medquestions'


class MedAnswers(models.Model):
    answer_id = models.AutoField(primary_key=True)
    answer_text = models.TextField()
    answer_image = models.TextField(null=True, blank=True)
    question_id = models.ForeignKey(MedQuestions, related_name='answers', on_delete=models.CASCADE)
    is_correct = models.BooleanField()
    explanation = models.TextField(null=True, blank=True)
    selection_count = models.IntegerField(default=0)

    class Meta:
        db_table = 'medanswers'


class StudentTests(models.Model):
    test_id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(
        'MedApplicant',
        on_delete=models.CASCADE,
        db_column='id'
    )
    test_template_id = models.ForeignKey(
        'MedTestTemplate',
        on_delete=models.CASCADE,
        db_column='test_template_id'
    )
    test_date = models.DateTimeField(auto_now_add=True, db_column='test_date')
    score = models.IntegerField(db_column='score')
    total_possible_score = models.IntegerField(db_column='total_possible_score')


class Meta:
    db_table = 'student_tests'


class StudentAnswers(models.Model):
    student_answer_id = models.AutoField(primary_key=True)
    test = models.ForeignKey(
        'StudentTests',
        on_delete=models.CASCADE,
        db_column='test_id',
        related_name='answers'
    )
    question = models.ForeignKey(
        MedQuestions,
        on_delete=models.CASCADE,
        db_column='question_id'
    )
    selected_answer = models.ForeignKey(
        MedAnswers,
        on_delete=models.CASCADE,
        db_column='selected_answer_id'
    )
    is_correct = models.BooleanField()

    class Meta:
        db_table = 'student_answers'

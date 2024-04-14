from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class MedApplicantManager(BaseUserManager):
    def create_user(self, student_email, student_name, password=None):
        if not student_email:
            raise ValueError('Users must have an email address')
        if not student_name:
            raise ValueError('Users must have a name')

        user = self.model(
            student_email=self.normalize_email(student_email),
            student_name=student_name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, student_email, student_name, password=None):
        user = self.create_user(
            student_email=self.normalize_email(student_email),
            student_name=student_name,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class MedApplicant(AbstractBaseUser):
    class Meta:
        db_table = 'medapplicants'

    student_id = models.AutoField(primary_key=True)
    student_name = models.CharField(max_length=50)
    student_email = models.EmailField(unique=True)
    registration_date = models.DateTimeField(auto_now_add=True)  # Automatically set the date when the object is created
    student_password = models.CharField(max_length=255)  # Use Django’s built-in password handling

    objects = MedApplicantManager()

    USERNAME_FIELD = 'student_email'
    REQUIRED_FIELDS = ['student_name']

    def __str__(self):
        return self.student_email

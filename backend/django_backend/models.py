from django.db import models


class MedicineStudents(models.Model):
    student_name = models.TextField()
    student_email = models.TextField()
    registration_date = models.DateTimeField()
    student_password = models.TextField()  # Ensure this is hashed and salted


class MedQuestions(models.Model):
    question_text = models.TextField()
    question_image = models.TextField(blank=True, null=True)
    question_category = models.TextField()

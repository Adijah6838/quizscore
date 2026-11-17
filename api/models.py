from django.db import models
from django.utils import timezone

class Assessment(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    time_limit_minutes = models.PositiveIntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Question(models.Model):
    assessment = models.ForeignKey(Assessment, related_name='questions', on_delete=models.CASCADE)
    text = models.TextField()
    points = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.text[:50]

class Choice(models.Model):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class Attempt(models.Model):
    STATUS_CHOICES = (
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('expired', 'Expired'),
    )
    assessment = models.ForeignKey(Assessment, related_name='attempts', on_delete=models.CASCADE)
    # Using a simple session key for now (in a real app, this would be a User ID)
    user_session = models.CharField(max_length=100) 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    score = models.FloatField(null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        # Prevents a user from having multiple attempts for the same assessment
        unique_together = ('assessment', 'user_session')

    def is_expired(self):
        if self.status != 'in_progress':
            return False
        deadline = self.started_at + timezone.timedelta(minutes=self.assessment.time_limit_minutes)
        return timezone.now() > deadline

    def __str__(self):
        return f"{self.user_session} - {self.assessment.title} ({self.status})"

class Answer(models.Model):
    attempt = models.ForeignKey(Attempt, related_name='answers', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE)

    class Meta:
        # A user can only submit one answer per question per attempt
        unique_together = ('attempt', 'question')

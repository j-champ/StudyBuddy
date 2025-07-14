from django.db import models
from django.contrib.auth.models import User

class Buddy(models.Model):
    user = models.ForeignKey(User, related_name='buddy_owner', on_delete=models.CASCADE)
    buddy = models.ForeignKey(User, related_name='buddy_peer', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} ↔ {self.buddy.username}"

class Task(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=120)
    deadline = models.DateField()
    pomodoro_goal = models.PositiveIntegerField(default=1)
    pomodoro_done = models.PositiveIntegerField(default=0)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class PomodoroSession(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)

class RewardLedger(models.Model):
    creditor = models.ForeignKey(User, related_name='credit_gain', on_delete=models.CASCADE)
    debtor = models.ForeignKey(User, related_name='credit_loss', on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    created = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.creditor}+{self.points} ← {self.debtor} ({self.created})"

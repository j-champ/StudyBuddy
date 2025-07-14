from django.db.models import Q
from django.core.management.base import BaseCommand
from django.utils import timezone
from checkins.models import Task, Buddy, RewardLedger
from django.db import transaction

class Command(BaseCommand):
    help = 'Apply penalties for uncompleted tasks'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        overdue_tasks = Task.objects.filter(
            deadline__lt=today,
            completed=False
        )

        for task in overdue_tasks:
            buddy_row = Buddy.objects.filter(
                Q(user=task.owner) | Q(buddy=task.owner)
            ).first()

            if not buddy_row:
                self.stdout.write(self.style.WARNING(
                    f"No buddy found for {task.owner}, skipping penalty."
                ))
                continue

            # figure out which side is the “other” user
            buddy = buddy_row.buddy if buddy_row.user == task.owner else buddy_row.user

            with transaction.atomic():
                RewardLedger.objects.create(
                    creditor=buddy,
                    debtor=task.owner,
                    points=10
                )
                task.completed = True
                task.save(update_fields=["completed"])

                self.stdout.write(self.style.SUCCESS(
                    f"Penalty: {task.owner} → {buddy} for task: {task.title}"
                ))

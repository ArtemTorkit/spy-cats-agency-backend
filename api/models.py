from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

class Cat(models.Model):
    name = models.CharField(max_length=100)
    years_of_experience = models.PositiveIntegerField()
    breed = models.CharField(max_length=50)
    salary = models.DecimalField(max_digits=10, decimal_places=2)

    hired_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.breed})"

    def clean(self):
        # make sure salary is not absurdly low/high (optional rule)
        if self.salary <= 0:
            raise ValidationError("Salary must be a positive number.")

        # you can also enforce minimum experience rules if required
        if self.years_of_experience > 50:
            raise ValidationError("Years of experience seems unrealistic.")
        
class Mission(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    assigned_cat = models.ForeignKey(
        'Cat', null=True, blank=True, on_delete=models.SET_NULL, related_name='missions'
    )
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def update_completion(self):
        """Mark mission as completed if all targets are completed."""
        if self.targets.exists() and not self.targets.filter(completed=False).exists():
            if not self.completed:
                self.completed = True
                self.save(update_fields=['completed'])
        else:
            if self.completed:
                self.completed = False
                self.save(update_fields=['completed'])


class Target(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name='targets')
    name = models.CharField(max_length=200)
    country = models.CharField(max_length=100)
    notes = models.TextField(blank=True)   # notes belong to the target directly
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('mission', 'name')  # uniqueness of target name per mission

    def __str__(self):
        return f"{self.name} ({self.country})"

    def save(self, *args, **kwargs):
        if self.completed and self.completed_at is None:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)
        # update mission state after target save
        self.mission.update_completion()
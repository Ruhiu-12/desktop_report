from django.db import models


class Lab(models.Model):
    name = models.CharField(max_length=50, unique=True)
    location = models.CharField(max_length=200, blank=True, default='')
    grid_columns = models.IntegerField(default=8, help_text='Number of columns in the floor grid')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Machine(models.Model):
    STATUS_CHOICES = [
        ('HEALTHY', 'Healthy'),
        ('FLAGGED', 'Flagged'),
        ('IN_REPAIR', 'In Repair'),
        ('DOWN', 'Down'),
    ]

    lab = models.ForeignKey(Lab, on_delete=models.CASCADE, related_name='machines')
    name = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='HEALTHY')
    grid_row = models.IntegerField(default=0, help_text='Row position in grid (0-indexed)')
    grid_col = models.IntegerField(default=0, help_text='Column position in grid (0-indexed)')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['grid_row', 'grid_col']
        unique_together = ['lab', 'name']

    def __str__(self):
        return f"{self.lab.name} - {self.name}"


class IssueTemplate(models.Model):
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]

    title = models.CharField(max_length=200, unique=True)
    default_priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return f"{self.title} ({self.default_priority})"

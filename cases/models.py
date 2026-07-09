from django.db import models
from django.conf import settings

class Case(models.Model):
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]

    STATUS_CHOICES = [
        ('NEW', 'New'),
        ('ASSIGNED', 'Assigned'),
        ('IN_PROGRESS', 'In Progress'),
        ('WAITING_REPORT', 'Waiting for Report'),
        ('PENDING_REVIEW', 'Pending Review'),
        ('CLOSED', 'Closed'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    asset_tag = models.CharField(max_length=50, blank=True, default='', help_text='Machine identifier e.g. CL3-PC01')
    image = models.ImageField(upload_to='cases/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    case_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    case_priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reported_cases'
    )

    technician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_cases'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Case'
        verbose_name_plural = 'Cases'

    def __str__(self):
        return f"{self.title} ({self.status})"

class Report(models.Model):
    case = models.OneToOneField(
        Case,
        on_delete=models.CASCADE,
        related_name='report'
    )
    technician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submitted_reports'
    )
    findings = models.TextField()
    solution_provided = models.TextField()
    image = models.ImageField(upload_to='reports/', blank=True, null=True)
    date_submitted = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date_submitted']
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'

    def __str__(self):
        return f"Report for {self.case.title}"

class CaseAuditLog(models.Model):
    case = models.ForeignKey(
        Case, 
        on_delete=models.CASCADE, 
        related_name='audit_logs'
    )
    action = models.CharField(max_length=255)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True
    )
    related_note = models.ForeignKey(
        'CaseNote',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.case.title} - {self.action}"


class CaseNote(models.Model):
    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name='notes'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Note by {self.author} on {self.case.title}"


class ReportImage(models.Model):
    report = models.ForeignKey(
        'Report',
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='reports/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.report}"
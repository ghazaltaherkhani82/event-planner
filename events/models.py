from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Event(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'Draft', 'پیش‌نویس'
        PUBLISHED = 'Published', 'منتشر شده'
        CLOSED = 'Closed', 'ثبت‌نام بسته شده'
        FINISHED = 'Finished', 'به پایان رسیده'
        CANCELLED = 'Cancelled', 'لغو شده'

    title = models.CharField(max_length=255, verbose_name="عنوان رویداد")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    capacity = models.PositiveIntegerField(verbose_name="ظرفیت")
    start_time = models.DateTimeField(verbose_name="زمان شروع")
    end_time = models.DateTimeField(verbose_name="زمان پایان")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name="وضعیت"
    )
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organized_events',
        verbose_name="برگزارکننده"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def transition_to(self, new_status):
        valid_transitions = {
            self.Status.DRAFT: [self.Status.PUBLISHED, self.Status.CANCELLED],
            self.Status.PUBLISHED: [self.Status.CLOSED, self.Status.FINISHED, self.Status.CANCELLED],
            self.Status.CLOSED: [self.Status.FINISHED, self.Status.PUBLISHED, self.Status.CANCELLED],
            self.Status.FINISHED: [],
            self.Status.CANCELLED: []
        }

        allowed = valid_transitions.get(self.status, [])
        if new_status not in allowed:
            raise ValidationError(f"تغییر وضعیت از {self.get_status_display()} به {new_status} مجاز نیست.")
        self.status = new_status
        self.save()

    def clean(self):
        super().clean()
        if self.start_time and self.end_time and self.end_time <= self.start_time:
            raise ValidationError("زمان پایان باید بعد از زمان شروع باشد.")

    def __str__(self):
        return self.title


class EventStage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='stages', verbose_name="رویداد")
    title = models.CharField(max_length=255, verbose_name="عنوان مرحله")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    order = models.PositiveIntegerField(default=1, verbose_name="ترتیب")
    capacity = models.PositiveIntegerField(blank=True, null=True, verbose_name="ظرفیت مرحله")
    start_time = models.DateTimeField(verbose_name="زمان شروع مرحله")
    end_time = models.DateTimeField(verbose_name="زمان پایان مرحله")
    stage_roles = models.CharField(max_length=255, blank=True, null=True, verbose_name="نقش‌های مرحله (سخنران/داور)")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.event.title} - مرحله {self.order}: {self.title}"


class EventResult(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='results', verbose_name="رویداد")
    participant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='event_results',
        verbose_name="شرکت‌کننده"
    )
    score = models.FloatField(default=0.0, verbose_name="امتیاز")
    rank = models.PositiveIntegerField(blank=True, null=True, verbose_name="رتبه")
    remarks = models.TextField(blank=True, null=True, verbose_name="توضیحات و بازخورد داور")
    published_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'participant')

    def clean(self):
        super().clean()
        status_str = str(self.event.status).upper()
        if status_str not in ['CLOSED', 'FINISHED', 'REGISTRATION_CLOSED']:
            raise ValidationError("ثبت نمرات و داوری تنها در وضعیت Closed یا Finished مجاز است.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"کارنامه {self.participant.username} در {self.event.title}"
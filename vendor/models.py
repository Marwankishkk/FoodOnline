from datetime import date, datetime, time
import pytz

from django.db import models

from accounts.models import User, UserProfile
from accounts.utils import send_notification

egypt_tz = pytz.timezone('Africa/Cairo')


class Vendor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, null=True, blank=True)
    vendor_name = models.CharField(max_length=50)
    vendor_slug = models.SlugField(max_length=100, unique=True)
    vendor_license = models.ImageField(upload_to='vendor/license')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.vendor_name
    
    def is_open(self):
        today = date.today().isoweekday()
        custom_day = (today + 1) % 7 + 2
        current_opening_hours = OpeningHour.objects.filter(vendor=self, day=custom_day)
        current_time = datetime.now(egypt_tz).time()
        time_fmt = '%I:%M %p'
        for hour in current_opening_hours:
            if not hour.is_closed:
                from_time = datetime.strptime(hour.from_hour, time_fmt).time()
                to_time = datetime.strptime(hour.to_hour, time_fmt).time()
                if from_time <= current_time <= to_time:
                    return True
                    break
                if hour.is_closed:
                    return False
        return False

    def save(self, *args, **kwargs):
        if self.pk is not None:
            orig = Vendor.objects.get(pk=self.pk)
            if orig.is_approved != self.is_approved:
                context = {
                    'user': self.user,
                    'is_approved': self.is_approved,
                    'email': self.user.email,
                }
                email_template = 'accounts/emails/admin_approval_email.html'
                if self.is_approved == True:
                    mail_subject = 'Congratulations! Your restaurant has been approved!'
                    send_notification(mail_subject, email_template, context)
                else:
                    mail_subject = 'We are sorry to inform you that your restaurant has been rejected!'
                    send_notification(mail_subject, email_template, context)

        return super(Vendor, self).save(*args, **kwargs)

DAY_CHOICES = [
    (1, 'Saturday'),
    (2, 'Sunday'),
    (3, 'Monday'),
    (4, 'Tuesday'),
    (5, 'Wednesday'),
    (6, 'Thursday'),
    (7, 'Friday'),
] 
HOUR_OF_DAY_24 = [(time(h, m).strftime('%I:%M %p'), time(h, m).strftime('%I:%M %p')) for h in range(0, 24) for m in (0, 30)]

class OpeningHour(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    day = models.IntegerField(choices=DAY_CHOICES)
    from_hour = models.CharField(choices=HOUR_OF_DAY_24, max_length=20)
    to_hour = models.CharField(choices=HOUR_OF_DAY_24, max_length=20)
    is_closed = models.BooleanField(default=False)

    class Meta:
        ordering = ('day', '-from_hour')
        unique_together = ('vendor', 'day', 'from_hour', 'to_hour')

    def __str__(self):
        return self.get_day_display()
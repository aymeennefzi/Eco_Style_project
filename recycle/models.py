from django.db import models
from django.urls import reverse
from accounts.models import Account


class DropPoint(models.Model):
    name = models.CharField(max_length=100, unique=True)
    location = models.CharField(max_length=255)
    description = models.TextField(max_length=300, blank=True)
    image = models.ImageField(upload_to='drop_points', blank=True)

    class Meta:
        verbose_name = 'Drop Point'
        verbose_name_plural = 'Drop Points'

    def __str__(self):
        return self.name

    def get_drop_point_details_url(self):
        return reverse('recycle:drop_point_details', args=[self.id])


class RecycledItem(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=300, blank=True)
    drop_point = models.ForeignKey(DropPoint, on_delete=models.CASCADE)
    status_choices = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('declined', 'Declined'),
    )
    status = models.CharField(max_length=10, choices=status_choices, default='pending')
    image = models.ImageField(upload_to='recycled_items', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Recycled Item'
        verbose_name_plural = 'Recycled Items'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_recycled_item_details_url(self):
        return reverse('recycle:recycled_item_details', args=[self.id])

    def get_status_display(self):
        return dict(self.status_choices).get(self.status)



class RecycledItemManager(models.Manager):
    def active_items(self):
        return self.filter(status='pending')

    def confirmed_items(self):
        return self.filter(status='confirmed')

    def declined_items(self):
        return self.filter(status='declined')



from django import forms
from .models import ReviewRating
from .models import Notification


class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ['review', 'rating']




class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = '__all__'




class NotificationUpdateForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['message', 'target_price', 'notify_on_sale']
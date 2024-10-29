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




class ChurnPredictionForm(forms.Form):
    age = forms.IntegerField()
    gender = forms.ChoiceField(choices=[('Male', 'Male'), ('Female', 'Female')])
    item_purchased = forms.CharField(max_length=100)
    category = forms.CharField(max_length=100)
    purchase_amount = forms.FloatField()
    location = forms.CharField(max_length=100)
    size = forms.CharField(max_length=10)
    color = forms.CharField(max_length=10)
    season = forms.CharField(max_length=10)
    review_rating = forms.FloatField()
    subscription_status = forms.ChoiceField(choices=[('Yes', 'Yes'), ('No', 'No')])
    shipping_type = forms.CharField(max_length=100)
    discount_applied = forms.ChoiceField(choices=[('Yes', 'Yes'), ('No', 'No')])
    promo_code_used = forms.ChoiceField(choices=[('Yes', 'Yes'), ('No', 'No')])
    previous_purchases = forms.IntegerField()
    payment_method = forms.CharField(max_length=100)
    frequency_of_purchases = forms.CharField(max_length=20)
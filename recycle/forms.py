from django import forms
from .models import RecycledItem

class RecycledItemForm(forms.ModelForm):
    class Meta:
        model = RecycledItem
        fields = ['name', 'description', 'drop_point', 'image']
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Describe the item you want to recycle...'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter item name'
            }),
            'drop_point': forms.Select(attrs={
                'class': 'form-control'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control'
            })
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Validate file size (limit to 5MB)
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Image size should not exceed 5MB")
            # Validate file type
            if not image.content_type in ['image/jpeg', 'image/png', 'image/jpg']:
                raise forms.ValidationError("Please upload a valid image file (JPEG, JPG or PNG)")
        return image
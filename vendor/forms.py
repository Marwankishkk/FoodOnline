from django import forms
from .models import Vendor, OpeningHour
from menu.models import Category, FoodItem

class VendorForm(forms.ModelForm):
    vendor_license = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info'}))
    class Meta:
        model = Vendor
        fields = ['vendor_name', 'vendor_license']
    
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'description']
class FoodItemForm(forms.ModelForm):
    class Meta:
        model = FoodItem
        fields = ['category', 'food_title', 'description', 'price', 'image', 'is_available']

class OpeningHourForm(forms.ModelForm):
    class Meta:
        model = OpeningHour
        fields = ['day', 'from_hour', 'to_hour', 'is_closed']
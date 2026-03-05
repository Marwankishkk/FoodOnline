from django.shortcuts import render
from .forms import VendorForm
from accounts.forms import UserForm
from accounts.models import User
from vendor.models import Vendor
# Create your views here.
def vprofile(request):
    return render(request, 'vendor/vprofile.html')
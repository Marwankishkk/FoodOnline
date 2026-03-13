from accounts.models import UserProfile
from vendor.models import Vendor


def get_vendor(request):   
    try:
        vendor = Vendor.objects.get(user=request.user)
        return {'vendor': vendor}
    except:
        return {'vendor': None}

def get_user_profile(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except:
        user_profile = None
    return dict(user_profile=user_profile)


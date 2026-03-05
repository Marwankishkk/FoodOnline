from vendor.models import Vendor
def get_vendor(request):   
    try:
        vendor = Vendor.objects.get(user=request.user)
        return {'vendor': vendor}
    except:
        return {'vendor': None}
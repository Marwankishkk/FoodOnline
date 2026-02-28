from django.contrib import messages

def messages(request):
    messages.success(request, 'Your account has been created successfully')
    messages.error(request, 'Your account has not been created successfully')
    messages.warning(request, 'Your account has not been created successfully')
    messages.info(request, 'Your account has not been created successfully')
    messages.debug(request, 'Your account has not been created successfully')
    return messages
from .models import StockRequest
def pending_requests_count(request):
    if request.user.is_authenticated :  # Adjust based on your user model
        count = StockRequest.objects.filter(status='Pending').count()
        return {'pending_requests_count': count}
    return {'pending_requests_count': 0}
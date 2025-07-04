from django.db import models
from django.contrib.auth.models import User
import uuid
import random
import string

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name
class Item(models.Model):
    name = models.CharField(max_length=100)
    product_number   = models.CharField(max_length=100, unique=True) 
    description = models.TextField()
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)
    quantity_in_stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)

    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    

    def __str__(self):
        return self.name
    
    
class StockIn(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)  # links stock-in to a product
    quantity = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now_add=True)
    supplier = models.CharField(max_length=255, blank=True, null=True)
    stock_added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='stockin_records')

    def __str__(self):
        return f"{self.quantity} units of {self.item.name} stocked in on {self.date.date()}"
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
class StockOut(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    date_requested = models.DateTimeField(auto_now_add=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    purpose = models.CharField(max_length=255, blank=True, null=True)
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='stockout_requests')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='stockout_approvals')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    date_approved = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.quantity} {self.item.name} requested by {self.requested_by} - {self.status}"
    
class StockRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Partially Approved', 'Partially Approved'),
        ('Rejected', 'Rejected'),
        ('Fulfilled', 'Fulfilled'),
    ]

    request_id = models.CharField(max_length=36, unique=True, blank=True, editable=False)

    department_user = models.ForeignKey(User, on_delete=models.CASCADE)
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True)
    item = models.ForeignKey('Item', on_delete=models.CASCADE)
    requested_quantity = models.PositiveIntegerField()
    reason = models.TextField(blank=True)
    request_date = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_requests')
    approved_quantity = models.PositiveIntegerField(null=True, blank=True)
    admin_remarks = models.TextField(blank=True, null=True)
    approved_date = models.DateTimeField(null=True, blank=True)
    is_viewed_by_maker = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.request_id} - {self.item.name} requested by {self.department.name}"

    def save(self, *args, **kwargs):
        if not self.request_id:
            self.request_id = self.generate_unique_request_id()
        super().save(*args, **kwargs)

    def generate_unique_request_id(self):
        return f"REQ-{uuid.uuid4().hex.upper()[:10]}"
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.user.username
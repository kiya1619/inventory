from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login , logout
from under.models import Item, Category, StockIn,   StockOut, Department, UserProfile, StockRequest
from django.db.models import Count
from django.contrib.auth.models import User, Group
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.timezone import now
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test




def is_checker(user):
    return user.groups.filter(name='checker').exists()
def is_maker(user):
    return user.groups.filter(name='maker').exists()
def is_admin(user):
    return user.groups.filter(name='admin').exists()



# Create your views here.
from django.db.models import Sum
def home(request):
    return render(request, 'temp/home.html')
def login_view(request): 
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.groups.filter(name='checker').exists():
                messages.success(request, "Welcome, " + user.username + "!")
                return redirect('dashboard_checker')
            if user.groups.filter(name='maker').exists():
                messages.success(request, "Welcome, " + user.username + "!")
                return redirect('dashboard_maker')
            messages.success(request, "Welcome, " + user.username + "!")
            return redirect("mainhome")
            
        else:
            messages.error(request, "Invalid username or password.")
   
    return render(request, 'temp/login.html')
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect
from .models import Department, UserProfile  # adjust import if needed
@user_passes_test(is_admin)
def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('firstname')
        last_name = request.POST.get('lastname')
        username = request.POST.get('username')
        email = request.POST.get('email')
        role = request.POST.get('role')
        department_id = request.POST.get('department')
        password1 = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('register')  # or render the same page

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('register')

        user = User.objects.create_user(
            username=username,
            password=password1,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )

        try:
            group = Group.objects.get(name=role)
            user.groups.add(group)
        except Group.DoesNotExist:
            messages.error(request, f"Role group '{role}' does not exist.")
            return redirect('register')

        department = None
        if department_id:
            try:
                department = Department.objects.get(id=int(department_id))
            except (Department.DoesNotExist, ValueError):
                messages.error(request, "Invalid department selected.")
                return redirect('register')

        UserProfile.objects.create(user=user, department=department)
        messages.success(request, "User registered successfully.")
        return redirect('register')  # or redirect to a user list page

    departments = Department.objects.all()
    context = {
        'departments': departments,
    }
    return render(request, 'admin_page/register.html', context)

@user_passes_test(is_admin)
def mainhome(request):
    items = Item.objects.all()
    total_categories = Category.objects.count()
    in_stock_items = Item.objects.filter(quantity_in_stock__gt=0).count()
    out_of_stock_items = Item.objects.filter(quantity_in_stock=0).count()
    total_items = items.count()
    
    
    context = {
        'items': items,
        'total_categories': total_categories,
        'in_stock_items': in_stock_items,
        'out_of_stock_items': out_of_stock_items,
        'total_items': total_items,
        'categories': Category.objects.annotate(item_count=Count('item'))

    }
    return render(request, 'admin_page/mainhome.html', context)

@user_passes_test(is_admin)
def items(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        product_number = request.POST.get('product_number')
        description = request.POST.get('description')
        category_id = request.POST.get('category')
        quantity_in_stock = request.POST.get('quantity_in_stock')
        image = request.FILES.get('image')
        unit_price = request.POST.get('unit_price')

        category = Category.objects.get(id=category_id)
        item = Item(name=name, product_number=product_number, description=description, category=category, quantity_in_stock=quantity_in_stock, image=image, unit_price=unit_price)
        item.save()
        messages.success(request, f"Item '{name}' added successfully.")

    context = {
        'categories': categories,
    }
    return render(request, 'admin_page/items.html', context)


def add_items_checker(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        product_number = request.POST.get('product_number')
        description = request.POST.get('description')
        category_id = request.POST.get('category')
        quantity_in_stock = request.POST.get('quantity_in_stock')
        image = request.FILES.get('image')
        unit_price = request.POST.get('unit_price')

        category = Category.objects.get(id=category_id)
        
        item = Item(name=name, product_number=product_number, description=description, category=category, quantity_in_stock=quantity_in_stock, image=image, unit_price=unit_price)
        item.save()
        try:
            send_mail(
                subject='New Item Added to Inventory',
                message=f"A new item has been added:\n\n"
                        f"Name: {name}\n"
                        f"Category: {category.name}\n"
                        f"Stock: {quantity_in_stock}\n"
                        f"Price: {unit_price}",
                from_email='abdisaworkmail@gmail.com',
                recipient_list=['abdisaworkmail@gmail.com'],  # Add multiple recipients if needed
                fail_silently=False,
            )
        except Exception as e:
            messages.warning(request, f"Item added, but email not sent: {e}")
        messages.success(request, f"Item '{name}' added successfully.")

    context = {
        'categories': categories,
    }
    return render(request, 'checker/add_items_checker.html', context)

def reports(request):
    total_requests = StockRequest.objects.count()
    approved_requests = StockRequest.objects.filter(status='Approved').count()
    pending_requests = StockRequest.objects.filter(status='Pending').count()
    rejected_requests = StockRequest.objects.filter(status='Rejected').count()
    top_requested_items = StockRequest.objects.values('item__name').annotate(total_requested=Count('item')).order_by('-total_requested')[:5]
    department_wise_requests = StockRequest.objects.values('department__name').annotate(total_requests=Count('id')).order_by('-total_requests')
    context = {
        'total_requests': total_requests,
        'approved_requests': approved_requests,
        'pending_requests': pending_requests,
        'rejected_requests': rejected_requests,
        'top_requested_items': top_requested_items,
        'department_wise_requests': department_wise_requests,
    }
    return render(request, 'admin_page/reports.html', context)
def sales(request): 
    return render(request, 'admin_page/sales.html')


@user_passes_test(is_admin)
def item_list(request):
    query = request.GET.get('q', '').strip()  # Get search query from GET params
    
    if query:
        # Filter items by name, product_number, or category name (case-insensitive)
        items = Item.objects.filter(
            Q(name__icontains=query) | 
            Q(product_number__icontains=query) | 
            Q(category__name__icontains=query)
        ).distinct()
    else:
        items = Item.objects.all()

    # Paginate with 10 items per page
    paginator = Paginator(items, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'items': page_obj.object_list,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'query': query,
    }
    return render(request, 'admin_page/item_list.html', context)
from django.contrib import messages
@user_passes_test(is_admin)
def stockin(request):
    items = Item.objects.all()
    if request.method == 'POST':
        item_id = request.POST.get('item')
        quantity = request.POST.get('quantity')
        supplier = request.POST.get('supplier')

        item = Item.objects.get(id=item_id)
        item.quantity_in_stock += int(quantity)
        item.save()

        stock_in = StockIn(item=item, quantity=quantity, supplier=supplier, stock_added_by = request.user)
        stock_in.save()

        messages.success(request, f"{quantity} units of '{item.name}' successfully stocked in.")

    context = {
        'items': items,
    }
    return render(request, 'admin_page/stockin.html', context)

@user_passes_test(is_admin)
def create_stockout_request(request):
    
    return render(request, 'admin_page/stockout.html')
@user_passes_test(is_admin)
def stockin_history(request):
    stock_ins = StockIn.objects.all()
    context = {
        'stock_ins': stock_ins,
    }
    return render(request, 'admin_page/stockin_history.html', context)

@user_passes_test(is_maker)
def maker_stockout_request(request):
    items = Item.objects.all()

    if request.method == 'POST':
        if request.user.is_authenticated:
            try:
                user_profile = UserProfile.objects.get(user=request.user)
                department = user_profile.department

                item_id = request.POST.get('item')
                quantity = request.POST.get('requested_quantity')
                reason = request.POST.get('reason')

                # Validate form inputs
                if not item_id or not quantity:
                    messages.error(request, "Item and quantity are required.")

                item = Item.objects.get(id=int(item_id))

                # Save StockRequest
                StockRequest.objects.create(
                    department_user=request.user,
                    department=department,
                    item=item,
                    requested_quantity=int(quantity),
                    reason=reason,
                )

                messages.success(request, "Stock request submitted successfully.")
            
            except UserProfile.DoesNotExist:
                return HttpResponse("User profile not found.")

            except Item.DoesNotExist:
                return HttpResponse("Invalid item selected.")

        else:
            return HttpResponse("You must be logged in to submit a request.")
    

       
    context = {
        'items': items,
    }
    return render(request, 'maker/maker_stockout_request.html', context)
@user_passes_test(is_checker)
def checker_stockout_list(request):
    return render(request, 'admin_page/checker_stockout_list.html')
@user_passes_test(is_maker)
def maker_dashboard(request):
    return render(request, 'maker/maker_dashboard.html')
def logout_view(request):
    logout(request)
    return redirect('home')


@user_passes_test(is_maker)
def item_list_maker(request):
    query = request.GET.get('q', '').strip()  # Get search query from GET params
    
    if query:
        # Filter items by name, product_number, or category name (case-insensitive)
        items = Item.objects.filter(
            Q(name__icontains=query) | 
            Q(product_number__icontains=query) | 
            Q(category__name__icontains=query)
        ).distinct()
    else:
        items = Item.objects.all()

    # Paginate with 10 items per page
    paginator = Paginator(items, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'items': page_obj.object_list,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'query': query,
    }
    return render(request, 'maker/item_list_maker.html', context)

@user_passes_test(is_maker)
def dashboard_maker(request):
    items = Item.objects.all()
    total_categories = Category.objects.count()
    in_stock_items = Item.objects.filter(quantity_in_stock__gt=0).count()
    out_of_stock_items = Item.objects.filter(quantity_in_stock=0).count()
    total_items = items.count()
    
    
    context = {
        'items': items,
        'total_categories': total_categories,
        'in_stock_items': in_stock_items,
        'out_of_stock_items': out_of_stock_items,
        'total_items': total_items,
        'categories': Category.objects.annotate(item_count=Count('item'))

    }
    return render(request, 'maker/dashboard_maker.html', context)
@user_passes_test(is_admin)
def allusers(request):
    query = request.GET.get('q', '').strip()  # Get search query from GET params
    if query:
        # Filter users by username or email (case-insensitive)
        users = User.objects.filter(
            Q(username__icontains=query) | 
            Q(email__icontains=query) | 
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).distinct()
      
    else:
        users = User.objects.all()
    
    
    context = { 
        'users': users,
        'query': query,
        
    }
    return render(request, 'admin_page/allusers.html', context)

@user_passes_test(is_admin)

def stockout_requests(request):
    stock_requests = StockRequest.objects.all()

    status = request.GET.get('status')  # Get the status from the query parameter
    if status:
        stock_requests = stock_requests.filter(status__iexact=status)

    q = request.GET.get('q', '')  # Get the search query
    if q:
        stock_requests = stock_requests.filter(
            Q(item__name__icontains=q) |
            Q(reason__icontains=q) |
            Q(department__name__icontains=q) |
            Q(request_id__icontains=q)
        )

    context = {
        'stock_requests': stock_requests,
        'selected_status': status,
        'search_query': q,
    }
    return render(request, 'admin_page/stockout_requests.html', context)

@user_passes_test(is_maker)

def myrequests(request):
    if request.user.is_authenticated:
        stock_requests = StockRequest.objects.filter(department_user=request.user)

        status = request.GET.get('status')
        if status:
            stock_requests = stock_requests.filter(status__iexact=status)

        q = request.GET.get('q', '')
        if q:
            stock_requests = stock_requests.filter(
                Q(item__name__icontains=q) |
                Q(reason__icontains=q) |
                Q(department__name__icontains=q) | 
                Q(request_id__icontains=q)
            )

    else:
        stock_requests = StockRequest.objects.none()  # Empty queryset for unauthenticated

    context = {
        'stock_requests': stock_requests,
        'search_query': q,  # Pass back the query to the template if needed
        'selected_status': status,
    }
    return render(request, 'maker/my_requests.html', context)

@user_passes_test(is_checker)
def dashboard_checker(request):
    items = Item.objects.all()
    total_categories = Category.objects.count()
    in_stock_items = Item.objects.filter(quantity_in_stock__gt=0).count()
    out_of_stock_items = Item.objects.filter(quantity_in_stock=0).count()
    total_items = items.count()
    
    
    context = {
        'items': items,
        'total_categories': total_categories,
        'in_stock_items': in_stock_items,
        'out_of_stock_items': out_of_stock_items,
        'total_items': total_items,
        'categories': Category.objects.annotate(item_count=Count('item'))

    }
    return render(request, 'checker/dashboard_checker.html', context)

@user_passes_test(is_checker)
def item_list_checker(request):
    query = request.GET.get('q', '').strip()  # Get search query from GET params
    
    if query:
        # Filter items by name, product_number, or category name (case-insensitive)
        items = Item.objects.filter(
            Q(name__icontains=query) | 
            Q(product_number__icontains=query) | 
            Q(category__name__icontains=query)
        ).distinct()
    else:
        items = Item.objects.all()

    # Paginate with 10 items per page
    paginator = Paginator(items, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'items': page_obj.object_list,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'query': query,
    }
    return render(request, 'checker/item_list_checker.html', context)
@user_passes_test(is_checker)
def checker_request(request):
    stock_requests = StockRequest.objects.all()
    status = request.GET.get('status')  # Get the status from the query parameter
    if status:
        stock_requests = StockRequest.objects.filter(status__iexact=status)
    else:
        stock_requests = StockRequest.objects.all()
    
   
    context = {
        'stock_requests': stock_requests,
    }
    return render(request, 'checker/checker_request.html', context)
@user_passes_test(is_checker)
def viewitems(request, id):
    requests = StockRequest.objects.filter(id=id)
    context = {
        'requests': requests,
    }
    return render(request, 'checker/viewitems.html', context)

@user_passes_test(is_checker)
def approve_request(request, id):
    if request.method == 'POST':
        try:
            stock_request = StockRequest.objects.get(id=id)
            stock_request.status = 'Approved'
            stock_request.approved_quantity = request.POST.get('approved_quantity')
            stock_request.approved_by = request.user
            stock_request.approved_date = now()
            #item update
            item = stock_request.item
            if item.quantity_in_stock >= int(stock_request.approved_quantity):
                item.quantity_in_stock -= int(stock_request.approved_quantity)
                item.save()  # ✅ This is what was missing
            else:
                return HttpResponse("Error: Not enough stock available.")
            stock_request.save()
            return redirect('viewitems', id=id)
        
        except StockRequest.DoesNotExist:
            return HttpResponse("Stock request not found.")
    return redirect('checker_request')

@user_passes_test(is_checker)
def view_approved(request, id):
    requests = StockRequest.objects.filter(id=id).first()
    context = {
        'requests': requests,
    }
    return render(request, 'checker/view_approved.html', context)

@user_passes_test(is_checker)
def view_rejected(request, id):
    requests = StockRequest.objects.filter(id=id).first()
    context = {
        'requests': requests,
    }
    return render(request, 'checker/view_rejected.html', context)

@user_passes_test(is_checker, login_url='access_denied')
def add_item_checker(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        product_number = request.POST.get('product_number')
        description = request.POST.get('description')
        category_id = request.POST.get('category')
        quantity_in_stock = request.POST.get('quantity_in_stock')
        image = request.FILES.get('image')
        unit_price = request.POST.get('unit_price')

        category = Category.objects.get(id=category_id)
        item = Item(name=name, product_number=product_number, description=description, category=category, quantity_in_stock=quantity_in_stock, image=image, unit_price=unit_price)
        item.save()
        return redirect('item_list_checker')  # Redirect to the item list after adding a new item
    context = {
        'categories': categories,
    }
    return render(request, 'checker/add_item_checker.html', context)

@user_passes_test(is_checker)
def stockin_checker(request):
    items = Item.objects.all()
    if request.method == 'POST':
        item_id = request.POST.get('item')
        quantity = request.POST.get('quantity')
        supplier = request.POST.get('supplier')

        item = Item.objects.get(id=item_id)
        item.quantity_in_stock += int(quantity)
        item.save()

        stock_in = StockIn(item=item, quantity=quantity, supplier=supplier, stock_added_by=request.user)
        stock_in.save()
    context = {
        'items': items,
    }
    return render(request, 'checker/stockin_checker.html', context)

@user_passes_test(is_checker)
def reject_request(request, id):
    if request.method == 'POST':
        try:
            stock_request = StockRequest.objects.get(id=id)
            stock_request.status = 'Rejected'
            stock_request.approved_by = request.user
            stock_request.approved_date = now()
            stock_request.save()
            return redirect('viewitems', id=id)
        except StockRequest.DoesNotExist:
            return HttpResponse("Stock request not found.")
    return redirect('checker_request')

@user_passes_test(is_admin)
def deleteitem_admin(request, id):
    try:
        item = Item.objects.get(id=id)
        item.delete()
        return redirect('item_list')  # Redirect to the item list after deletion
    except Item.DoesNotExist:
        return HttpResponse("Item not found.")
    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")
    
    
def access_denied(request):
    return render(request, 'temp/access_denied.html')

@user_passes_test(is_admin)
def categories(request):
    categories = Category.objects.all()
   
    
    context = {
        'categories': categories,
    }
    return render(request, 'admin_page/categories.html', context)

def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')

        if not name:
            messages.error(request, "Category name is required.")
            return redirect('add_category')
        if Category.objects.filter(name=name).exists():
            messages.error(request, "Category with this name already exists.")
            return redirect('add_category')
        category = Category(name=name, description=description)
        category.save()
        messages.success(request, "Category added successfully.")
        return redirect('categories')  # Redirect to the categories list after adding a new category
   
    return render(request, 'admin_page/add_category.html')  # Render the form for adding a category

def contact(request):
   
    return render(request, 'temp/contact.html')  # Render the contact form


def delete_users(request, id):
    try:
        user = User.objects.get(id=id)
        user.delete()
        messages.info(request, "User deleted successfully.")
        return redirect('allusers')  # Redirect to the user list after deletion
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('allusers')
    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
        return redirect('allusers')
    
# views.py
from django.core.mail import send_mail

def send_test_email(request):
    send_mail(
        subject='Test Email from Django',
        message='Hello! This is a test email sent from Django.',
        from_email='abdisaworkmail@gmail.com',
        recipient_list=['abdisaworkmail@gmail.com'],
        fail_silently=False,
    )
    return HttpResponse("Email sent successfully!")


def check_and_notify_low_stock(request):
    low_stock_items = Item.objects.filter(quantity_in_stock=0)

    if low_stock_items.exists():
        item_names = ", ".join([item.name for item in low_stock_items])
        message = f"The following items are out of stock:\n\n{item_names}"

        send_mail(
            subject='Stock Alert: Items Out of Stock',
            message=message,
            from_email='abdisaworkmail@gmail.com',
            recipient_list=['abdisaworkmail@gmail.com'],
            fail_silently=False,
        )
        return HttpResponse("Email sent for out-of-stock items.")
    else:
        return HttpResponse("No items out of stock.")
    
def view_items(request, id):
    try:
        item = Item.objects.get(id=id)
    except Item.DoesNotExist:
        return HttpResponse("Item not found.")
    if request.user.groups.filter(name='admin').exists():
        base = 'admin_page/base.html'
    elif request.user.groups.filter(name='maker').exists():
        base = 'maker/base.html'
    elif request.user.groups.filter(name='checker').exists():
        base = 'checker/base.html'
    else:
        base = 'base.html'  # fallback
    
    context = {
        'item': item,
        'base_template': base,

    }
    return render(request, 'temp/view_items.html', context)

def edit_item(request, id):
    try:
        item = Item.objects.get(id=id)
    except Item.DoesNotExist:
        messages.error(request, "Item not found.")
        return redirect('item_list')  # Redirect to the item list if item not found
    if request.user.groups.filter(name='admin').exists():
        base = 'admin_page/base.html'
    elif request.user.groups.filter(name='maker').exists():
        base = 'maker/base.html'
    elif request.user.groups.filter(name='checker').exists():
        base = 'checker/base.html'
    else:
        base = 'base.html'
    category = Category.objects.all()  # Get all categories for the dropdown
    if request.method == 'POST':
        item.name = request.POST.get('name', item.name)
        item.product_number = request.POST.get('product_number', item.product_number)
        item.description = request.POST.get('description', item.description)
        item.quantity_in_stock = request.POST.get('quantity_in_stock', item.quantity_in_stock)
        item.unit_price = request.POST.get('unit_price', item.unit_price)
        item.image = item.image  # Keep the existing image unless a new one is uploaded
        
        category_id = request.POST.get('category')
        
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
                item.category = category
            except Category.DoesNotExist:
                messages.error(request, "Invalid category selected.")
        
        if 'image' in request.FILES:
            item.image = request.FILES['image']
        
        item.save()
        messages.success(request, "Item updated successfully.")
        return redirect(edit_item, id=id)  # Redirect to the same page to see the updated item
    
    context = {
        'item': item,
        'base_template': base,
        'categories': category,
    }
    return render(request, 'temp/edit_items.html', context)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from .models import User, Block, Canteen, Contact
from canteenapp.models import Item
from django.contrib.auth import logout


def index(request):
    return render(request, 'index.html')

def login_view(request):
    if request.method == 'POST':  
        uname = request.POST['username']  
        password = request.POST['password']  
        print(uname)  
        
        try:
            user = User.objects.get(email=uname, password=password) 
            print(user)
            request.session['login_id'] = user.pk  
            if user.role == 'admin':
                request.session['user_id'] = user.pk
                request.session['user_name'] = user.name  
                return redirect('/admin_dashboard')
            
            elif user.role == 'caterer':
                request.session['user_id'] = user.pk
                request.session['user_name'] = user.name  
                return redirect('/caterer_dashboard')  
                
            elif user.role == 'user':
                # For user type
                request.session['user_id'] = user.pk
                request.session['user_name'] = user.name  
                return redirect('/user_dashboard')  

            messages.success(request, 'Login Successful!')
            return redirect('main:index')  

        except User.DoesNotExist:
            return HttpResponse("<script>alert('Invalid Username Or Password');window.location='/login'</script>")

    return render(request, 'login.html')

def logout_view(request):
    logout(request)  
    return redirect('main:index')

def admin_dashboard(request):
    user_id = request.session.get('user_id') 
    if not user_id:
        return redirect('main:login')

    user = get_object_or_404(User, pk=user_id)
    users_count = User.objects.filter(role='user').count()
    caterers_count = User.objects.filter(role='caterer').count() 
    canteens_count = Canteen.objects.count()  
    blocks_count = Block.objects.count() 

    context = {
        'users_count': users_count,
        'caterers_count': caterers_count,
        'canteens_count': canteens_count,
        'blocks_count': blocks_count,
    }
    return render(request, 'admin_dashboard.html', context)


def caterer_dashboard(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('main:login')
    
    user = get_object_or_404(User, pk=user_id)
    canteens = Canteen.objects.filter(caterer=user)
    items = Item.objects.filter(canteen__caterer=user)

    return render(request, 'caterer_dashboard.html', {
        'user': user,
        'canteens': canteens,
        'items': items,
    })

def user_dashboard(request):
    user_id = request.session.get('user_id')  
    if not user_id:
        return redirect('main:login')  

    user = get_object_or_404(User, pk=user_id)
    blocks = Block.objects.all()
    return render(request, 'user_dashboard.html', {'user': user, 'blocks': blocks})

def contact(request):
    if request.method == 'POST':
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        message = request.POST.get('message')

        contact = Contact(fname=fname, lname=lname, phone=phone, email=email, message=message)
        contact.save()
        messages.success(request, 'Your message has been sent successfully!')

    return render(request, 'contact.html')

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Profile, Post, LikePost

@login_required(redirect_field_name='reg')
def index(request):
    user_obj = User.objects.get(username=request.user)
    user_profile = Profile.objects.get(user=user_obj)

    posts = Post.objects.all()
    context ={
        'user_profile': user_profile,
        'posts': posts
    }
    return render(request, 'index.html', context)

def signup(request):

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email is taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username not available')
                return redirect('signup')
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()

            # Log user in and redirect to seetings page
            user_login = auth.authenticate(request, username=username, password=password)
            auth.login(request, user_login)
            # Create a Profiel object for the new user
            user_model = User.objects.get(username=username)
            new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
            new_profile.save()
            return redirect('settings')
        else:
            messages.info(request, 'Password are not the same')
            return redirect(signup)

    return render(request, 'signup.html')

def signin(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(request, username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('index')
        messages.info(request, 'Credential invalid')
        return redirect('signin')
    
    return render(request, 'signin.html')

@login_required
def logout(request):
    auth.logout(request)
    return redirect('signin')

@login_required(redirect_field_name='reg')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':

        if request.FILES.get('image') == None:
            image = user_profile.profile_img
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profile_img = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        
        if request.FILES.get('image') != None:
            image = request.FILES.get('image')
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profile_img = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        
        return redirect('settings')

    context = {
        'user_profile': user_profile,
    }
    return render(request, 'settings.html', context)

@login_required
def upload(request):

    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']

        new_post = Post.objects.create(
            user=user, image=image, caption=caption
        )
        new_post.save()
        return redirect('index')
    else:
        return redirect('index')
    return HttpResponse('UPLOAD')

def like_post(request):
    username = request.user.username
    post_id = request.GET['post_id']

    post = Post.objects.get(id=post_id)

    like_filter = LikePost.objects.filter(username=username, post_id=post_id).first()

    if like_filter == None:
        new_post = LikePost.objects.create(username=username, post_id=post_id)
        new_post.save()
        post.no_of_likes += 1
        post.save()
        return redirect('index')

    else:
        like_filter.delete()
        post.no_of_likes -= 1
        post.save()
        return redirect('index')
    
    
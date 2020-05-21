from base64 import b64encode

from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Permission
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse

from dog_shelter.forms import RegisterUserForm, DogCreateForm, DogUpdateForm, UpdateUserForm
from dog_shelter.recommendation_system.recommendation_system import recommend_dogs
from .models import Dog, Organization, DogImages, OrganizationAdmin
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User


def index(request):
    dogs = Dog.objects.all().count()
    organizations = Organization.objects.all().count()
    return render(request, 'index.html', context={'dogs': dogs, 'organizations': organizations})


def logout_view(request):
    logout(request)
    return redirect('index')


def dogs_list_view(request):
    dogs = []
    recommend_dogs_list_id = []
    if request.user.has_perm('dog_shelter.like_dog'):
        user_pk = request.user.pk
        recommend_dogs_list_id = recommend_dogs(user_pk)
        if recommend_dogs_list_id is not None:
            dogs = list(Dog.objects.filter(pk__in=recommend_dogs_list_id))
            dogs += list(Dog.objects.exclude(pk__in=recommend_dogs_list_id))
        else:
            dogs = list(Dog.objects.all())
    else:
        dogs = list(Dog.objects.all())

    dogsImages = list(DogImages.objects.all())
    for i in dogs:
        dog_images = list(filter(lambda x: x.dog_id == i.pk, dogsImages))
        if len(dog_images) > 0:
            i.image = b64encode(dog_images.pop().image).decode('utf-8')

    return render(request, 'dog_shelter/dogs_list.html', context={'dogs': dogs})


def register_user_view(request):
    if request.method == 'POST':
        form = RegisterUserForm(data=request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(user.password)
            perm = Permission.objects.get(name='Can like dog')
            user.save()
            user.user_permissions.add(perm)
            # user.save()
            return redirect('login')
        else:
            return render(request, "register.html", {"form": form})
    else:
        form = RegisterUserForm()
        return render(request, "register.html", {"form": form})


def update_user_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    liked_dogs = list(user.dog_set.all())
    for dog in liked_dogs:
        for img in list(dog.dogimages_set.all()):
            if img:
                dog.image = b64encode(img.image).decode('utf-8')

    if request.method == 'POST':
        form = UpdateUserForm(data=request.POST)
        if form.is_valid():
            if user.username != form.cleaned_data['username']:
                user.username = form.cleaned_data['username']

            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()

            return render(request, 'dog_shelter/user_info.html', {
                'form': form,
                'dogs': liked_dogs
            })
        else:
            return render(request, 'dog_shelter/user_info.html', {
                'form': form,
                'dogs': liked_dogs
            })

    else:
        form = UpdateUserForm(instance=user)
        return render(request, 'dog_shelter/user_info.html', {
            'form': form,
            'dogs': liked_dogs
        })


class OrganizationAdminView(generic.ListView):
    model = OrganizationAdmin


class OrganizationsListView(generic.ListView):
    model = Organization


@login_required
@permission_required('dog_shelter.can_add_dog')
def create_dog_view(request):
    if request.method == 'POST':
        form = DogCreateForm(request.POST, request.FILES)
        if form.is_valid():
            dog = form.save(commit=False)
            dog.organization = request.user.users.organization
            dog.save()
            files = request.FILES.getlist('photos')
            for file in files:
                f = file.read()
                DogImages.objects.create(image=f, dog=dog)
            return redirect('dogs')
        else:
            print(form.errors)
    else:
        form = DogCreateForm()
        return render(request, "dog_shelter/dog_form.html", {'form': form})


def dog_info_view(request, pk):
    dog_photos = []
    permission = False
    can_like = False
    dog = get_object_or_404(Dog, pk=pk)
    if dog:
        dog_photo = DogImages.objects.filter(dog=dog)
        for ph in dog_photo:
            dog_photos.append(b64encode(ph.image).decode('utf-8'))

    if request.user.is_authenticated and request.user.has_perm("dog_shelter.can_change_dog"):
        if request.user.users:
            permission = request.user.users.organization_id == dog.organization_id

    if request.user.has_perm("dog_shelter.like_dog"):
        can_like = True

    return render(
        request,
        'dog_shelter/dog_info.html',
        context={
            'dog': dog,
            'photos': dog_photos,
            'range': range(len(dog_photos)),
            'permission': permission,
        }
    )


def user_likes_dog_view(request):
    user = User.objects.get(pk=request.user.pk)
    dog_pk = request.GET.get('dog_pk', None)
    dog = Dog.objects.get(pk=int(dog_pk))
    dog.user_liked.add(user)
    dog.save()
    return JsonResponse({'uid': user, 'did': dog_pk}, safe=False)


def organization_info_view(request, pk):
    organization = Organization.objects.get(pk=pk)
    organization_admin = OrganizationAdmin.objects.filter(organization_id=pk).all()
    organization_dogs = list(organization.dog_set.all())
    for dog in organization_dogs:
        for img in list(dog.dogimages_set.all()):
            if img:
                dog.image = b64encode(img.image).decode('utf-8')
    if organization_admin:
        return render(
            request,
            'dog_shelter/organization_info.html',
            context={
                'organization': organization,
                'organization_admin': organization_admin,
                'dogs': organization_dogs
            }
        )


# class DogUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
#     model = Dog
#     fields = ('name', 'description', 'breed', 'age', 'size', 'disease_info')
#     permission_required = 'dog_shelter.can_change_dog'
#

def dog_update_view(request, pk):
    dog = get_object_or_404(Dog, pk=pk)
    if request.method == 'POST':
        form = DogUpdateForm(request.POST)
        if form.is_valid():
            dog.name = form.cleaned_data['name']
            dog.description = form.cleaned_data['description']
            dog.breed = form.cleaned_data['breed']
            dog.age = form.cleaned_data['age']
            dog.size = form.cleaned_data['size']
            dog.disease_info = form.cleaned_data['disease_info']
            dog.save()
            return redirect('dog-info', pk)
        else:
            return render(request, "dog_shelter/dog_update.html", {'form': form})
    else:
        form = DogUpdateForm(instance=dog)
        return render(request, "dog_shelter/dog_update.html", {'form': form})


class DogDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Dog
    permission_required = 'dog_shelter.can_delete_dog'
    success_url = reverse_lazy('dogs')

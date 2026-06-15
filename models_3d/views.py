from django.shortcuts import render

from models_3d.models import Model3D, Material, Color
from order.forms import AddToCartForm
from users.models import User


# Create your views here.

def index(request):
    models = Model3D.objects.all()[:4]
    context = {'user': request.user, 'models': models}
    return render(request, 'models_3d/index.html', context)


def catalog(request):
    models = Model3D.objects.all()

    context = {'models': models, 'user': request.user}

    return render(request, 'models_3d/catalog.html', context)


def model_detail(request, id: int):
    model = Model3D.objects.get(id=id)

    aggregated_options =  Material.objects.get_aggregated_options()

    form = AddToCartForm(aggregated_options=aggregated_options)

    context = {'model': model, 'aggregated_materials': aggregated_options, 'user': request.user, 'form': form}
    return render(request, 'models_3d/model_detail.html', context)
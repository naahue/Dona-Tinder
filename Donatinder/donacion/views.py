from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import IngresarDonacionForm, ModificarDonacionForm
from .models import Donacion


def _donacion_del_usuario(request, donacion_id):
    return get_object_or_404(Donacion, pk=donacion_id, donador=request.user)


@login_required
def ingresarDonacion(request):
    if request.method == 'POST':
        form = IngresarDonacionForm(request.POST, request.FILES)
        if form.is_valid():
            donacion = form.save(commit=False)
            donacion.donador = request.user
            donacion.save()
            return redirect('donacion:ingresarDonacion')
    else:
        form = IngresarDonacionForm()
    return render(request, 'donacion/ingresarDonacion.html', {'form': form})


@login_required
def verDonaciones(request, userId):
    if request.user.pk != userId:
        return redirect('donacion:verDonaciones', userId=request.user.pk)
    donaciones = Donacion.objects.filter(donador=request.user, retirado=False)
    return render(request, 'donacion/verDonaciones.html', {'donaciones': donaciones})


@login_required
def confirmarDonacion(request, donacionId):
    donacion = _donacion_del_usuario(request, donacionId)
    if request.method == 'POST':
        donacion.retirado = True
        donacion.save(update_fields=['retirado'])
        return redirect('donacion:verDonaciones', userId=request.user.pk)
    return render(request, 'donacion/confirmarDonacion.html', {'donacion': donacion})


@login_required
def ayuda(request):
    return render(request, 'donacion/ayuda.html')


@login_required
def inicio(request):
    qs = (
        Donacion.objects.filter(retirado=False)
        .exclude(donador=request.user)
        .order_by('-id')
    )
    items = [
        {
            'id': d.id,
            'nombre': d.nombre,
            'descripcion': d.descripcion,
            'estado': d.get_estado_display(),
            'imagen': d.imagen.url,
        }
        for d in qs
    ]
    return render(request, 'donacion/inicio.html', {'donaciones_data': items})


@login_required
def modificarDonacion(request, donacionId):
    donacion = _donacion_del_usuario(request, donacionId)
    if request.method == 'POST':
        form = ModificarDonacionForm(request.POST, request.FILES, instance=donacion)
        if form.is_valid():
            form.save()
            return redirect('donacion:verDonaciones', userId=request.user.pk)
    else:
        form = ModificarDonacionForm(instance=donacion)
    return render(request, 'donacion/modificarDonacion.html', {'form': form})


@login_required
def eliminarDonacion(request, donacionId):
    donacion = _donacion_del_usuario(request, donacionId)
    if request.method == 'POST':
        donacion.delete()
        return redirect('donacion:verDonaciones', userId=request.user.pk)
    return render(request, 'donacion/eliminarDonacion.html', {'donacion': donacion})

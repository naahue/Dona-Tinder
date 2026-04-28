from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import InicioSesionForm, ModificarContraseñaForm, ModificarDatosForm, RegistroForm


def registrar(request):
    if request.user.is_authenticated:
        return redirect('donacion:ingresarDonacion')

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            user = authenticate(
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1'],
            )
            if user is not None:
                login(request, user)
                return redirect('donacion:ingresarDonacion')
            print('Error al querer iniciar sesión. Intentelo nuevamente.')
        else:
            for error in form.errors.values():
                print(error)
    else:
        form = RegistroForm()

    return render(request, 'usuarios/registro.html', {'form': form})


def inicioSesion(request):
    message = None
    if request.method == 'POST':
        form = InicioSesionForm(request.POST)
        if form.is_valid():
            user = authenticate(
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                return redirect('donacion:ingresarDonacion')
            message = 'Error con el usuario o la contraseña'
            print('Error con el usuario o la contraseña')
    else:
        form = InicioSesionForm()
    return render(request, 'usuarios/inicioSesion.html', {'form': form, 'message': message})


@login_required
def salir(request):
    logout(request)
    return redirect('usuarios:inicioSesion')


@login_required
def modificar(request):
    if request.method == 'POST':
        form = ModificarDatosForm(request.POST)
        if form.is_valid():
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.save()
            return redirect('donacion:ingresarDonacion')
        for error in form.errors.values():
            print(error)
    else:
        form = ModificarDatosForm(
            initial={'first_name': request.user.first_name, 'last_name': request.user.last_name}
        )
    return render(request, 'usuarios/modificarDatos.html', {'form': form})


@login_required
def modificarContraseña(request):
    if request.method == 'POST':
        form = ModificarContraseñaForm(request.POST)
        if form.is_valid():
            request.user.set_password(form.cleaned_data['password1'])
            request.user.save()
            login(request, request.user)
            return redirect('donacion:ingresarDonacion')
        for error in form.errors.values():
            print(error)
    else:
        form = ModificarContraseñaForm()
    return render(request, 'usuarios/modificarContraseña.html', {'form': form})


@login_required
def eliminarCuenta(request):
    if request.method == 'POST':
        request.user.delete()
        logout(request)
        return redirect('usuarios:inicioSesion')
    return render(request, 'usuarios/eliminarCuenta.html')

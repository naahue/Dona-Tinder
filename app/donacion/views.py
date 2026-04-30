import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import DenunciaForm, IngresarDonacionForm, MensajeForm, ModificarDonacionForm
from .models import Conversacion, ConversacionOcultaPorUsuario, DecisionDonacion, Denuncia, Donacion, Mensaje, UsuarioBloqueo

_FILTROS_CONVERSACIONES = frozenset({'todos', 'visibles', 'ocultos'})


def _filtro_conversaciones_desde_query(query_dict, default='todos'):
    raw = (query_dict.get('filtro') or '').strip().lower()
    return raw if raw in _FILTROS_CONVERSACIONES else default


def _donacion_del_usuario(request, donacion_id):
    return get_object_or_404(Donacion, pk=donacion_id, donador=request.user)


def _aplicar_visibilidad_feed(donacion):
    donacion.mostrar_en_feed = (
        donacion.estado_publicacion == Donacion.EstadoPublicacion.ACTIVA and not donacion.retirado
    )


def _conjunto_usuarios_bloqueados_relacion(usuario):
    emitidos = UsuarioBloqueo.objects.filter(bloqueador=usuario).values_list('bloqueado_id', flat=True)
    recibidos = UsuarioBloqueo.objects.filter(bloqueado=usuario).values_list('bloqueador_id', flat=True)
    return set(emitidos) | set(recibidos)


def _hay_bloqueo_entre(user_a_id, user_b_id):
    return UsuarioBloqueo.objects.filter(
        Q(bloqueador_id=user_a_id, bloqueado_id=user_b_id)
        | Q(bloqueador_id=user_b_id, bloqueado_id=user_a_id)
    ).exists()


def _contraparte_chat(usuario, conversacion):
    donacion = conversacion.donacion
    if usuario.pk == conversacion.interesado_id:
        return donacion.donador
    if usuario.pk == donacion.donador_id:
        return conversacion.interesado
    return None


def _oculto_ids_para_usuario(usuario):
    return set(
        ConversacionOcultaPorUsuario.objects.filter(usuario=usuario).values_list(
            'conversacion_id', flat=True
        )
    )


def _redirect_tras_seguridad_chat(usuario, conversacion):
    if usuario.pk == conversacion.interesado_id:
        return redirect('donacion:mis_chats')
    return redirect('donacion:donacion_chats', donacionId=conversacion.donacion_id)


def _usuario_participa_conversacion(user, conversacion):
    donacion = conversacion.donacion
    return user.pk == conversacion.interesado_id or user.pk == donacion.donador_id


def _sync_escrituras_para_donacion(donacion):
    qs = Conversacion.objects.filter(donacion=donacion)
    ep = donacion.estado_publicacion
    if ep == Donacion.EstadoPublicacion.ENTREGADA:
        qs.update(escritura_bloqueada=True)
    elif ep == Donacion.EstadoPublicacion.RESERVADA and donacion.reservado_con_id:
        qs.exclude(interesado_id=donacion.reservado_con_id).update(escritura_bloqueada=True)
        qs.filter(interesado_id=donacion.reservado_con_id).update(escritura_bloqueada=False)
    else:
        qs.update(escritura_bloqueada=False)


def _aviso_interesado_mis_likes(donacion, user):
    if donacion.estado_publicacion == Donacion.EstadoPublicacion.ENTREGADA:
        return 'Esta donación ya fue marcada como entregada.'
    if donacion.estado_publicacion == Donacion.EstadoPublicacion.RESERVADA:
        if donacion.reservado_con_id != user.pk:
            return 'El donador reservó la donación para otra persona.'
    return None


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
    donaciones = list(
        Donacion.objects.filter(donador=request.user)
        .prefetch_related('conversaciones')
        .order_by('retirado', '-id')
    )
    ocultos = _oculto_ids_para_usuario(request.user)
    for d in donaciones:
        d.num_conversaciones_visibles = sum(
            1 for c in d.conversaciones.all() if c.pk not in ocultos
        )
    return render(request, 'donacion/verDonaciones.html', {'donaciones': donaciones})


@login_required
def confirmarDonacion(request, donacionId):
    donacion = _donacion_del_usuario(request, donacionId)
    if donacion.estado_publicacion != Donacion.EstadoPublicacion.ACTIVA:
        messages.error(request, 'No podés usar “Confirmar retiro” con el estado actual de la publicación.')
        return redirect('donacion:verDonaciones', userId=request.user.pk)
    if request.method == 'POST':
        donacion.retirado = True
        _aplicar_visibilidad_feed(donacion)
        donacion.save(update_fields=['retirado', 'mostrar_en_feed'])
        return redirect('donacion:verDonaciones', userId=request.user.pk)
    return render(request, 'donacion/confirmarDonacion.html', {'donacion': donacion})


@login_required
def ayuda(request):
    return render(request, 'donacion/ayuda.html')


@login_required
def inicio(request):
    decided_ids = DecisionDonacion.objects.filter(usuario=request.user).values_list(
        'donacion_id', flat=True
    )
    qs = (
        Donacion.objects.filter(
            retirado=False,
            mostrar_en_feed=True,
            estado_publicacion=Donacion.EstadoPublicacion.ACTIVA,
        )
        .exclude(donador=request.user)
    )
    bloqueados_relacion = _conjunto_usuarios_bloqueados_relacion(request.user)
    if bloqueados_relacion:
        qs = qs.exclude(donador_id__in=bloqueados_relacion)
    decided_ids = list(decided_ids)
    if decided_ids:
        qs = qs.exclude(pk__in=decided_ids)
    qs = qs.order_by('-id')
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
def mis_likes(request):
    decisiones = (
        DecisionDonacion.objects.filter(
            usuario=request.user,
            tipo=DecisionDonacion.Tipo.INTERES,
        )
        .select_related('donacion', 'donacion__donador')
        .order_by('-creado')
    )
    filas = []
    ocultos = _oculto_ids_para_usuario(request.user)
    for dec in decisiones:
        conv, _ = Conversacion.objects.get_or_create(
            donacion=dec.donacion, interesado=request.user
        )
        if conv.pk in ocultos:
            continue
        filas.append(
            {
                'decision': dec,
                'conversacion': conv,
                'aviso_interesado': _aviso_interesado_mis_likes(dec.donacion, request.user),
            }
        )
    return render(
        request,
        'donacion/mis_likes.html',
        {
            'filas': filas,
            'num_chats_ocultos': ConversacionOcultaPorUsuario.objects.filter(
                usuario=request.user,
                conversacion__interesado=request.user,
            ).count(),
        },
    )


@login_required
def mis_chats(request):
    filtro = _filtro_conversaciones_desde_query(request.GET)
    ocultos = _oculto_ids_para_usuario(request.user)
    decisiones = (
        DecisionDonacion.objects.filter(
            usuario=request.user,
            tipo=DecisionDonacion.Tipo.INTERES,
        )
        .select_related('donacion', 'donacion__donador')
        .order_by('-creado')
    )
    todas_filas = []
    for dec in decisiones:
        conv, _ = Conversacion.objects.get_or_create(donacion=dec.donacion, interesado=request.user)
        es_oculto = conv.pk in ocultos
        todas_filas.append(
            {
                'decision': dec,
                'conversacion': conv,
                'oculto': es_oculto,
                'aviso_interesado': _aviso_interesado_mis_likes(dec.donacion, request.user),
            }
        )
    n_ocultos = sum(1 for f in todas_filas if f['oculto'])
    n_visibles = len(todas_filas) - n_ocultos
    if filtro == 'visibles':
        filas = [f for f in todas_filas if not f['oculto']]
    elif filtro == 'ocultos':
        filas = [f for f in todas_filas if f['oculto']]
    else:
        filas = todas_filas
    counts = {'todos': len(todas_filas), 'visibles': n_visibles, 'ocultos': n_ocultos}
    return render(
        request,
        'donacion/mis_chats.html',
        {'filas': filas, 'filtro': filtro, 'counts': counts},
    )


@login_required
def mis_chats_ocultos(request):
    """Compatibilidad: antes era la página solo de ocultos."""
    return redirect('{}?filtro=ocultos'.format(reverse('donacion:mis_chats')))


@login_required
def denunciar_conversacion(request, conversacionId):
    conversacion = get_object_or_404(
        Conversacion.objects.select_related('donacion', 'donacion__donador'),
        pk=conversacionId,
    )
    if not _usuario_participa_conversacion(request.user, conversacion):
        messages.error(request, 'No autorizado.')
        return redirect('donacion:inicio')
    otro = _contraparte_chat(request.user, conversacion)
    if otro and _hay_bloqueo_entre(request.user.pk, otro.pk):
        messages.error(request, 'No podés hacer una denuncia avanzada porque el chat ya no está disponible.')
        return redirect('donacion:inicio')
    donacion_ctx = conversacion.donacion
    if request.method == 'POST':
        form = DenunciaForm(request.POST)
        if form.is_valid():
            Denuncia.objects.create(
                denunciante=request.user,
                conversacion=conversacion,
                comentario=(form.cleaned_data.get('comentario') or '').strip(),
            )
            messages.success(
                request,
                'Guardamos tu denuncia para revisión. Gracias por avisarnos.',
            )
            return redirect('donacion:chat_conversacion', conversacionId=conversacion.pk)
    else:
        form = DenunciaForm()
    return render(
        request,
        'donacion/denunciar_conversacion.html',
        {'form': form, 'conversacion': conversacion, 'donacion': donacion_ctx},
    )


@login_required
@require_POST
def conversacion_seguridad(request, conversacionId):
    conversacion = get_object_or_404(
        Conversacion.objects.select_related('donacion', 'donacion__donador'),
        pk=conversacionId,
    )
    if not _usuario_participa_conversacion(request.user, conversacion):
        messages.error(request, 'No autorizado.')
        return redirect('donacion:inicio')
    otro = _contraparte_chat(request.user, conversacion)
    if otro is None:
        messages.error(request, 'No se pudo identificar la contraparte.')
        return redirect('donacion:inicio')
    accion = request.POST.get('accion')
    if accion == 'ocultar':
        ConversacionOcultaPorUsuario.objects.get_or_create(usuario=request.user, conversacion=conversacion)
        messages.success(
            request,
            'Ocultamos la conversación en tus listas. Podés verla y mostrarla de nuevo en Chats (filtro “Ocultos”).',
        )
        return _redirect_tras_seguridad_chat(request.user, conversacion)
    if accion == 'mostrar':
        ConversacionOcultaPorUsuario.objects.filter(usuario=request.user, conversacion=conversacion).delete()
        messages.success(request, 'La conversación volvió a mostrarse en tus listas.')
        return redirect('donacion:chat_conversacion', conversacionId=conversacion.pk)
    if accion == 'bloquear':
        if otro.pk == request.user.pk:
            messages.error(request, 'No podés bloquearte a vos mismo.')
            return redirect('donacion:chat_conversacion', conversacionId=conversacion.pk)
        UsuarioBloqueo.objects.get_or_create(bloqueador=request.user, bloqueado=otro)
        ConversacionOcultaPorUsuario.objects.get_or_create(usuario=request.user, conversacion=conversacion)
        ConversacionOcultaPorUsuario.objects.get_or_create(usuario=otro, conversacion=conversacion)
        messages.warning(
            request,
            'Bloqueaste a esta persona. El chat quedó oculto para ambos y nadie puede volver a abrirlo.',
        )
        return _redirect_tras_seguridad_chat(request.user, conversacion)
    messages.error(request, 'Acción no válida.')
    return redirect('donacion:chat_conversacion', conversacionId=conversacion.pk)


@login_required
def chat_conversacion(request, conversacionId):
    conversacion = get_object_or_404(
        Conversacion.objects.select_related('donacion', 'donacion__donador'),
        pk=conversacionId,
    )
    if not _usuario_participa_conversacion(request.user, conversacion):
        messages.error(request, 'No podés acceder a este chat.')
        return redirect('donacion:inicio')
    donacion = conversacion.donacion
    otro = _contraparte_chat(request.user, conversacion)
    if otro is None:
        messages.error(request, 'No autorizado.')
        return redirect('donacion:inicio')
    if _hay_bloqueo_entre(request.user.pk, otro.pk):
        if UsuarioBloqueo.objects.filter(bloqueador=request.user, bloqueado_id=otro.pk).exists():
            bloqueo_msg = 'Bloqueaste a esta persona: este chat ya no está disponible.'
        else:
            bloqueo_msg = 'Este chat ya no está disponible porque la otra cuenta te bloqueó.'
        messages.error(request, bloqueo_msg)
        return redirect('donacion:inicio')
    esta_oculta_para_mi = ConversacionOcultaPorUsuario.objects.filter(
        usuario=request.user,
        conversacion=conversacion,
    ).exists()
    url_denunciar = reverse('donacion:denunciar_conversacion', kwargs={'conversacionId': conversacion.pk})
    url_seguridad = reverse('donacion:conversacion_seguridad', kwargs={'conversacionId': conversacion.pk})

    es_donador = request.user.pk == donacion.donador_id
    lista_chats_url = (
        reverse('donacion:donacion_chats', kwargs={'donacionId': donacion.pk}) + '?filtro=todos'
        if es_donador
        else None
    )

    motivo_bloqueo = None
    if conversacion.escritura_bloqueada:
        if donacion.estado_publicacion == Donacion.EstadoPublicacion.ENTREGADA:
            motivo_bloqueo = (
                'Esta donación ya fue marcada como entregada. No se pueden enviar más mensajes.'
            )
        elif (
            donacion.estado_publicacion == Donacion.EstadoPublicacion.RESERVADA
            and donacion.reservado_con_id != conversacion.interesado_id
        ):
            motivo_bloqueo = 'El donador reservó esta donación para otra persona.'
        else:
            motivo_bloqueo = 'Este chat está cerrado para nuevos mensajes.'

    es_chat_elegido = (
        donacion.estado_publicacion == Donacion.EstadoPublicacion.RESERVADA
        and donacion.reservado_con_id == conversacion.interesado_id
    )
    puede_reservar = (
        es_donador
        and donacion.estado_publicacion == Donacion.EstadoPublicacion.ACTIVA
        and conversacion.interesado_id != request.user.pk
    )
    mostrar_confirmar_entrega = es_donador and es_chat_elegido
    mostrar_cancelar_reserva = es_donador and (
        donacion.estado_publicacion == Donacion.EstadoPublicacion.RESERVADA
    )
    mostrar_reabrir = es_donador and (
        donacion.estado_publicacion == Donacion.EstadoPublicacion.ENTREGADA
    )

    if request.method == 'POST':
        form = MensajeForm(request.POST)
        if conversacion.escritura_bloqueada:
            messages.warning(request, 'Este chat está cerrado para nuevos mensajes.')
        elif form.is_valid():
            nuevo = form.save(commit=False)
            nuevo.conversacion = conversacion
            nuevo.autor = request.user
            nuevo.save()
            return redirect('donacion:chat_conversacion', conversacionId=conversacion.pk)
    else:
        form = MensajeForm()
    mensajes = conversacion.mensajes.select_related('autor').order_by('creado')
    return render(
        request,
        'donacion/chat.html',
        {
            'conversacion': conversacion,
            'donacion': donacion,
            'mensajes': mensajes,
            'form': form,
            'escritura_bloqueada': conversacion.escritura_bloqueada,
            'motivo_bloqueo': motivo_bloqueo,
            'es_donador': es_donador,
            'lista_chats_url': lista_chats_url,
            'puede_reservar': puede_reservar,
            'mostrar_confirmar_entrega': mostrar_confirmar_entrega,
            'mostrar_cancelar_reserva': mostrar_cancelar_reserva,
            'mostrar_reabrir': mostrar_reabrir,
            'esta_oculta_para_mi': esta_oculta_para_mi,
            'url_denunciar': url_denunciar,
            'url_seguridad_accion': url_seguridad,
        },
    )


@login_required
def donacion_chats(request, donacionId):
    filtro = _filtro_conversaciones_desde_query(request.GET)
    donacion = get_object_or_404(
        Donacion.objects.select_related('reservado_con'),
        pk=donacionId,
        donador=request.user,
    )
    todas = list(
        Conversacion.objects.filter(donacion=donacion)
        .select_related('interesado')
        .order_by('-creado')
    )
    ocultos = _oculto_ids_para_usuario(request.user)
    visibles = [c for c in todas if c.pk not in ocultos]
    solo_ocultas = [c for c in todas if c.pk in ocultos]
    if filtro == 'visibles':
        conversaciones = visibles
    elif filtro == 'ocultos':
        conversaciones = solo_ocultas
    else:
        conversaciones = todas
    counts = {'todos': len(todas), 'visibles': len(visibles), 'ocultos': len(solo_ocultas)}
    oculto_ids = ocultos
    puede_reabrir = donacion.estado_publicacion == Donacion.EstadoPublicacion.ENTREGADA
    puede_cancelar_reserva_global = (
        donacion.estado_publicacion == Donacion.EstadoPublicacion.RESERVADA
    )
    return render(
        request,
        'donacion/chats_donacion.html',
        {
            'donacion': donacion,
            'conversaciones': conversaciones,
            'filtro': filtro,
            'counts': counts,
            'oculto_ids': oculto_ids,
            'puede_reabrir': puede_reabrir,
            'puede_cancelar_reserva_global': puede_cancelar_reserva_global,
        },
    )


@login_required
@require_POST
def donacion_donador_accion(request, donacionId):
    accion = request.POST.get('accion')
    allowed = {'reservar', 'confirmar_entrega', 'cancelar_reserva', 'reabrir'}
    if accion not in allowed:
        messages.error(request, 'Acción no válida.')
        return redirect('donacion:verDonaciones', userId=request.user.pk)

    with transaction.atomic():
        donacion = get_object_or_404(
            Donacion.objects.select_for_update(),
            pk=donacionId,
            donador=request.user,
        )
        if accion == 'reservar':
            raw = request.POST.get('conversacion_id')
            try:
                cid = int(raw)
            except (TypeError, ValueError):
                messages.error(request, 'Datos inválidos.')
                return redirect('donacion:verDonaciones', userId=request.user.pk)
            conversacion = get_object_or_404(Conversacion, pk=cid, donacion_id=donacion.pk)
            if donacion.estado_publicacion != Donacion.EstadoPublicacion.ACTIVA:
                messages.error(request, 'La publicación ya no está disponible para reservar.')
                return redirect('donacion:chat_conversacion', conversacionId=conversacion.pk)
            candidato_id = conversacion.interesado_id
            if candidato_id == request.user.pk:
                messages.error(request, 'No podés reservarte a vos mismo.')
                return redirect('donacion:chat_conversacion', conversacionId=conversacion.pk)
            donacion.estado_publicacion = Donacion.EstadoPublicacion.RESERVADA
            donacion.reservado_con_id = candidato_id
            _aplicar_visibilidad_feed(donacion)
            donacion.save(update_fields=['estado_publicacion', 'reservado_con', 'mostrar_en_feed'])
            _sync_escrituras_para_donacion(donacion)
            messages.success(
                request,
                'Reservaste la donación para esta persona. Los demás chats quedaron bloqueados.',
            )
            return redirect('donacion:chat_conversacion', conversacionId=conversacion.pk)
        if accion == 'confirmar_entrega':
            if donacion.estado_publicacion != Donacion.EstadoPublicacion.RESERVADA:
                messages.error(
                    request,
                    'Solo podés confirmar la entrega cuando la publicación está reservada.',
                )
                return redirect('donacion:verDonaciones', userId=request.user.pk)
            donacion.estado_publicacion = Donacion.EstadoPublicacion.ENTREGADA
            donacion.retirado = True
            _aplicar_visibilidad_feed(donacion)
            donacion.save(
                update_fields=['estado_publicacion', 'retirado', 'mostrar_en_feed']
            )
            _sync_escrituras_para_donacion(donacion)
            messages.success(
                request,
                'Marcaste la donación como entregada y se cerraron los chats.',
            )
            return redirect('donacion:donacion_chats', donacionId=donacion.pk)
        if accion == 'cancelar_reserva':
            if donacion.estado_publicacion != Donacion.EstadoPublicacion.RESERVADA:
                messages.error(request, 'La publicación no está reservada.')
                return redirect('donacion:verDonaciones', userId=request.user.pk)
            donacion.estado_publicacion = Donacion.EstadoPublicacion.ACTIVA
            donacion.reservado_con = None
            _aplicar_visibilidad_feed(donacion)
            donacion.save(
                update_fields=['estado_publicacion', 'reservado_con', 'mostrar_en_feed']
            )
            _sync_escrituras_para_donacion(donacion)
            messages.success(
                request,
                'Cancelaste la reserva. La donación volvió a estar disponible en el feed.',
            )
            return redirect('donacion:donacion_chats', donacionId=donacion.pk)
        if accion == 'reabrir':
            if donacion.estado_publicacion != Donacion.EstadoPublicacion.ENTREGADA:
                messages.error(request, 'Solo podés reabrir una publicación ya entregada.')
                return redirect('donacion:verDonaciones', userId=request.user.pk)
            donacion.estado_publicacion = Donacion.EstadoPublicacion.ACTIVA
            donacion.reservado_con = None
            donacion.retirado = False
            _aplicar_visibilidad_feed(donacion)
            donacion.save(
                update_fields=[
                    'estado_publicacion',
                    'reservado_con',
                    'retirado',
                    'mostrar_en_feed',
                ]
            )
            _sync_escrituras_para_donacion(donacion)
            messages.success(
                request,
                'Reabriste la publicación; volvió al feed y se desbloquearon los chats.',
            )
            return redirect('donacion:verDonaciones', userId=request.user.pk)


def _parse_json_dict(request):
    try:
        return json.loads(request.body.decode())
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


@login_required
@require_POST
def api_registrar_decision(request):
    data = _parse_json_dict(request)
    if not isinstance(data, dict):
        return JsonResponse({'ok': False, 'error': 'json_invalido'}, status=400)
    action = data.get('action')
    donacion_id = data.get('donacion_id')
    if action not in ('interes', 'pass') or donacion_id is None:
        return JsonResponse({'ok': False, 'error': 'parametros'}, status=400)
    try:
        donacion_id_int = int(donacion_id)
    except (TypeError, ValueError):
        return JsonResponse({'ok': False, 'error': 'parametros'}, status=400)
    donacion = get_object_or_404(Donacion, pk=donacion_id_int)
    if donacion.donador_id == request.user.pk:
        return JsonResponse({'ok': False, 'error': 'propio'}, status=403)
    if donacion.donador_id in _conjunto_usuarios_bloqueados_relacion(request.user):
        return JsonResponse({'ok': False, 'error': 'no_disponible'}, status=400)
    if donacion.retirado or not donacion.mostrar_en_feed:
        return JsonResponse({'ok': False, 'error': 'no_disponible'}, status=400)
    if donacion.estado_publicacion != Donacion.EstadoPublicacion.ACTIVA:
        return JsonResponse({'ok': False, 'error': 'no_disponible'}, status=400)
    tipo_nuevo = (
        DecisionDonacion.Tipo.INTERES
        if action == 'interes'
        else DecisionDonacion.Tipo.PASS
    )
    existente = DecisionDonacion.objects.filter(
        usuario=request.user, donacion=donacion
    ).first()
    if existente:
        if existente.tipo == DecisionDonacion.Tipo.INTERES and tipo_nuevo == DecisionDonacion.Tipo.PASS:
            return JsonResponse({'ok': False, 'error': 'ya_interesado'}, status=409)
        if existente.tipo == tipo_nuevo:
            if tipo_nuevo == DecisionDonacion.Tipo.INTERES:
                Conversacion.objects.get_or_create(donacion=donacion, interesado=request.user)
            return JsonResponse({'ok': True})
        existente.tipo = tipo_nuevo
        existente.save(update_fields=['tipo'])
    else:
        DecisionDonacion.objects.create(
            usuario=request.user, donacion=donacion, tipo=tipo_nuevo
        )
    if tipo_nuevo == DecisionDonacion.Tipo.INTERES:
        Conversacion.objects.get_or_create(donacion=donacion, interesado=request.user)
    return JsonResponse({'ok': True})


@login_required
@require_POST
def api_deshacer_pass(request):
    data = _parse_json_dict(request)
    if not isinstance(data, dict):
        return JsonResponse({'ok': False, 'error': 'json_invalido'}, status=400)
    donacion_id = data.get('donacion_id')
    if donacion_id is None:
        return JsonResponse({'ok': False, 'error': 'parametros'}, status=400)
    try:
        donacion_id_int = int(donacion_id)
    except (TypeError, ValueError):
        return JsonResponse({'ok': False, 'error': 'parametros'}, status=400)
    deleted, _ = DecisionDonacion.objects.filter(
        usuario=request.user,
        donacion_id=donacion_id_int,
        tipo=DecisionDonacion.Tipo.PASS,
    ).delete()
    if deleted:
        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False, 'error': 'no_encontrado'}, status=400)


@login_required
def modificarDonacion(request, donacionId):
    donacion = _donacion_del_usuario(request, donacionId)
    if donacion.estado_publicacion != Donacion.EstadoPublicacion.ACTIVA:
        messages.error(request, 'Solo podés modificar donaciones en estado activo.')
        return redirect('donacion:verDonaciones', userId=request.user.pk)
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
    if donacion.estado_publicacion != Donacion.EstadoPublicacion.ACTIVA:
        messages.error(request, 'Solo podés eliminar donaciones en estado activo.')
        return redirect('donacion:verDonaciones', userId=request.user.pk)
    if request.method == 'POST':
        donacion.delete()
        return redirect('donacion:verDonaciones', userId=request.user.pk)
    return render(request, 'donacion/eliminarDonacion.html', {'donacion': donacion})

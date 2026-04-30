(function () {
  var THRESHOLD = 96;
  var maxRotate = 14;
  var UNDO_MS = 8000;

  function flyOutCard(cardTop, direction, done) {
    cardTop.style.transition = 'transform 0.32s ease-out';
    var w = window.innerWidth;
    var target = direction === 'left' ? -w : w;
    var rot = direction === 'left' ? -maxRotate * 1.4 : maxRotate * 1.4;
    cardTop.style.transform =
      'translateX(' + target + 'px) rotate(' + rot + 'deg)';
    var ribbonNope = cardTop.querySelector('.dt-ribbon-nope');
    var ribbonLike = cardTop.querySelector('.dt-ribbon-like');
    if (ribbonNope) ribbonNope.style.opacity = direction === 'left' ? '1' : '0';
    if (ribbonLike) ribbonLike.style.opacity = direction === 'right' ? '1' : '0';
    cardTop.addEventListener(
      'transitionend',
      function (ev) {
        if (ev.propertyName !== 'transform') return;
        done();
      },
      { once: true }
    );
  }

  var elJson = document.getElementById('inicio-donaciones-json');
  var mount = document.getElementById('inicio-mount');
  if (!elJson || !mount) return;

  var decisionUrl = mount.dataset.decisionUrl || '';
  var deshacerPassUrl = mount.dataset.deshacerPassUrl || '';
  var csrfForm = document.getElementById('dt-csrf-form');
  var csrfInput = csrfForm ? csrfForm.querySelector('[name=csrfmiddlewaretoken]') : null;

  var items = [];
  try {
    items = JSON.parse(elJson.textContent);
  } catch (e) {
    mount.innerHTML =
      '<div class="dt-inicio-msg">No se pudieron cargar las donaciones.</div>';
    return;
  }

  var index = 0;
  var passUndoTimer = null;
  var currentToastEl = null;

  function esc(s) {
    var d = document.createElement('div');
    d.textContent = s == null ? '' : String(s);
    return d.innerHTML;
  }

  function csrfToken() {
    return csrfInput ? csrfInput.value : '';
  }

  function postJson(url, body) {
    return fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken(),
      },
      credentials: 'same-origin',
      body: JSON.stringify(body),
    }).then(function (res) {
      return res.text().then(function (text) {
        var parsed = {};
        if (text) {
          try {
            parsed = JSON.parse(text);
          } catch (e) {
            parsed = {};
          }
        }
        return { ok: res.ok, status: res.status, data: parsed };
      });
    });
  }

  function removeUndoToast() {
    if (passUndoTimer !== null) {
      clearTimeout(passUndoTimer);
      passUndoTimer = null;
    }
    if (currentToastEl && currentToastEl.parentNode) {
      currentToastEl.parentNode.removeChild(currentToastEl);
    }
    currentToastEl = null;
  }

  function showPassUndoToast(donationId, restoreIndex) {
    removeUndoToast();
    var toast = document.createElement('div');
    toast.className = 'dt-inicio-toast';
    toast.setAttribute('role', 'status');
    toast.innerHTML =
      '<p class="dt-inicio-toast-text">La descartaste.</p>' +
      '<button type="button" class="btn btn-sm btn-outline-light dt-inicio-toast-btn">' +
      'Deshacer</button>';
    document.body.appendChild(toast);
    currentToastEl = toast;

    passUndoTimer = setTimeout(function () {
      passUndoTimer = null;
      if (currentToastEl && currentToastEl.parentNode) {
        currentToastEl.parentNode.removeChild(currentToastEl);
      }
      currentToastEl = null;
    }, UNDO_MS);

    toast.querySelector('button').addEventListener('click', function () {
      removeUndoToast();
      postJson(deshacerPassUrl, { donacion_id: donationId }).then(function (r) {
        if (!r.ok) {
          alert('No se pudo deshacer. Intentá de nuevo.');
          return;
        }
        index = restoreIndex;
        renderDeck();
      });
    });
  }

  function cardHtml(item) {
    return (
      '<img src="' +
      esc(item.imagen) +
      '" alt="' +
      esc(item.nombre) +
      '" draggable="false">' +
      '<div class="dt-swipe-card-body">' +
      '<h2>' +
      esc(item.nombre) +
      '</h2>' +
      '<span class="dt-swipe-estado">' +
      esc(item.estado) +
      '</span>' +
      '<p>' +
      esc(item.descripcion) +
      '</p>' +
      '</div>' +
      '<div class="dt-swipe-ribbons" aria-hidden="true">' +
      '<span class="dt-ribbon dt-ribbon-nope">NOPE</span>' +
      '<span class="dt-ribbon dt-ribbon-like">ME INTERESA</span>' +
      '</div>'
    );
  }

  function renderEnd(message, showReloadLink) {
    removeUndoToast();
    var html = '<div class="dt-inicio-msg"><p>' + esc(message) + '</p>';
    if (showReloadLink) {
      html +=
        '<p style="margin-top:1rem;"><a href=".">Volver al inicio</a></p>';
    }
    html += '</div>';
    mount.innerHTML = html;
  }

  function bindDrag(cardTop, onSwipeLeft, onSwipeRight) {
    var startX = 0;
    var dx = 0;
    var ribbonNope = cardTop.querySelector('.dt-ribbon-nope');
    var ribbonLike = cardTop.querySelector('.dt-ribbon-like');

    function setTransform(x) {
      var rot = Math.max(-maxRotate, Math.min(maxRotate, x * 0.06));
      cardTop.style.transform = 'translateX(' + x + 'px) rotate(' + rot + 'deg)';
      var oNope = x < -28 ? Math.min(1, (-x - 28) / 80) : 0;
      var oLike = x > 28 ? Math.min(1, (x - 28) / 80) : 0;
      if (ribbonNope) ribbonNope.style.opacity = String(oNope);
      if (ribbonLike) ribbonLike.style.opacity = String(oLike);
    }

    function resetDrag() {
      cardTop.style.transition = 'transform 0.22s ease-out';
      setTransform(0);
      if (ribbonNope) ribbonNope.style.opacity = '0';
      if (ribbonLike) ribbonLike.style.opacity = '0';
      setTimeout(function () {
        cardTop.style.transition = '';
      }, 230);
    }

    function onPointerDown(e) {
      if (e.button !== undefined && e.button !== 0) return;
      startX = e.clientX;
      dx = 0;
      cardTop.style.transition = '';
      cardTop.setPointerCapture(e.pointerId);
    }

    function onPointerMove(e) {
      if (!cardTop.hasPointerCapture(e.pointerId)) return;
      dx = e.clientX - startX;
      setTransform(dx);
    }

    function onPointerUp(e) {
      if (!cardTop.hasPointerCapture(e.pointerId)) return;
      cardTop.releasePointerCapture(e.pointerId);
      if (dx < -THRESHOLD) {
        onSwipeLeft();
      } else if (dx > THRESHOLD) {
        onSwipeRight();
      } else {
        resetDrag();
      }
    }

    cardTop.addEventListener('pointerdown', onPointerDown);
    cardTop.addEventListener('pointermove', onPointerMove);
    cardTop.addEventListener('pointerup', onPointerUp);
    cardTop.addEventListener('pointercancel', onPointerUp);

    return { resetDrag: resetDrag };
  }

  function renderDeck() {
    if (items.length === 0) {
      renderEnd(
        'Todavía no hay donaciones de otros usuarios disponibles. Volvé más tarde o pedile a alguien que publique una.',
        false
      );
      return;
    }

    if (index >= items.length) {
      renderEnd(
        'No hay más donaciones por ahora. Cuando haya objetos nuevos, aparecerán acá.',
        true
      );
      return;
    }

    mount.innerHTML = '';

    var wrap = document.createElement('div');
    wrap.className = 'dt-swipe-stack-wrap';

    if (index + 1 < items.length) {
      var under = document.createElement('article');
      under.className = 'dt-swipe-card dt-swipe-card--under';
      under.setAttribute('aria-hidden', 'true');
      under.innerHTML = cardHtml(items[index + 1]);
      wrap.appendChild(under);
    }

    var top = document.createElement('article');
    top.className = 'dt-swipe-card dt-swipe-card--top';
    top.innerHTML = cardHtml(items[index]);
    wrap.appendChild(top);

    mount.appendChild(wrap);

    var ctrl = document.createElement('div');
    ctrl.className = 'dt-swipe-controls';
    ctrl.innerHTML =
      '<button type="button" class="dt-swipe-btn dt-swipe-btn-nope" aria-label="Pasar">✕</button>' +
      '<button type="button" class="dt-swipe-btn dt-swipe-btn-like" aria-label="Me interesa">♥</button>';
    mount.appendChild(ctrl);

    function advanceAfterInteres() {
      removeUndoToast();
      index += 1;
      renderDeck();
    }

    var dragFns = bindDrag(top, swipeLeftCommitted, swipeRightCommitted);

    function swipeLeftCommitted() {
      var id = items[index].id;
      var restoreIndex = index;
      postJson(decisionUrl, { donacion_id: id, action: 'pass' }).then(function (r) {
        if (!r.ok) {
          dragFns.resetDrag();
          alert(
            r.data && r.data.error
              ? 'No se pudo guardar. Probá de nuevo.'
              : 'No se pudo guardar. Probá de nuevo.'
          );
          return;
        }
        flyOutCard(top, 'left', function () {
          index += 1;
          renderDeck();
          showPassUndoToast(id, restoreIndex);
        });
      });
    }

    function swipeRightCommitted() {
      var id = items[index].id;
      postJson(decisionUrl, { donacion_id: id, action: 'interes' }).then(function (r) {
        if (!r.ok) {
          dragFns.resetDrag();
          alert(
            r.data && r.data.error
              ? 'No se pudo guardar. Probá de nuevo.'
              : 'No se pudo guardar. Probá de nuevo.'
          );
          return;
        }
        flyOutCard(top, 'right', advanceAfterInteres);
      });
    }

    ctrl.querySelector('.dt-swipe-btn-nope').addEventListener('click', function () {
      swipeLeftCommitted();
    });
    ctrl.querySelector('.dt-swipe-btn-like').addEventListener('click', function () {
      swipeRightCommitted();
    });
  }

  renderDeck();
})();

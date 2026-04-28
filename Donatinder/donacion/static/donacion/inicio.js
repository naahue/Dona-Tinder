(function () {
  const THRESHOLD = 96;
  const maxRotate = 14;

  function flyOutCard(cardTop, direction, done) {
    cardTop.style.transition = 'transform 0.32s ease-out';
    const w = window.innerWidth;
    const target = direction === 'left' ? -w : w;
    const rot = direction === 'left' ? -maxRotate * 1.4 : maxRotate * 1.4;
    cardTop.style.transform =
      'translateX(' + target + 'px) rotate(' + rot + 'deg)';
    const ribbonNope = cardTop.querySelector('.dt-ribbon-nope');
    const ribbonLike = cardTop.querySelector('.dt-ribbon-like');
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

  const elJson = document.getElementById('inicio-donaciones-json');
  const mount = document.getElementById('inicio-mount');
  if (!elJson || !mount) return;

  let items = [];
  try {
    items = JSON.parse(elJson.textContent);
  } catch (e) {
    mount.innerHTML =
      '<div class="dt-inicio-msg">No se pudieron cargar las donaciones.</div>';
    return;
  }

  let index = 0;

  function esc(s) {
    const d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
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
    let html = '<div class="dt-inicio-msg"><p>' + esc(message) + '</p>';
    if (showReloadLink) {
      html +=
        '<p style="margin-top:1rem;"><a href=".">Volver al inicio</a></p>';
    }
    html += '</div>';
    mount.innerHTML = html;
  }

  function bindDrag(cardTop, onSwipeLeft, onSwipeRight) {
    let startX = 0;
    let dx = 0;
    const ribbonNope = cardTop.querySelector('.dt-ribbon-nope');
    const ribbonLike = cardTop.querySelector('.dt-ribbon-like');

    function setTransform(x) {
      const rot = Math.max(-maxRotate, Math.min(maxRotate, x * 0.06));
      cardTop.style.transform = 'translateX(' + x + 'px) rotate(' + rot + 'deg)';
      const oNope = x < -28 ? Math.min(1, (-x - 28) / 80) : 0;
      const oLike = x > 28 ? Math.min(1, (x - 28) / 80) : 0;
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
        flyOutCard(cardTop, 'left', onSwipeLeft);
      } else if (dx > THRESHOLD) {
        flyOutCard(cardTop, 'right', onSwipeRight);
      } else {
        resetDrag();
      }
    }

    cardTop.addEventListener('pointerdown', onPointerDown);
    cardTop.addEventListener('pointermove', onPointerMove);
    cardTop.addEventListener('pointerup', onPointerUp);
    cardTop.addEventListener('pointercancel', onPointerUp);
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

    const wrap = document.createElement('div');
    wrap.className = 'dt-swipe-stack-wrap';

    if (index + 1 < items.length) {
      const under = document.createElement('article');
      under.className = 'dt-swipe-card dt-swipe-card--under';
      under.setAttribute('aria-hidden', 'true');
      under.innerHTML = cardHtml(items[index + 1]);
      wrap.appendChild(under);
    }

    const top = document.createElement('article');
    top.className = 'dt-swipe-card dt-swipe-card--top';
    top.innerHTML = cardHtml(items[index]);
    wrap.appendChild(top);

    mount.appendChild(wrap);

    const ctrl = document.createElement('div');
    ctrl.className = 'dt-swipe-controls';
    ctrl.innerHTML =
      '<button type="button" class="dt-swipe-btn dt-swipe-btn-nope" aria-label="Pasar">✕</button>' +
      '<button type="button" class="dt-swipe-btn dt-swipe-btn-like" aria-label="Me interesa">♥</button>';
    mount.appendChild(ctrl);

    function advance() {
      index += 1;
      renderDeck();
    }

    bindDrag(top, advance, advance);

    ctrl.querySelector('.dt-swipe-btn-nope').addEventListener('click', function () {
      flyOutCard(top, 'left', advance);
    });
    ctrl.querySelector('.dt-swipe-btn-like').addEventListener('click', function () {
      flyOutCard(top, 'right', advance);
    });
  }

  renderDeck();
})();

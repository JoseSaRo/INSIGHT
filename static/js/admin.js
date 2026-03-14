$(document).ready(function () {
  console.log("✅ admin.js cargado correctamente");

  const sidenavEl = $('.sidenav');
  const gridEl = $('.grid');
  const SIDENAV_ACTIVE_CLASS = 'sidenav--active';
  const GRID_NO_SCROLL_CLASS = 'grid--noscroll';

  // 🔁 Alternador de clases
  function toggleClass(el, className) {
    if (el.hasClass(className)) {
      el.removeClass(className);
    } else {
      el.addClass(className);
    }
  }

  // 🍔 Mostrar/Ocultar menú lateral
  function setMenuClickListener() {
    $('.header__menu').on('click', function () {
      console.log('🍔 clicked menu icon');
      toggleClass(sidenavEl, SIDENAV_ACTIVE_CLASS);
      toggleClass(gridEl, GRID_NO_SCROLL_CLASS);
    });
  }

  // ❌ Cerrar menú lateral
  function setSidenavCloseListener() {
    $('.sidenav__brand-close').on('click', function () {
      toggleClass(sidenavEl, SIDENAV_ACTIVE_CLASS);
      toggleClass(gridEl, GRID_NO_SCROLL_CLASS);
    });
  }

  // 😎 Dropdown del avatar de usuario
  function setUserDropdownListener() {
    $('.header__avatar').on('click', function () {
      const dropdown = $(this).children('.dropdown');
      toggleClass(dropdown, 'dropdown--active');
    });
  }

  // 🔽 Expansión de submenús (ahora con delegación robusta)
  function setSidenavListeners() {
    const SUBHEADING_OPEN_CLASS = 'navList__subheading--open';
    const SUBLIST_HIDDEN_CLASS = 'subList--hidden';
  
    $(document).on('click', '.navList__subheading', function () {
      const $this = $(this);
      const parentLi = $this.closest('li');
      const subList = parentLi.find('.subList').first(); // buscamos dentro del <li>
  
      console.log("Subcategoría clickeada:", $this.text());
  
      $this.toggleClass(SUBHEADING_OPEN_CLASS);
      subList.toggleClass(SUBLIST_HIDDEN_CLASS);
    });
  }

  // 🔁 Restaurar layout si se cambia el tamaño de pantalla
  function addResizeListeners() {
    $(window).resize(function () {
      const width = window.innerWidth;
      if (width > 750) {
        sidenavEl.removeClass(SIDENAV_ACTIVE_CLASS);
        gridEl.removeClass(GRID_NO_SCROLL_CLASS);
      }
    });
  }

  // 📊 Inicializa DataTables
  function initDataTables() {
    console.log("Inicializando DataTables...");
    $('#usuariosTable').DataTable({
      language: {
        url: "https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json"
      }
    });
  }

  // 👁️ Mostrar/ocultar contraseñas
  function setPasswordToggle() {
    $('.toggle-password').on('click', function () {
      const targetId = $(this).data('target');
      const passwordInput = $('#' + targetId);
      const icon = $(this).find('i');

      if (passwordInput.attr('type') === 'password') {
        passwordInput.attr('type', 'text');
        icon.removeClass('fa-eye').addClass('fa-eye-slash');
      } else {
        passwordInput.attr('type', 'password');
        icon.removeClass('fa-eye-slash').addClass('fa-eye');
      }
    });
  }

  // ▶️ Inicializa todo
  addResizeListeners();
  setSidenavListeners();
  setUserDropdownListener();
  setMenuClickListener();
  setSidenavCloseListener();
  initDataTables();
  setPasswordToggle();
});

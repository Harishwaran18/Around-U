(function () {
    'use strict';

    const navbar = document.getElementById('navbar');
    const navToggle = document.getElementById('navToggle');
    const navLinks = document.getElementById('navLinks');

    if (navToggle && navLinks) {
        navToggle.addEventListener('click', function () {
            const isOpen = navLinks.classList.toggle('is-open');
            navToggle.setAttribute('aria-expanded', String(isOpen));
        });

        navLinks.addEventListener('click', function (event) {
            if (event.target.tagName === 'A') {
                navLinks.classList.remove('is-open');
                navToggle.setAttribute('aria-expanded', 'false');
            }
        });
    }

    if (navbar) {
        const syncNavbar = function () {
            navbar.classList.toggle('is-scrolled', window.scrollY > 8);
        };
        syncNavbar();
        window.addEventListener('scroll', syncNavbar, { passive: true });
    }

    document.querySelectorAll('.alert-close').forEach(function (button) {
        button.addEventListener('click', function () {
            const alert = button.closest('.alert');
            if (alert) alert.remove();
        });
    });

    document.querySelectorAll('.flash-messages .alert').forEach(function (alertEl) {
        window.setTimeout(function () {
            alertEl.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            alertEl.style.opacity = '0';
            alertEl.style.transform = 'translateX(100%)';
            window.setTimeout(function () {
                alertEl.remove();
            }, 400);
        }, 6000);
    });

    document.querySelectorAll('form[data-confirm]').forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!window.confirm(form.dataset.confirm)) {
                event.preventDefault();
            }
        });
    });

    document.querySelectorAll('form[data-auto-submit] select').forEach(function (select) {
        select.addEventListener('change', function () {
            select.form.submit();
        });
    });
})();

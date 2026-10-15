(function () {
  var side = document.getElementById('sidebar');
  var toggle = document.getElementById('side-toggle');
  if (side && toggle) toggle.addEventListener('click', function () { side.classList.toggle('open'); });

  // Ask for confirmation on elements marked with data-confirm (forms or buttons).
  document.addEventListener('submit', function (e) {
    var msg = e.target.getAttribute('data-confirm');
    if (msg && !window.confirm(msg)) e.preventDefault();
  });
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('button[data-confirm]');
    if (btn && !window.confirm(btn.getAttribute('data-confirm'))) e.preventDefault();
  });
})();

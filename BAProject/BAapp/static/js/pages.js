$(document).ready(function() {
  $('.datepicker').datepicker({
    format: 'dd/mm/yyyy',
    showClearBtn: true,
    i18n: {
      weekdaysAbbrev: ['D','L','M','X','J','V','S'],
      months:	
      [
        'Enero',
        'Febrero',
        'Marzo',
        'Abril',
        'Mayo',
        'Junio',
        'Julio',
        'Agosto',
        'Septiembre',
        'Octubre',
        'Noviembre',
        'Diciembre'
      ],
      monthsShort:
      [
        'Ene',
        'Feb',
        'Mar',
        'Abr',
        'May',
        'Jun',
        'Jul',
        'Ago',
        'Sep',
        'Oct',
        'Nov',
        'Dic'
      ],
      weekdays:
      [
        'Domingo',
        'Lunes',
        'Martes',
        'Miercoles',
        'Jueves',
        'Viernes',
        'Sábado'
      ],
      weekdaysShort:
      [
        'Dom',
        'Lun',
        'Mar',
        'Mié',
        'Jue',
        'Vie',
        'Sáb'
      ],
      cancel: 'Cancelar',
      clear: 'Limpiar'
    }
  });
});

function showChangeEstados(){
  $('.auxSem').show();
  $("#nego").hide();
  $("#mostrarChgEstSem").hide();
  $("#confirmarChgEstSem").show();
};

$(document).ready(function () {
  $(".contain").fadeOut("fast", function() {
    $(this).remove();
  });
});

function addBg(url) {
  var body = $("body");
  body.css('background-image', 'url('+ url +')');
}
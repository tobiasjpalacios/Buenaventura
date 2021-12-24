function openModalAlerta(){
    $.ajax({
      type: 'POST',
      url: "{% url 'detalleAlerta' %}",
      data: {csrfmiddlewaretoken: '{{ csrf_token }}'},
      success: function (data) { 
        $("#modalAlerta").html(data);
        $('#alerta').modal('open'); 
      },
      error: function (response) {
          console.log("Error")
      }
    })
  };

  function sendAlertaModal(){
    var selected = new Array();
    $('#tableAlertas input[type="checkbox"]:checked').each(function() {
        selected.push($(this).attr('data-id'));
    });    
    var jsonText = JSON.stringify(selected);
    var titulo = document.getElementById("tituloAlerta").value;
    if (titulo === ""){
      M.toast({html: 'Error! El Titulo no puede estar en blanco.'});
    } else {
      var descri = document.getElementById("descriAlerta").value;
      var categoria = document.getElementById("selectModalAlert").value;
      $.ajax({
          url: "{% url 'sendAlertaModal' %}",
          type: 'POST',
          data: {'jsonText':jsonText,'titulo':titulo,'descri':descri,'categoria':categoria,
            csrfmiddlewaretoken: '{{ csrf_token }}'},
          success: function(data){             
              M.toast({html: data.result});
              if (data.estado){
                $('#alerta').modal('close');
              };   
          },
          error: function (data) {
              console.log(data.result)
          }
      });
    };
  };

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
          'En',
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
$(document).ready(function(){
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
    $('.tooltipped').tooltip();
    $('select').formSelect();
    $('.fixed-action-btn').floatingActionButton({
    hoverEnabled: true
    });
    $("#form thead tr th").each(function(index){
        if ($(this).text() != "Operaciones" && $(this).text() != "Ver más"){
            headers.push($(this).text().toLowerCase().replace(/\s+/g, '_'));
        }
    })

    allTDLinebreak();

    // var btn_sm_1 = document.getElementById('btn-sm-1');
    
    // $(btn_sm_1).each(function () {
    //   $('[id="' + this.id + '"]:gt(0)').remove();
    // });
});

var modifyWasClicked = false;

function mScrollTo(id) {
    var elementPosition = $(id).offset().top;
    var navHeight = $("nav").height();

    $('html,body').animate({
      scrollTop: elementPosition - navHeight - 100
    }, 700);
}

$("#btnScrollTop").on('click', function() {
$('html,body').animate({
    scrollTop: 0
}, 700);
});

$("#btnScrollBottom").on('click', function() {
$('html,body').animate({
    scrollTop: $(document).height()
}, 700);
});

function contadoTasa(aggId) {
    var tipo_pago = document.getElementById("tp"+aggId);
    var tasa = document.getElementById("tas"+aggId);
    if (tipo_pago != null) {
      var selectedText = tipo_pago.options[tipo_pago.selectedIndex].text;
      if (selectedText.toLowerCase() === "contado") {
        tasa.disabled = true;
        tasa.value = 0;
      }
      else {
        tasa.disabled = false;
      }
      $('select').formSelect();
    }
}

var sm = false

function showMore(n) {

    var tdShow = $("td.show"+n);
    var thShow = $("th.show"+n);
    var tdNotShow = $("td.not-show"+n);
    var thNotShow = $("th.not-show"+n);
    // var iAnim = $("i.i"+n+"");

    thShow.toggleClass("show"+n+" not-show"+n);
    tdShow.toggleClass("show"+n+" not-show"+n);
    tdNotShow.toggleClass("not-show"+n+" show"+n);
    thNotShow.toggleClass("not-show"+n+" show"+n);
    // iAnim.toggleClass("rotate");

    if (n==0) {
      sm = !sm
    }

}

// funcion vista cliente
var vistaCliente = false;

function toggleClientView(n) {

  var clientView = $(".clientView");
  var clientViewSM = $(".clientViewSM");

  if($("#client-view-sw").is(":checked")) {

    clientView.show();
    clientViewSM.hide();
    $("#form-table-div").hide();
    $("#send-prop-btn").attr('disabled', true);

    vistaCliente = true;

  }
  else {

    clientView.css('display', '');
    clientViewSM.show();
    if (modifyWasClicked) {
      $("#form-table-div").show();
    }
    if (!isAccepted && !isCanceled) {
      $("#form-table-div").show();
    }
    $("#send-prop-btn").removeAttr('disabled');

    vistaCliente = false;

  }

  alertAnimation();

}

function alertAnimation() {
  var materialAlert = $(".materialert.error");

  if (vistaCliente) {
    materialAlert.css("display", "flex");
    materialAlert.css("animation", "alertAnimDown .5s ease 0s 1 normal forwards");
  }
  else {
    materialAlert.css("animation", "alertAnimUp .5s ease 0s 1 normal forwards");
    setTimeout(
      function() {
        materialAlert.css("display", "none");
      }
    , 500);
  }
}

function closeAlert(id) {
  $(id).css("display", "none");
}

// funcion editar despues de negocio confirmado

function addTable() {
    $("#modifyProp").hide();
    $("#form-table-div").detach().appendTo("#table-destination");
    $("#form-table-div").show();
    modifyWasClicked = true;
}

  function addTables(n, isBeforeFechaCierre) {
    if (!isBeforeFechaCierre) {
      $("#div-table-"+n).detach().appendTo("#table-destination");
      $("#div-table-"+n).show();
    }
}

$("#client-view-sw").change(function() {

  $(".card").toggleClass("tableClientView");
  $(".card-title").toggleClass("tableClientView");
  $(".card-action").toggleClass("tableClientView");
  $(".circle-container").toggle("display");
  $(".data-table").toggleClass("tableClientView");
  $(".prop-creator-name").toggleClass("tableClientView grey-text text-darken-3");
  $(".prop-date").toggleClass("tableClientView grey-text text-darken-4");
  $(".w1").toggle("display");
  $(".w2").toggle("display");
  $(".w2-hide").toggle("display");
  $(".w3").toggle("display");
  
});

function allTDLinebreak() {
  $("td:first-child").each(function() {
    var elem = $(this);
    var text = elem.text();
    if (!(elem.parent().attr('id') == 'extra')) {
      var textArray = text.split(" ");
      var i = 1;
      for (word in textArray) {
        if (i % 4 == 0) {
          textArray[word] = textArray[word] + "<br/>";
        }
        i++;
      }
      text = textArray.join(" ");
      elem.html(text);
    }
  })
}

//

setTimeout(function() {
  $(".blink_text").fadeIn();
}, 10000);

$(window).on('load', function () {
  $(".contain").fadeOut("fast", function() {
    $(this).remove();
  });
});

// table_edit

function articuloDatalist() {
  var artDatalist = document.getElementById("artDatalist");
  for (var i = 0; i < arts_data.length; i++) {
    var option = document.createElement('option');
    option.innerText = arts_data[i].empresa__nombre_comercial;
    option.setAttribute('value',''+arts_data[i].marca + ' ' + arts_data[i].ingrediente);
    option.setAttribute('id',''+arts_data[i].id);
    artDatalist.appendChild(option);        
  }
}

function resetIngredientesDatalist() {
  var input = document.getElementById("artSearch").value;
  if (!isEmpty(input)) {
    var datalist = document.getElementById("artDatalist");
    datalist.innerHTML = " ";
    for (var i = 0; i < arts_data.length; i++) {
      var option = document.createElement('option');
      option.innerText = arts_data[i].empresa__nombre_comercial;
      option.setAttribute('value',''+arts_data[i].marca + ' ' + arts_data[i].ingrediente);
      option.setAttribute('id',''+arts_data[i].id);
      datalist.appendChild(option);
    }
  }
}
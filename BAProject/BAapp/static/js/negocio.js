$(document).ready(function(){
    $('.datepicker').datepicker({
        format: 'dd/mm/yyyy',
        showClearBtn: true,
        i18n: {
          months: ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"],
          monthsShort: ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Set", "Oct", "Nov", "Dic"],
          weekdays: ["Domingo","Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"],
          weekdaysShort: ["Dom","Lun", "Mar", "Mie", "Jue", "Vie", "Sab"],
          weekdaysAbbrev: ["D","L", "M", "M", "J", "V", "S"]
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

    // var btn_sm_1 = document.getElementById('btn-sm-1');
    
    // $(btn_sm_1).each(function () {
    //   $('[id="' + this.id + '"]:gt(0)').remove();
    // });
});

var modifyWasClicked = false;

function mScrollTo(id) {
  console.log(id)
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
    $(".card.history-card").addClass("vista-cliente");
    $(".circle-neg").addClass("vista-cliente");

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
    $(".card.history-card").removeClass("vista-cliente");
    $(".circle-neg").removeClass("vista-cliente");

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
    vAlignCircle(0);
}

function addTables(n, isBeforeFechaCierre) {
  if (!isBeforeFechaCierre) {
    $("#div-table-"+n).detach().appendTo("#table-destination");
    $("#div-table-"+n).show();
  }
}

// $("#client-view-sw").change(function() {

//   // $(".card").toggleClass("tableClientView");
//   // $(".card-title").toggleClass("tableClientView");
//   // $(".card-action").toggleClass("tableClientView");
//   // $(".circle-container").toggle("display");
//   // $(".data-table").toggleClass("tableClientView");
//   // $(".prop-creator-name").toggleClass("tableClientView grey-text text-darken-3");
//   // $(".prop-date").toggleClass("tableClientView grey-text text-darken-4");
//   // $(".w1").toggle("display");
//   // $(".w2").toggle("display");
//   // $(".w2-hide").toggle("display");
//   // $(".w3").toggle("display");
  
// });

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

// table_edit

function articuloDatalist(n) {
  var artDatalist = document.getElementById("artDatalist"+n);
  for (var i = 0; i < arts_data.length; i++) {
    var option = document.createElement('option');
    option.setAttribute('value',''+arts_data[i].ingrediente + ' ' + arts_data[i].empresa__nombre_comercial);
    option.setAttribute('id',''+arts_data[i].id);
    artDatalist.appendChild(option);        
  }
}

function resetIngredientesDatalist(n) {
  var input = document.getElementById("artSearch"+n).value;
  if (!isEmpty(input)) {
    var datalist = document.getElementById("artDatalist"+n);
    datalist.innerHTML = " ";
    for (var i = 0; i < arts_data.length; i++) {
      var option = document.createElement('option');
      option.setAttribute('value',''+arts_data[i].ingrediente + ' ' + arts_data[i].empresa__nombre_comercial);
      option.setAttribute('id',''+arts_data[i].id);
      datalist.appendChild(option);
    }
  }
}

function vAlignCircle(n) {
  var parentHeight = $("#card" + n).height();
  var childHeight = $("#circle" + n).height();
  var offset = childHeight / 4;
  var marginTop = ((parentHeight - childHeight) / 2) + offset;
  $("#circle" + n).css('margin-top', marginTop);
}

function getArtId(n) {
  var artSearchInput = $("#artSearch"+n).val();
  var artId = parseInt($('#artDatalist'+n+' option[value="' + artSearchInput +'"]').attr("id"));
  return artId;
}

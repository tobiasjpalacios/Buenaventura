$(document).ready(function(){
  $('select').formSelect();
  $('.tooltipped').tooltip();
  $('.scrollspy').scrollSpy();
  $('.collapsible').collapsible();
  $('.fixed-action-btn').floatingActionButton();
  $('.modal').modal();
  $('.logis').hide();
  $('#ocultar').hide();
  $('#campo').hide();

  $('#mostrar').click(function(){
    $('#ocultar').show();
    $('.logistica').hide();
    $('#mostrar').hide();
    $('.logis').show();

  });

  $('#ocultar').click(function(){
      $('.logis').hide();
      $('.logistica').show();
      $('#ocultar').hide();
      $('#mostrar').show();
  });  

  $('input#input_text, textarea#textarea2').characterCounter();

  filtrar();
});

function searchBuscadorNegocio(){ 
    var value = $("#inputBuscadorNegocio").val().toLowerCase();
    $("#tableNegocios tr").filter(function() {
      $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
    });
};

// function selTipoFecha(){
//   var x = $('#selectTipoFecha').val();
//   y = document.getElementById("divFechasParam");
//   if (x == "0"){
//     y.style.display = "none";
//   } else {
//     y.style.display = "block";
//   }
// }

// esta funcion arregla los problemas relacionos con los multiple options de los filtros.
// todavia hay un "error", que cuando se actualiza un selected, se cierran las opciones.

function multipleOptionFirstItem(id, select, varId, todos, counter) {
  if (varId.length > 1 && varId[0] == "todos") {
    if (counter < 1) {
      todos.prop('selected', false);
      select.formSelect();
      counter++
    }
    else {
      $('#'+id+' > option').each(function() {
        if ($(this).val() != "todos") {
          $(this).prop('selected', false);
        }
        select.formSelect();
        counter=0
      })
    }
  }

  if (varId.length == 0) {
    todos.prop('selected', 'selected');
    select.formSelect();
  }

  return counter;
}

var i = 0
$('#selectVendedores').on('change', function(e) {

  var select = $(this);
  var vendedores = select.val();
  var todos = select.find('option:eq(0)');

  var fun = multipleOptionFirstItem('selectVendedores', select, vendedores, todos, i);
  i = fun;

});

var o = 0
$('#selectEstados').on('change', function(e) {

  var select = $(this);
  var estados = select.val();
  var todos = select.find('option:eq(0)');

  var fun = multipleOptionFirstItem('selectEstados', select, estados, todos, o);
  o = fun;

});

// scroll con filtro y head fijos

var $a = $("#fixedForScroll");

// table
var tableOffset = $("#tableNegocios").offset().top;
var $header = $("#tableNegocios > thead");
var $fixedHeader = $("#headerFixed").append($header.clone());
var headerWidth = $header.width()

// filter
var filterOffset = $("#navFiltro > div").offset().top;
var $fixedFilter = $("#filtroFixed");
var filterHeight = $("#navFiltro").height();
var filterWidth = $("#navFiltro").width();

// nav
var nav = $("nav");
var navHeight = nav.height();

$a.css({
  top:navHeight+"px"
});
$fixedFilter.css({
  width: filterWidth+"px"
});
$fixedHeader.css({
  width: filterWidth+"px"
});

var screenWidth = $(window).width();

// if (screenWidth > 992) {
//   $(window).bind("scroll", function() {
//     var offset = $(this).scrollTop();
  
//     if (offset >= tableOffset && $fixedHeader.is(":hidden")) {
//       $filterClone = $("#navFiltro > div").detach();
//       $fixedFilter = $("#filtroFixed").append($filterClone);
  
//       $.each($header.find('tr > th'), function(ind, val) {
//         var original_width = $(val).width();
//         $($fixedHeader.find('tr > th')[ind]).width(original_width);
//       });
  
//       $("#fixedForScroll").slideDown("fast");
//     }
//     else if (offset < tableOffset) {
//       var filterClone = $("#filtroFixed > div").detach();
//       $("#navFiltro").append(filterClone);
  
//       $("#fixedForScroll").slideUp("fast");
//     }
//   });
// }

// limpia filtros

function limpiarFiltros() {
  var $idDeNeg = $("#idDeNeg"); 
  var $fechaDesde = $("#fechaDesde");
  var $fechaHasta = $("#fechaHasta");
  var $inputBuscador = $("#inputBuscadorNegocio");

  $idDeNeg.val("");
  $fechaDesde.val("");
  $fechaHasta.val("");
  $inputBuscador.val("");

  $("#selectVendedores option[value='todos']").prop('selected', true).change();
  $("#selectEstados option[value='todos']").prop('selected', true).change();
  $("#selectTipo option[value='todos']").prop('selected', true).change();
  $("#selectTipo").formSelect();

  filtrar();
}
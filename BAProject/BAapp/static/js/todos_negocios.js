  $(document).ready(function(){
    $('select').formSelect();
  });

  $(document).ready(function(){
    $('.datepicker').datepicker();
  });

  $(document).ready(function() {
    $('input#input_text, textarea#textarea2').characterCounter();
  });
      
  function searchBuscadorNegocio(){ 
      var value = $("#inputBuscadorNegocio").val().toLowerCase();
      $("#tableNegocios tr").filter(function() {
        $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
      });
  };

  function selTipoFecha(){
    var x = $('#selectTipoFecha').val();
    y = document.getElementById("divFechasParam");
    if (x == "0"){
      y.style.display = "none";
    } else {
      y.style.display = "block";
    }
  }

  $(document).ready(function(){
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
});

// estas "funciones" arreglan los problemas relacionos con los multiple options de los filtros.
// todavia hay un "error", que cuando se actualiza un selected, se cierran las opciones.

var i = 0
$('#selectVendedores').on('change', function(e) {

  var select = $(this);
  var vendedores = select.val();
  var todos = select.find('option:eq(0)');

  if (vendedores.length > 1 && vendedores[0] == "todos") {
    if (i < 1) {
      todos.prop('selected', false);
      select.formSelect();
      i++
    }
    else {
      $('#selectVendedores > option').each(function() {
        if ($(this).val() != "todos") {
          $(this).prop('selected', false);
        }
        select.formSelect();
        i=0
      })
    }
  }

  if (vendedores.length == 0) {
    todos.prop('selected', 'selected');
    select.formSelect();
  }

});

var o = 0
$('#selectEstados').on('change', function(e) {

  var select = $(this);
  var estados = select.val();
  var todos = select.find('option:eq(0)');

  if (estados.length > 1 && estados[0] == "todos") {
    if (o < 1) {
      todos.prop('selected', false);
      select.formSelect();
      o++
    }
    else {
      $('#selectEstados > option').each(function() {
        if ($(this).val() != "todos") {
          $(this).prop('selected', false);
        }
        select.formSelect();
        o=0
      })
    }
  }

  if (estados.length == 0) {
    todos.prop('selected', 'selected');
    select.formSelect();
  }

});
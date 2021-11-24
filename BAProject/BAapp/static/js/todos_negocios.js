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

  function detalleNegocio(idProp){
    $.ajax({
      type: 'POST',
      url: "{% url 'detalleNegocio' %}",
      data: {'idProp':idProp,
      csrfmiddlewaretoken: '{{ csrf_token }}'},
      success: function (data) {
        $("#modalNegocio").html(data);
        $('#modalDetalleNegocio').modal('open'); 
      },
      error: function (response) {
          console.log("Error")
      }
    })
  };

  function detalleArticuloNegocio(idItem, funOrig){
    $.ajax({
      type: 'POST',
      url: "{% url 'detalleItem' %}",
      data: {'idItem':idItem,
      csrfmiddlewaretoken: '{{ csrf_token }}'},
      success: function (data) {
        $("#modalNegocio").html(data);
        $('#modalDetalleNegocio').modal('open');
      },
      error: function (response) {
          console.log("Error")
      }
    })
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

  function filtrar(){
    var errores = 0;
    var vendedores = $('#selectVendedores').val();
    var vendedor = JSON.stringify(vendedores);
    if(vendedor.length <= 2){
      M.toast({html: 'Error! El filtro Vendedor no puede estar en blanco.'});
      errores = 1;    
    };
    var estaV = vendedores.includes("todos");
    if (estaV){
        vendedor = "todos";
    };
    var estados = $('#selectEstados').val();
    var estado = JSON.stringify(estados);
    if (estado.length <= 2){
        M.toast({html: 'Error! El filtro Estado no puede estar en blanco.'});
        errores = 1;
    }
    var estaE = estados.includes("todos");
    if (estaE){
        estado = "todos";
    };
    var tipo = $('#selectTipo').val();    
    var tipoFecha = $('#selectTipoFecha').val();
    var fechaDesde = $('#fechaDesde').val();
    var fechaHasta = $('#fechaHasta').val();
    if (tipoFecha != "0"){
        if (fechaDesde === ""){
          M.toast({html: 'Error! "Fecha Desde" no puede estar en blanco.'});
          errores = 1;
        };
        if (fechaHasta === ""){
          M.toast({html: 'Error! "Fecha Hasta" no puede estar en blanco.'});
          errores = 1;
        };    
    };
    if (errores == 0){
      $.ajax({
          url: "{% url 'filtrarNegocios' %}",
          type: 'POST',
          data: {'vendedor':vendedor,'estado':estado,'tipo':tipo,
              'tipoFecha':tipoFecha,'fechaDesde':fechaDesde, 'fechaHasta':fechaHasta,
              csrfmiddlewaretoken: '{{ csrf_token }}'},
          success: function(data){ 
            $('#infoTabla').html(data);
          },
          error: function (data) {
              console.log(data)
          }
      });
    };
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
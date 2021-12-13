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
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
          var header = $(this).text().toLowerCase().replace(/\s+/g, '_')
          if (["_tasa_lightbulb_outline_", "_tasa_"].indexOf(header) !== -1) { // rancio
            header = 'tasa';
          }
          headers.push(header);
      }
  })

  $('.responsive-table').each(function() {
    var $table = $(this).find('table');
    var $headerCells = $table.find('thead tr th:not(.ignore, .ignore-op)');
    var $dataCells = $table.find('tbody tr td:not(.ignore, .ignore-op)');
    var columnCount = $headerCells.length;

    $headerCells.each(function(index) {
      if (index % columnCount >= showColumns) {
        $(this).addClass('hide-column');
      }
    })

    $dataCells.each(function(index) {
      if (index % columnCount >= showColumns) {
        $(this).addClass('hide-column');
      }
    })
  });

  $('.show-more-btn').click(function(e) {
    e.preventDefault();
    
    showMore($(this));
  });

  $("#client-view-sw").change(function() {
    toggleClientView();
  });

  $(".art-search").on('input', function() {
    isArtSearchValid($(this));
  });

  $(".dist-search").on('input', function() {
    isDistSearchValid($(this));
  })

  $('.responsive-table.history tbody tr').each(function() {
    var $this = $(this);
    var $art = $this.find('td:first-child');
    var $dist = $this.find('td:nth-child(2)');
    lineBreak($art);
    lineBreak($dist);
  });

  var lastScrollTop = 0;
  var $actionButton = $('.fixed-action-btn');
  var $switchContainer = $('.switch-container');

  $(window).scroll(function() {
    var scrollTop = $(this).scrollTop();

    if (scrollTop < lastScrollTop) {
      $actionButton.removeClass('hidden').fadeIn();
      $switchContainer.removeClass('hidden').fadeIn();
    }
    else {
      $actionButton.fadeOut().addClass('hidden');
      $switchContainer.fadeOut().addClass('hidden');
    }

    lastScrollTop = scrollTop;
  });
});

var modifyWasClicked = false;

function mScrollTo(id) {
  // console.log($(id));
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

function isArtSearchValid($this) {
  var userInput = $this.val();
  if (optionsArtsDatalist.indexOf(userInput) === -1) {
    $this.addClass('invalid');
  }
  else {
    $this.removeClass('invalid');
  }
}

var optionsDistDatalist;

function isDistSearchValid($this) {
  var userInput = $this.val()
  if (!optionsDistDatalist) {
    optionsDistDatalist = $this.parent().find('datalist option').map(function() {
      return this.value;
    }).get();
  }

  if (optionsDistDatalist.indexOf(userInput) === -1) {
    $this.addClass('invalid');
  }
  else {
    $this.removeClass('invalid');
  }
}

function showMore($this) {
  var $table = $this.parents('.responsive-table').find('table');
  var $headerCells = $table.find('thead tr th:not(.ignore, .ignore-op)');
  var $dataCells = $table.find('tbody tr td:not(.ignore, .ignore-op)');
  var isShowMore = $table.data('isShowMore');

  $headerCells.each(function() {
    var $cell = $(this);
    $cell.toggleClass('hide-column');
  })

  $dataCells.each(function() {
    var $cell = $(this);
    $cell.toggleClass('hide-column');
  })

  $table.data('isShowMore', !isShowMore)
}

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

// funcion vista cliente
var vistaCliente = false;

function toggleClientView() {

  if ($("#client-view-sw").is(":checked")) {

    $("#form-table-div").hide();
    $("#send-prop-btn").attr('disabled', true);
    $(".card.history-card").addClass("vista-cliente");
    $(".circle-neg").addClass("vista-cliente");
    $(".container__wrapper").show();
    $(".copy-btn").hide();

    $('.responsive-table.history').each(function() {
      var $table = $(this).find('table');
      var $headerCells = $table.find('thead tr th');
      var $dataCells = $table.find('tbody tr td');
      var columnCount = $headerCells.length;
      var $propCreatorName = $(this).parents('.container').find('.prop-creator-name');
      var $parent = $(this).parents('.col.s12');
      var $propCreatorName = $(this).parents('.container').find('.prop-creator-name');
      var $propDate = $(this).parents('.container').find('.prop-date');
      var $circleNeg = $(this).parents('.container').find('.circle-neg-container');
      var isThisComprador = $propCreatorName.data('iscomprador');

      $table.toggleClass("responsive-table responsive-vista-cliente");

      if (isThisComprador) {
        $propCreatorName.toggleClass("pull-s2 push-s1");
        $propDate.toggleClass("pull-s2 push-s1");
        $circleNeg.toggleClass("comprador vendedor");
        $parent.toggleClass("pull-s2 push-s1");
      }

      $propCreatorName.find('p').text($propCreatorName.data("comprador"));
  
      $headerCells.each(function() {
        var $cell = $(this);
        
        $cell.removeClass('hide-column');
        
        if ($cell.hasClass('ignore') && !$cell.hasClass('hide-column')) {
          $cell.addClass('hide-column');
        }
        
        if ($cell.html().toLowerCase() == "distribuidor" || $cell.html().toLowerCase() == "precio compra") {
          $cell.addClass('hide-column-responsive');
        }

        if ($cell.html().toLowerCase() == "precio venta") {
          $cell.html("Precio");
        }
      })
  
      $dataCells.each(function(index) {
        var $cell = $(this);
        var $headerCell = $headerCells.eq(index % columnCount);

        $cell.removeClass('hide-column');
        
        if ($cell.hasClass('ignore') && !$cell.hasClass('hide-column')) {
          $cell.addClass('hide-column');
        }

        if ($headerCell.html().toLowerCase() == "distribuidor" || $headerCell.html().toLowerCase() == "precio compra") {
          $cell.addClass('hide-column-responsive');
        }
      })
    });

    vistaCliente = true;

  }
  else {

    if (modifyWasClicked) {
      $("#form-table-div").show();
    }
    if (!isAccepted && !isCanceled) {
      $("#form-table-div").show();
    }
    $("#send-prop-btn").removeAttr('disabled');
    $(".card.history-card").removeClass("vista-cliente");
    $(".circle-neg").removeClass("vista-cliente");
    $(".container__wrapper").hide();
    $(".copy-btn").show();

    $('.responsive-table.history').each(function() {
      var $table = $(this).find('table');
      var $headerCells = $table.find('thead tr th');
      var $dataCells = $table.find('tbody tr td');
      var columnCount = $headerCells.length;
      var $parent = $(this).parents('.col.s12');
      var $propCreatorName = $(this).parents('.container').find('.prop-creator-name');
      var $propDate = $(this).parents('.container').find('.prop-date');
      var $circleNeg = $(this).parents('.container').find('.circle-neg-container');
      var isThisComprador = $propCreatorName.data('iscomprador');

      $table.toggleClass("responsive-table responsive-vista-cliente");
      
      if (isThisComprador) {
        $propCreatorName.find('p').text($propCreatorName.data("comprador"));
        $propCreatorName.toggleClass("pull-s2 push-s1");
        $propDate.toggleClass("pull-s2 push-s1");
        $circleNeg.toggleClass("comprador vendedor");
        $parent.toggleClass("pull-s2 push-s1");
      }
      else {
        $propCreatorName.find('p').text($propCreatorName.data("vendedor"));
      }
  
      $headerCells.each(function(index) {
        var $cell = $(this);
        
        if (index % columnCount >= showColumns) {
          $cell.addClass('hide-column');
          if ($cell.hasClass('ignore')) {
            $cell.removeClass('hide-column');
          }
        }

        if ($cell.html().toLowerCase() == "distribuidor" || $cell.html().toLowerCase() == "precio compra") {
          $cell.removeClass('hide-column-responsive');
        }

        if ($cell.html().toLowerCase() == "precio") {
          $cell.html("Precio venta");
        }
      })
  
      $dataCells.each(function(index) {
        var $cell = $(this);
        var $headerCell = $headerCells.eq(index % columnCount);
        
        if (index % columnCount >= showColumns) {
          $cell.addClass('hide-column');
          if ($cell.hasClass('ignore')) {
            $cell.removeClass('hide-column');
          }
        }

        if ($headerCell.html().toLowerCase() == "distribuidor" || $headerCell.html().toLowerCase() == "precio compra") {
          $cell.removeClass('hide-column-responsive');
        }
      })
    });

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

function lineBreak($this) {
  var text = $this.text();
  var words = text.split(" ");
  var formattedText = "";

  $.each(words, function(index, word) {
    formattedText += word;

    if ((index + 1) % 3 == 0) {
      formattedText += "<br>";
    }
    else {
      formattedText += " ";
    }
  });

  $this.html(formattedText);
}

// table_edit

var optionsArtsDatalist;

function articuloDatalist(n) {
  var artDatalist = document.getElementById("artDatalist"+n);
  for (var i = 0; i < arts_data.length; i++) {
    var option = document.createElement('option');
    if (arts_data[i].empresa__nombre_comercial) {
      option.setAttribute('value',''+arts_data[i].ingrediente + ' ' + arts_data[i].empresa__nombre_comercial);
      option.setAttribute('id',''+arts_data[i].id);
      artDatalist.appendChild(option);        
    }
  }
  if (!n || isAccepted) {
    optionsArtsDatalist = $(artDatalist).find('option').map(function() {
      return this.value;
    }).get()
  }
}

function articuloDatalistCliente() {
  var artDatalist = document.getElementById("artDatalist0");
  var last_item = arts_data[0].ingrediente;
  var option = document.createElement('option');
  option.setAttribute('value',''+arts_data[0].ingrediente);
  option.setAttribute('id',''+arts_data[0].id);
  artDatalist.appendChild(option);   
  for (var i = 1; i < arts_data.length; i++) {
    var curr_item = arts_data[i].ingrediente;
    // console.log(curr_item, last_item);
    if (last_item != curr_item) {
      option = document.createElement('option');
      option.setAttribute('value',''+arts_data[i].ingrediente);
      option.setAttribute('id',''+arts_data[i].id);
      artDatalist.appendChild(option);
      last_item = arts_data[i].ingrediente;
    }
  }

  optionsArtsDatalist = $(artDatalist).find('option').map(function() {
    return this.value;
  }).get()
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

function getArtId(n) {
  var artSearchInput = $("#artSearch"+n).val();
  var artId = parseInt($('#artDatalist'+n+' option[value="' + artSearchInput +'"]').attr("id"));
  return artId;
}

function getDistId(n) {
  var artSearchInput = $("#distSearch"+n).val();
  var artId = parseInt($('#artDatalist'+n+' option[value="' + artSearchInput +'"]').attr("id"));
  return artId;
}

function copyIdToClipboard(url, n) {
  var text = url + "#" + n;
  navigator.clipboard.writeText(text).then(function() {
    M.toast({html: "Copiado al portapapeles"});
  } , function() {
    M.toast({html: "Error al copiar al portapapeles"});
  })
}
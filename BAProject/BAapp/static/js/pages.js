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

  const inputMoneyList = document.querySelectorAll('.input-money');
  for (input of inputMoneyList) bindMoneyInput(input);
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

// Code from: https://codepen.io/fcfett/pen/qexOgQ

const isCurrencyValue = (val) => /^[0-9]$/.test(val);
const getNumbers = (val) => val.replace(/[^0-9]/g, '');
const formatValue = (val, currency = 'USD') => {
  const floatVal = +val.replace(/(\d{2})$/, '.$1');
  const splitedVal = floatVal.toFixed(2).split('.');
  return `${currency} ${splitedVal[0].replace(/(?=(\d{3})+(?!\d))/g, ',').replace(/^\,/g, '')}.${splitedVal[1]}`;
}

const bindMoneyInput = (input) => {
  const inputDataset = input.dataset;
  const currency = inputDataset.currency || 'USD';
  const defaultValue = `${currency} 0,00`;
  const maxLength = +input.getAttribute('max-length') || 9;
  const valueLength = maxLength + `00`.length;
  
  inputDataset.currency = currency;
  input.setAttribute('inputmode', 'numeric');
  input.setAttribute('max-length', valueLength);
  inputDataset.currentValue = inputDataset.currentValue ? `${currency} ${inputDataset.currentValue}` : defaultValue;
  input.value = inputDataset.currentValue;

  input.addEventListener('input', (event) => {
    const { data: input, target } = event;
    const targetDataset = target.dataset;
    const currentValue = targetDataset.currentValue;
    const clearVal = getNumbers(currentValue);
    const preventedValue = target.value;
    const maxLength = target.getAttribute('max-length');

    /* 
    TODO: Add/remove values in the middle of the string using the properties below
    */
    //const cursorStart = target.selectionStart;
    //const cursorEnd = target.selectionEnd;
    //const selectionLength = cursorEnd - cursorStart;
    //console.log(currentValue, input, preventedValue, cursorStart, cursorEnd, selectionLength);

    let newVal;
    if (!input) {
      if (preventedValue.length === 0) {
        newVal = defaultValue;
      } else {
        newVal = formatValue(clearVal.slice(0, -1), currency);
      }
    } else {
      if (isCurrencyValue(input)) {
        if (preventedValue.length > 1) {
          newVal = `${clearVal}${input}`;
        } else {
          newVal = `00${input}`;
        }
        newVal = formatValue(newVal, currency);
      }
      newVal = newVal && getNumbers(newVal).length <= maxLength
        ? newVal
        : currentValue;
    }

    target.value = targetDataset.currentValue = newVal;

  }, false);

  triggerEvent(input);
}

// Code from: https://codepen.io/fcfett/pen/qexOgQ

function triggerEvent(input) {
  const inputEvent = new Event('input', {
    bubbles: true,
    cancelable: true,
  });
  input.dispatchEvent(inputEvent);
}

function formatForMoneyInput(input, inputValue) {
  var split1 = inputValue.split(' ')[1];
  var split2 = split1.split(/[,.]/);
  var number = split2.join('') + '0';
  input.dataset.currentValue = number;
  input.value = number;
  triggerEvent(input);
  return number;
}

function getNumberFromInput(value) {
  var split1 = value.split(' ')[1];
  var split2 = split1.split(/[,.]/);
  var len = split2.length;
  var decimalPart = split2.pop(split2[len-1]);
  var integerPart = split2.join('');
  var number = integerPart + '.' + decimalPart;
  return +number;
}
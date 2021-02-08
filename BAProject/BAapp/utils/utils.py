from io import BytesIO, FileIO

from openpyxl import load_workbook, Workbook
from openpyxl.styles import PatternFill
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import quote_sheetname, get_column_letter
from django.db import transaction
from django.db.models.fields.reverse_related import ManyToOneRel

from BAapp.models import Articulo, Empresa, Retencion

def _read_header(ws):
    header = {}
    for i in range(len(ws[1])):
        key = ws[1][i].value.lower().replace(" ", "_")
        header[key] = i
    return header

def sheet_reader(sheet):
    wb = load_workbook(filename=sheet)

    emp_sheet = wb["empresas"]
    emp_header = _read_header(emp_sheet)

    with transaction.atomic():
        for c in emp_sheet.iter_rows(2, values_only=True):
            instance = Empresa()
            if (c[emp_header["id"]]):
                instance = Empresa.objects.get(id=c[emp_header["id"]])
            if (not c[emp_header["razon_social"]]):
                break
            for v in emp_header.keys():
                if (v=="retenciones"):
                    if (c[emp_header[v]]):    
                        rets = c[emp_header[v]].split("+")
                        for ret in rets:
                            obj = Retencion.objects.get(name=ret)
                            instance.retenciones.add(obj)
                    continue
                setattr(instance, v, c[emp_header[v]])
            instance.save()

    art_sheet = wb["articulos"]
    art_header = _read_header(art_sheet)

    with transaction.atomic():
        for c in art_sheet.iter_rows(2, values_only=True):
            instance = Articulo()
            if (c[art_header["id"]]):
                instance = Articulo.objects.get(id=c[art_header["id"]])
            if (not c[art_header["marca"]]):
                break
            for v in art_header.keys():
                if (v=="empresa"):
                    instance.empresa = Empresa.objects.get(
                        razon_social=c[art_header["empresa"]])
                    continue
                setattr(instance, v, c[art_header[v]])
            instance.save()

def _get_actual_fields(model):
    fields = []
    for i in model._meta.get_fields():
        if (not isinstance(i, ManyToOneRel)):
            fields.append(i.name)
    return fields

def _write_header(sheet, fields):
    fill = PatternFill(
        fill_type="solid",
        start_color="9AC0CD",
        end_color="9AC0CD")
    for i in range(len(fields)):
        sheet.cell(1,i+1).value = fields[i].replace("_", " ").title()
        sheet.cell(1,i+1).fill = fill

def _readable_column_width(ws):
    dims = {}
    for row in ws.rows:
        for cell in row:
            if cell.value:
                dims[cell.column_letter] = max(
                    dims.get(cell.column_letter, 0), 
                    len(str(cell.value))+1
                )
    for col, value in dims.items():
        ws.column_dimensions[col].width = value

def _get_ret_names_list(retentions):
    for ret in retentions:
        yield ret[0]

def sheet_writer():
    wb = Workbook()

    # Create the sheets and write the headers
    art_sheet = wb.active
    art_sheet.title = "articulos"
    art_fields = _get_actual_fields(Articulo)
    print(art_fields)
    _write_header(art_sheet, art_fields)

    emp_sheet = wb.create_sheet(title="empresas")
    emp_fields = _get_actual_fields(Empresa)
    _write_header(emp_sheet, emp_fields)

    ing_sheet = wb.create_sheet(title="ingredientes")
    ing_fields = ('Nombre',)
    _write_header(ing_sheet, ing_fields)

    #write the data to the workbook
    row = 2
    for articulo in Articulo.objects.all():
        for field in range(len(art_fields)):
            cell = art_sheet.cell(row, field+1)
            if (art_fields[field] == "empresa"):
                cell.value = str(getattr(articulo, art_fields[field])) 
                continue
            cell.value = getattr(articulo, art_fields[field])
        row += 1

    row = 2
    for empresa in Empresa.objects.all():
        for field in range(len(emp_fields)):
            cell = emp_sheet.cell(row,field+1)
            if (emp_fields[field] == "retenciones"):
                cell.value = "+".join(
                    _get_ret_names_list(
                        empresa.retenciones.all().values_list('name')
                    )
                )
                continue
            cell.value = getattr(empresa, emp_fields[field])
        row += 1

    row = 2
    for ingrediente in Articulo.objects.all().values("ingrediente").distinct():
        cell = ing_sheet.cell(row,1)
        cell.value = ingrediente['ingrediente']
        row += 1

    # Data Validation
    empdv = DataValidation(
        type='list',
        formula1="{0}!${1}$2:${1}$3039".format(
            quote_sheetname(emp_sheet.title),
            get_column_letter(emp_fields.index("razon_social")+1))
        )
    art_sheet.add_data_validation(empdv)
    empdv.add("{0}2:{0}3039".format(
        get_column_letter(art_fields.index("empresa")+1))
    )

    ingdv = DataValidation(
        type='list',
        formula1="{0}!${1}$2:{1}$3039".format(
            quote_sheetname(ing_sheet.title),
            get_column_letter(ing_fields.index("Nombre")+1))
        )
    art_sheet.add_data_validation(ingdv)
    ingdv.add("{0}2:{0}3039".format(
        get_column_letter(art_fields.index("ingrediente")+1))
    )

    # Styling
    _readable_column_width(art_sheet)
    _readable_column_width(emp_sheet)
    _readable_column_width(ing_sheet)

    file = FileIO("dump.xlsx", 'w+')
    wb.save(file)
    file.seek(0)

    return file
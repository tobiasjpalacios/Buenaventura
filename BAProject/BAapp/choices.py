HO = 'Hombre'
MU = 'Mujer'
NB = 'Otro'

GENERO_CHOICES = (
    (HO , 'Hombre'),
    (MU , 'Mujer'),
    (NB , 'Otro'),
)

AU = 'Autonomo'
PR = 'Particular'

CATEGORIA_CHOICES = (
    (AU , 'Autonomo'),
    (PR , 'Particular'),
)

RI ='Responsable Inscripto'
RIM ='Responsable Inscripto M'
CF = 'Consumidor Final'
EX ='Exento'
MO ='Monotributo'

IVA_CHOICES = {
	(RI,'Responsable Inscripto'),
	(RIM,'Responsable Inscripto M'),
	(CF,'Consumidor Final'),
	(EX,'Exento'),
	(MO,'Monotributo'),
}

AR = 'Arrendamiento'
HN = 'Honorarios'
IN = 'Insumos'
SE = 'Servicios'
TR = 'Transporte'

RET_GANANCIA_CHOICES = {
	(AR,'Arrendamiento'),
	(EX,'Exento'),
	(HN,'Honorarios'),
	(IN,'Insumos'),
	(SE,'Servicios'),
	(TR,'Transporte'),
}

kWh = '1000 kWh'
BO = 'Bonificación'
CM = 'Centímetros'
CM3 = 'Cm Cúbicos'
CU = 'Curie'
DA3 = 'Dam Cúbicos'
DO = 'Docenas'
GR = 'Gramo Activo'
M3 = 'Metros Cúbicos'
M2 = 'Metros Cuadrados'
MC = 'Microcurie'
MG = 'Migrogramos'
ML = 'Mililitros'
MM = 'Milimetros'
NG = 'Nanogramos'
MM = 'Milimetros'
OU = 'Otras Unidades'
PAK = 'Packs'
PAR = 'Pares'
PG = 'Picogramos'
QU = 'Quilates'
TO = 'Toneladas'
UI = 'Uiactant'

UNIDAD_CHOICES = {
	(kWh,'1000 kWh'),
	(BO,'Bonificación'),
	(CM,'Centímetros'),
	(CM3,'Cm Cúbicos'),
	(CU,'Curie'),
	(DA3,'Dam Cúbicos'),
	(DO,'Docenas'),
	(GR,'Gramo Activo'),
	(M3,'Metros Cúbicos'),
	(M2,'Metros Cuadrados'),
	(MC,'Microcurie'),
	(MG,'Migrogramos'),
	(ML,'Mililitros'),
	(MM,'Milimetros'),
	(NG,'Nanogramos'),
	(MM,'Milimetros'),
	(PAK,'Packs'),
	(PAR,'Pares'),
	(PG,'Picogramos'),
	(QU,'Quilates'),
	(TO,'Toneladas'),
	(UI,'Uiactant'),
	(OU,'Otras Unidades'),
}

DO = 'Dolar'
DOB = 'Dolar Blue'
PA = 'Peso Argentino'

DIVISA_CHOICES = {
	(DO,''),
	(DOB,''),
	(PA,''),

}
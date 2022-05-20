GENERO_CHOICES = (
    ('HO' , 'Hombre'),
    ('MU' , 'Mujer'),
    ('NB' , 'Otro'),
)

BANDA_TOXICOLOGICA_CHOICES = (
	('I', 'I'),
	('II', 'II'),
	('III', 'III'),
	('VI', 'VI'),
	('LA', 'LA'),
	('LB', 'LB'),
)

CATEGORIA_CHOICES = (
    ("AU" , 'Autonomo'),
    ("PR" , 'Particular'),
)

IVA_CHOICES = {
	("RI",'Responsable Inscripto'),
	("RIM",'Responsable Inscripto M'),
	("CF",'Consumidor Final'),
	("EX",'Exento'),
	("MO",'Monotributo'),
}

UNIDAD_CHOICES = (
	("kWh",'1000 kWh'),
	("BO",'Bonificación'),
	("CM",'Centímetros'),
	("CM3",'Cm Cúbicos'),
	("CU",'Curie'),
	("DA3",'Dam Cúbicos'),
	("DO",'Docenas'),
	("GR",'Gramo Activo'),
	("M3",'Metros Cúbicos'),
	("M2",'Metros Cuadrados'),
	("MC",'Microcurie'),
	("MG",'Migrogramos'),
	("ML",'Mililitros'),
	("MM",'Milimetros'),
	("NG",'Nanogramos'),
	("MM",'Milimetros'),
	("PAK",'Packs'),
	("PAR",'Pares'),
	("PG",'Picogramos'),
	("QU",'Quilates'),
	("TO",'Toneladas'),
	("UI",'Uiactant'),
	("OU",'Otras Unidades'),
)

DIVISA_CHOICES = (
	('AR','Pesos'),
    ('USD','Dolar'),
)

TASA_CHOICES = (
	(None,"Elija tasa"),
	("0","0%"),
	("0.3","0.3%"),
	("0.4","0.4%"),
	("0.5","0.5%"),
	("0.6","0.6%"),
	("0.7","0.70%"),
	("0.75","0.75%"),
	("0.85","0.85%"),
	("1","1.00%"),
	("2","2.00%"),
	("2.5","2.50%"),
	("2.75","2.75%"),
	("3","3.00%"),
	("3.5","3.50%"),
	("3.6","36.00%"),
	("inc","INCLUIDA"),
)

TIPO_DE_NEGOCIO_CHOICES = (
	("VT","Venta"),
	("CS","Consignacion"),
)

TIPO_NOTA = (
	("CR","Credito"),
	("DV","Débito"),
)

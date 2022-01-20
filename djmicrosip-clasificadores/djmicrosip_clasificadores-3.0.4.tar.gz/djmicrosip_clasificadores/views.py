#encoding:utf-8
from .forms import *
from .models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
#from django.db.models import get_app, get_models
from django_microsip_base.libs.models_base.models import Articulo, ArticuloPrecio, ArticuloClave,Clasificadores,ClasificadoresValores,ElementosClasificadores, VentasDocumento, VentasDocumentoDetalle,ClienteDireccion,ClienteClave, Almacen,PuntoVentaDocumento,PuntoVentaDocumentoDetalle,Cajero,Caja,ClienteDireccion,GrupoLineas,LineaArticulos,LibresArticulos,Impuesto,PuntoVentaDocumentoImpuesto,VentasDocumentoImpuesto,ClienteUsuario
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission
from datetime import datetime
from django.forms.models import inlineformset_factory
from django.conf import settings
#Login
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as do_login
# Django
from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.list import ListView
from django.db import router, connections,connection
from django.core import management
from django.db.models import Q,Count
from microsip_api.comun.sic_db import first_or_none
from .send_mail import send_mail_contrasena
from django.utils.crypto import get_random_string
from django_microsip_base.libs.models_base.models import ConexionDB,DatabaseSucursal
from base64 import decodestring
from django.core.files import File
# Python
import json
import random
import string
import re, io,os,errno
# import cStringIO as StringIO
from io import StringIO
import base64
from PIL import Image
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True



def randomString(stringLength=10):
	"""Generate a random string of fixed length """
	letters = string.ascii_lowercase
	return ''.join(random.choice(letters) for i in range(stringLength))

def eliminar_detalle(request,id_detalle,id_pedido):
	# modulo=Registry.objects.get(nombre='SIC_Clasificadores_Modulo').get_value()
	# tipo_documento=Registry.objects.get(nombre='SIC_Clasificadores_Tipo_Documento').get_value()
	# if modulo=="PV":
	# 	pedido=first_or_none(PuntoVentaDocumento.objects.filter(id=id_pedido))
	# 	detalle_venta=first_or_none(PuntoVentaDocumentoDetalle.objects.filter(id=id_detalle,documento_pv=pedido))
	# 	if detalle_venta:
	# 		detalle_venta.delete()
	# 		return redirect('/pedidos_web/view_pedido/'+str(pedido.id)+'/')
	# elif modulo=="V":
	# 	pedido=first_or_none(VentasDocumento.objects.filter(id=id_pedido))
	# 	detalle_venta=first_or_none(VentasDocumentoDetalle.objects.filter(id=id_detalle,documento=pedido))
	# 	if detalle_venta:
	# 		detalle_venta.delete()
	# 		return redirect('/pedidos_web/view_pedido/'+str(pedido.id)+'/')
	carrito_temporal=first_or_none(CarritoTemporal.objects.filter(id=id_pedido))
	carrito_temporal_detalle=first_or_none(CarritoTemporalDetalle.objects.filter(carrito_temporal=carrito_temporal,id=id_detalle))
	if carrito_temporal_detalle:
		carrito_temporal_detalle.delete()

	return redirect('/pedidos_web/view_pedido/'+str(carrito_temporal.id)+'/')


def definir_documento(request,folio_pedido):
	modulo=Registry.objects.get(nombre='SIC_Clasificadores_Modulo').get_value()
	tipo_documento=Registry.objects.get(nombre='SIC_Clasificadores_Tipo_Documento').get_value()
	cajero_id=Registry.objects.get(nombre='SIC_Clasificadores_Cajero').get_value()
	caja_id=Registry.objects.get(nombre='SIC_Clasificadores_Caja').get_value()
	cajero=first_or_none(Cajero.objects.filter(id=cajero_id))
	caja=first_or_none(Caja.objects.filter(id=caja_id))
	sucursal_id=None
	usuario=request.user
	cliente_usuario=first_or_none(ClienteUsuario.objects.filter(usuario=usuario.id))
	if cliente_usuario:
		cliente_id=cliente_usuario.cliente.id
	else:
		cliente_id=Registry.objects.get(nombre='SIC_Clasificadores_Cliente_predeterminado').get_value()
	
	data=info_cliente(cliente_id)
	pedido_=None
	detalle_venta=None
	if int(settings.MICROSIP_VERSION) >= 2020:
		print("version")
		print(settings.MICROSIP_VERSION)
		using = router.db_for_write(Articulo)
		c = connections[using].cursor()
		query = "select sucursal_id from sucursales where nombre='Matriz'"
		c.execute(query)
		sucursal_id = c.fetchall()[0][0]

	print("---------",sucursal_id,folio_pedido)
	print(modulo)
	if modulo=="PV":
		print("punto venta")
		if folio_pedido:
			pedido_=first_or_none(PuntoVentaDocumento.objects.filter(folio=folio_pedido,tipo='O').exclude(estado__in=['C','P']))
			if not pedido_:
				request.session['folio_pedido']=None
				if sucursal_id:
					pedido_ = PuntoVentaDocumento.objects.create(
							id = -1,
							caja = caja,
							cajero = cajero,
							cliente = data["cliente"],
							almacen = caja.almacen,
							moneda = data["moneda"],
							tipo = 'O',
							fecha = datetime.now(),
							hora = datetime.now().strftime('%H:%M:%S'),
							clave_cliente = data["clave"],
							tipo_cambio = 1,
							aplicado = 'S',
							estatus = 'P',
							importe_neto = 0.01,
							total_impuestos = 0,
							importe_donativo = 0,
							total_fpgc = 0,
							descripcion = 'ORDEN WEB',
							usuario_creador = cajero.usuario,
							sucursal_id=sucursal_id,
						)
				else:
					pedido_ = PuntoVentaDocumento.objects.create(
							id = -1,
							caja = caja,
							cajero = cajero,
							cliente = data["cliente"],
							almacen = caja.almacen,
							moneda = data["moneda"],
							tipo = 'O',
							fecha = datetime.now(),
							hora = datetime.now().strftime('%H:%M:%S'),
							clave_cliente = data["clave"],
							tipo_cambio = 1,
							aplicado = 'S',
							estatus = 'P',
							importe_neto = 0.01,
							total_impuestos = 0,
							importe_donativo = 0,
							total_fpgc = 0,
							descripcion = 'ORDEN WEB',
							usuario_creador = cajero.usuario,
						)

				request.session['folio_pedido'] = pedido_.folio
		else:
			if sucursal_id:
				print("yes")
				pedido_ = PuntoVentaDocumento.objects.create(
						id = -1,
						caja = caja,
						cajero = cajero,
						cliente = data["cliente"],
						almacen = caja.almacen,
						moneda = data["moneda"],
						tipo = 'O',
						fecha = datetime.now(),
						hora = datetime.now().strftime('%H:%M:%S'),
						clave_cliente = data["clave"],
						tipo_cambio = 1,
						aplicado = 'S',
						importe_neto = 0.01,
						total_impuestos = 0,
						importe_donativo = 0,
						total_fpgc = 0,
						descripcion = 'ORDEN WEB',
						usuario_creador = cajero.usuario,
						sucursal_id=sucursal_id,
					)
			else:
				print("nope")
				print(caja,cajero,data["cliente"],caja.almacen,data["moneda"],data["clave"],'ORDEN WEB',cajero.usuario)
				pedido_ = PuntoVentaDocumento.objects.create(
						id = -1,
						caja = caja,
						cajero = cajero,
						cliente = data["cliente"],
						almacen = caja.almacen,
						moneda = data["moneda"],
						tipo = 'O',
						fecha = datetime.now(),
						hora = datetime.now().strftime('%H:%M:%S'),
						clave_cliente = data["clave"],
						tipo_cambio = 1,
						aplicado = 'S',
						importe_neto = 0.01,
						total_impuestos = 0,
						importe_donativo = 0,
						total_fpgc = 0,
						descripcion = 'ORDEN WEB',
						usuario_creador = cajero.usuario,
					)

			request.session['folio_pedido'] = pedido_.folio

		detalle_venta=PuntoVentaDocumentoDetalle.objects.filter(documento_pv=pedido_)

	elif modulo=="V":
		print("venta")
		if folio_pedido:
			pedido_=first_or_none(VentasDocumento.objects.filter(folio=folio_pedido,tipo=tipo_documento).exclude(estado__in=['C','P']))
			if not pedido_:
				request.session['folio_pedido']=None
				if sucursal_id:
					pedido_ = VentasDocumento.objects.create(
						tipo=tipo_documento,
						subtipo='N',
						fecha=datetime.now(),
						cliente=data["cliente"],
						cliente_clave=data["clave"],
						cliente_direccion=data["direccion"],
						direccion_consignatario=data["direccion"],
						almacen=data["almacen"],
						moneda=data["moneda"],
						estado='N',
						aplicado='S',
						descripcion='ORDEN WEB' ,
						# importe_neto=,
						sistema_origen='VE',
						condicion_pago=data["condicion_de_pago"],
						modalidad_facturacion=None,
						sucursal_id=sucursal_id,
					)
				else:
					pedido_ = VentasDocumento.objects.create(
						tipo=tipo_documento,
						subtipo='N',
						fecha=datetime.now(),
						cliente=data["cliente"],
						cliente_clave=data["clave"],
						cliente_direccion=data["direccion"],
						direccion_consignatario=data["direccion"],
						almacen=data["almacen"],
						moneda=data["moneda"],
						estado='N',
						aplicado='S',
						descripcion='ORDEN WEB' ,
						# importe_neto=,
						sistema_origen='VE',
						condicion_pago=data["condicion_de_pago"],
						modalidad_facturacion=None,
					)
				request.session['folio_pedido'] = pedido_.folio
		else:
			if sucursal_id:
				pedido_ = VentasDocumento.objects.create(
					tipo=tipo_documento,
					subtipo='N',
					fecha=datetime.now(),
					cliente=data["cliente"],
					cliente_clave=data["clave"],
					cliente_direccion=data["direccion"],
					direccion_consignatario=data["direccion"],
					almacen=data["almacen"],
					moneda=data["moneda"],
					estado='N',
					aplicado='S',
					descripcion='ORDEN WEB' ,
					# importe_neto=,
					sistema_origen='VE',
					condicion_pago=data["condicion_de_pago"],
					modalidad_facturacion=None,
					sucursal_id=sucursal_id,
				)
			else:
				pedido_ = VentasDocumento.objects.create(
					tipo=tipo_documento,
					subtipo='N',
					fecha=datetime.now(),
					cliente=data["cliente"],
					cliente_clave=data["clave"],
					cliente_direccion=data["direccion"],
					direccion_consignatario=data["direccion"],
					almacen=data["almacen"],
					moneda=data["moneda"],
					estado='N',
					aplicado='S',
					descripcion='ORDEN WEB' ,
					# importe_neto=,
					sistema_origen='VE',
					condicion_pago=data["condicion_de_pago"],
					modalidad_facturacion=None,
				)
			
			request.session['folio_pedido'] = pedido_.folio

		detalle_venta=VentasDocumentoDetalle.objects.filter(documento=pedido_)
	
	datos_pedido={
		'pedido':pedido_,
		'detalle_venta':detalle_venta,

	}
	return datos_pedido



@login_required(login_url='/login/')
def index(request, template_name='djmicrosip_clasificadores/index.html'):
	directorio=settings.MEDIA_ROOT+'\\imagenes_articulos\\'

	try:
		os.mkdir(directorio)
	except OSError:
		print("La creación del directorio %s falló" % directorio)
	else:
		print("Se ha creado el directorio: %s " % directorio)
		
	using = router.db_for_write(Articulo)
	c = connections[using].cursor()
	clasificadores = None
	clasificadores_libre = None
	clasificadores_valores = None
	clasificador_padre_valor=None
	busqueda=None
	valores_list=None
	folio_pedido=None
	valores=None
	mensaje=None
	existencia=False
	cantidad_pedido=0
	tipo_art=None
	limite_existencia=Registry.objects.get(nombre='SIC_Clasificadores_LimiteExistencia').get_value()
	compatible= Registry.objects.get( nombre = 'SIC_Clasificadores_Compatible').get_value()
	venta= Registry.objects.get( nombre = 'SIC_Clasificadores_Venta').get_value()
	imagenes= Registry.objects.get( nombre = 'SIC_Clasificadores_Imagenes').get_value()
	cliente_id=Registry.objects.get(nombre='SIC_Clasificadores_Cliente_predeterminado').get_value()
	clasificador_padre_id=Registry.objects.get(nombre='SIC_Clasificadores_Clasificador_Padre').get_value()
	clasificador_padre=first_or_none(Clasificadores.objects.filter(clasificador_id=clasificador_padre_id))
	valores_calsificador_padre=ClasificadoresValores.objects.filter(clasificador=clasificador_padre)

	if limite_existencia == "True":
		limite_existencia=True
	else:
		limite_existencia=False
	if compatible == "True":
		compatible=True
	else:
		compatible=False
	if venta == "True":
		venta=True
	else:
		venta=False
	if imagenes == "True":
		imagenes=True
	else:
		imagenes=False

	cliente_d=first_or_none(ClienteDireccion.objects.filter(rfc_curp=request.user.username))
	if cliente_d:
		cliente_id=cliente_d.cliente.id
	print("*********cliente*********")	
	print(cliente_d)	
	print(cliente_id)	

	form=ArticuloAnexosForm(request.POST or None)
	if 'folio_pedido' in request.session:
		folio_pedido = request.session['folio_pedido']
	
	if venta:
		cliente=first_or_none(Cliente.objects.filter(id=cliente_id))
		carrito=CarritoTemporal.objects.get_or_create(cliente=cliente)
		detalle_venta=None
		if carrito:
			carrito=carrito[0]
			detalle_venta=CarritoTemporalDetalle.objects.filter(carrito_temporal=carrito)

	else:
		carrito=None
		detalle_venta=None

	articulos_id=[]
	libres_list=[]
	nombres_list=[]
	claves_list=[]

	# lista_articulos_existencia=get_todos_existencia()
		
	#detalle_venta=None

	linea_id=Registry.objects.get(nombre='SIC_Clasificadores_Linea').get_value()
	linea=first_or_none(LineaArticulos.objects.filter(id=linea_id))
	#print(linea_id,linea)
	# query=''' select  a.articulo_id from articulos a left join orsp_in_aux_art(a.articulo_id,'Consolidado','01/01/2000',current_date, 'N','N') b on b.articulo_id = a.articulo_id where b.inv_fin_unid > 0 '''
	# c.execute(query)
	# lista_exist = c.fetchall()
	# print("******")
	# print(lista_exist)	


	if linea:
		articulos_list=Articulo.objects.filter(estatus='A',linea=linea).order_by('nombre')
	else:
		articulos_list=Articulo.objects.filter(estatus='A').order_by('nombre')



	#print(articulos_list)
	form_busqueda=FilterForm(request.POST or None)
	page = request.GET.get('page')
	if request.GET.get('clasificador_padre_valor'):
		clasificador_padre_valor=request.GET.get('clasificador_padre_valor')	
	if request.GET.get('mensaje'):
		mensaje=request.GET.get('mensaje')
	if request.GET.get('existencia'):
		existencia=request.GET.get('existencia')
	if request.GET.get('clas_val'):
		clasificadores=json.loads(request.GET.get('clas_val'))
		clasificadores_libre=json.loads(request.GET.get('clas_val'))
	if request.GET.get('busqueda'):
		busqueda=request.GET.get('busqueda')
	if request.GET.get('tipo_art'):
		tipo_art=request.GET.get('tipo_art')
	clasificadores_padre_existentes=ClasificadorAsignacion.objects.filter(
		clasificador_padre=clasificador_padre_id,clasificador_padre_valor=clasificador_padre_valor).values_list('clasificador_asignado')
	clas_all=Clasificadores.objects.exclude(clasificador_id=clasificador_padre_id)
	clas_val_all=ClasificadoresValores.objects.filter(valor_clasif_id__in=clasificadores_padre_existentes)
	elementos=ElementosClasificadores.objects.all()
	
	if clasificadores and clasificador_padre_valor:
		valores=ClasificadoresValores.objects.filter(valor_clasif_id__in=clasificadores).values_list("clasificador")
		if clasificador_padre_valor:
			clasificadores_libre.append(int(clasificador_padre_valor))
		#print(clasificadores_libre)
		elementos=elementos.filter(valor_clasificador__in=clasificadores_libre).values(
			'elemento_id').annotate(repeat=Count('elemento_id'))

		articulos_id=[elemento["elemento_id"] if elemento["repeat"] == len(clasificadores_libre) else elemento["elemento_id"] if len(clasificadores_libre) == 1 else None for elemento in elementos]
		articulos_list=articulos_list.filter(id__in=articulos_id)
		valores_list=[valor[0] for valor in valores]
		#print(valores_list)
		clasificador_padre_valor=int(clasificador_padre_valor)
	elif clasificador_padre_valor:
  
		elementos_=ElementosClasificadores.objects.filter(valor_clasificador=clasificador_padre_valor).values(
			'elemento_id')
		
		articulos_id=[elemento["elemento_id"] for elemento in elementos_]

		articulos_list=articulos_list.filter(id__in=articulos_id)
		clasificador_padre_valor=int(clasificador_padre_valor)
	
	if form_busqueda.is_valid():
		busqueda=form_busqueda.cleaned_data['busqueda']
		existencia=form_busqueda.cleaned_data['sin_existencia']
		tipo_art=form_busqueda.cleaned_data['tipo_art']
		page=1
		if busqueda:
			if venta:
				libres=None
			else:
				libres=LibresArticulos.objects.filter(no_serie__icontains=busqueda).values_list("articulo_id")
			# print("***************************************")
			# print(libres)
			if libres:
				libres_list=[valor[0] for valor in libres]

			nombres=Articulo.objects.filter(nombre__icontains=busqueda).values_list("id")
			
			if nombres:
				nombres_list=[valor[0] for valor in nombres]
			#valores_list=[valor[0] for valor in nombres]			
			articulos_claves=ArticuloClave.objects.filter(clave__icontains=busqueda).values_list("articulo__id")			
			if articulos_claves:
				claves_list=[valor[0] for valor in articulos_claves]			
			valores_list=libres_list+nombres_list+claves_list
			# print("XOXOXOXOXOXOXOXOXOXOXOXOX")
			# print(valores_list)
							
			articulos_list=articulos_list.filter(id__in=valores_list)
				# print(articulos_list)
	else:
		if busqueda:
			if venta:
				libres=None
			else:
				libres=LibresArticulos.objects.filter(no_serie__icontains=busqueda).values_list("articulo_id")
			# print("***************************************")
			# print(libres)
			if libres:
				libres_list=[valor[0] for valor in libres]

			nombres=Articulo.objects.filter(nombre__icontains=busqueda).values_list("id")
			
			if nombres:
				nombres_list=[valor[0] for valor in nombres]
			#valores_list=[valor[0] for valor in nombres]			
			articulos_claves=ArticuloClave.objects.filter(clave__icontains=busqueda).values_list("articulo__id")			
			if articulos_claves:
				claves_list=[valor[0] for valor in articulos_claves]			
			valores_list=libres_list+nombres_list+claves_list
			# print("XOXOXOXOXOXOXOXOXOXOXOXOX")
			# print(valores_list)
							
			articulos_list=articulos_list.filter(id__in=valores_list)
				# print(articulos_list)
				# print(articulos_list)
			# if venta:
			# 	libres=None
			# else:
			# 	libres=LibresArticulos.objects.filter(no_serie__icontains=busqueda)
			# if libres:
			# 	libre=libres.values("articulo_id")
			# 	articulos_list=articulos_list.filter(id__in=libres)
			# else:				
			# 	articulos_list=articulos_list.filter(nombre__icontains=busqueda)
			
			# articulos_claves=ArticuloClave.objects.filter(clave__icontains=busqueda).values_list("articulo__id")
			# #valores_list=[valor[0] for valor in articulos_claves]
			# if articulos_claves:
			# 	articulos_list=articulos_list.filter(id__in=articulos_claves)	      
			# 	print(articulos_list)			
	#print(articulos_list)
	paginator = Paginator(articulos_list, 50) 

	try:
		articulos = paginator.page(page)
	except PageNotAnInteger:
		
		articulos = paginator.page(1)
	except EmptyPage:
		
		articulos = paginator.page(paginator.num_pages)

	#print(articulos)
	#print(articulos)
	# print(articulos_list)

	# print(cliente_d)
	# print(cliente_id)
	for articulo in articulos:
		#print(articulo)
		data=GetArticulo(articulo.id,19,cliente_id)
		query = ''' EXECUTE PROCEDURE PRECIO_CON_IMPTO(%s, %s,'N','P','N')'''
		c.execute(query, [articulo.id, data["precio"]])
		precio_con_impuesto = c.fetchall()[0][0]
		# print("before")
		# print(articulos)
		if venta==False:
			detalle=first_or_none(VentasDocumentoDetalle.objects.filter(articulo=articulo))
			articulos_libre=first_or_none(LibresArticulos.objects.filter(articulo_id=articulo.id,))
			
			if detalle:
				#print(detalle.documento.tipo)
				if detalle.documento.tipo=="F":
					articulo.color="#ff00004d"
				if detalle.documento.tipo=="R":
					articulo.color="#ffa50070"
				if detalle.documento.tipo=="P":
					articulo.color="#ffff004d"
			else:
				articulo.color="#0080004d"
			articulo.costo=articulos_libre.costo
			articulo.no_serie=articulos_libre.no_serie		
			articulo.fecha_compra=articulos_libre.fecha_compra				
			articulo.refaccion=articulos_libre.refaccion		
			articulo.flete=articulos_libre.flete		

		articulo_anex=ArticuloAnexos.objects.filter(articulo=articulo)
		# print ("-------------------------------")
		# print (articulo_anex)
		if articulo_anex:
			articulo.img=articulo_anex or None
			articulo.pedm=articulo_anex or None
		else:
			for detalle in detalle_venta:
				if detalle.articulo.id == articulo.id:
					articulo.cantidad=detalle.cantidad	
			cantidad_pedido=len(detalle_venta)		
			# 	print("************************")
			# 	print(articulo.img)

			# print(articulo.color)
		
		articulo.existencia=data["existencia"]
		articulo.clave=data["clave"]
		articulo.precio=precio_con_impuesto

	
	# print("--------0000000-------")
	# print(imagenes)
	context={
		'articulos':articulos,
		'clasificadores':clasificadores,
		'clasificadores_valores':clasificadores_valores,
		'clas_all':clas_all,
		'clas_val_all':clas_val_all,
		'form_busqueda':form_busqueda,
		'form':form,
		'busqueda':busqueda,
		'tipo_art':tipo_art,
		'carrito':carrito,
		'cantidad_pedido':cantidad_pedido,
		'valores':valores_list  ,
		'clasificador_padre':clasificador_padre,
		'clasificadores_padre':valores_calsificador_padre,
		'clasificador_padre_valor':clasificador_padre_valor,
		'limite_existencia':limite_existencia,
		'compatible':compatible,
		'venta':venta,
		'imagenes':imagenes,
		'mensaje':mensaje,
		'existencia':str(existencia),
	}

	return render(request, template_name,context)

def GetArticulo(articulo_id,id_almacen,id_cliente):
	#Manda llamar las existencias y precios desde un procedimiento
	try:
		
		using = router.db_for_write(Articulo)
		c = connections[using].cursor()
		# c.execute("EXECUTE PROCEDURE CALC_EXIS_ARTALM %s,%s,CURRENT_DATE;" %(articulo_id,id_almacen) )
		# existencia=c.fetchall()[0][0]
		c.execute("EXECUTE PROCEDURE GET_PRECIO_ARTCLI %s,%s,CURRENT_DATE,0;" %(id_cliente,articulo_id) )
		precio=c.fetchall()[0][0]
		# print("---------------------------------")
		# print(precio)
		c.execute("EXECUTE PROCEDURE GET_CLAVE_ART %s;" %(articulo_id) )
		clave=c.fetchall()[0][1]
		c.execute("EXECUTE PROCEDURE orsp_in_aux_art  %s,'Consolidado','01/01/2000',CURRENT_DATE,'N','N'"%(articulo_id))
		existencia=c.fetchall()[0][6]
		#print(exist)
		data={
			"existencia":existencia,
			"precio":precio,
			"clave":clave,
		}
		c.close()
	except Exception as e:
		print(e)

	return (data)

def get_todos_almacenes(request):
	id_articulo=request.GET['id_articulo']
	lista=[]
	data={}
	try:
		
		using = router.db_for_write(Articulo)
		c = connections[using].cursor()
		c.execute("select * from orsp_in_aux_art  (%s,'Todos','01/01/2000',CURRENT_DATE,'N','N')"%(id_articulo))
		todos=c.fetchall()
		for todo in todos:
			data["almacen"]=todo[2]
			data["existencia"]=int(todo[6])
			lista.append(data)
			data={}
		c.close()
	except Exception as e:
		print(e)

	return HttpResponse(json.dumps(lista), content_type='application/json')

def compatibilidad_articulo(request):
	id_articulo=request.GET['id_articulo']
	id_pedido=request.GET['id_pedido']
	cliente_id=Registry.objects.get(nombre='SIC_Clasificadores_Cliente_predeterminado').get_value()
	articulo=Articulo.objects.get(id=id_articulo)
	lista=[]
	data={}
	articulos=ArticulosCompatibilidad.objects.filter(articulo=articulo).values_list('articulo_compatible')
	articulos_compatibles=Articulo.objects.filter(id__in=articulos)
	modulo=Registry.objects.get(nombre='SIC_Clasificadores_Modulo').get_value()
	tipo_documento=Registry.objects.get(nombre='SIC_Clasificadores_Tipo_Documento').get_value()

	for articulo in articulos_compatibles:
		if modulo=="PV":
			detalle_venta=first_or_none(PuntoVentaDocumentoDetalle.objects.filter(documento_pv__folio=id_pedido,articulo=articulo))
		elif modulo=="V":
			detalle_venta=first_or_none(VentasDocumento.objects.filter(documento__folio=id_pedido,articulo=articulo))
		print(detalle_venta)
		data_articulo=GetArticulo(articulo.id,19,cliente_id)
		data["id"]=articulo.id
		data["articulo"]=articulo.nombre
		data["clave"]=data_articulo["clave"]
		data["existencia"]=str(data_articulo["existencia"])
		data["precio"]=str(data_articulo["precio"])
		if detalle_venta:
			data["cantidad"]=str(detalle_venta.unidades)
		else:
			data["cantidad"]="0"

		lista.append(data)
		data={}

	return HttpResponse(json.dumps(lista), content_type='application/json')

def preferencias(request):
	padre = first_or_none(Registry.objects.filter(nombre='PreferenciasEmpresa'))
	if not Registry.objects.filter( nombre = 'SIC_Clasificadores_Cliente_predeterminado' ).exists():
			Registry.objects.create(
				nombre = 'SIC_Clasificadores_Cliente_predeterminado',
				tipo = 'V',
				padre = padre,
				valor= '',
			)
	if not Registry.objects.filter( nombre = 'SIC_Clasificadores_Tiempo_Espera' ).exists():
		Registry.objects.create(
			nombre = 'SIC_Clasificadores_Tiempo_Espera',
			tipo = 'V',
			padre = padre,
			valor= '',
		)
	if not Registry.objects.filter( nombre = 'SIC_Clasificadores_Clasificador_Padre' ).exists():
		Registry.objects.create(
			nombre = 'SIC_Clasificadores_Clasificador_Padre',
			tipo = 'V',
			padre = padre,
			valor= '',
		)
	if not Registry.objects.filter( nombre = 'SIC_Clasificadores_Cajero' ).exists():
		Registry.objects.create(
			nombre = 'SIC_Clasificadores_Cajero',
			tipo = 'V',
			padre = padre,
			valor= '',
		)
	if not Registry.objects.filter( nombre = 'SIC_Clasificadores_Caja' ).exists():
		Registry.objects.create(
			nombre = 'SIC_Clasificadores_Caja',
			tipo = 'V',
			padre = padre,
			valor= '',
		)
	if not Registry.objects.filter( nombre = 'SIC_Clasificadores_LimiteExistencia' ).exists():
		Registry.objects.create(
			nombre = 'SIC_Clasificadores_LimiteExistencia',
			tipo = 'V',
			padre = padre,
			valor= '',
		)
	if not Registry.objects.filter( nombre = 'SIC_Clasificadores_Modulo' ).exists():
		Registry.objects.create(
			nombre = 'SIC_Clasificadores_Modulo',
			tipo = 'V',
			padre = padre,
			valor= '',
		)
	if not Registry.objects.filter( nombre = 'SIC_Clasificadores_Tipo_Documento' ).exists():
		Registry.objects.create(
			nombre = 'SIC_Clasificadores_Tipo_Documento',
			tipo = 'V',
			padre = padre,
			valor= '',
		)
	if not Registry.objects.filter( nombre = 'SIC_Clasificadores_BD_Automatica' ).exists():
		Registry.objects.create(
			nombre = 'SIC_Clasificadores_BD_Automatica',
			tipo = 'V',
			padre = padre,
			valor= '',
		)
	if not Registry.objects.filter( nombre = 'SIC_Clasificadores_Email' ).exists():
			Registry.objects.create(
				nombre = 'SIC_Clasificadores_Email',
				tipo = 'V',
				padre = padre,
				valor= '',
			)
	if not Registry.objects.filter( nombre = 'SIC_Clasificadores_Password' ).exists():
			Registry.objects.create(
				nombre = 'SIC_Clasificadores_Password',
				tipo = 'V',
				padre = padre,
				valor= '',
			)
	if not Registry.objects.filter( nombre = 'SIC_Clasificadores_Servidro_Correo' ).exists():
			Registry.objects.create(
				nombre = 'SIC_Clasificadores_Servidro_Correo',
				tipo = 'V',
				padre = padre,
				valor= '',
			)
	if not Registry.objects.filter( nombre = 'SIC_Clasificadores_Puerto' ).exists():
			Registry.objects.create(
				nombre = 'SIC_Clasificadores_Puerto',
				tipo = 'V',
				padre = padre,
				valor= '',
			)
	if not Registry.objects.filter( nombre = 'SIC_Clasificadores_Compatible' ).exists():
			Registry.objects.create(
				nombre = 'SIC_Clasificadores_Compatible',
				tipo = 'V',
				padre = padre,
				valor= '',
			)
	if not Registry.objects.filter( nombre = 'SIC_Clasificadores_Venta' ).exists():
			Registry.objects.create(
				nombre = 'SIC_Clasificadores_Venta',
				tipo = 'V',
				padre = padre,
				valor= '',
			)
	if not Registry.objects.filter( nombre = 'SIC_Clasificadores_Descripcion_Correo' ).exists():
			Registry.objects.create(
				nombre = 'SIC_Clasificadores_Descripcion_Correo',
				tipo = 'V',
				padre = padre,
				valor= '',
			)
	if not Registry.objects.filter( nombre = 'SIC_Clasificadores_Imagenes' ).exists():
			Registry.objects.create(
				nombre = 'SIC_Clasificadores_Imagenes',
				tipo = 'V',
				padre = padre,
				valor= '',
			)
	if not Registry.objects.filter( nombre = 'SIC_Clasificadores_Linea' ).exists():
			Registry.objects.create(
				nombre = 'SIC_Clasificadores_Linea',
				tipo = 'V',
				padre = padre,
				valor= '',
			)
	limite_existencia=Registry.objects.get(nombre='SIC_Clasificadores_LimiteExistencia').get_value()
	modulo=Registry.objects.get(nombre='SIC_Clasificadores_Modulo').get_value()
	tipo_documento=Registry.objects.get(nombre='SIC_Clasificadores_Tipo_Documento').get_value()
	base_datos_automatica=Registry.objects.get(nombre='SIC_Clasificadores_BD_Automatica').get_value()
	cliente_id=Registry.objects.get(nombre='SIC_Clasificadores_Cliente_predeterminado').get_value()
	cliente=first_or_none(Cliente.objects.filter(id=cliente_id))
	tiempo_espera=Registry.objects.get(nombre='SIC_Clasificadores_Tiempo_Espera').get_value()
	clasificador_padre_id=Registry.objects.get(nombre='SIC_Clasificadores_Clasificador_Padre').get_value()
	cajero_id=Registry.objects.get(nombre='SIC_Clasificadores_Cajero').get_value()
	caja_id=Registry.objects.get(nombre='SIC_Clasificadores_Caja').get_value()
	cajero=first_or_none(Cajero.objects.filter(id=cajero_id))
	caja=first_or_none(Caja.objects.filter(id=caja_id))
	clasificador_padre=first_or_none(Clasificadores.objects.filter(clasificador_id=clasificador_padre_id))

	email= Registry.objects.get( nombre = 'SIC_Clasificadores_Email').get_value()
	password= Registry.objects.get( nombre = 'SIC_Clasificadores_Password').get_value()
	servidor_correo= Registry.objects.get( nombre = 'SIC_Clasificadores_Servidro_Correo').get_value()
	puerto= Registry.objects.get( nombre = 'SIC_Clasificadores_Puerto').get_value()
	compatible= Registry.objects.get( nombre = 'SIC_Clasificadores_Compatible').get_value()
	venta= Registry.objects.get( nombre = 'SIC_Clasificadores_Venta').get_value()
	imagenes= Registry.objects.get( nombre = 'SIC_Clasificadores_Imagenes').get_value()
	descripcion_correo= Registry.objects.get( nombre = 'SIC_Clasificadores_Descripcion_Correo').get_value()

	linea_id=Registry.objects.get(nombre='SIC_Clasificadores_Linea').get_value()
	linea=first_or_none(LineaArticulos.objects.filter(id=linea_id))

	valores_calsificador_padre=ClasificadoresValores.objects.filter(clasificador=clasificador_padre)
	all_valores=ClasificadoresValores.objects.exclude(valor_clasif_id__in=valores_calsificador_padre)

	clasificadores_padre_existentes=ClasificadorAsignacion.objects.filter(clasificador_padre=clasificador_padre_id).values_list('clasificador_asignado')
	clasificadores_padre_todos=ClasificadorAsignacion.objects.filter(clasificador_padre=clasificador_padre_id)
	todos_clasificadores=ClasificadoresValores.objects.filter(valor_clasif_id__in=clasificadores_padre_existentes)
	for clas in todos_clasificadores:
		for clas_todos in clasificadores_padre_todos:
			if clas.valor_clasif_id == clas_todos.clasificador_asignado:
				clas.valor_padre=clas_todos.clasificador_padre_valor

	if limite_existencia == "True":
		limite_existencia=True
	else:
		limite_existencia=False
	if compatible == "True":
		compatible=True
	else:
		compatible=False
	if venta == "True":
		venta=True
	else:
		venta=False
	if imagenes == "True":
		imagenes=True
	else:
		imagenes=False

	print("*****")
	print(venta)
	
	form_initial=None
	if cliente:
		form_initial = {
			'cliente':cliente,
			'tiempo_espera':tiempo_espera,
			'clasificador_padre':clasificador_padre,
			'cajero':cajero,
			'caja':caja,
			'limite_existencia':limite_existencia,
			'modulo':modulo,
			'tipo_documento':tipo_documento,
			'base_datos_automatica':base_datos_automatica,
			'email':email,
			'password':password,
			'servidor_correo':servidor_correo,
			'puerto':puerto,
			'compatible':compatible,
			'venta':venta,
			'descripcion_correo':descripcion_correo,
			'imagenes':imagenes,
			'linea':linea,
		}

	form = PreferenciasManageForm(request.POST or None,initial=form_initial,conexion_activa = request.session['conexion_activa'])
	if form.is_valid():
		form.save()
		valores_calsificador_padre=ClasificadoresValores.objects.filter(clasificador=clasificador_padre)
		all_valores=ClasificadoresValores.objects.exclude(valor_clasif_id__in=valores_calsificador_padre)

	context = {
		'form': form,
		'valores_calsificador_padre':valores_calsificador_padre,
		'all_valores':all_valores,
		'todos_clasificadores':todos_clasificadores,
	}
	return render(request, 'djmicrosip_clasificadores/preferencias.html', context)

def actualiza_base_datos(request):
	
	try:
		padre = first_or_none(Registry.objects.filter(nombre='PreferenciasEmpresa'))
		if not Registry.objects.filter( nombre = 'SIC_Clasificadores_Cliente_predeterminado' ).exists():
				Registry.objects.create(
					nombre = 'SIC_Clasificadores_Cliente_predeterminado',
					tipo = 'V',
					padre = padre,
					valor= '',
				)
		if not Registry.objects.filter( nombre = 'SIC_Clasificadores_Pedido_Temporal_Id' ).exists():
				Registry.objects.create(
					nombre = 'SIC_Clasificadores_Pedido_Temporal_Id',
					tipo = 'V',
					padre = padre,
					valor= '',
				)
		using = router.db_for_write(Articulo)
		print("**************************")
		print(using)
		management.call_command('syncdb', database=using)
	except Exception as e:
		pass

	return redirect('/pedidos_web/preferencias/')

def crear_pedido_temporal(request):

	if request.GET.get('lista_articulos'):
		lista_articulos=json.loads(request.GET.get('lista_articulos'))
	if request.GET.get('pedido_id'):
		pedido_id=request.GET.get('pedido_id')
		print("id",pedido_id)
	using = router.db_for_write(Articulo)
	c = connections[using].cursor()
	# modulo=Registry.objects.get(nombre='SIC_Clasificadores_Modulo').get_value()
	# tipo_documento=Registry.objects.get(nombre='SIC_Clasificadores_Tipo_Documento').get_value()
	# if modulo=="PV":
	# 	pedido=first_or_none(PuntoVentaDocumento.objects.filter(folio=pedido_id,tipo='O'))
	# elif modulo=="V":
	# 	pedido=first_or_none(VentasDocumento.objects.filter(folio=pedido_id,tipo=tipo_documento))
	#print(pedido)
	for detalle in lista_articulos:
		# print(detalle["id"],detalle["cantidad"])
		articulo=first_or_none(Articulo.objects.filter(id=detalle["id"]))
		print(articulo)
		query = ''' EXECUTE PROCEDURE PRECIO_CON_IMPTO(%s, %s,'N','Q','N')'''
		c.execute(query, [articulo.id, detalle["precio"]])
		precio_sin_impuesto = c.fetchall()[0][0] 
		carrito_temporal=first_or_none(CarritoTemporal.objects.filter(id=pedido_id))
		obj=first_or_none(CarritoTemporalDetalle.objects.filter(carrito_temporal=carrito_temporal,articulo=articulo))
		if obj:
			obj.cantidad=detalle["cantidad"]
			obj.precio=detalle["precio"]
			obj.save()
		else:
			CarritoTemporalDetalle.objects.create(
					carrito_temporal=carrito_temporal,
					articulo=articulo,
					cantidad=detalle["cantidad"],
					precio=detalle["precio"],
				)
		# if modulo=="PV":
		# 	obj = first_or_none(PuntoVentaDocumentoDetalle.objects.filter(documento_pv=pedido,articulo=articulo))
		# 	if obj:
		# 		obj.unidades=detalle["cantidad"]
		# 		obj.precio_total_neto=detalle["precio"]*detalle["cantidad"]
		# 		obj.save()
		# 	else:
		# 		PuntoVentaDocumentoDetalle.objects.create(
		# 			id =-1,
		# 			documento_pv=pedido,
		# 			articulo=articulo,
		# 			unidades=detalle["cantidad"],
		# 			precio_unitario=precio_sin_impuesto,
		# 			precio_unitario_impto=detalle["precio"],
		# 			precio_total_neto=detalle["precio"]*detalle["cantidad"],
		# 			porcentaje_descuento=0,
		# 			porcentaje_comis=0,
		# 			clave_articulo=detalle["clave"],
		# 			rol='N',
		# 			posicion=-1,
		# 			unidades_dev=0,
		# 			)
		# elif modulo=="V":
		# 	obj = first_or_none(VentasDocumentoDetalle.objects.filter(documento=pedido,articulo=articulo))
		# 	if obj:
		# 		obj.unidades=detalle["cantidad"]
		# 		obj.precio_total_neto=detalle["precio"]*detalle["cantidad"]
		# 		obj.save()
		# 	else:
		# 		VentasDocumentoDetalle.objects.create(
		# 			documento=pedido,
		# 			articulo=articulo,
		# 			unidades=detalle["cantidad"],
		# 			precio_unitario=detalle["precio"],
		# 			precio_total_neto=detalle["precio"]*detalle["cantidad"],
		# 			articulo_clave=detalle["clave"],
		# 			)
	
	data={}

	return HttpResponse(json.dumps(data), content_type='application/json')

def view_pedido(request,id):
	cliente_id=Registry.objects.get(nombre='SIC_Clasificadores_Cliente_predeterminado').get_value()
	total=0
	total2=0
	modulo=Registry.objects.get(nombre='SIC_Clasificadores_Modulo').get_value()
	tipo_documento=Registry.objects.get(nombre='SIC_Clasificadores_Tipo_Documento').get_value()
	folio_pedido=None
	mensaje=""
	# if modulo=="PV":
	# 	venta=first_or_none(PuntoVentaDocumento.objects.filter(id=id,tipo='O'))
	# 	detalle_venta=PuntoVentaDocumentoDetalle.objects.filter(documento_pv=venta)
	# elif modulo=="V":
	# 	venta=first_or_none(VentasDocumento.objects.filter(id=id,tipo=tipo_documento))
	# 	detalle_venta=VentasDocumentoDetalle.objects.filter(documento=venta)
	carrito_temporal=CarritoTemporal.objects.get(id=id)
	print("---------carrito_temporal-------")
	print(carrito_temporal)
	detalle_venta=CarritoTemporalDetalle.objects.filter(carrito_temporal=carrito_temporal)
	using = router.db_for_write(Articulo)
	c = connections[using].cursor()
	if request.method=='POST' and 'guardar' in request.POST:
		data=definir_documento(request,folio_pedido)
		pedido=data["pedido"]

		for detalle in detalle_venta:
			query = ''' EXECUTE PROCEDURE PRECIO_CON_IMPTO(%s, %s,'N','Q','N')'''
			c.execute(query, [detalle.articulo.id, detalle.precio])
			precio_sin_impuesto = c.fetchall()[0][0] 
			
			c.execute("EXECUTE PROCEDURE GET_CLAVE_ART %s;" %(detalle.articulo.id) )
			clave=c.fetchall()[0][1]
			
			total=total+(precio_sin_impuesto*detalle.cantidad)
			total2=total2+(detalle.precio*detalle.cantidad)
			
			if modulo=="PV":
					PuntoVentaDocumentoDetalle.objects.create(
						id =-1,
						documento_pv=pedido,
						articulo=detalle.articulo,
						unidades=detalle.cantidad,
						precio_unitario=precio_sin_impuesto,
						precio_unitario_impto=detalle.precio,
						precio_total_neto=precio_sin_impuesto*detalle.cantidad,
						porcentaje_descuento=0,
						porcentaje_comis=0,
						clave_articulo=clave,
						rol='N',
						posicion=-1,
						unidades_dev=0,
						)
			elif modulo=="V":
					VentasDocumentoDetalle.objects.create(
						documento=pedido,
						articulo=detalle.articulo,
						unidades=detalle.cantidad,
						precio_unitario=precio_sin_impuesto,
						precio_total_neto=precio_sin_impuesto*detalle.cantidad,
						articulo_clave=clave,
						)

		impuesto=first_or_none(Impuesto.objects.filter(es_predet='S'))
		if modulo=="PV":
			pedido.total_impuestos=total2-total
			# pedido.save()
			pedido.importe_neto=total
			pedido.save()
			query = ''' INSERT INTO impuestos_doctos_pv(DOCTO_PV_ID,IMPUESTO_ID,VENTA_NETA,PCTJE_IMPUESTO,IMPORTE_IMPUESTO) VALUES(%s,%s,%s,%s,%s) '''
			c.execute(query, [pedido.id,impuesto.id,total,impuesto.porcentaje,total2-total])
			# PuntoVentaDocumentoImpuesto.objects.create(
			# 	documento_pv=pedido,
			# 	impuesto=impuesto,
			# 	venta_neta=total,
			# 	porcentaje_impuestos=impuesto.porcentaje,
			# 	importe_impuesto=total2-total
			# 	)

			carrito_temporal.delete()
			mensaje="PEDIDO GURDADO CORRECTAMENTE"
		elif modulo=="V":
			pedido.impuestos_total=total2-total
			# pedido.save()
			pedido.importe_neto=total
			pedido.save()
			print("///////////////////////////")
			print(pedido.impuestos_total)
			query = ''' INSERT INTO impuestos_doctos_ve(DOCTO_VE_ID,IMPUESTO_ID,VENTA_NETA,PCTJE_IMPUESTO,IMPORTE_IMPUESTO) VALUES(%s,%s,%s,%s,%s) '''
			c.execute(query, [pedido.id,impuesto.id,total,impuesto.porcentaje,total2-total])
			carrito_temporal.delete()
			mensaje="PEDIDO GURDADO CORRECTAMENTE"
			# VentasDocumentoImpuesto.objects.create(
			# 	documento=pedido,
			# 	impuesto=impuesto,
			# 	venta_neta=total,
			# 	porcentaje=impuesto.porcentaje,
			# 	importe=total2-total
			# 	)
		return redirect('/pedidos_web/?mensaje='+mensaje)
		
	if request.method=='POST' and 'eliminar' in request.POST:
		carrito_temporal.delete()
		mensaje="PEDIDO ELIMINADO"
		

		return redirect('/pedidos_web/')
	
	for detalle in detalle_venta:
		total=total+(detalle.precio*detalle.cantidad)
		print(total)
		detalle.precio_neto=detalle.precio*detalle.cantidad
	context = {
		"venta":carrito_temporal,
		"detalle_venta":detalle_venta,
		"cantidad_pedido":len(detalle_venta),
		"total":total,
		"mensaje":mensaje,
	}
	return render(request, 'djmicrosip_clasificadores/view_pedido.html', context)

def info_cliente(id_cliente):
	almacen=first_or_none(Almacen.objects.filter(ALMACEN_ID=19))
	if id_cliente:
		direcciones_cliente = ClienteDireccion.objects.filter(cliente_id=id_cliente)
		cliente_clave = ClienteClave.objects.filter(cliente__id=id_cliente)
		cliente=Cliente.objects.filter(id=id_cliente)[0]
		moneda=cliente.moneda
		condicion_de_pago=cliente.condicion_de_pago
		#print(moneda.id,condicion_de_pago.id)
		# print(direcciones_cliente)
	if cliente_clave:
		clave_cliente=cliente_clave[0].clave
	else:
		clave_cliente=""
	lista_direccion={}
	direccion={}

	for direccion_cliente in direcciones_cliente:
		if direccion_cliente.es_ppal:
			direccion=direccion_cliente
	print(direccion)
	data={
		'direccion':direccion,
		'cliente':cliente,
		'clave':clave_cliente,
		'moneda':moneda,
		'condicion_de_pago':condicion_de_pago,
		'almacen':almacen,
		}
	return data

def clasificador_asignacion(request):
	if request.GET.get('lista_clasificadores'):
		lista_clasificadores=json.loads(request.GET.get('lista_clasificadores'))
	if request.GET.get('clasificador_padre_valor'):
		clasificador_padre_valor=request.GET.get('clasificador_padre_valor')
	if request.GET.get('clasificador_padre'):
		clasificador_padre=request.GET.get('clasificador_padre')
	data={}
	print(lista_clasificadores)
	clasificadores_asignacion=ClasificadorAsignacion.objects.filter(clasificador_padre=clasificador_padre,clasificador_padre_valor=clasificador_padre_valor)
	
	for clas_asign in clasificadores_asignacion:
		if not clas_asign.clasificador_asignado in lista_clasificadores:
			clas_asign.delete()

	for clasificador in lista_clasificadores:
		ClasificadorAsignacion.objects.get_or_create(clasificador_padre=clasificador_padre,clasificador_padre_valor=clasificador_padre_valor, clasificador_asignado=clasificador)

	return HttpResponse(json.dumps(data), content_type='application/json')

def crear_usuarios_clientes(request):
	if request.GET.get('cliente_id'):
		cliente_id=request.GET.get('cliente_id')
	cliente=first_or_none(Cliente.objects.filter(id=cliente_id))
	inf_cliente=first_or_none(ClienteDireccion.objects.filter(cliente=cliente,es_ppal='S'))
	password=""
	if inf_cliente.rfc_curp:
		try:
			usuario = User.objects.get(username__exact=inf_cliente.rfc_curp)
			password=""
		except ObjectDoesNotExist:
			rfc=(inf_cliente.rfc_curp).replace("-","")
			rfc=rfc.replace(" ","")
			print(rfc)
			password = randomString(10)
			guardar=str(password)+","+inf_cliente.email
			user = User.objects.create_user(username = rfc, password=password,first_name=cliente.nombre,last_name='usuario_externo',email=guardar)
			usuario_cliente=ClienteUsuario.objects.get_or_create(cliente=cliente,usuario=user.id)

			using = router.db_for_write(Articulo)
			c = connections[using].cursor()
			query = "CREATE USER %s PASSWORD '%s' active"%(rfc,password)
			c.execute(query)
			c.execute('COMMIT')
	
	data={
		"password":password,
	}


	return HttpResponse(json.dumps(data), content_type='application/json')

def usuario_cliente(request):
	clientes=Cliente.objects.filter(estatus='A')

	page = request.GET.get('page')

	form_busqueda=FilterForm(request.POST or None)
	
	if form_busqueda.is_valid():
		busqueda=form_busqueda.cleaned_data['busqueda']
		print(busqueda)
		if busqueda:
			clientes=clientes.filter(nombre__icontains=busqueda)

	paginator = Paginator(clientes, 50) 
	try:
		clientes = paginator.page(page)
	except PageNotAnInteger:
		
		clientes = paginator.page(1)
	except EmptyPage:
		
		clientes = paginator.page(paginator.num_pages)

	for cliente in clientes:
		cliente_usuario=first_or_none(ClienteUsuario.objects.filter(cliente=cliente))
		if cliente_usuario:
			client_usuario=first_or_none(User.objects.filter(id=cliente_usuario.usuario))
			cliente.usuario=client_usuario

	clientes_usuario=User.objects.all()
	
	context = {
		"clientes_usuario":clientes_usuario,
		"clientes":clientes,
		"form_busqueda":form_busqueda,
	}
	
	return render(request, 'djmicrosip_clasificadores/usuarios_clientes.html', context)

def compatibilidad_articulos(request):
	articulos=Articulo.objects.filter(estatus='A').order_by('nombre')
	cliente_id=Registry.objects.get(nombre='SIC_Clasificadores_Cliente_predeterminado').get_value()
	form=FilterForm(request.POST or None)
	busqueda=None
	
	page = request.GET.get('page')
	busqueda = request.GET.get('busqueda')

	if form.is_valid():
		busqueda=form.cleaned_data['busqueda']
		if  busqueda:
			print(busqueda)
			articulos_clave=ArticuloClave.objects.filter(Q(articulo__nombre__icontains=busqueda)|Q(clave__icontains=busqueda)).filter(rol__es_ppal='S').values_list(
			'articulo__id')
			articulos=articulos.filter(id__in=articulos_clave)
	else:
		if  busqueda:
			print(busqueda)
			articulos_clave=ArticuloClave.objects.filter(Q(articulo__nombre__icontains=busqueda)|Q(clave__icontains=busqueda)).filter(rol__es_ppal='S').values_list(
			'articulo__id')
			articulos=articulos.filter(id__in=articulos_clave)
	
	paginator = Paginator(articulos, 50) 
	try:
		articulos = paginator.page(page)
	except PageNotAnInteger:
		
		articulos = paginator.page(1)
	except EmptyPage:
		
		articulos = paginator.page(paginator.num_pages)
	
	for articulo in articulos:
		data=GetArticulo(articulo.id,19,cliente_id)
		articulo.clave=data["clave"]

	context = {
		'articulos':articulos,
		'form':form,
		'busqueda':busqueda,
	}
	
	return render(request, 'djmicrosip_clasificadores/compatibilidad.html', context)

def asignar_compatibilidad_articulos(request,id):
	articulo=Articulo.objects.get(id=id)
	compatibilidad=ArticulosCompatibilidad.objects.filter(articulo__id=id)
	ids=compatibilidad.values_list('articulo_compatible')
	print(ids)
	articulos_compatibilidad=Articulo.objects.filter(id__in=ids)
	lista_articulos_compatibilidad=compatibilidad.values_list('articulo__id')
	
	form=ArticuloFindForm(request.POST or None)
	articulos=None
	
	if form.is_valid():
		articulos=Articulo.objects.exclude(id__in=ids)
		nombre=form.cleaned_data['nombre']
		linea=form.cleaned_data['linea']
		grupo=form.cleaned_data['grupo']
		print(nombre,linea,grupo)
		if nombre:
			articulos=articulos.filter(nombre__icontains=nombre)
		if linea:
			articulos=articulos.filter(linea=linea)
		if grupo:
			articulos=articulos.filter(linea__grupo=grupo)
	
	context = {
		'articulo':articulo,
		'articulos':articulos,
		'articulos_compatibilidad':articulos_compatibilidad,
		'form':form,
	}
	
	return render(request, 'djmicrosip_clasificadores/asignar_compatibilidad_articulos.html', context)

def guardar_articulos_compatibles(request):
	if request.GET.get('lista_articulos'):
		lista_articulos=json.loads(request.GET.get('lista_articulos'))
	if request.GET.get('articulo_id'):
		articulo_id=request.GET.get('articulo_id')
	articulo=Articulo.objects.get(id=articulo_id)
	articulos_compatibilidad=ArticulosCompatibilidad.objects.filter(articulo__id=articulo_id)
	lista_articulos_compatibilidad=articulos_compatibilidad.values_list('articulo_compatible')
	
	for arti_comp in articulos_compatibilidad:
		if arti_comp.articulo_compatible in lista_articulos:
			ArticulosCompatibilidad.objects.get_or_create(articulo=articulo ,articulo_compatible=arti_comp.articulo_compatible)
		else:
			arti_comp.delete()

	for art in lista_articulos:
		if not art in lista_articulos_compatibilidad:
			ArticulosCompatibilidad.objects.get_or_create(articulo=articulo ,articulo_compatible=art)
	
	print(lista_articulos)
	data={}


	return HttpResponse(json.dumps(data), content_type='application/json')

def cambiar_contrasena(request):
	articulos=None
	username=request.user.username
	form_initial={
		'usuario':username,
		'anterior_contrasena':None,
		'nueva_contrasena':None,
	}
	mensaje=None
	form=UsuarioForm(request.POST or None,initial=form_initial)
	
	if form.is_valid():
		try:
			usuario=form.cleaned_data['usuario']
			anterior_contrasena=form.cleaned_data['anterior_contrasena']	
			nueva_contrasena=form.cleaned_data['nueva_contrasena']
			usuario=User.objects.get(username__exact=usuario)
			usuario.set_password(nueva_contrasena)
			email_separar=usuario.email.split(",")
			contrasena=email_separar[0]
			correos=email_separar[1]
			contrasena=nueva_contrasena+","+email_separar[1]
			usuario.email=contrasena
			usuario.save()
			using = router.db_for_write(Articulo)
			c = connections[using].cursor()
			query = "ALTER USER %s PASSWORD '%s'"%(username,nueva_contrasena)
			c.execute(query)
			c.execute('COMMIT')
			mensaje=u"Cambio de contraseña exitoso"
		except Exception as e:
			mensaje=u"Ocurrio un error al cambiar la contraseña, intentelo mas tarde o contacte con el administrador"
	context={
		'form':form,
		'mensaje':mensaje,
	}
	return render(request, 'djmicrosip_clasificadores/cambiar_contraseña.html', context)

def recuperar_contrasena(request):
	mensaje=""
	if request.method=='POST' and 'enviar' in request.POST:
		try:
			usuario=first_or_none(User.objects.filter(id=request.POST["id_usuario"]))
			email_separar=usuario.email.split(",")
			contrasena=email_separar[0]
			correos=email_separar[1]
			destinatarios=(correos).split(';')
			email = DatabaseSucursal.objects.get(name='SIC_Clasificadores_Email')
			password = DatabaseSucursal.objects.get(name='SIC_Clasificadores_Password')
			servidor_correo = DatabaseSucursal.objects.get(name='SIC_Clasificadores_Servidro_Correo')
			puerto = DatabaseSucursal.objects.get(name='SIC_Clasificadores_Puerto')
			descripcion_correo= Registry.objects.get( nombre = 'SIC_Clasificadores_Descripcion_Correo').get_value()
			print(usuario,email,password,servidor_correo,puerto)
			file=None
			contenido=u"<html lang='es'><p>%s %s</p><p><strong>USUARIO: %s</strong></p><p><strong>CONTRSEÑA: %s</strong></p></html>"%(descripcion_correo,usuario.first_name,usuario.username,str(contrasena))
			nombre=""
			data={}
			bandera=send_mail_contrasena(servidor_correo.empresa_conexion,puerto.empresa_conexion,email.empresa_conexion,password.empresa_conexion,destinatarios,"CONTRSEÑA DE ACCESO",contenido,file,nombre)
			mensaje=u"Reenvio correcto"
		except Exception as e:
			print(e)
			mensaje=u"Ocurrio un error al enviar la contraseña, intentelo mas tarde o contacte con el administrador"


	print(mensaje)
	context={
		'mensaje':mensaje,
	}
	return render(request, 'djmicrosip_clasificadores/recuperar_contrasena.html', context)

def find_user(request):
	usuario=None
	if request.GET.get('nombre_cliente'):
		nombre_cliente=request.GET.get('nombre_cliente')
		try:
			usuario = User.objects.get(username__exact=nombre_cliente)
		except ObjectDoesNotExist:
			usuario=None
	data={}

	if usuario:
		data["mensaje"]="Si"
		data["id_usuario"]=str(usuario.id)
	else:
		data["mensaje"]="No"
		data["id_cliente"]=""

	return HttpResponse(json.dumps(data), content_type='application/json')

def save_img(request):
	usuario=None
	articulo_anex=None
	if request.GET.get('articulo_id'):
		articulo_id=request.GET.get('articulo_id')
		articulo=first_or_none(Articulo.objects.filter(id=articulo_id))

	# if request.GET.get('img_art'):
	# 	img_art=request.GET.get('img_art')
	# 	dat_img_art=img_art.split(".")

	# if request.GET.get('pedm_art'):
	# 	pedm_art=request.GET.get('pedm_art')
	# 	dat_pedm_art=pedm_art.split(".")
	
	if request.GET.get('img_art_data'):
		if articulo:
			articulo_anex=ArticuloAnexos.objects.get_or_create(articulo=articulo,imagen_art=None)[0]
			#print("****************")
			#print(articulo_anex)
		pedm_art_data=request.GET.get('img_art_data')
		data_url_pattern = re.compile('data:image/(png|jpeg);base64,(.*)$')
		#signature_url = pedm_art_data
		
		if pedm_art_data is not None and len(pedm_art_data) > 0:

			signature_data = data_url_pattern.match(pedm_art_data).group(2)
			signature_data = bytes(signature_data, encoding='utf8')
			missing_padding = len(signature_data) % 4
			if missing_padding != 0:
				signature_data += b'='* (4 - missing_padding)
			
			signature_data = base64.b64decode(signature_data)	
			img_io = io.BytesIO(signature_data)
			img = Image.open(img_io)
			
		if articulo_anex:
			url_pedm_art=str(articulo.id)+"_"+str(articulo_anex.id)+".png"
			img.save(settings.MEDIA_ROOT+'\\imagenes_articulos\\'+url_pedm_art)

			articulo_anex.imagen_art='imagenes_articulos/'+url_pedm_art
			articulo_anex.save()
	
	if request.GET.get('pedm_art_data'):
		if articulo:
			articulo_anex=first_or_none(ArticuloAnexos.objects.filter(articulo=articulo))
			if not articulo_anex:
				articulo_anex=ArticuloAnexos.objects.get_or_create(articulo=articulo)[0]
			print("****************")
			print(articulo_anex)
		pedm_art_data=request.GET.get('pedm_art_data')
		data_url_pattern = re.compile('data:image/(png|jpeg);base64,(.*)$')
		signature_url = pedm_art_data
		signature_data = data_url_pattern.match(signature_url).group(2)
		signature_data = bytes(signature_data)
		signature_data = decodestring(signature_data)
		img_io = io.BytesIO(signature_data)
		if articulo_anex:
			url_pedm_art=str(articulo.id)+".png"
			articulo_anex.pedm_art.save(url_pedm_art, File(img_io))
	#print(img_art)
	#print(pedm_art)
	#print(img_art_data)
	#print(pedm_art_data)
	
	data={}
	data["mensaje"]="Imagen Guardada"
	


	return HttpResponse(json.dumps(data), content_type='application/json')

def enviar_contrasena(request,id):
	cliente=ClienteDireccion.objects.get(cliente__id=id)
	usuario_cliente=first_or_none(ClienteUsuario.objects.filter(cliente__id=id))
	usuario=first_or_none(User.objects.filter(id=usuario_cliente.usuario))
	destinatarios=(cliente.email).split(';')
	datos_empresa = Registry.objects.get(nombre='DatosEmpresa')
	datos_empresa = Registry.objects.filter(padre=datos_empresa)
	nombre=datos_empresa.get(nombre='Nombre').get_value()
	email= Registry.objects.get( nombre = 'SIC_Clasificadores_Email').get_value()
	password= Registry.objects.get( nombre = 'SIC_Clasificadores_Password').get_value()
	servidor_correo= Registry.objects.get( nombre = 'SIC_Clasificadores_Servidro_Correo').get_value()
	puerto= Registry.objects.get( nombre = 'SIC_Clasificadores_Puerto').get_value()
	descripcion_correo= Registry.objects.get( nombre = 'SIC_Clasificadores_Descripcion_Correo').get_value()
	#superkarelyrubio@hotmail.com
	email_separar=usuario.email.split(",")
	contrasena=email_separar[0]
	correos=email_separar[1]
	file=None
	contenido=u"<html lang='es'><p>%s %s</p><p><strong>USUARIO: %s</strong></p><p><strong>CONTRSEÑA: %s</strong></p></html>"%(descripcion_correo,cliente.cliente.nombre,usuario.username,str(contrasena))
	nombre=""
	data={}
	bandera=send_mail_contrasena(servidor_correo,puerto,email,password,destinatarios,"CONTRSEÑA DE ACCESO",contenido,file,nombre)
	if bandera:
		data["mensaje"]="Correo Enviado"
		print(data)
	else:
		data["mensaje"]="Hubo un error al enviar el correo"
		print(data)

	return HttpResponse(json.dumps(data), content_type='application/json')
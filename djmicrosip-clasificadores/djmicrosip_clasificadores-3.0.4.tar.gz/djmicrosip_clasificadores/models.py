from django.db import models
#Python
from datetime import datetime
#Own
from .storage import OverwriteStorage
from django.contrib.auth.models import User
from django_microsip_base.libs.models_base.models import Articulo,Cliente
from decimal import Decimal


class ClasificadorAsignacion(models.Model):
	clasificador_padre=models.IntegerField(blank=True, null=True, db_column='CLASIFICADOR_PADRE')
	clasificador_padre_valor=models.IntegerField(blank=True, null=True, db_column='CLASIFICADOR_PADRE_VALOR')
	clasificador_asignado=models.IntegerField(blank=True, null=True, db_column='CLASIFICADOR_ASIGNADO')

	class Meta:
		db_table = 'SIC_CLASIFICADOR_ASIGNACION'
		app_label = 'models_base'

class ArticulosCompatibilidad(models.Model):
	id=models.AutoField(primary_key=True, db_column='ARTICULOS_COMPATIBILIDAD_ID')
	articulo=models.ForeignKey('Articulo', blank=True, null=True, db_column='ARTICULO_ID',on_delete=models.CASCADE)
	articulo_compatible=models.IntegerField(blank=True, null=True, db_column='ARTICULO_COMPATIBLE')

	class Meta:
		db_table = 'SIC_ARTICULOS_COMPATIBILIDAD'
		app_label = 'models_base'

class ArticuloAnexos(models.Model):
	id=models.AutoField(primary_key=True, db_column='ARTICULO_ANEXO_ID')
	articulo=models.ForeignKey('Articulo', blank=True, null=True, db_column='ARTICULO_ID',on_delete=models.CASCADE)
	imagen_art = models.ImageField(blank=True, null=True , upload_to='imagenes_articulos', db_column='SIC_IMAGEN_ART', storage=OverwriteStorage())
	pedm_art = models.ImageField(blank=True, null=True , upload_to='pedimentos_articulos', db_column='SIC_PEDM_ART', storage=OverwriteStorage())
	

	class Meta:
		db_table = 'SIC_ARTICULO_ANEXOS'
		app_label = 'models_base'

# class ClienteUsuario(models.Model):
# 	id=models.AutoField(primary_key=True, db_column='CLIENTE_USUARIO_ID')
# 	cliente=models.ForeignKey('Cliente', blank=True, null=True, db_column='CLIENTE_ID',on_delete=models.CASCADE)
# 	usuario=models.IntegerField(blank=True, null=True, db_column='USUARIO_ID')

# 	class Meta:
# 		db_table = 'SIC_CLIENTE_USUARIO'
# 		app_label = 'models_base'

class CarritoTemporal(models.Model):
	id=models.AutoField(primary_key=True, db_column='CARRITO_TEMPORAL_ID')
	folio= models.CharField(max_length=9,db_column='FOLIO',null=True)
	cliente = models.ForeignKey('Cliente', blank=True, null=True, db_column='CLIENTE_ID',on_delete=models.CASCADE)
	
	class Meta:
		db_table = 'SIC_CARRITO_TEMP'
		app_label = 'models_base'

class CarritoTemporalDetalle(models.Model):
	id=models.AutoField(primary_key=True, db_column='CARRITO_TEMPORAL_DET_ID')
	carrito_temporal=models.ForeignKey('CarritoTemporal', db_column='CARRITO_TEMPORAL_ID',on_delete=models.CASCADE)
	articulo=models.ForeignKey('Articulo', db_column='ARTICULO_ID',on_delete=models.CASCADE)
	cantidad = models.DecimalField(max_digits=18, decimal_places=6,db_column='CANTIDAD')
	precio = models.DecimalField(max_digits=18, decimal_places=6,db_column='PRECIO')
	
	class Meta:
		db_table = 'SIC_CARRITO_TEMP_DET'
		app_label = 'models_base'
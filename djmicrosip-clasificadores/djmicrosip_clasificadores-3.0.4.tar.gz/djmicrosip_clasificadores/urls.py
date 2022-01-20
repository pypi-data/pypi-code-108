# from django.conf.urls import patterns, url
from django.urls import path,include
from .views import *

urlpatterns = (
	path('', index),
	path('preferencias/', preferencias),
	path('get_todos_almacenes/', get_todos_almacenes),
	path('compatibilidad_articulo/', compatibilidad_articulo),
	path('actualiza_base_datos/', actualiza_base_datos),
	path('crear_pedido_temporal/', crear_pedido_temporal),
	path('clasificador_asignacion/', clasificador_asignacion),
	path('crear_usuarios_clientes/', crear_usuarios_clientes),
	path('usuario_cliente/', usuario_cliente),
	path('cambiar_contrasena/', cambiar_contrasena),
	path('recuperar_contrasena/', recuperar_contrasena),
	path('find_user/', find_user),
	path('save_img/', save_img),
	path('enviar_contrasena/<int:id>/', enviar_contrasena),
	path('compatibilidad_articulos/', compatibilidad_articulos),
	path('guardar_articulos_compatibles/', guardar_articulos_compatibles),
	path('asignar_compatibilidad_articulos/<int:id>/', asignar_compatibilidad_articulos),
	path('eliminar_detalle/<int:id_detalle>/<int:id_pedido>/', eliminar_detalle),
	path('view_pedido/<int:id>/', view_pedido),
)


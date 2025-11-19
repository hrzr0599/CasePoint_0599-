from django.contrib import admin
from .models import Usuario, Marca, Producto, Pedido, ProductoPedido, Empleado

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
	list_display = ('id', 'nombre', 'apellido', 'correo', 'telefono')


@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
	list_display = ('id', 'nombre', 'pais_origen', 'fundador')


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
	list_display = ('id', 'nombre', 'precio', 'stock', 'id_marca', 'departamento', 'categoria')


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
	list_display = ('id', 'id_usuario', 'fecha_pedido', 'estado_pedido', 'total')


@admin.register(ProductoPedido)
class ProductoPedidoAdmin(admin.ModelAdmin):
	list_display = ('id', 'producto', 'pedido', 'cantidad')


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
	list_display = ('id', 'nombre', 'apellido', 'puesto', 'correo', 'telefono')

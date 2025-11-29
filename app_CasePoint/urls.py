from django.urls import path
from . import views

app_name = 'app_CasePoint'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('nosotros/', views.nosotros, name='nosotros'),
    path('departamentos/', views.departamentos, name='departamentos'),
    path('categorias/', views.categorias, name='categorias'),
    path('marcas/', views.marcas, name='marcas'),
    path('marca/<int:marca_id>/', views.marca_detalle, name='marca_detalle'),
    path('categoria/<str:categoria>/', views.categoria_detalle, name='categoria_detalle'),
    path('departamento/<str:departamento>/', views.departamento_detalle, name='departamento_detalle'),
    path('producto/<int:pk>/', views.producto_detalle, name='producto_detalle'),
    path('registrarse/', views.registrarse, name='registrarse'),
    path('iniciar_sesion/', views.iniciar_sesion, name='iniciar_sesion'),
    path('logout/', views.cerrar_sesion, name='logout'),
    path('perfil/', views.perfil, name='perfil'),

    # Cart
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/checkout/', views.checkout, name='checkout'),
    path('cart/payment/', views.payment_details, name='payment_details'),
    path('cart/confirm/', views.checkout_confirm, name='checkout_confirm'),

    # Admin (simple)
    path('empleado/login/', views.admin_login, name='admin_login'),
    path('empleado/', views.admin_home, name='admin_home'),

    # CRUD for Usuario (under empleado/)
    path('empleado/usuarios/', views.ver_usuarios, name='ver_usuarios'),
    path('empleado/usuarios/agregar/', views.agregar_usuario, name='agregar_usuario'),
    path('empleado/usuarios/actualizar/<int:pk>/', views.actualizar_usuario, name='actualizar_usuario'),
    path('empleado/usuarios/eliminar/<int:pk>/', views.eliminar_usuario, name='eliminar_usuario'),

    # CRUD for Marca
    path('empleado/marcas/', views.ver_marcas, name='ver_marcas'),
    path('empleado/marcas/agregar/', views.agregar_marca, name='agregar_marca'),
    path('empleado/marcas/actualizar/<int:pk>/', views.actualizar_marca, name='actualizar_marca'),
    path('empleado/marcas/eliminar/<int:pk>/', views.eliminar_marca, name='eliminar_marca'),

    # CRUD for Producto
    path('empleado/productos/', views.ver_productos, name='ver_productos'),
    path('empleado/productos/agregar/', views.agregar_producto, name='agregar_producto'),
    path('empleado/productos/actualizar/<int:pk>/', views.actualizar_producto, name='actualizar_producto'),
    path('empleado/productos/eliminar/<int:pk>/', views.eliminar_producto, name='eliminar_producto'),

    # CRUD for Pedido
    path('empleado/pedidos/', views.ver_pedidos, name='ver_pedidos'),
    path('empleado/pedidos/agregar/', views.agregar_pedido, name='agregar_pedido'),
    path('empleado/pedidos/ver/<int:pk>/', views.ver_pedido, name='ver_pedido'),
    path('empleado/pedidos/actualizar/<int:pk>/', views.actualizar_pedido, name='actualizar_pedido'),
    path('empleado/pedidos/eliminar/<int:pk>/', views.eliminar_pedido, name='eliminar_pedido'),

    # CRUD for Empleado
    path('empleado/empleados/', views.ver_empleados, name='ver_empleados'),
    path('empleado/empleados/agregar/', views.agregar_empleado, name='agregar_empleado'),
    path('empleado/empleados/actualizar/<int:pk>/', views.actualizar_empleado, name='actualizar_empleado'),
    path('empleado/empleados/eliminar/<int:pk>/', views.eliminar_empleado, name='eliminar_empleado'),
]

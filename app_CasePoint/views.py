from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponseRedirect
from decimal import Decimal

from .models import Usuario, Marca, Producto, Pedido, ProductoPedido, Empleado

# Helper: departments and categories from model choices
DEPARTMENTS = dict(Producto.DEPARTAMENTO_CHOICES)
CATEGORIES = dict(Producto.CATEGORIA_CHOICES)

def inicio(request):
    productos = Producto.objects.order_by('nombre').all()
    marcas = Marca.objects.order_by('nombre').all()
    return render(request, 'inicio.html', {'productos': productos, 'marcas': marcas})

def nosotros(request):
    return render(request, 'nosotros.html')

def departamentos(request):
    return render(request, 'departamentos.html', {'departamentos': Producto.DEPARTAMENTO_CHOICES})

def categorias(request):
    return render(request, 'categorias.html', {'categorias': Producto.CATEGORIA_CHOICES})

def marcas(request):
    marcas = Marca.objects.order_by('nombre').all()
    return render(request, 'marcas.html', {'marcas': marcas})

def marca_detalle(request, marca_id):
    marca = get_object_or_404(Marca, pk=marca_id)
    productos = marca.productos.order_by('nombre').all()
    return render(request, 'inicio.html', {
        'productos': productos,
        'marcas': Marca.objects.all(),
        'selected_brand': marca,
    })

def categoria_detalle(request, categoria):
    productos = Producto.objects.filter(categoria=categoria).order_by('nombre')
    # obtener etiqueta legible de la categoría (si existe en choices)
    categorias_map = dict(Producto.CATEGORIA_CHOICES)
    categoria_label = categorias_map.get(categoria, categoria)
    return render(request, 'inicio.html', {
        'productos': productos,
        'marcas': Marca.objects.all(),
        'selected_categoria': categoria,
        'selected_categoria_display': categoria_label,
    })

def departamento_detalle(request, departamento):
    productos = Producto.objects.filter(departamento=departamento).order_by('nombre')
    departamentos_map = dict(Producto.DEPARTAMENTO_CHOICES)
    departamento_label = departamentos_map.get(departamento, departamento)
    return render(request, 'inicio.html', {
        'productos': productos,
        'marcas': Marca.objects.all(),
        'selected_departamento': departamento,
        'selected_departamento_display': departamento_label,
    })

def producto_detalle(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    return render(request, 'producto_detalle.html', {'producto': producto})

def registrarse(request):
    if request.method == 'POST':
        data = request.POST
        usuario = Usuario.objects.create(
            nombre=data.get('nombre',''),
            apellido=data.get('apellido',''),
            correo=data.get('correo',''),
            telefono=data.get('telefono',''),
            direccion=data.get('direccion',''),
            contrasena=data.get('contrasena',''),
            codigo_postal=data.get('codigo_postal',''),
        )
        request.session['usuario_id'] = usuario.id
        return redirect('app_CasePoint:inicio')
    return render(request, 'registrarse.html')

def iniciar_sesion(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        contrasena = request.POST.get('contrasena')
        try:
            usuario = Usuario.objects.get(correo=correo, contrasena=contrasena)
            request.session['usuario_id'] = usuario.id
            return redirect('app_CasePoint:inicio')
        except Usuario.DoesNotExist:
            return render(request, 'iniciar_sesion.html', {'error': 'Credenciales inválidas'})
    return render(request, 'iniciar_sesion.html')

def cerrar_sesion(request):
    request.session.pop('usuario_id', None)
    request.session.pop('cart', None)
    return redirect('app_CasePoint:inicio')

def perfil(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('app_CasePoint:registrarse')
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    pedidos = usuario.pedidos.order_by('-fecha_pedido').all()
    if request.method == 'POST':
        data = request.POST
        usuario.nombre = data.get('nombre', usuario.nombre)
        usuario.apellido = data.get('apellido', usuario.apellido)
        usuario.correo = data.get('correo', usuario.correo)
        usuario.telefono = data.get('telefono', usuario.telefono)
        usuario.direccion = data.get('direccion', usuario.direccion)
        usuario.codigo_postal = data.get('codigo_postal', usuario.codigo_postal)
        if data.get('contrasena'):
            usuario.contrasena = data.get('contrasena')
        usuario.save()
        return redirect('app_CasePoint:perfil')
    return render(request, 'perfil.html', {'usuario': usuario, 'pedidos': pedidos})

# CART
def _get_cart(request):
    return request.session.setdefault('cart', {})

def add_to_cart(request, product_id):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('app_CasePoint:registrarse')
    cart = _get_cart(request)
    # single product only once per pedido
    if str(product_id) not in cart:
        cart[str(product_id)] = 1
    request.session['cart'] = cart
    return redirect('app_CasePoint:view_cart')

def view_cart(request):
    cart = _get_cart(request)
    items = []
    subtotal = Decimal('0.00')
    for pid, qty in cart.items():
        try:
            p = Producto.objects.get(pk=int(pid))
            items.append({'producto': p, 'cantidad': qty, 'total': p.precio * qty})
            subtotal += p.precio * qty
        except Producto.DoesNotExist:
            continue
    shipping = Decimal('10.00') if items else Decimal('0.00')
    total = subtotal + shipping
    return render(request, 'cart.html', {'items': items, 'subtotal': subtotal, 'shipping': shipping, 'total': total})

def remove_from_cart(request, product_id):
    cart = _get_cart(request)
    cart.pop(str(product_id), None)
    request.session['cart'] = cart
    return redirect('app_CasePoint:view_cart')

def checkout(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('app_CasePoint:registrarse')
    cart = _get_cart(request)
    if not cart:
        return redirect('app_CasePoint:view_cart')
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    items = []
    subtotal = Decimal('0.00')
    for pid, qty in cart.items():
        p = get_object_or_404(Producto, pk=int(pid))
        items.append({'producto': p, 'cantidad': qty, 'total': p.precio * qty})
        subtotal += p.precio * qty
    shipping = Decimal('10.00')
    total = subtotal + shipping
    return render(request, 'checkout.html', {'items': items, 'subtotal': subtotal, 'shipping': shipping, 'total': total, 'usuario': usuario})

def checkout_confirm(request):
    if request.method != 'POST':
        return redirect('app_CasePoint:view_cart')
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('app_CasePoint:registrarse')
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    metodo_pago = request.POST.get('metodo_pago', 'TC')
    cart = _get_cart(request)
    if not cart:
        return redirect('app_CasePoint:view_cart')
    pedido = Pedido.objects.create(id_usuario=usuario, metodo_pago=metodo_pago)
    for pid, qty in cart.items():
        producto = get_object_or_404(Producto, pk=int(pid))
        ProductoPedido.objects.create(producto=producto, pedido=pedido, cantidad=qty)
    # Pedido.save will calculate total
    pedido.save()
    # empty cart
    request.session['cart'] = {}
    return render(request, 'checkout_success.html', {'pedido': pedido})

# Admin simple views
def admin_login(request):
    if request.method == 'POST':
        emp_id = request.POST.get('id')
        contrasena = request.POST.get('contrasena')
        # allow hardcoded credential
        if str(emp_id) == '599' and str(contrasena) == '18':
            request.session['is_admin'] = True
            return redirect('app_CasePoint:admin_home')
        # try database
        try:
            empleado = Empleado.objects.get(id=emp_id, contrasena=contrasena)
            request.session['is_admin'] = True
            return redirect('app_CasePoint:admin_home')
        except Empleado.DoesNotExist:
            return render(request, 'admin/admin_login.html', {'error': 'Credenciales inválidas'})
    return render(request, 'admin/admin_login.html')

def admin_home(request):
    if not request.session.get('is_admin'):
        return redirect('app_CasePoint:admin_login')
    return render(request, 'admin/admin.html')

### CRUD Usuario
def ver_usuarios(request):
    if not request.session.get('is_admin'):
        return redirect('app_CasePoint:admin_login')
    usuarios = Usuario.objects.all()
    return render(request, 'admin/Usuario/ver_usuarios.html', {'usuarios': usuarios})

def agregar_usuario(request):
    if not request.session.get('is_admin'):
        return redirect('app_CasePoint:admin_login')
    if request.method == 'POST':
        data = request.POST
        Usuario.objects.create(
            nombre=data.get('nombre',''), apellido=data.get('apellido',''), correo=data.get('correo',''),
            telefono=data.get('telefono',''), direccion=data.get('direccion',''), contrasena=data.get('contrasena',''),
            codigo_postal=data.get('codigo_postal',''))
        return redirect('app_CasePoint:ver_usuarios')
    return render(request, 'admin/Usuario/agregar_usuario.html')

def actualizar_usuario(request, pk):
    if not request.session.get('is_admin'):
        return redirect('app_CasePoint:admin_login')
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        data = request.POST
        usuario.nombre = data.get('nombre', usuario.nombre)
        usuario.apellido = data.get('apellido', usuario.apellido)
        usuario.correo = data.get('correo', usuario.correo)
        usuario.telefono = data.get('telefono', usuario.telefono)
        usuario.direccion = data.get('direccion', usuario.direccion)
        usuario.contrasena = data.get('contrasena', usuario.contrasena)
        usuario.codigo_postal = data.get('codigo_postal', usuario.codigo_postal)
        usuario.save()
        return redirect('app_CasePoint:ver_usuarios')
    return render(request, 'admin/Usuario/actualizar_usuario.html', {'usuario': usuario})

def eliminar_usuario(request, pk):
    if not request.session.get('is_admin'):
        return redirect('app_CasePoint:admin_login')
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        usuario.delete()
        return redirect('app_CasePoint:ver_usuarios')
    return render(request, 'admin/Usuario/eliminar_usuario.html', {'usuario': usuario})

### CRUD Marca
def ver_marcas(request):
    if not request.session.get('is_admin'):
        return redirect('app_CasePoint:admin_login')
    marcas = Marca.objects.all()
    return render(request, 'admin/Marca/ver_marcas.html', {'marcas': marcas})

def agregar_marca(request):
    if not request.session.get('is_admin'):
        return redirect('app_CasePoint:admin_login')
    if request.method == 'POST':
        data = request.POST
        Marca.objects.create(nombre=data.get('nombre',''), imagen_url=data.get('imagen_url',''), año_fundada=int(data.get('año_fundada') or 0), fundador=data.get('fundador',''), pais_origen=data.get('pais_origen',''), descripcion=data.get('descripcion',''))
        return redirect('app_CasePoint:ver_marcas')
    return render(request, 'admin/Marca/agregar_marca.html')

def actualizar_marca(request, pk):
    if not request.session.get('is_admin'):
        return redirect('app_CasePoint:admin_login')
    marca = get_object_or_404(Marca, pk=pk)
    if request.method == 'POST':
        data = request.POST
        marca.nombre = data.get('nombre', marca.nombre)
        marca.imagen_url = data.get('imagen_url', marca.imagen_url)
        marca.año_fundada = int(data.get('año_fundada') or marca.año_fundada)
        marca.fundador = data.get('fundador', marca.fundador)
        marca.pais_origen = data.get('pais_origen', marca.pais_origen)
        marca.descripcion = data.get('descripcion', marca.descripcion)
        marca.save()
        return redirect('app_CasePoint:ver_marcas')
    return render(request, 'admin/Marca/actualizar_marca.html', {'marca': marca})

def eliminar_marca(request, pk):
    if not request.session.get('is_admin'):
        return redirect('app_CasePoint:admin_login')
    marca = get_object_or_404(Marca, pk=pk)
    if request.method == 'POST':
        marca.delete()
        return redirect('app_CasePoint:ver_marcas')
    return render(request, 'admin/Marca/eliminar_marca.html', {'marca': marca})

### CRUD Producto
def ver_productos(request):
    if not request.session.get('is_admin'):
        return redirect('app_CasePoint:admin_login')
    productos = Producto.objects.all()
    return render(request, 'admin/Producto/ver_productos.html', {'productos': productos})

def agregar_producto(request):
    if not request.session.get('is_admin'):
        return redirect('app_CasePoint:admin_login')
    marcas = Marca.objects.all()
    if request.method == 'POST':
        data = request.POST
        Producto.objects.create(
            nombre=data.get('nombre',''), precio=Decimal(data.get('precio') or '0.00'), descripcion=data.get('descripcion',''), stock=int(data.get('stock') or 0), disponibilidad=data.get('disponibilidad','D'), id_marca=Marca.objects.get(pk=int(data.get('id_marca'))), departamento=data.get('departamento','M'), categoria=data.get('categoria','CQ'), imagen_url=data.get('imagen_url','')
        )
        return redirect('app_CasePoint:ver_productos')
    return render(request, 'admin/Producto/agregar_producto.html', {'marcas': marcas, 'departamentos': Producto.DEPARTAMENTO_CHOICES, 'categorias': Producto.CATEGORIA_CHOICES, 'disponibilidades': Producto.DISPONIBILIDAD_CHOICES})

def actualizar_producto(request, pk):
    if not request.session.get('is_admin'):
        return redirect('app_CasePoint:admin_login')
    producto = get_object_or_404(Producto, pk=pk)
    marcas = Marca.objects.all()
    if request.method == 'POST':
        data = request.POST
        producto.nombre = data.get('nombre', producto.nombre)
        producto.precio = Decimal(data.get('precio') or producto.precio)
        producto.descripcion = data.get('descripcion', producto.descripcion)
        producto.stock = int(data.get('stock') or producto.stock)
        producto.disponibilidad = data.get('disponibilidad', producto.disponibilidad)
        producto.id_marca = Marca.objects.get(pk=int(data.get('id_marca')))
        producto.departamento = data.get('departamento', producto.departamento)
        producto.categoria = data.get('categoria', producto.categoria)
        producto.imagen_url = data.get('imagen_url', producto.imagen_url)
        producto.save()
        return redirect('app_CasePoint:ver_productos')
    return render(request, 'admin/Producto/actualizar_producto.html', {'producto': producto, 'marcas': marcas, 'departamentos': Producto.DEPARTAMENTO_CHOICES, 'categorias': Producto.CATEGORIA_CHOICES, 'disponibilidades': Producto.DISPONIBILIDAD_CHOICES})

def eliminar_producto(request, pk):
    if not request.session.get('is_admin'):
        return redirect('app_CasePoint:admin_login')
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        return redirect('app_CasePoint:ver_productos')
    return render(request, 'admin/Producto/eliminar_producto.html', {'producto': producto})

### CRUD Pedido
def ver_pedidos(request):
    if not request.session.get('is_admin'):
        return redirect('app_CasePoint:admin_login')
    pedidos = Pedido.objects.all()
    return render(request, 'admin/Pedido/ver_pedidos.html', {'pedidos': pedidos})


def ver_pedido(request, pk):
    """Mostrar detalle de un pedido y sus productos relacionados (ProductoPedido)."""
    if not request.session.get('is_admin'):
        return redirect('app_CasePoint:admin_login')
    pedido = get_object_or_404(Pedido, pk=pk)
    # obtener items relacionados
    items_qs = ProductoPedido.objects.filter(pedido=pedido).select_related('producto')
    items = []
    subtotal = Decimal('0.00')
    for it in items_qs:
        line_total = (it.producto.precio * it.cantidad)
        items.append({'producto': it.producto, 'cantidad': it.cantidad, 'line_total': line_total})
        subtotal += line_total
    shipping = Decimal('10.00') if items else Decimal('0.00')
    total = subtotal + shipping
    return render(request, 'admin/Pedido/ver_pedido.html', {'pedido': pedido, 'items': items, 'subtotal': subtotal, 'shipping': shipping, 'total': total})

def agregar_pedido(request):
    if not request.session.get('is_admin'):
        return redirect('app_CasePoint:admin_login')
    usuarios = Usuario.objects.all()
    productos = Producto.objects.all()
    if request.method == 'POST':
        data = request.POST
        pedido = Pedido.objects.create(id_usuario=Usuario.objects.get(pk=int(data.get('id_usuario'))), metodo_pago=data.get('metodo_pago','TC'))
        # add a single producto-pedido
        ProductoPedido.objects.create(producto=Producto.objects.get(pk=int(data.get('producto'))), pedido=pedido, cantidad=int(data.get('cantidad') or 1))
        pedido.save()
        return redirect('app_CasePoint:ver_pedidos')
    return render(request, 'admin/Pedido/agregar_pedido.html', {'usuarios': usuarios, 'productos': productos, 'metodos': Pedido.METODO_PAGO_CHOICES})

def actualizar_pedido(request, pk):
    if not request.session.get('is_admin'):
        return redirect('app_CasePoint:admin_login')
    pedido = get_object_or_404(Pedido, pk=pk)
    if request.method == 'POST':
        data = request.POST
        pedido.estado_pedido = data.get('estado_pedido', pedido.estado_pedido)
        pedido.metodo_pago = data.get('metodo_pago', pedido.metodo_pago)
        pedido.save()
        return redirect('app_CasePoint:ver_pedidos')
    return render(request, 'admin/Pedido/actualizar_pedido.html', {'pedido': pedido, 'estados': Pedido.ESTADO_CHOICES, 'metodos': Pedido.METODO_PAGO_CHOICES})

def eliminar_pedido(request, pk):
    if not request.session.get('is_admin'):
        return redirect('app_CasePoint:admin_login')
    pedido = get_object_or_404(Pedido, pk=pk)
    if request.method == 'POST':
        pedido.delete()
        return redirect('app_CasePoint:ver_pedidos')
    return render(request, 'admin/Pedido/eliminar_pedido.html', {'pedido': pedido})

### CRUD Empleado
def ver_empleados(request):
    if not request.session.get('is_admin'):
        return redirect('app_CasePoint:admin_login')
    empleados = Empleado.objects.all()
    return render(request, 'admin/Empleado/ver_empleados.html', {'empleados': empleados})

def agregar_empleado(request):
    if not request.session.get('is_admin'):
        return redirect('app_CasePoint:admin_login')
    if request.method == 'POST':
        data = request.POST
        Empleado.objects.create(nombre=data.get('nombre',''), apellido=data.get('apellido',''), puesto=data.get('puesto',''), correo=data.get('correo',''), telefono=data.get('telefono',''), contrasena=data.get('contrasena',''))
        return redirect('app_CasePoint:ver_empleados')
    return render(request, 'admin/Empleado/agregar_empleado.html')

def actualizar_empleado(request, pk):
    if not request.session.get('is_admin'):
        return redirect('app_CasePoint:admin_login')
    empleado = get_object_or_404(Empleado, pk=pk)
    if request.method == 'POST':
        data = request.POST
        empleado.nombre = data.get('nombre', empleado.nombre)
        empleado.apellido = data.get('apellido', empleado.apellido)
        empleado.puesto = data.get('puesto', empleado.puesto)
        empleado.correo = data.get('correo', empleado.correo)
        empleado.telefono = data.get('telefono', empleado.telefono)
        empleado.contrasena = data.get('contrasena', empleado.contrasena)
        empleado.save()
        return redirect('app_CasePoint:ver_empleados')
    return render(request, 'admin/Empleado/actualizar_empleado.html', {'empleado': empleado})

def eliminar_empleado(request, pk):
    if not request.session.get('is_admin'):
        return redirect('app_CasePoint:admin_login')
    empleado = get_object_or_404(Empleado, pk=pk)
    if request.method == 'POST':
        empleado.delete()
        return redirect('app_CasePoint:ver_empleados')
    return render(request, 'admin/Empleado/eliminar_empleado.html', {'empleado': empleado})
from django.shortcuts import render

# Create your views here.

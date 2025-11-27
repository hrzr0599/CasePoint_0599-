from django.db import models
from django.utils import timezone

class Usuario(models.Model):
	nombre = models.CharField(max_length=100)
	apellido = models.CharField(max_length=100)
	correo = models.EmailField(unique=True)
	telefono = models.CharField(max_length=20, unique=True)
	direccion = models.CharField(max_length=255)
	contrasena = models.CharField(max_length=255) # Se recomienda usar un hash de la contraseña en una aplicación real
	codigo_postal = models.CharField(max_length=10)

	def __str__(self):
		return f"{self.nombre} {self.apellido}"

class Marca(models.Model):
	nombre = models.CharField(max_length=100, unique=True)
	imagen_url = models.URLField(max_length=200)
	año_fundada = models.PositiveSmallIntegerField()
	fundador = models.CharField(max_length=100, unique=True)
	pais_origen = models.CharField(max_length=100)
	descripcion = models.TextField()

	def __str__(self):
		return self.nombre

class Producto(models.Model):
	DEPARTAMENTO_CHOICES = [
		('M', 'Mujeres'),
		('H', 'Hombres'),
		('U', 'Unisex'),
		('J', 'Jovenes'),
		('I', 'Infantil'),
	]

	CATEGORIA_CHOICES = [
		('CQ', 'Chaquetas'),
		('ZP', 'Zapatos'),
		('PF', 'Perfumes'),
		('SW', 'Sweaters'),
		('CM', 'Camisas'),
		('PN', 'Pantalones'),
		('VS', 'Vestidos'),
		('JR', 'Joyeria'),
		('BA', 'Bolsos y Accesorios'),
	]

	DISPONIBILIDAD_CHOICES = [
		('D', 'Disponible'),
		('A', 'Agotado'),
	]

	DISPONIBILIDAD_CHOICES = [
		('D', 'Disponible'),
		('A', 'Agotado'),
	]

	nombre = models.CharField(max_length=255, unique=True)
	precio = models.DecimalField(max_digits=10, decimal_places=2)
	descripcion = models.TextField()
	stock = models.PositiveIntegerField()
	disponibilidad = models.CharField(max_length=1, choices=DISPONIBILIDAD_CHOICES, default='D')
	id_marca = models.ForeignKey(Marca, on_delete=models.CASCADE, related_name='productos')
	departamento = models.CharField(max_length=1, choices=DEPARTAMENTO_CHOICES)
	categoria = models.CharField(max_length=2, choices=CATEGORIA_CHOICES)
	imagen_url = models.URLField(max_length=200)

	def __str__(self):
		return self.nombre

class Pedido(models.Model):
	ESTADO_CHOICES = [
		('P', 'Pendiente'),
		('PR', 'En proceso'),
		('E', 'Enviado'),
		('C', 'Completado'),
	]

	METODO_PAGO_CHOICES = [
		('TC', 'Tarjeta de Crédito'),
		('TD', 'Tarjeta de Debito'),
		('PP', 'Paypal'),
		('AP', 'Apple Pay'),
		('GP', 'Google Pay'),
	]

	id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='pedidos')
	fecha_pedido = models.DateTimeField(default=timezone.now)
	estado_pedido = models.CharField(max_length=2, choices=ESTADO_CHOICES, default='P')
	productos = models.ManyToManyField(Producto, through='ProductoPedido')
	total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
	metodo_pago = models.CharField(max_length=2, choices=METODO_PAGO_CHOICES)

	def save(self, *args, **kwargs):
		# Calcular el total y la cantidad de productos antes de guardar
		super().save(*args, **kwargs) # Guardar primero para que los ManyToManyField se puedan relacionar
		self.total = sum(item.cantidad * item.producto.precio for item in self.productopedido_set.all())
		super().save(update_fields=['total']) # Guardar de nuevo para actualizar el total

	def __str__(self):
		return f"Pedido {self.id} de {self.id_usuario.nombre} {self.id_usuario.apellido}"

class ProductoPedido(models.Model):
	producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
	pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
	cantidad = models.PositiveIntegerField(default=1)

	class Meta:
		unique_together = ('producto', 'pedido')

	def __str__(self):
		return f"{self.cantidad} x {self.producto.nombre} en Pedido {self.pedido.id}"

class Empleado(models.Model):
	PUESTO_CHOICES = [
		('ADM', 'Administrador'),
	]

	nombre = models.CharField(max_length=100)
	apellido = models.CharField(max_length=100)
	puesto = models.CharField(max_length=3, choices=PUESTO_CHOICES)
	correo = models.EmailField(unique=True)
	telefono = models.CharField(max_length=20, unique=True)
	contrasena = models.CharField(max_length=255, unique=True) # Se recomienda usar un hash de la contraseña en una aplicación real

	def __str__(self):
		return f"{self.nombre} {self.apellido} ({self.puesto})"

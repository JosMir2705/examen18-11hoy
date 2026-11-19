from django.db import models
from django.contrib.auth.models import User

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    def __str__(self): return self.nombre

class Pedido(models.Model):
    ESTADOS = [('pendiente', 'Pendiente'), ('enviado', 'Enviado'), ('entregado', 'Entregado')]
    cliente = models.ForeignKey(User, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    fecha = models.DateTimeField(auto_now_add=True)

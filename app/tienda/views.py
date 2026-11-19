from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django.views.generic import TemplateView
from django.db.models import Q
from PIL import Image
from .models import Producto, Pedido
from .serializers import ProductoSerializer, PedidoSerializer

class EsAdminOSoloLectura(permissions.BasePermission):
    """Rol Administrador: CRUD completo. Resto: solo lectura."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            request.user.is_staff or request.user.groups.filter(name='Administrador').exists())

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [EsAdminOSoloLectura]

class PedidoViewSet(viewsets.ModelViewSet):
    serializer_class = PedidoSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        u = self.request.user
        if u.is_staff or u.groups.filter(name='Administrador').exists():
            return Pedido.objects.all()
        return Pedido.objects.filter(cliente=u)
    def perform_create(self, serializer):
        serializer.save(cliente=self.request.user)

_clasificador = None
class ClasificarImagen(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser]
    def post(self, request):
        global _clasificador
        if _clasificador is None:
            from transformers import pipeline
            _clasificador = pipeline('image-classification', model='google/vit-base-patch16-224')
        img = Image.open(request.FILES['imagen']).convert('RGB')
        resultados = _clasificador(img, top_k=3)
        palabras = set()
        for r in resultados:
            for w in r['label'].replace(',', ' ').split():
                if len(w) > 3: palabras.add(w)
        q = Q()
        for w in palabras:
            q |= Q(nombre__icontains=w) | Q(categoria__icontains=w)
        productos = Producto.objects.filter(q) if palabras else []
        return Response({
            'resultados': [{'etiqueta': r['label'], 'confianza': round(r['score'] * 100, 2)} for r in resultados],
            'productos_relacionados': ProductoSerializer(productos, many=True).data,
        })

class Inicio(TemplateView):
    template_name = 'index.html'

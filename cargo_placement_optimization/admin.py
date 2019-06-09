from django.contrib import admin
from cargo_placement_optimization.models import Cars, Orders, Objectss, Places, ObjectsForOrders

# Регистрация таблиц в администраторской панели
admin.site.register(Cars)
admin.site.register(Objectss)
admin.site.register(Places)
admin.site.register(ObjectsForOrders)
admin.site.register(Orders)
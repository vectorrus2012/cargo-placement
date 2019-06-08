from django.contrib import admin
from cargo_placement_optimization import views
from django.conf.urls import url
from django.urls import path

urlpatterns = [
    path('information', views.information),  # Информация о сервисе
    path('admin/', admin.site.urls),  # Админка
    path('about/contact', views.contact),  # Контакты
    path('base/objects', views.show_objects),  # Просмотр объектов
    path('base/add_object', views.add_object),  # Добавление объектов
    path('base/cars', views.show_car),  # Просмотр машины
    path('base/add_car', views.add_car),  # Добавление машины
    path('base/add_place', views.add_place),  # Добавить место доставки
    path('base/ViewPlace', views.show_place),  # Показать места доставки
    path('base/View_Order', views.show_orders),  # Показать заказы
    path('base/add_order', views.add_order),  # Добавить заказы
    path('create_map', views.map_params),  # Страница заполнения параметров
    path('map_create', views.map_create),  # Страница с результатами
    path('base/View_objects_for_order', views.show_objects_for_order),  # Показать объекты для заказа
    path('base/add_objects_for_order', views.add_objects_for_order),  # Добавить объект для заказа
    url(r'^base/select_new_ord_params/(?P<id_ord>\d+)/$', views.select_new_ord_params, name='select_new_ord_params'),
    url(r'^base/select_new_ord_params/(?P<id_ord>\d+)/change_ord_params', views.change_ord_params,
        name='change_ord_params'),
    url(r'^base/select_new_pl_params/(?P<id_pl>\d+)/$', views.select_new_pl_params, name='select_new_pl_params'),
    url(r'^base/select_new_pl_params/(?P<id_pl>\d+)/change_pl_params', views.change_pl_params,
        name='change_pl_params'),
    url(r'^base/select_new_obj_params/(?P<id_obj>\d+)/$', views.select_new_obj_params, name='select_new_obj_params'),
    url(r'^base/select_new_obj_params/(?P<id_obj>\d+)/change_car_params$', views.change_obj_params,
        name='change_obj_params'),
    url(r'^base/select_new_car_brand/(?P<id_car>\d+)/$', views.select_new_car_brand, name='select_new_car_brand'),
    url(r'^base/select_new_car_brand/(?P<id_car>\d+)/change_car_params$', views.change_car_params, name='change_car_params'),
    url(r'^base/select_car/(?P<id_order>\d+)/$', views.select_car, name='select_car'),
    url(r'^base/select_car/(?P<id_order>\d+)/change_car', views.change_car, name='change_car'),
    url(r'^base/objects/(?P<id_obj>\d+)/del', views.delete_object, name='del_obj'),
    url(r'^base/cars/(?P<id_car>\d+)/del', views.delete_car, name='del_car'),
    url(r'^base/places/(?P<id_place>\d+)/del', views.delete_place, name='del_place'),
    url(r'^base/orders/(?P<id_order>\d+)/del', views.delete_order, name='del_order'),
    url(r'^base/objects_for_orders/(?P<id_obj_for_order>\d+)/del', views.delete_object_for_order, name='del_obj_for_order'),
    url(r'^login/$', views.LoginFormView.as_view()),  # Авторизация
    url(r'^exit/$', views.LogoutView.as_view()),  # Разлогинивание
    url('', views.index)  # Главная страница
]

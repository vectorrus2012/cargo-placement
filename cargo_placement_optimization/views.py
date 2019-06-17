from django.shortcuts import render
from .models import Cars, Orders, Objectss, Places, ObjectsForOrders
from django.http import HttpResponseRedirect, HttpResponse
import datetime
from django.utils.timezone import utc
from django.views.generic.edit import FormView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.views.generic.base import View
from .alghorithm import *


class LogoutView(View): # Разлогинивание
    def get(self, request):
        # Выполняем выход для пользователя, запросившего данное представление.
        logout(request)

        # После чего, перенаправляем пользователя на главную страницу.
        return HttpResponseRedirect("/")


class LoginFormView(FormView):  # Форма авторизации
    form_class = AuthenticationForm
    # Аналогично регистрации, только используем шаблон аутентификации.
    template_name = "login.html"
    # В случае успеха перенаправим на главную.
    success_url = "/"


    def form_valid(self, form):
        # Получаем объект пользователя на основе введённых в форму данных.
        self.user = form.get_user()
        # Выполняем аутентификацию пользователя.
        login(self.request, self.user)
        return super(LoginFormView, self).form_valid(form)


# Показать главную страницу
def index(request):
    return render(request, 'home.html')


# Показать страницу с информацией
def information(request):
    return render(request, 'Information.html')


# Показать контактную информацию
def contact(request):
    return render(request, 'contact_information.html')


# Показать страницу отправки параметров карты расположения
def map_params(request):
    return render(request, 'create_map/create_map.html')


# Генерация карты расположения грузов
def map_create(request):
    id_orders = request.POST.get("id_order")
    if Orders.objects.filter(id_Orders=id_orders).count() != 0:  # Если есть хотя бы 1 объект
        order = Orders.objects.get(id_Orders=id_orders)  # Идентификатор заказа
        car = Cars.objects.get(id_Car=order.id_car)  # Получить данные машины
        if car.trailer_ax_count == 2 and car.car_ax_count == 2:  # 2 оси автомобиля и 2 оси полуприцепа
            max_weight = 36   # Допустимая полная масса состава
            max_load = 18  # Допустимая нагрузка на ось (тонны)
        elif car.trailer_ax_count == 3 and car.car_ax_count == 2:  # 3 оси полуприцепа и 2 оси автомобиля
            max_weight = 38  # Допустимая полная масса состава
            max_load = 18  # Допустимая нагрузка на ось (тонны)
        elif car.trailer_ax_count == 2 and car.car_ax_count == 3:  # 2 оси полуприцепа и 3 оси автомобиля
            max_weight = 37  # Допустимая полная масса состава
            max_load = 25  # Допустимая нагрузка на ось (тонны)
        elif car.trailer_ax_count == 3 and car.car_ax_count == 3:  # 3 оси полуприцепа и 3 оси автомобиля
            max_weight = 38  # Допустимая полная масса состава
            max_load = 25  # Допустимая нагрузка на ось (тонны)
        places_count = 66  # Количество мест в прицепе еврофуры
        if request.method == "POST":  # Если из формы вызывается метод post
            optimise_method = request.POST.get("optimise")  # Метод оптимизации
            # Множество объектов для заказа
            objects_for_order = ObjectsForOrders.objects.filter(id_order=request.POST.get("id_order"))
            objects_id = []     # ID объекта
            objects_count = []  # количество объектов для заказа
            objects_order = []  # Порядок погрузки
            objects_weights = []  # Веса объектов
            objects_price = []  # Цены объектов
            counter = 0  # Счётчик для цикла
            for obj in objects_for_order:  # Получение id, количества объектов и порядок погрузки
                objects_count.append(obj.count)  # Количество объектов
                for i in range(objects_count[counter]):  # Заполнение всех объектов
                    objects_id.append(obj.id_object.id_Objectss)
                    objects_order.append(obj.order_placement)
                counter += 1  # +1 к счётчику цикла
            obj_count = len(objects_id)
            common_weight = 0
            for i in range(obj_count):
                objectss = Objectss.objects.get(id_Objectss=objects_id[i])
                objects_weights.append(objectss.weight)
                common_weight += (float(objectss.weight))/1000  # Заполнение общий вес вещей
                objects_price.append(objectss.base_price)  # Заполнение цен на объекты
            weight_load_max = (max_weight - (car.maxWeight + car.trailer_weight))*1000  # Максимально допустимый вес (тонны)
            reloaded = True  # Изначально True для активации цикла. Используется для сообщения о перегрузе
            obj_ids = []
            while (reloaded == True) and (len(objects_id) > 0):
                # Вызов функции оптимизации из внешнего модуля
                obj_ids = solve_knapsack(optimise_method, objects_id, objects_weights, weight_load_max, objects_price)
                k = 0
                packed_objs_weight = 0  # Общий вес груза
                for i in objects_id:
                    for j in obj_ids:
                        if i == j:
                            packed_objs_weight += objects_weights[k]  # Если объект погружен +1 вес этого объекта
                    k += 1
                packed_objs_weight = packed_objs_weight/1000  # Перевод общего веса в тонны
                # Расчёт нагрузок на оси
                res = solve_cargo(car.trailer_ax_count, car.car_ax_count, car.maxWeight, car.trailer_weight,
                                packed_objs_weight)  # Проверка перегруза
                reloaded = False  # Изначально False для выхода из цикла, если нет перегруза
                for i in range(3):  # Получение процентов перегруза по осям (без общей нагрузки)
                    if res[i] >= max_load + ((max_load*2)/100) :  # Если перегруз больше двух процентов
                        reloaded = True
                        del objects_id[-1] # Удалить последний непомещённый объект
                        del objects_order[-1] # Удалить порядок погрузки этого объекта
                        common_weight -= (float(objects_weights[-1]))/1000  # -1 вес этого объекта из общего
                        del objects_weights[-1]  # -1 вес объекта
                        del objects_price[-1]  # -1 Цена объекта
            k = 0
            new__ord_list = []  # новый список с порядком погрузки, соответствующий вместимым вещам
            for i in objects_id:
                for j in obj_ids:
                    if i == j:
                        new__ord_list.append(objects_order[k])
                k += 1
            result = [obj_ids for _, obj_ids in sorted(zip(new__ord_list, obj_ids))]  # Сортировка по порядку погрузки
            result = result[:places_count]  # Срез до количества мест
            up = []  # Верхние объекты
            down = []  # Нижние объекты
            counter2 = 2  # счётчик цикла
            for obj in result:
                if counter2 % 2 == 0:
                    up.append(obj)
                else:
                    down.append(obj)
                counter2 += 1
            counter2 = 0  # Обнуление счётчика
            right_up = []  # Правый верх
            left_up = []  # Левый верх
            for obj in up:
                if counter2 % 2 == 0:
                    right_up.append(obj)
                else:
                    left_up.append(obj)
                counter2 += 1    
            counter2 = 0
            right_down = []  # Правый низ
            left_down = []  # Левый низ
            for obj in down:
                if counter2 % 2 == 0:
                    right_down.append(obj)
                else:
                    left_down.append(obj)
                counter2 += 1           
            objects_info_up_right = Objectss.objects.filter(id_Objectss__in=right_up)  # Получить информацию о помещённых предметах (верхний ряд, справа)
            objects_info_down_right = Objectss.objects.filter(id_Objectss__in=right_down)  # Получить информацию о помещённых предметах (нижний ряд, справа)
            objects_info_up_left = Objectss.objects.filter(id_Objectss__in=left_up)  # Получить информацию о помещённых предметах (верхний ряд, слева)
            objects_info_down_left = Objectss.objects.filter(id_Objectss__in=left_down)  # Получить информацию о помещённых предметах (нижний ряд, слева)
            new_not_packed_items = list(set(objects_id)-set(result))  # Список не погруженных вещей
            not_packed_info = Objectss.objects.filter(id_Objectss__in=new_not_packed_items)  # Информаци о не погруженных вещях
        return render(request, 'create_map/Create_map_result.html', {"up_right_objects_ids": right_up,"up_left_objects_ids": left_up,
        "down_right_objects_ids":right_down, "down_left_objects_ids":left_down, 
        "obj_info_up_right": objects_info_up_right, "obj_info_down_right": objects_info_down_right, 
        "obj_info_up_left": objects_info_up_left, "obj_info_down_left": objects_info_down_left,  "not_packed": not_packed_info})
    else:
        return render(request, 'error/data.html')  # Если заказ не найден, то показ ошибки


# Показать список имеющихся объектов
def show_objects(request):
    objects = Objectss.objects.all().order_by("-date_add")  # Сортировка результата выборки по дате
    return render(request, 'base/ViewObjects.html', {"objectss": objects})


# Показать список автомобилей
def show_car(request):
    cars = Cars.objects.all().order_by("-date_add")  # Сортировка результата выборки по дате
    return render(request, 'base/ViewCars.html', {"Cars": cars})


# Показать список мест для доставки
def show_place(request):
    place = Places.objects.all().order_by("city")  # Сортировка результата выборки по дате
    return render(request, 'base/ViewPlace.html', {"Place": place})


# Показать список договоров
def show_orders(request):
    orders = Orders.objects.all().order_by("id_Orders")  # Сортировка результата выборки по дате
    return render(request, 'base/View_Order.html', {"Orders": orders})


def show_objects_for_order(request):
    obj_for_order = ObjectsForOrders.objects.all().order_by("-date_add")
    return render(request, 'base/ViewObjectsForOrders.html', {"obj_for_order":obj_for_order})


# Добавление объекта
def add_object(request):
    if request.method == "POST":  # Если из формы вызывается метод post
        objects = Objectss()  # Создаётся новый объект класса
        objects.id_Objectss = request.POST.get("id")
        objects.name = request.POST.get("name")
        objects.weight = request.POST.get("weight")
        objects.manufacturer = request.POST.get("manufacturer")
        objects.consignment = request.POST.get("consignment")
        objects.base_price = request.POST.get("base_price")
        objects.stock_num = request.POST.get("stock_num")
        objects.date_add = datetime.datetime.utcnow().replace(tzinfo=utc)  # Время добавления
        objects.save()
    return render(request, 'base/add_object.html')


# Добавление места доставки
def add_place(request):
    if request.method == "POST":  # Если из формы вызывается метод post
        places = Places()  # Создаётся новый объект класса
        places.id_Places = request.POST.get("id")
        places.name = request.POST.get("name")
        places.company = request.POST.get("company")
        places.country = request.POST.get("country")
        places.state = request.POST.get("state")
        places.city = request.POST.get("city")
        places.street = request.POST.get("street")
        places.link = request.POST.get("link")
        places.date_add = datetime.datetime.utcnow().replace(tzinfo=utc)  # Время добавления
        places.save()
    return render(request, 'base/add_place.html')


# Добавление автомобилей
def add_car(request):
    if request.method == "POST":  # Если из формы вызывается метод post
        cars = Cars()  # Создаётся новый объект класса
        cars.id_Car = request.POST.get("id")
        cars.Brand = request.POST.get("Brand")
        cars.Model = request.POST.get("Model")
        cars.maxWeight = request.POST.get("maxWeight")
        cars.trailer_weight = request.POST.get("trailer_weight")
        cars.trailer_ax_count = request.POST.get("trailer_ax_count")
        cars.car_ax_count = request.POST.get("car_ax_count")
        cars.date_add = datetime.datetime.utcnow().replace(tzinfo=utc)  # Время добавления
        cars.save()
    return render(request, 'base/add_car.html')


# Добавление заказов
def add_order(request):
    if request.method == "POST":  # Если из формы вызывается метод post
        id_car = request.POST.get("id_car")
        exist = False
        if len(Cars.objects.filter(id_Car=id_car)) != 0:  # Если машина существует
            order = Orders()  # Создаётся новый объект класса
            order.id_Orders = request.POST.get("id")
            order.id_car = Cars.objects.get(id_Car=id_car)
            order.date_departure = request.POST.get("date_departure")+" "+request.POST.get("time_departure")
            order.date_completion = request.POST.get("date_completion")+" "+request.POST.get("time_completion")
            order.date_add = datetime.datetime.utcnow().replace(tzinfo=utc)  # Время добавления
            order.save()
            exist = True
        if exist:
            return render(request, 'base/add_order.html')
        else:
            return render(request, 'error/data.html')  # Если автомобиль не найден, то показ ошибки
    else:
        return render(request, 'base/add_order.html')


# Добавление объектов для заказа
def add_objects_for_order(request):
    if request.method == "POST":  # Если из формы вызывается метод post
        k = 0
        if Objectss.objects.filter(id_Objectss=request.POST.get("id_obj")).count() != 0:
            k += 1
        if Orders.objects.filter(id_Orders=request.POST.get("id_order")).count() != 0:
            k += 1
        if Places.objects.filter(id_Places=request.POST.get("id_place_delievery")).count() != 0:
            k += 1
        if k == 3:
            obj_order = ObjectsForOrders()  # Создаётся новый объект класса
            obj_order.id_ObjectsForOrders = request.POST.get("id")
            obj_order.id_object = Objectss.objects.get(id_Objectss=request.POST.get("id_obj"))
            obj_order.order_placement = request.POST.get("order_placement")
            obj_order.id_order = Orders.objects.get(id_Orders=request.POST.get("id_order")) 
            obj_order.id_place_to_delivery = Places.objects.get(id_Places=request.POST.get("id_place_delievery"))
            obj_order.count = request.POST.get("count")
            obj_order.date_add = datetime.datetime.utcnow().replace(tzinfo=utc)  # Время добавления
            obj_order.save()
        else:
            return render(request, 'error/data.html') 
    return render(request, 'base/add_obj_for_order.html')


# Удаление объектов 
def delete_object(request, id_obj):
    Objectss.objects.get(id_Objectss=id_obj).delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# Удаление машин
def delete_car(request, id_car):
    Cars.objects.get(id_Car=id_car).delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# Удаление мест доставки
def delete_place(request, id_place):
    Places.objects.get(id_Places=id_place).delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# Удаление заказов
def delete_order(request, id_order):
    Orders.objects.get(id_Orders=id_order).delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# Удаление объектов для заказа
def delete_object_for_order(request, id_obj_for_order):
    ObjectsForOrders.objects.get(id_ObjectsForOrders=id_obj_for_order).delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# Список машин для выбора в заказе
def select_car(request, id_order):
    cars = Cars.objects.all().order_by("-date_add")  # Сортировка результата выборки по дате
    current_order = Orders.objects.get(id_Orders=id_order)
    current_car = Cars.objects.get(id_Car=current_order.id_car)
    return render(request, 'base/edit/orders/change_car.html', {"Cars": cars, "current_car": current_car,
                                                                "current_order":id_order})


# Сменить машину для заказа на выбранную
def change_car(request, id_order):
    if request.method == "POST":  # Если из формы вызывается метод post
        new_car = Cars.objects.get(id_Car=request.POST.get("car_id"))
        # Обновление используемой машины в заказе
        Orders.objects.filter(id_Orders=id_order).update(id_car=new_car.id_Car)
    orders = Orders.objects.all().order_by("-date_add")  # Сортировка результата выборки по дате
    return render(request, 'base/View_Order.html', {"Orders": orders})


# Показать форму изменения параметров машины
def select_new_car_brand(request, id_car):
    cars = Cars.objects.filter(id_Car=id_car)
    return render(request, 'base/edit/car/brand.html', {"Car": cars})


# Изменить параметры машины
def change_car_params(request, id_car):
    if request.method == "POST":  # Если из формы вызывается метод post
        Cars.objects.filter(id_Car=id_car).update(
            Brand=request.POST.get("new_brand"))  # Обновление брэнда машины
        Cars.objects.filter(id_Car=id_car).update(
            Model=request.POST.get("new_model"))  # Обновление модели машины
        try:  # Если строка является числом, перевести в число
            new_tr_weight = float(request.POST.get("new_trailer_weight").replace(',', '.'))
            Cars.objects.filter(id_Car=id_car).update(
                trailer_weight=new_tr_weight)  # Обновление веса прицепа
        except:
            del new_tr_weight
        try:
            new_tr_ax_count = int(request.POST.get("new_trailer_ax_count"))
            Cars.objects.filter(id_Car=id_car).update(
                trailer_ax_count=new_tr_ax_count)  # Обновление количества осей машины
        except:
            del new_tr_ax_count
        try:
            new_car_ax_count = int(request.POST.get("new_car_ax_count"))
            Cars.objects.filter(id_Car=id_car).update(
                car_ax_count=new_car_ax_count)  # Обновление количества осей прицепа
        except:
            del new_car_ax_count
        try:  # Если строка является числом, перевести в строку
            new_weight = float(request.POST.get("new_max_weight").replace(',', '.'))
            Cars.objects.filter(id_Car=id_car).update(
                maxWeight=new_weight)  # Обновление веса машины
        finally:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# Показать форму изменения параметров погружаемого объекта
def select_new_obj_for_order_params(request, id_obj_for_order):
    objs = ObjectsForOrders.objects.filter(id_ObjectsForOrders=id_obj_for_order)
    return render(request, 'base/edit/obj_for_orders/change_obj.html', {"obj": objs})


# Изменить параметры погружаемого объекта
def change_obj_for_order_params(request, id_obj_for_order):
    if request.method == "POST":  # Если из формы вызывается метод post
        try:  # Если строка является числом, перевести в строку
            new_order_placement = int(request.POST.get("new_order_placement"))
            ObjectsForOrders.objects.filter(id_ObjectsForOrders=id_obj_for_order).update(
                order_placement=new_order_placement)  # Обновление порядка погрузки
            new_count = int(request.POST.get("new_count"))
            ObjectsForOrders.objects.filter(id_ObjectsForOrders=id_obj_for_order).update(
                count=new_count)  # Обновление количества объектов
        finally:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# Показать форму изменения параметров объекта
def select_new_obj_params(request, id_obj):
    objs = Objectss.objects.filter(id_Objectss=id_obj)
    return render(request, 'base/edit/objects/obj.html', {"obj": objs})


# Изменить параметры объекта
def change_obj_params(request, id_obj):
    if request.method == "POST":  # Если из формы вызывается метод post
        Objectss.objects.filter(id_Objectss=id_obj).update(
            manufacturer=request.POST.get("new_manufacturer"))  # Обновление производителя
        Objectss.objects.filter(id_Objectss=id_obj).update(
            name=request.POST.get("new_name"))  # Обновление названия машины
        Objectss.objects.filter(id_Objectss=id_obj).update(
            consignment=request.POST.get("new_consignment"))  # Обновление партии
        Objectss.objects.filter(id_Objectss=id_obj).update(
            base_price=request.POST.get("new_base_price"))  # Обновление цены производителя
        Objectss.objects.filter(id_Objectss=id_obj).update(
            stock_num=request.POST.get("new_stock_num"))  # Обновление номера склада
        try:  # Если строка является числом, перевести в строку
            new_weight = float(request.POST.get("new_weight").replace(',', '.'))
            Objectss.objects.filter(id_Objectss=id_obj).update(
                weight=new_weight)  # Обновление веса объекта
        finally:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# Показать форму изменения параметров места доставки
def select_new_pl_params(request, id_pl):
    pls = Places.objects.filter(id_Places=id_pl)
    return render(request, 'base/edit/places/pl.html', {"pl": pls})

# Изменить параметры места доставки
def change_pl_params(request, id_pl):
    if request.method == "POST":  # Если из формы вызывается метод post
        Places.objects.filter(id_Places=id_pl).update(
            name=request.POST.get("new_name"))  # Обновление Название места доставки
        Places.objects.filter(id_Places=id_pl).update(
            company=request.POST.get("new_company"))  # Обновление Компания/Владелец места доставки
        Places.objects.filter(id_Places=id_pl).update(
            country=request.POST.get("new_country"))  # Обновление партии
        Places.objects.filter(id_Places=id_pl).update(
            state=request.POST.get("new_state"))  # Обновление штата/региона
        Places.objects.filter(id_Places=id_pl).update(
            city=request.POST.get("new_city"))  # Обновление города
        Places.objects.filter(id_Places=id_pl).update(
            street=request.POST.get("new_street"))  # Обновление улицы
        Places.objects.filter(id_Places=id_pl).update(
            link=request.POST.get("new_link"))  # Обновление координат
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# Показать форму изменения параметров заказа
def select_new_ord_params(request, id_ord):
    ords = Orders.objects.filter(id_Orders=id_ord)
    return render(request, 'base/edit/orders/change_ord.html', {"ords": ords})


# Изменить параметры заказа
def change_ord_params(request, id_ord):
    if request.method == "POST":  # Если из формы вызывается метод post
        dep_time = request.POST.get("new_dep_time")
        comp_time = request.POST.get("new_comp_time")
        dep_date = request.POST.get("new_dep_date")
        if dep_date != "" and dep_time != "":
            Orders.objects.filter(id_Orders=id_ord).update(
                date_departure=dep_date+" "+dep_time)  # Обновление Даты отправки заказа
        comp_date = request.POST.get("new_comp_date")
        if comp_date != "" and comp_time != "":
            Orders.objects.filter(id_Orders=id_ord).update(
                date_completion=comp_date+" "+comp_time)  # Обновление Даты завершения отправки заказа
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

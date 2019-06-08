from django.db import models


class Reviews(models.Model):  # табличка в бд с отзывами
    message = models.TextField()  # Содержание отзыва
    email = models.TextField()  # Электронный адрес пользователя
    name = models.TextField()  # Имя пользователя
    mark = models.IntegerField()  # Оценка
    date = models.DateTimeField()  # Дата отзыва


class Cars(models.Model):
    id_Car = models.TextField(primary_key=True)  # Идентификатор машины
    Brand = models.TextField()  # Брэнд машины
    Model = models.TextField()  # Модель машины
    maxWeight = models.FloatField()  # Вес машины
    trailer_weight = models.FloatField()  # Вес прицепа
    trailer_ax_count = models.IntegerField()  # Количество осей полуприцепа
    car_ax_count = models.IntegerField()  # Количество осей машины
    date_add = models.DateTimeField()  # Дата добавления

    def __str__(self):
        template = '{0.id_Car}'
        return template.format(self)


class Places(models.Model):
    id_Places = models.TextField(primary_key=True)  # Идентификатор места доставки объекта
    name = models.TextField()  # Название места доставки
    company = models.TextField()  # Компания/Владелец места доставки
    country = models.TextField()  # Страна доставки
    state = models.TextField()  # Штат/ областиь доставки
    city = models.TextField()  # Город доставки
    street = models.TextField()  # Улица доставки
    link = models.TextField()  # Место на карте (ссылка)
    date_add = models.DateTimeField()  # Дата добавления


class Orders(models.Model):
    id_Orders = models.TextField(primary_key=True)   # Идентификатор заказа
    id_car = models.ForeignKey('Cars', on_delete=models.CASCADE)  # Машина, на которой производится доставка
    date_departure = models.DateTimeField()  # Дата и время отправки заказа
    date_completion = models.DateTimeField()  # Дата и время завершения заказа
    date_add = models.DateTimeField()  # Дата добавления

    def __str__(self):
        template = '{0.id_Orders} {0.id_car}'
        return template.format(self)


class Objectss(models.Model):
    id_Objectss = models.TextField(primary_key=True)  # Идентификатор объекта
    weight = models.FloatField()  # Вес объекта
    name = models.TextField()  # Наименование объекта
    manufacturer = models.TextField()  # Производитель
    consignment = models.TextField()  # Партия
    base_price = models.FloatField()  # Цена
    stock_num = models.TextField()  # Номер склада
    date_add = models.DateTimeField()  # Дата добавления


class ObjectsForOrders(models.Model):
    id_ObjectsForOrders = models.TextField(primary_key=True)  # Идентификатор объекта для заказа
    id_object = models.ForeignKey('Objectss', on_delete=models.CASCADE)  # Идентификатор объекта
    # Очерёдность (объекты, доставляемые раьнше, будут находиться ближе для удобства извлечения)
    order_placement = models.IntegerField()
    id_order = models.ForeignKey('Orders', on_delete=models.CASCADE)  # Идентификатор заказа
    id_place_to_delivery = models.ForeignKey('Places',
                                             on_delete=models.CASCADE)  # Идентификатор места доставки объекта
    count = models.BigIntegerField()  # Количество объектов для доставки
    date_add = models.DateTimeField()  # Дата добавления

    def __str__(self):
        template = '{0.id_ObjectsForOrders} {0.id_object} {0.id_order} {0.id_place_to_delivery}'
        return template.format(self)

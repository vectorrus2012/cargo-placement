from ortools.algorithms import pywrapknapsack_solver


# Расчёт численного значения нагрузки
def solve_cargo(axis_count, auto_axis_count, car_weight, trailer_weight, cargo_weight):
    # Значения в тоннах
    npr = (trailer_weight + cargo_weight) * 0.75  # Нaгpузкa нa пpицeп
    # 0 - перегруз на оси прицепа, 1 - ось грузового автомобиля, 2 - задняя ось автомобиля 3 - передняя 4 - общая
    res = []
    every_trailer_axis = npr / axis_count  # Просчёт перегруза оси прицепа
    res.append(every_trailer_axis)  # Просчёт перегруза оси прицепа
    on_auto_axi = ((trailer_weight + cargo_weight) * 0.25) + car_weight  # На ось грузового автомобиля
    res.append(on_auto_axi)  # Просчёт перегруза оси автомобиля
    on_back_auto_axis = (on_auto_axi * 0.75) / auto_axis_count  # Ha зaдние ocи aвтoмoбиля
    res.append(on_back_auto_axis)  # Просчёт перегруза задней оси автомобиля
    on_forward_axis = on_auto_axi - on_back_auto_axis - on_back_auto_axis  # На переднюю ось
    res.append(on_forward_axis)  # Просчёт перегруза передней оси автомобиля
    # Общая нагрузка на оси
    common_load = (every_trailer_axis * axis_count) + (on_back_auto_axis * 2) + on_forward_axis
    res.append(common_load)
    return res  # Возвращает проценты перегрузов по осям


def solve_knapsack(method, objects_id, weights, every_trailer_axis, objects_price):
    flat_list = []  # список весов
    for j in range(1):
        flat_list.append([])
        for i in range(len(weights)):
            flat_list[j].append(weights[i])  # Заполнение списка весов
    capacities = [every_trailer_axis]  # Максимальная вместимость
    if method == "Weight":  # Если оптимизация по весу
        values = flat_list[0]  # ценность не учитывается. У всех объектов одинаковая
        # Иннициализация алгоритма решения для загрузки максимальным весом
        solver = pywrapknapsack_solver.KnapsackSolver(
            pywrapknapsack_solver.KnapsackSolver.
            KNAPSACK_DYNAMIC_PROGRAMMING_SOLVER,
            'test')
        solver.Init(values, flat_list, capacities)
        computed_value = solver.Solve()
        packed_items = [x for x in range(0, len(flat_list[0]))
                        if solver.BestSolutionContains(x)]  
        packed_items_ids = []
        for i in packed_items:  # Получение id упакованных вещей
            packed_items_ids.append(objects_id[i])
    elif method == "Value":  # Если оптимизация по ценности
        # Инициализация алгоритма решения для загрузки максимально ценными вещами
        solver_2 = pywrapknapsack_solver.KnapsackSolver(
              pywrapknapsack_solver.KnapsackSolver.
              KNAPSACK_MULTIDIMENSION_BRANCH_AND_BOUND_SOLVER,
              'test')
        capacities = [every_trailer_axis]
        solver_2.Init(objects_price, flat_list, capacities)
        packed_items = [x for x in range(0, len(flat_list[0]))
                        if solver_2.BestSolutionContains(x)]
        packed_items_ids = []  # Идентификаторы получаемых вещей
        for i in packed_items:  # Получение id упакованных вещей
            packed_items_ids.append(objects_id[i])
    return packed_items_ids
from typing import List, Dict, OrderedDict
from exceptions import WrongPriceException, NoPromotionsFoundException
from promotion import Promotion

import collections


def count_average_discount(promotions: List[Promotion], decimal_points: int = 2) -> float:
    """
    Считает средний размер скидки
    :param promotions: Акции
    :param decimal_points: До скольки знаков округлять
    :return:
    """
    discount_sum = 0
    count = 0
    for promotion in promotions:
        try:
            discount_sum += count_discount(promotion)
            count += 1
        except WrongPriceException:
            continue
    if count == 0:
        raise NoPromotionsFoundException('No promotions with correct prices')
    return round(discount_sum / count, decimal_points)

def count_discount(promotion: Promotion, decimal_points: int = 2) -> float:
    """
    Считает скидку в акции
    :param promotion: Акция
    :param decimal_points: До скольки знаков округлять
    :return:
    """
    if promotion.price is None:
        raise WrongPriceException(f'Miss current price')
    if promotion.old_price is None:
        raise WrongPriceException(f'Miss old price')
    if promotion.old_price <= 0 or promotion.price <= 0:
        raise WrongPriceException(f'Price cannot be zero or negative')
    return round(100 * (promotion.old_price - promotion.price) / promotion.old_price, decimal_points)


def get_category_to_promotions(promotions: List[Promotion],
                               no_category_name: str = 'Без категории') -> Dict[str, List[Promotion]]:
    """
    Составляет словарь {категория: акции}
    :param promotions: Акции
    :param no_category_name: Название категории для товаров без категории
    :return:
    """
    category_to_promotions = {}
    for promotion in promotions:
        category_name = promotion.category_name if promotion.category_name != '' else no_category_name
        if category_to_promotions.get(category_name) is None:
            category_to_promotions[category_name] = []
        category_to_promotions[category_name].append(promotion)
    return category_to_promotions

def count_category_to_average_discount(promotions: List[Promotion], decimal_points: int = 2, order_asc: bool = True,
                                       no_category_name: str = 'Без категории') -> OrderedDict[str, float]:
    """
    Считает среднюю скидку каждой категории
    :param promotions: Акции
    :param decimal_points: До скольки знаков округлять
    :param order_asc: True - отсортировать в возрастающем порядке
                      False - в убывающем
    :param no_category_name: Название категории для товаров без категории
    :return:
    """
    category_to_promotions = get_category_to_promotions(promotions, no_category_name)
    category_to_discount = {}
    for category, category_promotions in category_to_promotions.items():
        try:
            category_to_discount[category] = count_average_discount(category_promotions, decimal_points)
        except NoPromotionsFoundException:
            category_to_discount[category] = 0

    return collections.OrderedDict(sorted(category_to_discount.items(),
                                          key=lambda item: item[1] if order_asc else -item[1]))

import asyncio
from typing import List

from async_parser import get_all_stores_promotion_data
from promotion import Promotion
from promotions_analyser import count_average_discount, count_category_to_average_discount, get_category_to_promotions


def print_store_data(store_id: int, promotions: List[Promotion]):
    print(f'Store {store_id}:')

    average_discount = count_average_discount(promotions)
    print(f'\tAverage discount is {average_discount}%')

    category_to_promotions = get_category_to_promotions(promotions)
    category_to_discount = count_category_to_average_discount(promotions, order_asc=False)
    print(f'\tCategory average discounts:')
    print('\t\t' + '\n\t\t'.join([f'{cat} - {disc}% ({len(category_to_promotions.get(cat))} товаров)' \
                                  for cat, disc in category_to_discount.items()]))


def main():
    stores = [8958, 61350]
    # stores = [8958]
    store_to_promotions = asyncio.run(get_all_stores_promotion_data(stores))
    for store in stores:
        print_store_data(store, store_to_promotions[store])


if __name__ == '__main__':
    main()

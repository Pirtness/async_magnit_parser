import asyncio
import aiohttp
from typing import List, Dict, Callable

from config import MAGNIT_API_PROMOTIONS_URL
from promotion import Promotion


async def get_all_stores_promotion_data(store_ids: List[int], category_id: int = None) -> Dict[int, List[Promotion]]:
    """
    Получает словарь со скидками магазинов {id магазина: скидки}
    :param store_ids: список id магазинов
    :param category_id: категория скидок, по умолчанию берутся акции всех категорий
    :return:
    """
    headers = _get_default_magnit_headers()

    store_to_task = {}
    async with aiohttp.ClientSession(headers=headers) as client:
        for store_id in store_ids:
            task = asyncio.create_task(_get_store_promotions_data(client, store_id, category_id))
            store_to_task[store_id] = task

        await asyncio.gather(*store_to_task.values())

    store_to_data = dict(map(lambda item: (item[0], item[1].result()), store_to_task.items()))
    return store_to_data


def collect_all_iteratively(limit: int):
    """
    Декоратор, который применяется к функции, возвращающей список
    Функция будет вызываться до тех пор, пока не вернет пустой список
    В каждый вызов передается словарь параметров с ключами offset и limit
    Каждую итерацию offset увеличивается на limit
    :return:
    """
    def decorator(func: Callable[[aiohttp.ClientSession, dict], list]):
        async def wrapper(client: aiohttp.ClientSession, params: dict = None):
            if params is None:
                params = {}
            params['offset'] = 0
            params['limit'] = limit

            total_result = []
            last_result = None
            while last_result is None or len(last_result) > 0:
                last_result = await func(client, params)
                total_result.extend(last_result)
                params['offset'] += limit

            return total_result
        return wrapper
    return decorator


async def _get_store_promotions_data(client: aiohttp.ClientSession, store_id: int, category_id: int = None,
                                     sort_by: str = 'priority', order: str = 'desc',
                                     adult: bool = True) -> List[Promotion]:
    """
    Получает json со скидками магазина
    :param store_id: id магазина
    :param category_id: категория скидок, по умолчанию берутся акции всех категорий
    :param adult: показывать ли товары для взрослых
    :return:
    """
    params = {
        'categoryId': category_id,
        'storeId': store_id,
        'sortBy': sort_by,
        'order': order,
        'adult': str(adult).lower()
    }
    # Убираем параметры со значением None
    params = dict(filter(lambda item: item[1] is not None, params.items()))

    return await _get_store_promotions_data_by_params(client, params)


@collect_all_iteratively(limit=36)
async def _get_store_promotions_data_by_params(client: aiohttp.ClientSession, params: dict) -> List[Promotion]:
    async with client.get(MAGNIT_API_PROMOTIONS_URL, params=params, raise_for_status=True) as resp:
        result = (await resp.json())['data']
    # Валидация ответа
    return list(map(lambda p: Promotion.model_validate(p), result))


def _get_default_magnit_headers() -> dict:
    return {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Referer': 'https://magnit.ru/',
        'X-Device-Id': 'bm0h29is9e',
        'X-Device-Platform': 'Web',
        'X-Device-Tag': 'disabled',
        'X-Platform-Version': 'window.navigator.userAgent',
        'X-App-Version': '0.1.0',
    }

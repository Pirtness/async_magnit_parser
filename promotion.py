from pydantic import BaseModel, Field
from datetime import date

class Promotion(BaseModel):
    """Акция магнита"""
    id: str
    name: str
    description: str
    category_name: str = Field(alias='categoryName')
    article_category: str = Field(alias='articleCategory')
    discount_category: str = Field(alias='discountCategory')
    price: int = None
    old_price: int = Field(alias='oldPrice', default=None)
    start_date: date = Field(alias='startDate')
    end_date: date = Field(alias='endDate')
    product_code: str = Field(alias='productCode')
    priority: int
    type: str
    alcohol: bool
    image: str
    image_url: str = Field(alias='imageUrl')

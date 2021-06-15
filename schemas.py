from pydantic import BaseModel, validator
from typing import Optional
from datetime import date
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date, Boolean, LargeBinary, DateTime, exc, JSON

# Для получения данных пользователю

class UserBase(BaseModel):
    username: Optional[str]
    password: Optional[bytes]
    email: Optional[str]
    default: Optional[bool]
    status: Optional[str]
    is_buyer: Optional[bool]
    is_provider: Optional[bool]

    @validator('email')
    def email_must_contain_a_dog(cls, email):
        if ('@' not in email) or ('.' not in email) or (('com' or 'ru') not in email):
            raise ValueError('Введите корректный Email')
        return email


# Для отправки данных пользователю
class UserIn(UserBase):
    id: Optional[str]

    class Config:
        orm_mode = True


# Для получения данных пользователю
class TenderBase(BaseModel):
    name: Optional[str]
    view_product: Optional[str]
    category: Optional[str]
    discription: Optional[str]
    haract: Optional[dict]

    @validator('name')
    def name_validator(cls, name):
        if len(name) < 2:
            raise ValueError('Имя должно быть больше двух букв')
        return name

    @validator('discription')
    def description_validator(cls, discription):
        if len(discription) < 10:
            raise ValueError('Описание должно быть длинее')
        return discription


# Для отправки данных пользователю
class TenderIn(TenderBase):
    id: Optional[str]

    class Config:
        orm_mode = True


# Для получения данных пользователю


def compares(a: int, b: int, flag: bool) -> int:
    if flag:
        if a > b:
            raise ValueError('Левая граница не может быть больше правой')
    else:
        if a < b:
            raise ValueError('Правая граница не может быть меньше левой')
    return a


"""
    id = Column('id', Integer, primary_key=True)
    user_id = Column('user_id', Integer, ForeignKey('users.id'), nullable=False)
    offer_name = Column('offer_name', String, nullable=False) # Название офферты
    image = Column('image', String, nullable=False)                        # Изображение
    unit_izmerenie = Column('izmerenie', String, nullable=False)  # Единица измерения
    cost_of_unit = Column('cost_of_unit', String, nullable=False) # Цена за один элемент продукта
    status = Column('STATUS', String, nullable=False) # STATUS OF FAIL
    left_border_of_products = Column('left_border_of_product', Integer, nullable=False) # Минимальное кол-во на складе
    right_border_of_products = Column('right_border_of_products', Integer, nullable=True) # Макс. кол-во на складе
    haract = Column('characteristics', JSON, nullable=False)                            # Характеристики
    region_postavka = Column('region', String, nullable=False)  # Регион поставки
    delivery_time_from = Column('delivery_time_from', Integer, nullable=False) # Доставка от такого-то числа
    delivery_time_to = Column('delivery_time_to', Integer, nullable=False) # Доставка до такого-то числа
    date_start = Column('date_start', String, nullable=False) # дата действия с
    date_end = Column('date_end', String, nullable=False) # дата действия по
    model = Column('model', String, nullable=False) # дата действия по
    manufacturer = Column('manufacturer', String, nullable=False) # дата действия по
    country = Column('countre', String, nullable=False) # Страна
    view_product = Column('view_product', String, nullable=False) # Вид продукции
    category = Column('category', String, nullable=False) # Категория
    vendore_code = Column('vendore_code', String, nullable=False) # Артикул оферты
    nds = Column('nds', String, nullable=False) # Артикул оферты
"""


# date
class OfferBase(BaseModel):
    user_id: Optional[int]
    offer_name: Optional[str]
    image: Optional[str]
    unit_izmerenie: Optional[str]
    cost_of_unit: Optional[str]
    status: Optional[str]
    left_border_of_products: Optional[int]
    right_border_of_products: Optional[int]
    haract: Optional[dict]
    region_postavka: Optional[str]
    delivery_time_from: Optional[int]
    delivery_time_to: Optional[int]
    date_start: Optional[str]
    date_end: Optional[str]
    model: Optional[str]
    manufacturer: Optional[str]
    country: Optional[str]
    view_product: Optional[str]
    category: Optional[str]
    vendore_code: Optional[str]
    nds: Optional[str]

    class Config:
        arbitrary_types_allowed = True

    @validator('offer_name')
    def name_validator(cls, offer_name):
        if len(offer_name) < 3:
            raise ValueError('Имя продукта должно быть длинее')
        return offer_name

    @validator('cost_of_unit')
    def costs_validator(cls, cost_of_unit):
        try:
            array = cost_of_unit.split()

            a = int(array[0])

            if isinstance(a, int):
                return str(a)
            else:
                raise ValueError('Валюта указывается числом!')

        except ValueError as E:
            return {"Error": E}
        except Exception as EE:
            return {"Error1": EE}

    @validator('status')
    def status_validator(cls, status):
        if status not in ['cancel', "accept", "modering"]:
            raise ValueError('Неверный статус')
        return status

        _normalize_left_border = \
            validator('left_border_of_products', 'right_border_of_products', flag=True,
                      allow_reuse=True)(compares)

        _normalize_right_border = \
            validator('right_border_of_products', 'left_border_of_products', flag=False,
                      allow_reuse=True)(compares)

        _normalize_left_delivery = \
            validator('delivery_time_from', 'delivery_time_to', flag=True, allow_reuse=True)(compares)

        _normalize_right_delivery = \
            validator('delivery_time_to', 'delivery_time_from', flag=False, allow_reuse=True)(compares)

        # _normalize_left_border_of_date = \
        #     validator('date_start', 'date_end', flag=True, allow_reuse=True)(compares)

        # _normalize_right_border_of_date = \
        #     validator('date_end', 'date_start', flag=False, allow_reuse=True)(compares)


# Для отправки данных пользователю
class OfferIn(OfferBase):
    id: Optional[str]

    class Config:
        orm_mode = True


class CategoryBase(BaseModel):
    name: Optional[str]

    @validator('name')
    def name_validator(cls, name):
        if len(name) < 3:
            raise ValueError('Имя категории должно быть длинее')
        return name


class CategoryIn(CategoryBase):
    id: Optional[int]

    class Config:
        orm_mode = True

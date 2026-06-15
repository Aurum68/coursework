from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest

from models_3d.models import Material, Model3D, Color


class Cart:
    def __init__(self, request: WSGIRequest):
        self.session = request.session
        cart_data = self.session.get(settings.CART_SESSION_ID)
        if not cart_data:
            cart_data = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart_data


    def add(self, item: dict[str, Any]):
        if item['item_key'] not in self.cart.keys():
            self.cart[item['item_key']] = item
        else:
            self.cart[item['item_key']]['quantity'] += 1

        self.save()
        print(self.session[settings.CART_SESSION_ID])


    def update(self, item_key, quantity, scale):
        self.cart[item_key]['quantity'] = quantity
        self.cart[item_key]['scale'] = scale
        self.save()
        return self.get_cart_item(item_key)


    def delete(self, item_key):
        del self.cart[item_key]
        self.save()


    def clear(self):
        self.cart.clear()
        self.save()


    def save(self):
        self.session.modified = True


    def get_items(self):
        model_ids = [item['model_id'] for item in self.cart.values()]
        color_ids = [item['color'] for item in self.cart.values()]

        all_models = {str(m.id): m for m in Model3D.objects.filter(id__in=model_ids)}
        all_colors = {str(c.id): c for c in Color.objects.filter(id__in=color_ids)}

        aggregated_options = Material.objects.get_aggregated_options()

        for key, value in self.cart.items():
            model = all_models.get(str(value['model_id']), None)
            if not model:
                continue

            color = all_colors.get(str(value['color']), None)
            if not color:
                continue

            price = self.__calculate_item_price(aggregated_options, value, model)

            yield {
                'item_key': key,
                'quantity': value['quantity'],
                'material': value['material'],
                'color': color,
                'scale': value['scale'],
                'model': model,
                'price_per_unit': price,
                'total_price': price * value['quantity'],
            }




    def get_cart_item(self, item_key):
        item = self.cart[item_key]
        aggregated_options = Material.objects.get_aggregated_options()
        model = Model3D.objects.get(id=item['model_id'])
        if not model:
            raise Exception('Model not found')

        color = Color.objects.get(id=item['color'])
        if not color:
            raise Exception('Color not found')

        price = self.__calculate_item_price(aggregated_options, item, model)

        return {
            'item_key': item_key,
            'quantity': item['quantity'],
            'material': item['material'],
            'color': color,
            'scale': item['scale'],
            'model': model,
            'price_per_unit': price,
            'total_price': price * item['quantity'],
        }


    @staticmethod
    def __calculate_item_price(aggregated_options: list[dict[str, Any]], item: dict[str, Any], model: Model3D) -> Decimal:
        mat_price = [option['price'] for option in aggregated_options if option['name'] == item['material']]

        mat_price = mat_price[0] if mat_price else Decimal('0.00')

        price = (mat_price * model.price * (Decimal(item['scale']) / Decimal(100))).quantize(Decimal('0.00'),
                                                                                             rounding=ROUND_HALF_UP)
        return price


    def get_serialized_item(self, item_key: str):
        item = self.get_cart_item(item_key)
        return self.serialize_item(item)


    @staticmethod
    def serialize_item(item: dict[str, Any]):
        return {
            'item_key': item['item_key'],
            'quantity': item['quantity'],
            'material': item['material'],
            'color': item['color'].to_dict(),
            'scale': item['scale'],
            'model': item['model'].to_dict(),
            'price_per_unit': item['price_per_unit'],
            'total_price': item['total_price'],
        }


    @property
    def total_items(self):
        return sum([item['quantity'] for item in self.cart.values()])

    @property
    def total_cart_price(self):
        return sum([item['total_price'] for item in self.get_items()])
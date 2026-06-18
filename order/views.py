import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST, require_GET

from models_3d.models import Material
from order.forms import AddToCartForm
from order.models import Order, OrderItem
from order.services import Cart


@require_POST
@login_required
def add_to_cart(request, model_id: int):
    aggregated_options = Material.objects.get_aggregated_options()
    form = AddToCartForm(request.POST, aggregated_options=aggregated_options)

    if form.is_valid():
        material = form.cleaned_data.get('material')
        color = form.cleaned_data.get('color')
        scale = form.cleaned_data.get('scale')

        item_key = f'{model_id}-{material}-{color.id}-{scale}'

        cart = Cart(request)
        cart.add(
            {
                'item_key': item_key,
                'quantity': 1,
                'material': material,
                'color': color.id,
                'scale': scale,
                'model_id': model_id
            }
        )
    else:
        print(form.errors)

    return redirect('model_detail', id=model_id)


@require_GET
@login_required
def cart(request):
    cart_service = Cart(request)

    context = {'cart': cart_service}

    return render(request, 'order/cart/cart.html', context=context)


@require_POST
@login_required
def update_cart(request):
    try:
        data = json.loads(request.body.decode('utf-8'))

        item_key = data.get('item_key', None)
        quantity = data.get('quantity', None)
        scale = data.get('scale', None)

        if item_key is None or quantity is None or scale is None:
            return JsonResponse({'status': 'error', 'message': 'Missing data'}, status=400)

        if quantity < 0:
            return JsonResponse({'status': 'error', 'message': 'Quantity must be positive'}, status=400)

        if scale <= 0:
            return JsonResponse({'status': 'error', 'message': 'Scale must be positive'}, status=400)

        cart = Cart(request)

        if item_key not in cart.cart.keys():
            return JsonResponse({'status': 'error', 'message': 'Item not found'}, status=400)

        if quantity == 0:
            cart.delete(item_key)
            return JsonResponse({
                'status': 'success',
                'message': 'Item deleted',
                'total_items': cart.total_items,
                'total_cart_price': str(cart.total_cart_price),
            },
                status=200)

        updated_item_data = cart.update(item_key=item_key, quantity=quantity, scale=scale)

        response_data = {
            'status': 'ok',
            'item': Cart.serialize_item(updated_item_data),
            'total_items': cart.total_items,
            'total_cart_price': str(cart.total_cart_price),
        }
        return JsonResponse(response_data)

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        print(f"Error updating cart: {e}")
        return JsonResponse({'status': 'error', 'message': 'Internal server error'}, status=500)


@require_POST
@login_required
@transaction.atomic
def create_order(request):
    user = request.user
    cart = Cart(request)

    if user.balance < cart.total_cart_price:
        messages.error(request, 'You do not have enough money!')
        return redirect('cart')

    order = Order.objects.create(
        user=user,
        total_price=cart.total_cart_price
    )

    cart_items = cart.get_items()

    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            model_3d=item['model'],
            material_name=item['material'],
            color=item['color'],
            quantity=item['quantity'],
            price=item['price_per_unit'],
            scale=item['scale'],
        )

    user.balance -= cart.total_cart_price
    user.save()

    cart.clear()

    messages.success(request, 'Order created.')
    return redirect('cart')


@require_GET
def orders(request):
    orders = (Order.objects.filter(user=request.user).prefetch_related('orderitem_set')
              .annotate(items_count=Count('orderitem')).order_by('-created_at'))
    context = {'orders': orders}
    return render(request, 'order/order_list.html', context=context)


@require_GET
def order_detail(request, order_id):
    order = Order.objects.get(id=order_id)
    context = {'order': order, 'statuses': Order.OrderStatus}
    return render(request, 'order/order_detail.html', context=context)


@transaction.atomic
@require_POST
def cancel_order(request, order_id):
    order = Order.objects.get(id=order_id)
    order.status = Order.OrderStatus.CANCELLED
    order.save()
    user = request.user
    user.balance += order.total_price
    user.save()
    messages.success(request, 'Order canceled.')
    return redirect('orders')
// Файл: static/js/cart.js

// --- Блок 1: Утилиты и Конфигурация ---
// ------------------------------------------

// Получаем CSRF токен для безопасных POST-запросов
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const CSRF_TOKEN = getCookie('csrftoken');
const UPDATE_CART_URL = '/cart/update/'; // URL для обновления корзины

// --- Блок 2: Работа с сервером (API) ---
// -----------------------------------------

// Одна функция, ответственная за все запросы к серверу
async function api_updateCart(itemKey, quantity, scale) {
    try {
        const response = await fetch(UPDATE_CART_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': CSRF_TOKEN
            },
            body: JSON.stringify({ item_key: itemKey, quantity, scale })
        });

        if (!response.ok) {
            console.error('Ошибка ответа сервера:', response);
            return null; // Возвращаем null в случае ошибки
        }
        return await response.json(); // Возвращаем данные в формате JSON
    } catch (error) {
        console.error('Ошибка сети или выполнения запроса:', error);
        return null;
    }
}

// --- Блок 3: Обновление интерфейса (UI) ---
// --------------------------------------------

// Функция, которая обновляет только итоговую сводку
function ui_updateSummary(data) {
    document.getElementById('total-items-count').textContent = data.total_items;
    document.getElementById('subtotal-price').textContent = `${data.total_cart_price} ₽`;
    document.getElementById('total-price').textContent = `${data.total_cart_price} ₽`;
}

// Функция, которая обновляет один конкретный товар
function ui_updateCartItem(itemElement, itemData) {
     itemElement.querySelector('.quantity-input').value = itemData.quantity;
     itemElement.querySelector('.cart-item-price').textContent = `${itemData.total_price} ₽`;
}

// Функция, которая показывает сообщение о пустой корзине
function ui_showEmptyCart() {
    const layout = document.querySelector('.cart-layout');
    if (layout) {
        layout.innerHTML = `
            <div class="cart-empty" style="width: 100%;">
                <h2>Ваша корзина пуста</h2>
                <p>Самое время добавить в нее что-нибудь интересное!</p>
                <a href="/models/" class="btn btn-primary">Перейти в каталог</a>
            </div>`;
    }
}

// --- Блок 4: Инициализация и Обработчики Событий ---
// ----------------------------------------------------

// Функция, которая "оживляет" один товар в корзине
function initializeCartItem(itemElement) {
    const itemKey = itemElement.dataset.itemKey;
    const quantityInput = itemElement.querySelector('.quantity-input');
    const scaleSlider = itemElement.querySelector('.scale-slider');
    const scaleValueDisplay = itemElement.querySelector('.scale-value');

    const updateItem = async (quantity, scale) => {
        const data = await api_updateCart(itemKey, quantity, scale);
        if (!data) return; // Если была ошибка, ничего не делаем

        // Если товар еще существует, обновляем его
        if (data.item) {
            ui_updateCartItem(itemElement, data.item);
        } else {
            // Иначе - удаляем из DOM
            itemElement.remove();
        }

        // Обновляем общую сводку
        ui_updateSummary(data);

        // Если товаров 0, показываем сообщение о пустой корзине
        if (data.total_items === 0) {
            ui_showEmptyCart();
        }
    };

    itemElement.querySelector('.plus').addEventListener('click', () => {
        updateItem(parseInt(quantityInput.value) + 1, parseInt(scaleSlider.value));
    });

    itemElement.querySelector('.minus').addEventListener('click', () => {
        const newQuantity = parseInt(quantityInput.value) - 1;
        if (newQuantity < 1){
            return;
        }
        updateItem(newQuantity, parseInt(scaleSlider.value));
    });

    itemElement.querySelector('.remove-item-btn').addEventListener('click', () => {
        if (confirm('Вы уверены, что хотите удалить товар?')) {
            updateItem(0, parseInt(scaleSlider.value));
        }
    });

    scaleSlider.addEventListener('input', () => {
        scaleValueDisplay.textContent = scaleSlider.value;
    });

    scaleSlider.addEventListener('change', () => {
        updateItem(parseInt(quantityInput.value), parseInt(scaleSlider.value));
    });
}

// --- Точка входа: Запускаем все после загрузки страницы ---
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.cart-item').forEach(initializeCartItem);
});
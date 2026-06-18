// ========== ПЕРЕСЧЁТ ЦЕНЫ НА ДЕТАЛЬНОЙ СТРАНИЦЕ (ФИНАЛЬНАЯ ВЕРСИЯ) ==========
document.addEventListener('DOMContentLoaded', function() {
    const materialSelect = document.getElementById('materialSelect');
    const colorSelect = document.getElementById('colorSelect');
    const scaleInput = document.getElementById('scale');
    const priceDisplay = document.getElementById('priceDisplay');

    if (materialSelect && colorSelect && scaleInput && priceDisplay) {
        const basePrice = parseFloat(priceDisplay.dataset.basePrice);

        function updatePrice() {
            const selectedMaterialOption = materialSelect.options[materialSelect.selectedIndex];

            let materialPricePerGram = parseFloat(selectedMaterialOption.dataset.price);

            let currentScale = parseInt(scaleInput.value);

            let scaleFactor = currentScale / 100

            let finalPrice = basePrice * materialPricePerGram * scaleFactor;

            priceDisplay.innerText = finalPrice.toFixed(2) + ' ₽';
        }

        function updateAvailableColors() {
            const selectedMaterialOption = materialSelect.options[materialSelect.selectedIndex];
            const colorsData = selectedMaterialOption.dataset.colors;

            const customOptionsContainer = document.querySelector('.custom-options');
            const customSelectTrigger = document.querySelector('.custom-select__trigger span');

            if (!colorsData || !customOptionsContainer) {
                return;
            }

            const availableColors = JSON.parse(colorsData);

            colorSelect.innerHTML = '';
            customOptionsContainer.innerHTML = '';

            if (availableColors.length > 0) {
                availableColors.forEach((color, index) => {
                    const option = document.createElement('option');
                    option.value = color.id;
                    option.innerText = color.name;
                    colorSelect.appendChild(option);

                    const customOption = document.createElement('span');
                    customOption.classList.add('custom-option');
                    customOption.dataset.value = color.id; // Сохраняем ID
                    customOption.innerText = color.name;
                    customOption.style.setProperty('--color-hex', color.hex);

                    customOption.addEventListener('click', () => {
                        customSelectTrigger.textContent = color.name;
                        colorSelect.value = color.id;
                        document.querySelector('.custom-select').classList.remove('open');
                    });

                    customOptionsContainer.appendChild(customOption);

                    if (index === 0) {
                        option.selected = true;
                        customSelectTrigger.textContent = color.name;
                    }
                });
            } else {
                customSelectTrigger.textContent = 'Цвета не найдены';
            }
        }

        const customSelect = document.querySelector('.custom-select');
        if (customSelect) {
            const trigger = customSelect.querySelector('.custom-select__trigger');
            trigger.addEventListener('click', () => {
                customSelect.classList.toggle('open');
            });
        }

        function handleMaterialChange() {
            updatePrice();
            updateAvailableColors();
        }

        materialSelect.addEventListener('change', handleMaterialChange);
        scaleInput.addEventListener('input', updatePrice);

        handleMaterialChange();
    }

    const togglePasswordIcons = document.querySelectorAll('.toggle-password');
    togglePasswordIcons.forEach(icon => {
        icon.addEventListener('click', function () {
            const passwordInput = this.previousElementSibling;

            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);

            this.classList.toggle('bi-eye');
            this.classList.toggle('bi-eye-slash');
        });
    });
});
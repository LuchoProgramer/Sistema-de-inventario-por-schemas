// static/js/filtrado.js

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('product-search').addEventListener('input', function() {
        var searchValue = this.value.toLowerCase();
        var products = document.querySelectorAll('#product-list li');
        products.forEach(function(product) {
            if (product.textContent.toLowerCase().includes(searchValue)) {
                product.style.display = ''; // Mostrar el producto si coincide
            } else {
                product.style.display = 'none'; // Ocultar el producto si no coincide
            }
        });
    });
});

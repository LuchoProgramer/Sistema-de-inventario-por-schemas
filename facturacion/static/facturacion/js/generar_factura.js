document.addEventListener('DOMContentLoaded', function() {
    const nuevoClienteCheck = document.getElementById('nuevo_cliente_check');
    const nuevoClienteForm = document.getElementById('nuevo_cliente_form');
    const totalFacturaInput = document.getElementById('total_factura');
    const saldoRestanteInput = document.getElementById('saldo_restante');
    const paymentMethodsContainer = document.getElementById('payment-methods-container');
    const addPaymentMethodButton = document.getElementById('add-payment-method');

    // Mostrar/ocultar el formulario de nuevo cliente
    nuevoClienteCheck.addEventListener('change', function() {
        nuevoClienteForm.style.display = this.checked ? 'block' : 'none';
    });

    // Convertimos el total de la factura a número
    const totalFactura = parseFloat(totalFacturaInput.value);

    // Función para recalcular el saldo restante
    function recalcularSaldoRestante() {
        let totalPagado = 0;

        // Sumar todos los montos de pago
        paymentMethodsContainer.querySelectorAll('input[name="montos_pago"]').forEach(function(input) {
            const monto = parseFloat(input.value) || 0;
            totalPagado += monto;
        });

        // Calcular el saldo restante
        const saldoRestante = totalFactura - totalPagado;
        saldoRestanteInput.value = saldoRestante.toFixed(2);  // Mostrar el saldo con dos decimales

        // Validación: Si el saldo restante es menor que 0, mostrar alerta
        if (saldoRestante < 0) {
            alert("El monto total pagado excede el valor de la factura.");
        }
    }

    // Escuchar los cambios en los montos de pago
    paymentMethodsContainer.addEventListener('input', recalcularSaldoRestante);

    // Función para agregar un nuevo método de pago
    function agregarMetodoDePago() {
        const newPaymentMethod = paymentMethodsContainer.children[0].cloneNode(true);

        // Limpiar el monto y el método de pago en el nuevo campo
        newPaymentMethod.querySelector('select').value = '01';
        newPaymentMethod.querySelector('input').value = '';

        // Añadir el nuevo método de pago y recalcular el saldo restante
        paymentMethodsContainer.appendChild(newPaymentMethod);
        recalcularSaldoRestante();  // Recalcular después de añadir
    }

    // Agregar un evento para agregar métodos de pago al hacer clic en el botón
    addPaymentMethodButton.addEventListener('click', agregarMetodoDePago);
});

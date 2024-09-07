document.addEventListener('DOMContentLoaded', function() {
    const nuevoClienteCheck = document.getElementById('nuevo_cliente_check');
    const nuevoClienteForm = document.getElementById('nuevo_cliente_form');
    const totalFacturaInput = document.getElementById('total_factura');
    const saldoRestanteInput = document.getElementById('saldo_restante');
    const paymentMethodsContainer = document.getElementById('payment-methods-container');
    const addPaymentMethodButton = document.getElementById('add-payment-method');
    const form = document.querySelector('form');
    const clienteSelect = document.getElementById('cliente');
    const identificacionInput = document.getElementById('identificacion');

    // Mostrar/ocultar el formulario de nuevo cliente
    nuevoClienteCheck.addEventListener('change', function() {
        nuevoClienteForm.style.display = this.checked ? 'block' : 'none';
    });

    // Convertimos el total de la factura a número
    const totalFactura = parseFloat(totalFacturaInput.value) || 0;

    // Función para recalcular el saldo restante
    function recalcularSaldoRestante() {
        let totalPagado = 0;

        paymentMethodsContainer.querySelectorAll('input[name="montos_pago"]').forEach(function(input) {
            const monto = parseFloat(input.value) || 0;
            totalPagado += monto;
        });

        const saldoRestante = totalFactura - totalPagado;
        saldoRestanteInput.value = saldoRestante.toFixed(2);

        if (saldoRestante < 0) {
            alert("El monto total pagado excede el valor de la factura.");
        }
    }

    paymentMethodsContainer.addEventListener('input', recalcularSaldoRestante);

    function agregarMetodoDePago() {
        const newPaymentMethod = paymentMethodsContainer.children[0].cloneNode(true);
        newPaymentMethod.querySelector('select').value = '01';
        newPaymentMethod.querySelector('input').value = '';
        paymentMethodsContainer.appendChild(newPaymentMethod);
        recalcularSaldoRestante();
    }

    addPaymentMethodButton.addEventListener('click', agregarMetodoDePago);

    form.addEventListener('submit', function(event) {
        event.preventDefault();

        if (!clienteSelect.value && (!nuevoClienteCheck.checked || !identificacionInput.value)) {
            alert("Por favor, selecciona un cliente o ingresa los datos de un nuevo cliente.");
            return;
        }

        fetch(form.action, {
            method: 'POST',
            body: new FormData(form),
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                const errorAlert = document.createElement('div');
                errorAlert.className = 'alert alert-danger';
                errorAlert.role = 'alert';
                errorAlert.innerText = data.error;
                form.prepend(errorAlert);
            } else if (data.pdf_url && data.redirect_url) {
                // Open the PDF in a new tab
                window.open(data.pdf_url, '_blank');

                // Redirect to the new page (home)
                window.location.href = data.redirect_url;
            }
        })
        .catch(error => console.error('Error:', error));
    });
});

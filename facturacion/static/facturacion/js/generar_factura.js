document.addEventListener('DOMContentLoaded', function () {
    const totalFacturaInput = document.getElementById('total_factura');
    const saldoRestanteInput = document.getElementById('saldo_restante');
    const paymentMethodsContainer = document.getElementById('payment-methods-container');
    const addPaymentMethodButton = document.getElementById('add-payment-method');
    const form = document.querySelector('form');
    const clienteSelect = document.getElementById('cliente');
    const identificacionInput = document.getElementById('identificacion');
    const nuevoClienteCheck = document.getElementById('nuevo_cliente_check');
    const nuevoClienteForm = document.getElementById('nuevo_cliente_form');

    // Convertir el total de la factura a decimal con dos decimales
    const totalFactura = parseFloat(totalFacturaInput.value).toFixed(2);

    // Mostrar u ocultar el formulario de nuevo cliente
    nuevoClienteCheck.addEventListener('change', function () {
        nuevoClienteForm.style.display = this.checked ? 'block' : 'none';
    });

    // Normalizar el separador decimal (coma a punto)
    function normalizarMonto(monto) {
        return parseFloat(monto.replace(',', '.')) || 0;
    }

    // Función para actualizar el saldo restante con tolerancia por redondeo
    function actualizarSaldoRestante() {
        const totalFactura = normalizarMonto(totalFacturaInput.value);
        let sumaPagos = 0;

        // Iterar sobre los montos de pago y sumar sus valores normalizados
        document.querySelectorAll('input[name="montos_pago"]').forEach(input => {
            sumaPagos += normalizarMonto(input.value);
        });

        let saldoRestante = (totalFactura - sumaPagos).toFixed(2);

        // Tolerancia mínima para evitar errores de redondeo
        if (Math.abs(saldoRestante) < 0.01) {
            saldoRestante = '0.00';
        }

        saldoRestanteInput.value = saldoRestante;

        console.log(`Total Factura: ${totalFactura}, Pagos: ${sumaPagos}, Saldo Restante: ${saldoRestante}`);

        if (saldoRestante < 0) {
            alert("El monto total pagado excede el valor de la factura.");
        }
    }

    // Asignar eventos a los inputs de montos de pago
    function asignarEventoMontoPago(input) {
        input.addEventListener('input', actualizarSaldoRestante);
    }

    // Función para agregar un nuevo método de pago
    function agregarMetodoDePago() {
        const newPaymentMethod = paymentMethodsContainer.children[0].cloneNode(true);
        newPaymentMethod.querySelector('select').value = '01'; // Valor por defecto
        const input = newPaymentMethod.querySelector('input');
        input.value = '';
        paymentMethodsContainer.appendChild(newPaymentMethod);

        asignarEventoMontoPago(input);
        actualizarSaldoRestante();
    }

    // Asignar eventos a los inputs existentes al cargar la página
    document.querySelectorAll('input[name="montos_pago"]').forEach(asignarEventoMontoPago);

    // Evento para agregar un nuevo método de pago
    addPaymentMethodButton.addEventListener('click', agregarMetodoDePago);

    // Manejo del envío del formulario
    form.addEventListener('submit', function (event) {
        event.preventDefault();

        if (!clienteSelect.value && (!nuevoClienteCheck.checked || !identificacionInput.value)) {
            alert("Por favor, selecciona un cliente o ingresa los datos de un nuevo cliente.");
            return;
        }

        // Enviar el formulario con fetch
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
                window.open(data.pdf_url, '_blank');
                window.location.href = data.redirect_url;
            }
        })
        .catch(error => console.error('Error:', error));
    });
});

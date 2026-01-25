// JavaScript for handling payment process in the cart
document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("paymentForm").addEventListener("submit", function (event) {
        event.preventDefault(); // Prevent default form submission

        let formData = new FormData(this);

        fetch("{% url 'process-payment' %}", {
            method: "POST",
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                closeModal(); // Close payment modal

                // Display the bill in a pop-up
                let billPopup = document.createElement("div");
                billPopup.id = "billPopup";
                billPopup.className = "fixed inset-0 flex items-center justify-center bg-gray-900 bg-opacity-50";
                billPopup.innerHTML = `
                    <div class="bg-gray-800 text-white p-6 rounded-lg shadow-lg w-96 relative">
                        <button id="closeBillPopup" class="absolute top-2 right-2 text-white hover:text-gray-300 text-xl">&times;</button>
                        ${data.bill_html} <!-- Insert the bill HTML -->
                        <button id="redirectToOrders" class="mt-4 w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-500">
                            View Order Summary
                        </button>
                    </div>
                `;
                document.body.appendChild(billPopup);

                // Close the bill pop-up and refresh page
                document.getElementById("closeBillPopup").addEventListener("click", function () {
                    location.reload(); // Refresh the page
                });

                // Redirect to order summary
                document.getElementById("redirectToOrders").addEventListener("click", function () {
                    window.location.href = "{% url 'order-summary' %}"; // Update with your actual order summary URL
                });

            } else {
                alert(data.message);
            }
        })
        .catch(error => console.error("Error:", error));
    });
});

// =====================================
// SHOW / HIDE PASSWORD
// =====================================

function togglePassword() {

    const password = document.getElementById("password");

    if (!password) {
        return;
    }

    if (password.type === "password") {
        password.type = "text";
    } else {
        password.type = "password";
    }
}


// =====================================
// AUTO HIDE FLASH MESSAGES
// =====================================

setTimeout(function () {

    const alerts = document.querySelectorAll(".alert");

    alerts.forEach(function (alert) {

        alert.style.transition = "opacity 0.5s";

        alert.style.opacity = "0";

        setTimeout(function () {
            alert.remove();
        }, 500);

    });

}, 4000);


// =====================================
// MARKS VALIDATION
// =====================================

const marksInput = document.getElementById("marks");

if (marksInput) {

    marksInput.addEventListener("input", function () {

        const marks = Number(this.value);

        if (marks < 0 || marks > 100) {

            this.setCustomValidity(
                "Marks must be between 0 and 100."
            );

        } else {

            this.setCustomValidity("");

        }

    });

}


// =====================================
// DELETE / IMPORTANT ACTION CONFIRMATION
// =====================================

const confirmButtons =
    document.querySelectorAll(".confirm-action");

confirmButtons.forEach(function (button) {

    button.addEventListener("click", function (event) {

        const message =
            button.dataset.message ||
            "Are you sure you want to continue?";

        if (!confirm(message)) {

            event.preventDefault();

        }

    });

});
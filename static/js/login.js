// =========================================
// Vignan E.M. School
// Login Page JavaScript
// =========================================

document.addEventListener("DOMContentLoaded", function () {

    // ==========================
    // Input Animation
    // ==========================

    const inputs = document.querySelectorAll("input");

    inputs.forEach(input => {

        input.addEventListener("focus", function () {

            this.style.borderColor = "#0B5CAB";
            this.style.boxShadow = "0 0 10px rgba(11,92,171,0.25)";

        });

        input.addEventListener("blur", function () {

            this.style.borderColor = "#dcdcdc";
            this.style.boxShadow = "none";

        });

    });

    // ==========================
    // Form Validation
    // ==========================

    const forms = document.querySelectorAll("form");

    forms.forEach(form => {

        form.addEventListener("submit", function (e) {

            const username = form.querySelector("input[name='username']");
            const password = form.querySelector("input[name='password']");

            if (username.value.trim() === "") {

                alert("Please enter Username / Student ID");

                username.focus();

                e.preventDefault();

                return;

            }

            if (password.value.trim() === "") {

                alert("Please enter Password");

                password.focus();

                e.preventDefault();

                return;

            }

            // Login Animation

            const button = form.querySelector("button");

            button.innerHTML = "Logging in...";

            button.disabled = true;

        });

    });

});

// =========================================
// Show / Hide Password
// =========================================

function togglePassword(id) {

    const password = document.getElementById(id);

    if (!password) return;

    if (password.type === "password") {

        password.type = "text";

    }

    else {

        password.type = "password";

    }

}

// =========================================
// Reset Button
// =========================================

function resetButton(button) {

    button.disabled = false;

    button.innerHTML = "Login";

}

// =========================================
// Fade In Animation
// =========================================

window.onload = function () {

    document.body.style.opacity = "1";

};
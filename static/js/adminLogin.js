// When "Forgot Password?" is clicked, fade out the login form and display the recovery form
document.getElementById('forgotPass').addEventListener('click', function () {
    switchToRecoverPasswordForm();
});
function switchToRecoverPasswordForm() {
    const loginForm = document.getElementById('form-login');
    const recoverForm = document.getElementById('form-recover-password');

    // Fade out the login form
    loginForm.style.opacity = '0';
    loginForm.style.transform = 'translateY(-50px)';

    // After the transition, hide the login form and show the recovery form
    setTimeout(() => {
        loginForm.style.display = 'none';
        recoverForm.style.display = 'block';
        recoverForm.style.opacity = '0';  // Start with opacity 0
        recoverForm.style.transform = 'translateY(50px)';  // Start with slide down

        // Fade in the recovery form
        setTimeout(() => {
            recoverForm.style.opacity = '1';
            recoverForm.style.transform = 'translateY(0)';
        }, 100);
    }, 500);  // Wait for the fade-out transition to complete
};

function switchToNewPasswordForm() {
    const recoverForm = document.getElementById('form-recover-password');
    const newPasswordForm = document.getElementById('form-new-password');

    // Fade out the login form
    recoverForm.style.opacity = '0';
    recoverForm.style.transform = 'translateY(-50px)';

    // After the transition, hide the login form and show the recovery form
    setTimeout(() => {
        recoverForm.style.display = 'none';
        newPasswordForm.style.display = 'block';
        newPasswordForm.style.opacity = '0';  // Start with opacity 0
        newPasswordForm.style.transform = 'translateY(50px)';  // Start with slide down

        // Fade in the recovery form
        setTimeout(() => {
            newPasswordForm.style.opacity = '1';
            newPasswordForm.style.transform = 'translateY(0)';
        }, 100);
    }, 500);  // Wait for the fade-out transition to complete
}

// Function to switch to the login form after successfully changing the password
function switchToLoginForm() {
    const loginForm = document.getElementById('form-login');
    const newPasswordForm = document.getElementById('form-new-password');

    // Fade out the "Set New Password" form
    newPasswordForm.style.opacity = '0';
    newPasswordForm.style.transform = 'translateY(-50px)';

    // After the transition, hide the new password form and show the login form
    setTimeout(() => {
        newPasswordForm.style.display = 'none';
        loginForm.style.display = 'block';
        loginForm.style.opacity = '0';  // Start with opacity 0
        loginForm.style.transform = 'translateY(50px)';  // Start with slide down

        // Fade in the login form
        setTimeout(() => {
            loginForm.style.opacity = '1';
            loginForm.style.transform = 'translateY(0)';
        }, 100);
    }, 500);  // Wait for the fade-out transition to complete
}

// Handle security questions form submission with AJAX
document.getElementById('form-recover-password').addEventListener('submit', function (event) {
    event.preventDefault(); // Prevent traditional form submission
    const formData = new FormData(this);
    messageQuestionsBox = document.getElementById('message-questions');  // Get the message box element

    fetch('/check_answers', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Hide the recovery form and show the new password form
                messageQuestionsBox.textContent = '';  // Clear the message box
                switchToNewPasswordForm();

                // Clear the inputs in the recovery form when the answers are correct
                document.getElementById('form-recover-password').reset();
            } else {
                // Show error message if answers are incorrect
                messageQuestionsBox.textContent = data.message;
                messageQuestionsBox.style.color = "red";  // Set the message color to red for visibility
            }
        });
});

// Handle new password form submission with AJAX
document.getElementById('form-new-password').addEventListener('submit', function (event) {
    event.preventDefault(); // Prevent traditional form submission
    const formData = new FormData(this);
    const messagePasswordBox = document.getElementById('message-password');  // Get the message box element

    const newPassword = document.getElementById('new-password').value;
    const verifyNewPassword = document.getElementById('verify-new-password').value;

    // Check if passwords match before submitting the form
    if (newPassword === verifyNewPassword) {
        fetch('/reset_password', {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Password changed successfully, show login form
                    switchToLoginForm();
                } else {
                    messagePasswordBox.textContent = data.message;  // Display server response message
                    messagePasswordBox.style.color = "red";  // Set message color to red for error visibility
                }
            });
    } else {
        messagePasswordBox.textContent = "Passwords do not match!";  // Display "Passwords do not match!" message
        messagePasswordBox.style.color = "red";  // Set the message color to red for visibility
    }
});

// Function to toggle password visibility
function togglePasswordVisibility(toggleButton, passwordField, eyeIcon) {
    toggleButton.addEventListener('click', () => {
        // Toggle between 'password' and 'text' input type
        const inputType = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordField.setAttribute('type', inputType);

        // Toggle eye icon
        eyeIcon.classList.toggle('bi-eye');
        eyeIcon.classList.toggle('bi-eye-slash');
    });
}

// Elements for 'New Password' field
const toggleNewPassword = document.getElementById('toggle-new-password');
const newPasswordInput = document.getElementById('new-password');
const eyeNewPassword = document.getElementById('eye-new-password');

// Elements for 'Verify New Password' field
const toggleVerifyPassword = document.getElementById('toggle-verify-password');
const verifyPasswordInput = document.getElementById('verify-new-password');
const eyeVerifyPassword = document.getElementById('eye-verify-password');

// Elements for 'Password' field
const togglePassword = document.getElementById('toggle-password');
const passwordInput = document.getElementById('password');
const eyePassword = document.getElementById('eye-password');

// Apply the toggle function to all password fields
togglePasswordVisibility(toggleNewPassword, newPasswordInput, eyeNewPassword);
togglePasswordVisibility(toggleVerifyPassword, verifyPasswordInput, eyeVerifyPassword);
togglePasswordVisibility(togglePassword, passwordInput, eyePassword);

// Clear the "Passwords do not match!" message when the user starts typing in the password fields
document.getElementById('security-answer1').addEventListener('input', function () {
    messageBox.textContent = '';  // Clear the message
});
document.getElementById('security-answer2').addEventListener('input', function () {
    messageBox.textContent = '';  // Clear the message
});
document.getElementById('security-answer3').addEventListener('input', function () {
    messageBox.textContent = '';  // Clear the message
});

document.getElementById('new-password').addEventListener('input', function () {
    messageBox.textContent = '';  // Clear the message
});

document.getElementById('verify-new-password').addEventListener('input', function () {
    messageBox.textContent = '';  // Clear the message
});

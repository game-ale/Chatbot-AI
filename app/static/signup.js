// signup.js

document.addEventListener('DOMContentLoaded', () => {
    const signupForm = document.getElementById('signupForm');
    const passwordField = document.getElementById('password');
    const confirmPasswordField = document.getElementById('confirm_password');
    
    // Add a submit event listener to the form
    signupForm.addEventListener('submit', (event) => {
        // Check if passwords match
        if (passwordField.value !== confirmPasswordField.value) {
            event.preventDefault(); // Prevent form submission
            alert('Passwords do not match!');
        }
    });

    // Optionally, display a message in the console when the page loads
    console.log("Signup page loaded.");
});

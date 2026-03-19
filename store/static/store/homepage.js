// Add an event listener to the window object that listens for when the user scrolls
window.addEventListener('scroll', function() {
    // Get the back-to-top button element from the DOM
    var backToTopButton = document.querySelector('.back-to-top-wrapper');
    // If the user has scrolled down beyond 2000 pixels
    if (window.scrollY > 2000) {
        // Add the 'show' CSS class to the back-to-top button element
        backToTopButton.classList.add('show');
    } else {
        // Otherwise, remove the 'show' CSS class from the back-to-top button element
        backToTopButton.classList.remove('show');
    }
});

// Get the image of the man from the DOM
let manImg = document.querySelector(".col-10 img");
// Set the initial height of the image to 0
let height1 = 0;
// Set the initial direction of the animation to down
let direction = 1;
// Set up an interval that runs every 50 milliseconds
let manAnimation = setInterval(function() {
    // If the height of the image is greater than or equal to 20 pixels
    if (height1 >= 20) {
        // Reverse the direction of the animation to move the image up
        direction = -1;
        // If the height of the image is less than or equal to 0 pixels
    } else if (height1 <= 0) {
        // Reverse the direction of the animation to move the image down
        direction = 1;
    }
    // Increment or decrement the height of the image based on the current direction
    height1 += direction;
    // Apply a CSS transform to the image to move it up or down based on the current height
    manImg.style.transform = `translateY(-${height1}px)`;
}, 50);

// Get the image of the perfume from the DOM
let perfumeImg = document.getElementById("perfumeImg");
// Set the initial height of the image to 0
let height = 0;
// Set the initial direction of the animation to down
let direction2 = 1;
// Set up an interval that runs every 50 milliseconds
let perfumeAnimation = setInterval(function() {
    // If the height of the image is greater than or equal to 20 pixels
    if (height >= 20) {
        // Reverse the direction of the animation to move the image up
        direction2 = -1;
        // If the height of the image is less than or equal to 0 pixels
    } else if (height <= 0) {
        // Reverse the direction of the animation to move the image down
        direction2 = 1;
    }
    // Increment or decrement the height of the image based on the current direction
    height += direction2;
    // Apply a CSS transform to the image to move it up or down based on the current height
    perfumeImg.style.transform = `translateY(-${height}px)`;
}, 50);

// Add a mouseenter event listener to the man image
manImg.addEventListener('mouseenter', function() {
    // Stop the man animation by clearing the interval
    clearInterval(manAnimation);
});

// Add a mouseleave event listener to the man image
manImg.addEventListener('mouseleave', function() {
    // Restart the man animation by setting the interval again
    manAnimation = setInterval(function() {
        // If the height of the image is greater than or equal to 20 pixels
        if (height1 >= 20) {
            // Reverse the direction of the animation to move the image up
            direction = -1;
            // If the height of the image is less than or equal to 0 pixels
        } else if (height1 <= 0) {
            // Reverse the direction of the animation to move the image down
            direction = 1;
        }
        // Increment or decrement the height of the image based on the current direction
        height1 += direction;
        // Apply a CSS transform to the image to move it up or down based on the current height
        manImg.style.transform = `translateY(-${height1}px)`;
    }, 50);
});

// Add a mouseenter event listener to the perfume image
perfumeImg.addEventListener('mouseenter', function() {
    // Stop the perfume animation by clearing the interval
    clearInterval(perfumeAnimation);
});

// Add a mouseleave event listener to the perfume image
perfumeImg.addEventListener('mouseleave', function() {
    // Restart the perfume animation by setting the interval again
    perfumeAnimation = setInterval(function() {
        // If the height of the image is greater than or equal to 20 pixels
        if (height >= 20) {
            // Reverse the direction of the animation to move the image up
            direction2 = -1;
            // If the height of the image is less than or equal to 0 pixels
        } else if (height <= 0) {
            // Reverse the direction of the animation to move the image down
            direction2 = 1;
        }
        // Increment or decrement the height of the image based on the current direction
        height += direction2;
        // Apply a CSS transform to the image to move it up or down based on the current height
        perfumeImg.style.transform = `translateY(-${height}px)`;
    }, 50);
});

// Define a function that is called when the user submits their email address to subscribe to a newsletter
function subscribe() {
    // Get the email input element, heading element, text element, and error element from the DOM
    let emailInput = document.getElementById("subscribe-email");
    let heading = document.getElementById("subscribe-heading");
    let text = document.getElementById("subscribe-text");
    let error = document.getElementById("subscribe-error");

    // Get the value of the email input and trim any whitespace from the beginning and end
    let email = emailInput.value.trim();
    // Define a regular expression pattern that matches valid email addresses
    let emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    // If the email address is not empty
    if (email !== "") {
        // If the email address matches the valid email address pattern
        if (emailPattern.test(email)) {
            // Update the heading and text elements to thank the user for subscribing
            heading.textContent = "Thank you for subscribing to our newsletter";
            text.textContent = "";
            error.textContent = "";
            // If the email address does not match the valid email address pattern
        } else {
            // Update the error element to ask the user to enter a valid email address
            error.textContent = "Please enter a valid email address";
        }
        // If the email address is empty
    } else {
        // Clear the error element
        error.textContent = "";
    }
}
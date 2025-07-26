// Displays the selected image.

const options = document.querySelectorAll('ul.image-select-list li input[type="radio"]');
const selectedImage = document.querySelector('div.image-select button img.selected-image');
options.forEach((option) => {
    option.addEventListener('change', () => {
        if (option.checked) {
            selectedImage.src = option.dataset.staticUrl;
        }
    })
})

// Apply the initial value (checked) when rendering the page.
window.addEventListener("load", () => {
    options.forEach((option) => {
        if (option.checked) {
            selectedImage.src = option.dataset.staticUrl;
        }
    })
})

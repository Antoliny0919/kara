const getDynamicFields = (fields) => {
    const dynamicFields = fields.map(fieldName => [
        document.getElementById(inputFieldIdPrefix + fieldName),
        document.getElementById(displayFieldIdPrefix + fieldName)
    ]);
    return dynamicFields;
}

const dynamicDisplayTextField= ['receiver', 'receptionist'];
const inputFieldIdPrefix = 'id_';
const displayFieldIdPrefix = 'display_';
const displayDefaultValue = '?';
const dynamicTextFields = getDynamicFields(dynamicDisplayTextField);

dynamicTextFields.forEach(([inputNode, displayNode]) => {
    inputNode.addEventListener('input', () => {
        let value = inputNode.value;
        if (!value) {
            value = displayDefaultValue;
        }
        displayNode.textContent = value;
    })
});

const dynamicDisplayChoiceField = ["side"];
const dynamicChoiceFields = getDynamicFields(dynamicDisplayChoiceField);

dynamicChoiceFields.forEach(([groupNode, displayNode]) => {
    const checkedInput = groupNode.querySelector('input[type="radio"]:checked');
    const displayValue = checkedInput.parentNode.textContent;
    displayNode.textContent = displayValue;
    const options = groupNode.querySelectorAll('input[type="radio"]');
    options.forEach((option) => {
        option.addEventListener('change', () => {
            const displayValue = option.parentNode.textContent;
            displayNode.textContent = displayValue;
        })
    });
});

const dynamicDisplayDateField = ["wedding_date"]
const dynamicDateFields = getDynamicFields(dynamicDisplayDateField);

dynamicDateFields.forEach(([groupNode, displayNode]) => {
    const inputNodes = groupNode.querySelectorAll('input[type="text"]');
    const displayNodes = displayNode.querySelectorAll(`[id^=${displayFieldIdPrefix}]`);
    inputNodes.forEach((inputNode, index) => {
        inputNode.addEventListener('input', () => {
            const displayNode = displayNodes[index];
            let value = inputNode.value;
            if (!value) {
                value = displayDefaultValue;
            }
            displayNode.textContent = value;
        })
    })
})

const dynamicDisplayImageField = ["cover_image"]

const dynamicImageFields = getDynamicFields(dynamicDisplayImageField);

dynamicImageFields.forEach(([groupNode, displayNode]) => {
    const options = groupNode.querySelectorAll('ul li input[type="radio"]');
    options.forEach((option) => {
        option.addEventListener('change', () => {
            if (option.checked) {
                displayNode.src = option.dataset.staticUrl;
            }
        })
    })
})

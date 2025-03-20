const bioTextArea = document.getElementById('bio')

bioTextArea.addEventListener('click', () => {

    bioTextArea.focus()
    const inputFieldValue = bioTextArea.value

    if (inputFieldValue == 0) {
        bioTextArea.setSelectionRange(0,0)
    }
    else {
        bioTextArea.setSelectionRange(0,inputFieldValue.length)
    }
})
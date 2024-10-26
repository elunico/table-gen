

[...document.getElementsByTagName('select')].forEach(item => item.addEventListener('change', (event) => {
    console.log(event.currentTarget.options[event.currentTarget.selectedIndex].value);
}))

globalThis.togglePopoutInfo = function () {
    const tooltip = document.getElementById('popout-info');

    if (tooltip.style.display === 'none') {
        tooltip.style.display = 'block';
    } else {
        tooltip.style.display = 'none';
    }
};

globalThis.hidePopoutInfo = function () {
    const tooltip = document.getElementById('popout-info');
    if (tooltip) {
        tooltip.style.display = 'none';
    }
};

document.addEventListener('DOMContentLoaded', function () {
    const liveSearchBox = document.querySelector('.live-search-box');
    const liveSearchListRows = document.querySelectorAll('.live-search-list [data-search-term]');

    if (!liveSearchBox) return;

    liveSearchBox?.addEventListener('input', function () {
        const searchTerm = liveSearchBox.value.toLowerCase();
        liveSearchListRows.forEach(row => {
            const rowData = row.dataset.searchTerm;
            row.style.display = rowData.includes(searchTerm) ? '' : 'none';
            // row.innerHTML = row.innerHTML.replaceAll(searchTerm, '<mark>'+searchTerm+'</mark>');
        });
    });
});


document.addEventListener("DOMContentLoaded", function () {
    const flipCard = document.getElementById("flipCard");
    const flipTrigger = document.getElementById("flipTrigger");
    const flipBackTrigger = document.getElementById("flipBackTrigger");

    flipTrigger.addEventListener("click", () => {
        flipCard.classList.add("flipped");
    });

    flipBackTrigger.addEventListener("click", () => {
        flipCard.classList.remove("flipped");
    });


    const flipCard2 = document.getElementById("flipCard2");
    const flipTrigger2 = document.getElementById("flipTrigger2");
    const flipBackTrigger2 = document.getElementById("flipBackTrigger2");

    flipTrigger2.addEventListener("click", () => {
        flipCard2.classList.add("flipped");
    });

    flipBackTrigger2.addEventListener("click", () => {
        flipCard2.classList.remove("flipped");
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const liveSearchBox = document.querySelector('.live-search-box');
    const liveSearchListRows = document.querySelectorAll('.live-search-list [data-search-term]');

    if (!liveSearchBox) return;

    liveSearchBox.addEventListener('input', function () {
        const searchTerm = liveSearchBox.value.toLowerCase();
        liveSearchListRows.forEach(row => {
            const rowData = row.dataset.searchTerm;
            row.style.display = rowData.includes(searchTerm) ? '' : 'none';
            // row.innerHTML = row.innerHTML.replaceAll(searchTerm, '<mark>'+searchTerm+'</mark>');
        });
    });
});


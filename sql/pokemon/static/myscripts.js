
let liveSearchBox = document.querySelector('.live-search-box'); // Select the live-search-box with CSS selectors
let liveSearchListRows = document.querySelectorAll('.live-search-list tbody tr') // Select the live-search-list trs with CSS selectors

liveSearchBox.addEventListener('keyup', filterPokemon); // Run the function 'filterPokemon' whenever you type a key

function filterPokemon() {
    let searchTerm = liveSearchBox.value.toLowerCase();
    for (let liveSearchListRow of liveSearchListRows) {
        let rowData = liveSearchListRow.dataset.searchTerm;
        if (rowData.includes(searchTerm)) {
            liveSearchListRow.style.display = ''; // Remove CSS style 'display'
        } else {
            liveSearchListRow.style.display = 'none'; // Set CSS style 'display' to 'none'
        }
    }
}


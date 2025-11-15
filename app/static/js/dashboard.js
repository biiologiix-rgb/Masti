document.addEventListener('DOMContentLoaded', function() {
    // Initialize date filter functionality
    initDateFilter();
    
    // Handle responsive table
    handleResponsiveTable();
    
    // Set up resize listener (with debounce)
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(handleResponsiveTable, 250);
    });
});

function initDateFilter() {
    const dateInput = document.getElementById('dateFilter');
    const prevBtn = document.getElementById('prevDate');
    const nextBtn = document.getElementById('nextDate');
    
    // Check if elements exist
    if (!dateInput || !prevBtn || !nextBtn) return;
    
    const today = new Date().toISOString().split('T')[0];

    function submitWithDate() {
        const date = dateInput.value;
        const params = new URLSearchParams(window.location.search);
        params.set('date', date);
        window.location.search = params.toString();
    }

    function updateNextBtn() {
        nextBtn.disabled = (dateInput.value >= today);
    }

    prevBtn.addEventListener('click', function() {
        let current = new Date(dateInput.value);
        current.setDate(current.getDate() - 1);
        dateInput.value = current.toISOString().split('T')[0];
        updateNextBtn();
        submitWithDate();
    });

    nextBtn.addEventListener('click', function() {
        let current = new Date(dateInput.value);
        current.setDate(current.getDate() + 1);
        const newDate = current.toISOString().split('T')[0];
        if (newDate <= today) {
            dateInput.value = newDate;
            updateNextBtn();
            submitWithDate();
        }
    });

    dateInput.addEventListener('change', function() {
        updateNextBtn();
        submitWithDate();
    });

    updateNextBtn();
}

function handleResponsiveTable() {
    const table = document.getElementById('studentsTable');
    if (!table) return;
    
    if (window.innerWidth < 768) {
        convertTableToCards();
    } else {
        convertCardsToTable();
    }
}

function convertTableToCards() {
    const table = document.getElementById('studentsTable');
    if (!table) return;
    
    const headers = [];
    const thead = table.querySelector('thead tr');
    
    if (thead) {
        thead.querySelectorAll('th').forEach((th, index) => {
            headers[index] = th.textContent.replace(/↕$/, '').trim();
        });
    }
    
    table.querySelectorAll('tbody tr').forEach(row => {
        const cells = row.querySelectorAll('td');
        cells.forEach((cell, index) => {
            if (headers[index]) {
                cell.setAttribute('data-label', headers[index]);
            }
        });
    });
}

function convertCardsToTable() {
    const table = document.getElementById('studentsTable');
    if (!table) return;
    
    table.querySelectorAll('tbody td').forEach(cell => {
        cell.removeAttribute('data-label');
    });
}
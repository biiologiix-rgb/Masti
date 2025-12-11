document.addEventListener('DOMContentLoaded', function() {
    // Date navigation functionality
    const dateInput = document.getElementById('dateFilter');
    const prevBtn = document.getElementById('prevDate');
    const nextBtn = document.getElementById('nextDate');
    const rollFilter = document.getElementById('rollFilter');
    const clearFilter = document.getElementById('clearFilter');
    const attendanceRows = document.querySelectorAll('.attendance-row');
    const noResults = document.getElementById('noResults');
    
    if (!dateInput || !prevBtn || !nextBtn) return;
    
    const today = new Date().toISOString().split('T')[0];

    function updateNextBtn() {
        nextBtn.disabled = (dateInput.value >= today);
    }

    function submitWithDate() {
        const date = dateInput.value;
        const params = new URLSearchParams(window.location.search);
        params.set('date', date);
        window.location.search = params.toString();
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

    // Roll number filter functionality
    function filterByRoll() {
        const searchTerm = rollFilter.value.trim().toLowerCase();
        let hasMatches = false;
        
        attendanceRows.forEach(row => {
            const rollCell = row.querySelector('td:first-child');
            const rollNumber = rollCell.textContent.trim().toLowerCase();
            const isMatch = rollNumber.includes(searchTerm);
            
            row.classList.toggle('d-none', !isMatch);
            row.classList.toggle('highlight-row', isMatch && searchTerm !== '');
            
            if (isMatch) hasMatches = true;
        });
        
        noResults.classList.toggle('d-none', hasMatches || searchTerm === '');
    }
    
    rollFilter.addEventListener('input', filterByRoll);
    
    clearFilter.addEventListener('click', function() {
        rollFilter.value = '';
        filterByRoll();
        rollFilter.focus();
    });
    
    // Highlight row if URL contains roll number
    function checkInitialRollFilter() {
        const params = new URLSearchParams(window.location.search);
        const rollParam = params.get('roll');
        
        if (rollParam) {
            rollFilter.value = rollParam;
            filterByRoll();
            
            // Scroll to the first matching row
            const firstMatch = document.querySelector('.attendance-row.highlight-row');
            if (firstMatch) {
                firstMatch.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }
    }

    updateNextBtn();
    checkInitialRollFilter();
    
    // Responsive table enhancements
    function handleResponsiveTable() {
        // Additional responsive logic if needed
    }
    
    // Initial check
    handleResponsiveTable();
    
    // Window resize listener with debounce
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(handleResponsiveTable, 100);
    });
});
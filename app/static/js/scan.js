// scan.js

function showCountdownAndConfirm(data, field, course) {
    const studentInfo = document.getElementById('student-info');
    // Remove any existing countdown box
    const oldCountdown = document.getElementById('countdown');
    if (oldCountdown) oldCountdown.remove();

    // Add countdown box
    const countdownDiv = document.createElement('div');
    countdownDiv.id = 'countdown';
    countdownDiv.innerHTML = `
        <p class="mt-3 text-center text-danger fw-bold">
            Marking attendance in <span id="countdown-seconds">5</span> seconds...
        </p>
        <div class="d-flex justify-content-center gap-2">
            <button id="cancel-auto" class="btn btn-warning">Cancel</button>
            <button id="confirm-now" class="btn btn-success">Confirm Now</button>
        </div>
    `;
    studentInfo.appendChild(countdownDiv);

    // Use a local variable for seconds
    let secondsRemaining = 5;
    const countdownInterval = setInterval(() => {
        secondsRemaining--;
        document.getElementById('countdown-seconds').innerText = secondsRemaining;
        if (secondsRemaining <= 0) {
            clearInterval(countdownInterval);
            countdownDiv.remove();
            markAttendance(data, field, course);
        }
    }, 1000);

    // Cancel handler
    document.getElementById('cancel-auto').addEventListener('click', () => {
        clearInterval(countdownInterval);
        countdownDiv.innerHTML = `<p class="text-danger">Auto attendance canceled. Please use the manual button.</p>`;
    });

    // Confirm Now handler
    document.getElementById('confirm-now').addEventListener('click', () => {
        clearInterval(countdownInterval);
        countdownDiv.remove();
        markAttendance(data, field, course);
    });
}

function markAttendance(data, field, course) {
    fetch('/mark-attendance', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: data.user_id, field, course })
    })
    .then(res => res.json())
    .then(response => {
        if (response.status === 'already_marked' || response.status === 'closed') {
            document.getElementById('attendance-alert').innerHTML = `
                <div class="alert alert-warning alert-dismissible fade show mt-3" role="alert">
                        ${response.message}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                </div>
                `;
            setTimeout(() => {
                const alertDiv = document.querySelector('#attendance-alert .alert');
                if (alertDiv) alertDiv.remove();
            }, 5000);
            return;
        }
        window.location.href = `/attendance-dashboard/${field}/${course}`;
    });
}

// Make these functions globally accessible
window.showCountdownAndConfirm = showCountdownAndConfirm;
window.markAttendance = markAttendance;
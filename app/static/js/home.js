function initializePage() {
    initializeAnimations();
    initializeParallax();
    initializeNavigation();
    initializeTextAnimation();
    initializeCourseDropdown();
    restoreFormState();
}

// Add this new function
function restoreFormState() {
    const fieldSelect = document.getElementById("field");
    const courseSelect = document.getElementById("course");
    const scannerWrapper = document.getElementById("scanner-wrapper");
    
    if (fieldSelect && fieldSelect.value && courseSelect && courseSelect.value) {
        scannerWrapper.style.display = 'flex';
        startCamera();
    }
}

// document.addEventListener('DOMContentLoaded', function() {
//     initializeAnimations();
//     initializeParallax();
//     initializeNavigation();
//     initializeTextAnimation();
//     initializeCourseDropdown();
// });
document.addEventListener('DOMContentLoaded', initializePage);
document.addEventListener('pageshow', initializePage);

// Initialize all animations
function initializeAnimations() {
    // Fade in elements on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
            }
        });
    }, observerOptions);

    // Observe all sections
    document.querySelectorAll('section').forEach(section => {
        observer.observe(section);
    });

    // Observe cards and panels
    document.querySelectorAll('.card-3d, .glass-panel, .service-card').forEach(card => {
        observer.observe(card);
    });
}

// Parallax Scrolling Effect
function initializeParallax() {
    let ticking = false;

    function updateParallax() {
        const scrolled = window.pageYOffset;
        const parallaxElements = document.querySelectorAll('.parallax-section');

        parallaxElements.forEach((element, index) => {
            const speed = 0.5 + (index * 0.1);
            const yPos = -(scrolled * speed);
            element.style.transform = `translateY(${yPos}px)`;
        });

        // Update background elements
        const birds = document.querySelectorAll('.bird');
        birds.forEach((bird, index) => {
            const speed = 0.3 + (index * 0.1);
            const yPos = scrolled * speed;
            bird.style.transform = `translateY(${yPos}px)`;
        });

        const particles = document.querySelectorAll('.particle');
        particles.forEach((particle, index) => {
            const speed = 0.2 + (index * 0.05);
            const yPos = scrolled * speed;
            particle.style.transform = `translateY(${yPos}px)`;
        });

        ticking = false;
    }

    function requestTick() {
        if (!ticking) {
            requestAnimationFrame(updateParallax);
            ticking = true;
        }
    }

    window.addEventListener('scroll', requestTick);
}

// Navigation functionality
function initializeNavigation() {
    const nav = document.querySelector('nav');
    const navItems = document.querySelectorAll('.nav-item');

    // Navbar scroll effect
    window.addEventListener('scroll', () => {
        if (window.scrollY > 100) {
            nav.style.background = 'rgba(15, 23, 42, 0.95)';
            nav.style.backdropFilter = 'blur(20px)';
        } else {
            nav.style.background = 'rgba(15, 23, 42, 0.8)';
            nav.style.backdropFilter = 'blur(10px)';
        }
    });

    // Smooth scroll for navigation links
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = item.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            if (targetSection) {
                targetSection.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Active navigation item
    window.addEventListener('scroll', () => {
        let current = '';
        const sections = document.querySelectorAll('section');
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (scrollY >= (sectionTop - 200)) {
                current = section.getAttribute('id');
            }
        });

        navItems.forEach(item => {
            item.classList.remove('active');
            if (item.getAttribute('href') === `#${current}`) {
                item.classList.add('active');
            }
        });
    });
}

// Text Animation Effect - Typewriter
function initializeTextAnimation() {
    const textContainer = document.querySelector('.text-animation-text');
    const texts = [
        'Facial Recognition ',
        'Real-time Face Scanning',
        'Verified Registrations',
        'Digital Attendance ',
        'Automated Notifications'
    ];
    
    let currentIndex = 0;
    let currentText = '';
    let letterIndex = 0;
    let isDeleting = false;
    let isPaused = false;

    function typeWriter() {
        const fullText = texts[currentIndex];
        
        if (isPaused) {
            setTimeout(typeWriter, 1000);
            isPaused = false;
            return;
        }
        
        if (isDeleting) {
            currentText = fullText.substring(0, letterIndex - 1);
            letterIndex--;
        } else {
            currentText = fullText.substring(0, letterIndex + 1);
            letterIndex++;
        }
        
        textContainer.textContent = currentText;
        
        let typeSpeed = isDeleting ? 50 : 100;
        
        if (!isDeleting && currentText === fullText) {
            typeSpeed = 2000; // Pause at end
            isDeleting = true;
        } else if (isDeleting && currentText === '') {
            isDeleting = false;
            letterIndex = 0;
            currentIndex = (currentIndex + 1) % texts.length;
            typeSpeed = 500; // Pause before starting new text
        }
        
        setTimeout(typeWriter, typeSpeed);
    }
    
    // Start the typewriter effect
    typeWriter();
}
// Service Card Interactions
document.addEventListener('DOMContentLoaded', () => {
    const serviceCards = document.querySelectorAll('.service-card');
    
    serviceCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            const icon = card.querySelector('.service-icon');
            icon.style.animation = 'none';
            setTimeout(() => {
                icon.style.animation = '';
            }, 10);
        });
    });
});

// Course Dropdown Functionality
function initializeCourseDropdown() {
    const fieldCourseMap = {
        BTech: ['CSE', 'Civil', 'Mechanical'],
        BCA: ['AI-ML', 'Computer Applications','Cyber Security'],
        Nursing: ['General Nursing', 'Pediatrics', 'Psychiatric']
    };

    const fieldSelect = document.getElementById("field");
    const courseSelect = document.getElementById("course");

    // Debugging logs
    console.log("Field select element:", fieldSelect);
    console.log("Course select element:", courseSelect);

    // Populate courses when field changes
    fieldSelect.addEventListener("change", function() {
        console.log("Field changed to:", this.value);
        courseSelect.innerHTML = '<option value="" selected disabled class="placeholder-option">Select Course</option>';
        
        if (this.value && fieldCourseMap[this.value]) {
            fieldCourseMap[this.value].forEach(course => {
                const opt = document.createElement("option");
                opt.value = course;
                opt.textContent = course;
                courseSelect.appendChild(opt);
            });
        }
        
        // Enable the course dropdown
        courseSelect.disabled = false;
        console.log("Course options:", courseSelect.options);
    });

    // Initialize course dropdown state
    courseSelect.disabled = !fieldSelect.value;

    // Refresh icon logic
    document.getElementById('refreshField').addEventListener('click', function() {
        fieldSelect.selectedIndex = 0;
        courseSelect.innerHTML = '<option value="" selected disabled class="placeholder-option">Select Course</option>';
        courseSelect.disabled = true;
        document.getElementById('scanner-wrapper').style.display = 'none';
        
        const studentInfo = document.getElementById("student-info");
        const studentHeading = document.getElementById("student-info-heading");
        if (studentInfo) studentInfo.style.display = 'none';
        if (studentHeading) studentHeading.style.display = 'none';
    });

    // Show scanner when both are selected
    courseSelect.addEventListener('change', function() {
        if (fieldSelect.value && this.value) {
            document.getElementById('scanner-wrapper').style.display = 'flex';
            startCamera();
        
    
            // Auto scan after delay
            let countdownEl = document.getElementById('scan-countdown');
            let countdownText = document.getElementById('countdown-text');
            const delaySelect = document.getElementById('scanDelay');
            
            function getSelectedDelay() {
                return parseInt(delaySelect.value) || 6;
            }
            
            let seconds = getSelectedDelay();
            countdownText.innerText = seconds;
            countdownEl.style.display = 'block';
            
            let countdownInterval = setInterval(() => {
                seconds--;
                countdownText.innerText = seconds;
                
                if (seconds <= 0) {
                    clearInterval(countdownInterval);
                    countdownEl.style.display = 'none';
                    countdownText.innerText = '';
                    captureAndSend();
                }
            }, 1000);
        }
    });
}

function startCamera() {
    const video = document.getElementById('video');
    
    navigator.mediaDevices.getUserMedia({ video: { facingMode: "user",width: { ideal: 640 }, height: { ideal: 480 } } })
        .then(stream => {
            video.srcObject = stream;
        })
        .catch(err => {
            console.error("Camera access denied:", err);
        });
}

function captureAndSend() {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const image = canvas.toDataURL('image/jpeg');
    const field = document.getElementById('field').value;
    const course = document.getElementById('course').value;
    
    fetch('/scan-face', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ image, field, course })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'match') {
            document.getElementById('student-info').style.display = 'block';
            document.getElementById('student-info-heading').style.display = 'block';
            document.getElementById('student-name').innerText = data.username;
            document.getElementById('student-roll').innerText = data.roll;
            document.getElementById('student-field').innerText = data.field;
            document.getElementById('student-course').innerText = data.course;
            
            showCountdownAndConfirm(data, field, course);
        } else {
            alert("Face not recognized.");
        }
    })
    .catch(error => {
        console.error("Error:", error);
    });
}

function showCountdownAndConfirm(data, field, course) {
    const countdownEl = document.getElementById('scan-countdown');
    const countdownNumber = document.getElementById('countdown-number');
    const countdownText = document.getElementById('countdown-text');
    const confirmButton = document.getElementById('mark-attendance');
    const delaySelect = document.getElementById('scanDelay');
    
    // Use user-selected or fallback default delay
    function getDefaultDelay() {
        const isMobile = /Mobi|Android/i.test(navigator.userAgent);
        return isMobile ? 7 : 5;
    }
    
    if (!delaySelect.value) {
        delaySelect.value = getDefaultDelay();
    }
    
    let seconds = parseInt(delaySelect.value) || 6;
    countdownEl.style.display = 'block';
    
    // Countdown logic
    const interval = setInterval(() => {
        seconds--;
        countdownNumber.innerText = seconds;
        countdownText.innerText = seconds;
        
        if (seconds <= 0) {
            clearInterval(interval);
            countdownEl.style.display = 'none';
            confirmAttendance(); // Automatically confirm if user does not act
        }
    }, 1000);
    
    // If user clicks confirm manually
    confirmButton.onclick = () => {
        clearInterval(interval);
        countdownEl.style.display = 'none';
        confirmAttendance();
    };
    
    // Submission logic
    function confirmAttendance() {
        fetch('/mark-attendance', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ user_id: data.user_id, field, course })
        }).then(() => {
            window.location.href = `/attendance-dashboard/${field}/${course}`;
        });
    }
}
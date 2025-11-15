
document.getElementById('togglePassword').addEventListener('click', function() {
      const passwordInput = document.getElementById('password');
      const confirmPasswordInput = document.getElementById('confirmPassword');
      const icon = this.querySelector('i');
      
      if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        confirmPasswordInput.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
      } else {
        passwordInput.type = 'password';
        confirmPasswordInput.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
      }
    });
    
    // Password strength checker
    document.getElementById('password').addEventListener('input', function() {
      const password = this.value;
      const strengthBar = document.getElementById('passwordStrengthBar');
      const requirements = {
        length: password.length >= 8,
        uppercase: /[A-Z]/.test(password),
        number: /[0-9]/.test(password),
        special: /[^A-Za-z0-9]/.test(password)
      };
      
      // Update requirement indicators
      updateRequirement('lengthReq', requirements.length);
      updateRequirement('uppercaseReq', requirements.uppercase);
      updateRequirement('numberReq', requirements.number);
      updateRequirement('specialReq', requirements.special);
      
      // Calculate strength score (0-4)
      const strengthScore = Object.values(requirements).filter(Boolean).length;
      
      // Update strength bar
      let strengthPercent = strengthScore * 25;
      let strengthColor = '#ef4444'; // red
      
      if (strengthScore >= 4) {
        strengthColor = '#10b981'; // green
      } else if (strengthScore >= 2) {
        strengthColor = '#f59e0b'; // yellow
      }
      
      strengthBar.style.width = strengthPercent + '%';
      strengthBar.style.backgroundColor = strengthColor;
    });
    
    function updateRequirement(elementId, isValid) {
      const element = document.getElementById(elementId);
      if (isValid) {
        element.classList.add('valid');
        element.classList.remove('invalid');
        element.querySelector('i').className = 'fas fa-check-circle';
      } else {
        element.classList.add('invalid');
        element.classList.remove('valid');
        element.querySelector('i').className = 'fas fa-circle';
      }
    }
    
    // Confirm password validation
    document.getElementById('confirmPassword').addEventListener('input', function() {
      const password = document.getElementById('password').value;
      const confirmPassword = this.value;
      const feedback = document.getElementById('confirmPasswordFeedback');
      
      if (confirmPassword && password !== confirmPassword) {
        this.classList.add('is-invalid');
        feedback.style.display = 'block';
      } else {
        this.classList.remove('is-invalid');
        feedback.style.display = 'none';
      }
    });
    
    // Username validation
    document.getElementById('username').addEventListener('input', function() {
      const username = this.value;
      const feedback = document.getElementById('usernameFeedback');
      
      if (username.length > 0 && (username.length < 3 || username.length > 20)) {
        this.classList.add('is-invalid');
        feedback.style.display = 'block';
      } else {
        this.classList.remove('is-invalid');
        feedback.style.display = 'none';
      }
    });
    
    // Email validation
    document.getElementById('email').addEventListener('input', function() {
      const email = this.value;
      const feedback = document.getElementById('emailFeedback');
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      
      if (email && !emailRegex.test(email)) {
        this.classList.add('is-invalid');
        feedback.style.display = 'block';
      } else {
        this.classList.remove('is-invalid');
        feedback.style.display = 'none';
      }
    });

    
    // Enhanced register function with loading state
    async function register() {
      const username = document.getElementById('username').value.trim();
      const email = document.getElementById('email').value.trim();
      const password = document.getElementById('password').value;
      const confirmPassword = document.getElementById('confirmPassword').value;
      const termsChecked = document.getElementById('termsCheck').checked;
      const registerBtn = document.querySelector('.btn-register');
      const originalBtnText = registerBtn.innerHTML;
      
      // Validate form
      let isValid = true;
      
      if (!username || username.length < 3 || username.length > 20) {
        document.getElementById('username').classList.add('is-invalid');
        isValid = false;
      }
      
      if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        document.getElementById('email').classList.add('is-invalid');
        isValid = false;
      }
      
      if (!password || password.length < 8) {
        document.getElementById('password').classList.add('is-invalid');
        isValid = false;
      }
      
      if (password !== confirmPassword) {
        document.getElementById('confirmPassword').classList.add('is-invalid');
        isValid = false;
      }
      
      if (!termsChecked) {
        document.getElementById('termsCheck').classList.add('is-invalid');
        isValid = false;
      }
      
      if (!isValid) {
        showAlert('Please fix the errors in the form.', 'danger');
        return;
      }
      
      // Show loading state
      registerBtn.disabled = true;
      registerBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Creating account...';
      
      try {
        const response = await fetch("/auth/register", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ username, email, password })
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
          showAlert('Account created successfully! Redirecting to login...', 'success');
          setTimeout(() => {
            window.location.href = "index.html";
          }, 2000);
        } else {
          showAlert(data.message || 'Registration failed. Please try again.', 'danger');
        }
      } catch (error) {
        showAlert('Network error. Please try again later.', 'danger');
      } finally {
        // Reset button state
        registerBtn.disabled = false;
        registerBtn.innerHTML = originalBtnText;
      }
    }
    
    // Show alert message
    function showAlert(message, type) {
      // Remove any existing alerts
      const existingAlert = document.querySelector('.alert');
      if (existingAlert) {
        existingAlert.remove();
      }
      
      const alertDiv = document.createElement('div');
      alertDiv.className = `alert alert-${type} alert-dismissible fade show mt-3`;
      alertDiv.setAttribute('role', 'alert');
      alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
      `;
      
      const form = document.querySelector('form');
      form.insertBefore(alertDiv, form.firstChild);
      
      // Auto-dismiss after 5 seconds
      setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alertDiv);
        bsAlert.close();
      }, 5000);
    }


    
    
    // hidden cam function
// function showScannerDiv() {
//     document.getElementById('scanner-div').style.display = 'block';
//     startCamera();
// }
  
  

// function startCamera() {
//   navigator.mediaDevices.getUserMedia({ video: true })
//     .then(stream => {
//       const video = document.getElementById('video');
//       video.srcObject = stream;
//     })
//     .catch(err => {
//       console.error("Error accessing webcam: ", err);
//     });
// }

// function capture() {
//   const video = document.getElementById('video');
//   const canvas = document.getElementById('canvas');
//   canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
//   const dataURL = canvas.toDataURL('image/jpeg'); // Base64 image
//   document.getElementById('image').value = dataURL;
// }
function showScannerDiv() {
  document.getElementById('scanner-div').style.display = 'block';
  startCamera();
}

function startCamera() {
  // navigator.mediaDevices.getUserMedia({ video: { facingMode: "user", width: { ideal: 480 }, height: { ideal: 360 } } })
  // navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } })
  navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
      const video = document.getElementById('video');
      video.srcObject = stream;
      video.play();
    })
    .catch(err => {
      console.error("Error accessing webcam: ", err);
    });
}
function capture() {
  const video = document.getElementById('video');
  const canvas = document.getElementById('canvas');
  const context = canvas.getContext('2d');

  if (!video || !canvas || !context) {
    console.error("Video or canvas not found!");
    return;
  }

  context.drawImage(video, 0, 0, canvas.width, canvas.height);
  const dataURL = canvas.toDataURL('image/jpeg');

  console.log("Base64 length:", dataURL.length); // Debug

  if (!dataURL.startsWith("data:image")) {
    alert("Failed to capture image. Please try again.");
    return;
  }

  document.getElementById('image').value = dataURL;
}

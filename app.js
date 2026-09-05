const API_BASE_URL = "http://127.0.0.1:8000";

let currentStream = null;
let currentEmployee = null;
let tempRegistrationData = null;

// Switch Auth Tabs
function switchAuthTab(tab) {
  document.getElementById('tab-login-btn').classList.toggle('active', tab === 'login');
  document.getElementById('tab-register-btn').classList.toggle('active', tab === 'register');
  document.getElementById('login-section').classList.toggle('active', tab === 'login');
  document.getElementById('register-section').classList.toggle('active', tab === 'register');

  if (tab === 'login') {
    startCamera('login-video');
  } else {
    stopCamera();
  }
}

// Face Method Toggle for Login
function setFaceMethod(method) {
  document.getElementById('btn-camera-mode').classList.toggle('active', method === 'camera');
  document.getElementById('btn-upload-mode').classList.toggle('active', method === 'upload');
  document.getElementById('face-camera-box').classList.toggle('hidden', method !== 'camera');
  document.getElementById('face-upload-box').classList.toggle('hidden', method !== 'upload');

  if (method === 'camera') {
    startCamera('login-video');
  } else {
    stopCamera();
  }
}

// Camera Controls
async function startCamera(videoId) {
  stopCamera();
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    currentStream = stream;
    const videoElem = document.getElementById(videoId);
    if (videoElem) videoElem.srcObject = stream;
  } catch (err) {
    console.error("Camera error: ", err);
  }
}

function stopCamera() {
  if (currentStream) {
    currentStream.getTracks().forEach(track => track.stop());
    currentStream = null;
  }
}

// Standard Login
async function handleStandardLogin(e) {
  e.preventDefault();
  const identifier = document.getElementById('login-identifier').value;
  
  // Note: Backend endpoint for fetching employee details
  try {
    const res = await fetch(`${API_BASE_URL}/employees/${identifier}`);
    if (res.ok) {
      const data = await res.json();
      showDashboard(data);
    } else {
      alert("Employee not found");
    }
  } catch (err) {
    alert("Connection error with server");
  }
}

// Face Login (Camera Capture)
async function captureAndLogin() {
  const video = document.getElementById('login-video');
  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth || 640;
  canvas.height = video.videoHeight || 480;
  canvas.getContext('2d').drawImage(video, 0, 0);

  canvas.toBlob(async (blob) => {
    const formData = new FormData();
    formData.append('image', blob, 'capture.jpg');

    try {
      const res = await fetch(`${API_BASE_URL}/auth/login-face`, {
        method: 'POST',
        body: formData
      });
      const result = await res.json();
      if (result.success) {
        showDashboard(result.employee);
      } else {
        alert(result.message || "Face not recognized");
      }
    } catch (err) {
      alert("Login request failed");
    }
  }, 'image/jpeg');
}

// Face Login (File Upload)
async function uploadAndLogin() {
  const fileInput = document.getElementById('login-file-input');
  if (!fileInput.files[0]) return alert("Please select an image");

  const formData = new FormData();
  formData.append('image', fileInput.files[0]);

  try {
    const res = await fetch(`${API_BASE_URL}/auth/login-face`, {
      method: 'POST',
      body: formData
    });
    const result = await res.json();
    if (result.success) {
      showDashboard(result.employee);
    } else {
      alert(result.message || "Face not recognized");
    }
  } catch (err) {
    alert("Login failed");
  }
}

// Registration Steps
function proceedToFaceRegistration() {
  const name = document.getElementById('reg-name').value;
  const age = document.getElementById('reg-age').value;
  const email = document.getElementById('reg-email').value;
  const city = document.getElementById('reg-city').value;

  if (!name || !age || !email || !city) {
    return alert("Please fill all fields");
  }

  tempRegistrationData = { name, age, email, city };
  document.getElementById('reg-step-1').classList.add('hidden');
  document.getElementById('reg-step-2').classList.remove('hidden');
  startCamera('reg-video');
}

function backToStep1() {
  document.getElementById('reg-step-2').classList.add('hidden');
  document.getElementById('reg-step-1').classList.remove('hidden');
  stopCamera();
}

function setRegFaceMethod(method) {
  document.getElementById('btn-reg-camera').classList.toggle('active', method === 'camera');
  document.getElementById('btn-reg-upload').classList.toggle('active', method === 'upload');
  document.getElementById('reg-camera-box').classList.toggle('hidden', method !== 'camera');
  document.getElementById('reg-upload-box').classList.toggle('hidden', method !== 'upload');

  if (method === 'camera') {
    startCamera('reg-video');
  } else {
    stopCamera();
  }
}

// Submit Registration
async function submitRegistrationWithCamera() {
  const video = document.getElementById('reg-video');
  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth || 640;
  canvas.height = video.videoHeight || 480;
  canvas.getContext('2d').drawImage(video, 0, 0);

  canvas.toBlob((blob) => {
    executeRegistration(blob, 'capture.jpg');
  }, 'image/jpeg');
}

async function submitRegistrationWithFile() {
  const fileInput = document.getElementById('reg-file-input');
  if (!fileInput.files[0]) return alert("Please select an image");
  executeRegistration(fileInput.files[0], fileInput.files[0].name);
}

async function executeRegistration(imageBlob, fileName) {
  const formData = new FormData();
  formData.append('name', tempRegistrationData.name);
  formData.append('age', tempRegistrationData.age);
  formData.append('email', tempRegistrationData.email);
  formData.append('city', tempRegistrationData.city);
  formData.append('image', imageBlob, fileName);

  try {
    const res = await fetch(`${API_BASE_URL}/employees/register`, {
      method: 'POST',
      body: formData
    });
    const result = await res.json();
    if (result.success) {
      alert("Registration successful!");
      // Fetch employee profile & show dashboard
      const empRes = await fetch(`${API_BASE_URL}/employees/${result.employee_id}`);
      const empData = await empRes.json();
      showDashboard(empData);
    } else {
      alert(result.detail || "Registration failed");
    }
  } catch (err) {
    alert("Registration error");
  }
}

// Dashboard & Attendance
function showDashboard(emp) {
  stopCamera();
  currentEmployee = emp;
  
  document.getElementById('emp-name').innerText = emp.name;
  document.getElementById('emp-id-badge').innerText = `ID: #${emp.employee_id}`;
  document.getElementById('emp-email').innerText = emp.email;
  document.getElementById('emp-city').innerText = emp.city;
  document.getElementById('emp-age').innerText = emp.age;
  document.getElementById('emp-created').innerText = new Date(emp.created_at).toLocaleDateString();

  document.getElementById('auth-screen').classList.remove('active');
  document.getElementById('dashboard-screen').classList.add('active');
}

async function handleCheckIn() {
  if (!currentEmployee) return;
  try {
    const res = await fetch(`${API_BASE_URL}/attendance/check-in/${currentEmployee.employee_id}`, {
      method: 'POST'
    });
    const data = await res.json();
    if (res.ok) {
      alert("Checked in successfully!");
    } else {
      alert(data.detail || "Check-in failed");
    }
  } catch (err) {
    alert("Check-in request error");
  }
}

async function handleCheckOut() {
  if (!currentEmployee) return;
  try {
    const res = await fetch(`${API_BASE_URL}/attendance/check-out/${currentEmployee.employee_id}`, {
      method: 'POST'
    });
    const data = await res.json();
    if (res.ok) {
      alert("Checked out successfully!");
      // Logout and return to main screen
      location.reload();
    } else {
      alert(data.detail || "Check-out failed");
    }
  } catch (err) {
    alert("Check-out request error");
  }
}

// Initial Call
startCamera('login-video');
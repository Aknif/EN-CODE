// auth.js
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const loginErrorMessageDiv = document.getElementById('login-error-message');
    const registerErrorMessageDiv = document.getElementById('register-error-message');
    const registerSuccessMessageDiv = document.getElementById('register-success-message');

    // --- LOGIN FORM LOGIC ---
    if (loginForm) {
        loginForm.addEventListener('submit', async function(event) {
            event.preventDefault();
            if (loginErrorMessageDiv) loginErrorMessageDiv.classList.add('hidden');

            const usernameInput = document.getElementById('login-username');
            const passwordInput = document.getElementById('login-password');
            const rememberMeCheckbox = document.getElementById('remember-me');

            if (!usernameInput || !passwordInput) {
                console.error("Login form inputs not found");
                if(loginErrorMessageDiv) {
                    loginErrorMessageDiv.textContent = "เกิดข้อผิดพลาดในหน้าเว็บ (ไม่พบช่องข้อมูล)";
                    loginErrorMessageDiv.classList.remove('hidden');
                }
                return;
            }

            const username = usernameInput.value.trim();
            const password = passwordInput.value;
            const rememberMe = rememberMeCheckbox ? rememberMeCheckbox.checked : false;

            if (username === "" || password === "") {
                 if(loginErrorMessageDiv) {
                    loginErrorMessageDiv.textContent = 'ชื่อผู้ใช้และรหัสผ่านห้ามว่าง';
                    loginErrorMessageDiv.classList.remove('hidden');
                }
                return;
            }

            try {
                const response = await fetch('http://127.0.0.1:5500/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        username: username,
                        password: password,
                        remember_me: rememberMe
                    })
                });

                const contentType = response.headers.get("content-type");
                let data;
                if (contentType && contentType.includes("application/json")) {
                    data = await response.json();
                } else {
                    const errorText = await response.text();
                    console.error("Login response not JSON:", errorText);
                    throw new Error(`Server responded with non-JSON content (status: ${response.status}). Check backend /login endpoint.`);
                }


                if (response.ok) {
                    window.location.href = 'hub.html';
                } else {
                    if(loginErrorMessageDiv) {
                        loginErrorMessageDiv.textContent = data.error || 'เกิดข้อผิดพลาดในการเข้าสู่ระบบ';
                        loginErrorMessageDiv.classList.remove('hidden');
                    } else {
                        alert(`Error: ${data.error || 'เกิดข้อผิดพลาดในการเข้าสู่ระบบ'}`);
                    }
                }
            } catch (error) {
                console.error("Login fetch error:", error);
                if(loginErrorMessageDiv) {
                    loginErrorMessageDiv.textContent = error.message.includes("non-JSON") ? error.message : 'ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้ หรือการตอบกลับไม่ถูกต้อง';
                    loginErrorMessageDiv.classList.remove('hidden');
                } else {
                    alert(error.message.includes("non-JSON") ? error.message : 'ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้ หรือการตอบกลับไม่ถูกต้อง');
                }
            }
        });
    }

    // --- REGISTER FORM LOGIC ---
    if (registerForm) {
        registerForm.addEventListener('submit', async function(event) {
            event.preventDefault();

            if(registerErrorMessageDiv) registerErrorMessageDiv.classList.add('hidden');
            if(registerSuccessMessageDiv) registerSuccessMessageDiv.classList.add('hidden');

            const usernameInput = document.getElementById('register-username');
            const emailInput = document.getElementById('register-email');
            const passwordInput = document.getElementById('register-password');
            const confirmPasswordInput = document.getElementById('confirm-password');

            if (!usernameInput || !passwordInput || !confirmPasswordInput || !emailInput) {
                 console.error("Register form inputs not found");
                if(registerErrorMessageDiv) {
                    registerErrorMessageDiv.textContent = "เกิดข้อผิดพลาดในหน้าเว็บ (ไม่พบช่องข้อมูล)";
                    registerErrorMessageDiv.classList.remove('hidden');
                }
                return;
            }

            const username = usernameInput.value.trim();
            const email = emailInput.value.trim();
            const password = passwordInput.value;
            const confirmPassword = confirmPasswordInput.value;

            if (username === "" || password === "" || email === "") {
                 if(registerErrorMessageDiv) {
                    registerErrorMessageDiv.textContent = 'ชื่อผู้ใช้, อีเมล และรหัสผ่านห้ามว่าง';
                    registerErrorMessageDiv.classList.remove('hidden');
                }
                return;
            }

            if (password !== confirmPassword) {
                if(registerErrorMessageDiv) {
                    registerErrorMessageDiv.textContent = 'รหัสผ่านและการยืนยันรหัสผ่านไม่ตรงกัน';
                    registerErrorMessageDiv.classList.remove('hidden');
                }
                return;
            }

            try {
                const response = await fetch('http://127.0.0.1:5500/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, email, password })
                });

                const contentType = response.headers.get("content-type");
                let data;
                if (contentType && contentType.includes("application/json")) {
                    data = await response.json();
                } else {
                    const errorText = await response.text();
                    console.error("Register response not JSON:", errorText);
                    throw new Error(`Server responded with non-JSON content (status: ${response.status}). Check backend /register endpoint.`);
                }

                if (response.ok) {
                    if(registerSuccessMessageDiv) {
                        registerSuccessMessageDiv.textContent = data.message + " คุณสามารถเข้าสู่ระบบได้เลย";
                        registerSuccessMessageDiv.classList.remove('hidden');
                    } else {
                        alert(data.message + " คุณสามารถเข้าสู่ระบบได้เลย");
                    }
                    registerForm.reset();
                } else {
                    if(registerErrorMessageDiv) {
                        registerErrorMessageDiv.textContent = data.error || 'เกิดข้อผิดพลาดในการลงทะเบียน';
                        registerErrorMessageDiv.classList.remove('hidden');
                    } else {
                        alert(`Error: ${data.error || 'เกิดข้อผิดพลาดในการลงทะเบียน'}`);
                    }
                }
            } catch (error) {
                console.error("Register fetch error:", error);
                 if(registerErrorMessageDiv) {
                    registerErrorMessageDiv.textContent = error.message.includes("non-JSON") ? error.message : 'ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้ หรือการตอบกลับไม่ถูกต้อง';
                    registerErrorMessageDiv.classList.remove('hidden');
                } else {
                    alert(error.message.includes("non-JSON") ? error.message : 'ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้ หรือการตอบกลับไม่ถูกต้อง');
                }
            }
        });
    }
});
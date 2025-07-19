// main.js
document.addEventListener('DOMContentLoaded', function() {
    const navbar = document.getElementById('main-navbar');
    let navItemsThatRequireAuth = null;

    async function updateNavbarBasedOnAuth() {
        if (!navbar) {
            return;
        }

        navItemsThatRequireAuth = navbar.querySelectorAll('.nav-item-auth');
        const staticNavItems = navbar.querySelectorAll('.nav-item-static');

        const dynamicElements = navbar.querySelectorAll('.auth-link-dynamic');
        dynamicElements.forEach(el => el.remove());

        try {
            // ***** แก้ไขบรรทัดนี้ *****
            const response = await fetch('/check_auth_status', {
                method: 'GET',
                credentials: 'include'
            });

            const contentType = response.headers.get("content-type");
            if (!contentType || !contentType.includes("application/json")) {
                const errorText = await response.text();
                console.error('Error checking login status: Server did not return JSON. Response:', errorText);
                throw new Error(`Server responded with non-JSON content (status: ${response.status}). Check backend /check_auth_status endpoint.`);
            }

            const data = await response.json();

            if (data.logged_in && data.user) {
                staticNavItems.forEach(item => item.style.display = '');
                navItemsThatRequireAuth.forEach(item => item.style.display = '');

                const welcomeContainer = document.createElement('div');
                welcomeContainer.className = 'auth-link-dynamic flex items-center space-x-3 ml-auto';

                const avatarLink = document.createElement('a');
                avatarLink.href = 'user_settings.html';
                avatarLink.className = 'relative flex-shrink-0';
                avatarLink.title = "ตั้งค่าบัญชี";

                const avatarDiv = document.createElement('div');
                avatarDiv.className = 'w-10 h-10 rounded-full bg-blue-400 text-white flex items-center justify-center text-lg font-bold border-2 border-white shadow-sm';
                avatarDiv.textContent = data.user.username ? data.user.username.charAt(0).toUpperCase() : 'U';
                avatarLink.appendChild(avatarDiv);

                const notificationCount = data.user.notifications || 0;
                if (notificationCount > 0) {
                    const badge = document.createElement('span');
                    badge.className = 'absolute -top-1 -right-1 bg-yellow-400 text-gray-800 text-xs font-bold rounded-full h-5 w-5 flex items-center justify-center border-2 border-white';
                    badge.textContent = notificationCount;
                    avatarLink.appendChild(badge);
                }
                welcomeContainer.appendChild(avatarLink);

                const usernameSpan = document.createElement('span');
                usernameSpan.className = 'text-blue-100 font-medium hidden md:inline';
                usernameSpan.textContent = `${data.user.username} (นักเรียน)`;
                welcomeContainer.appendChild(usernameSpan);

                navbar.appendChild(welcomeContainer);

                const logoutButton = document.createElement('a');
                logoutButton.href = '#';
                logoutButton.id = 'logout-button';
                logoutButton.textContent = 'ออกจากระบบ';
                logoutButton.className = 'auth-link-dynamic hover:text-red-300 transition cursor-pointer bg-red-500 hover:bg-red-600 px-3 py-1.5 rounded-md text-sm text-white ml-3';
                logoutButton.addEventListener('click', handleLogout);
                navbar.appendChild(logoutButton);

            } else {
                staticNavItems.forEach(item => {
                    if (!item.classList.contains('nav-item-auth')) {
                        item.style.display = '';
                    } else {
                        item.style.display = 'none';
                    }
                });
                if (navItemsThatRequireAuth) navItemsThatRequireAuth.forEach(item => item.style.display = 'none');

                const authButtonsContainer = document.createElement('div');
                authButtonsContainer.className = 'auth-link-dynamic flex items-center space-x-4 ml-auto';
                const loginLink = document.createElement('a');
                loginLink.href = 'login.html';
                loginLink.textContent = 'เข้าสู่ระบบ';
                loginLink.className = 'hover:text-blue-200 transition';
                if (window.location.pathname.includes('login.html')) {
                    loginLink.classList.add('text-white', 'font-semibold', 'border-b-2', 'border-blue-300');
                }
                authButtonsContainer.appendChild(loginLink);
                const registerLink = document.createElement('a');
                registerLink.href = 'register.html';
                registerLink.textContent = 'ลงทะเบียน';
                registerLink.className = 'hover:text-blue-200 transition';
                if (window.location.pathname.includes('register.html')) {
                    registerLink.classList.add('text-white', 'font-semibold', 'border-b-2', 'border-blue-300');
                }
                authButtonsContainer.appendChild(registerLink);
                navbar.appendChild(authButtonsContainer);
            }
        } catch (error) {
            console.error('Error in updateNavbarBasedOnAuth:', error.message);
            // Fallback UI
            if (navbar) {
                const existingAuthLinks = navbar.querySelectorAll('.auth-link-dynamic');
                existingAuthLinks.forEach(link => link.remove());

                const authButtonsContainerFallback = document.createElement('div');
                authButtonsContainerFallback.className = 'auth-link-dynamic flex items-center space-x-4 ml-auto';
                const loginLink = document.createElement('a');
                //loginLink.href = 'login.html'; loginLink.textContent = 'เข้าสู่ระบบ';
                loginLink.className = 'hover:text-blue-200 transition';
                authButtonsContainerFallback.appendChild(loginLink);
                const registerLink = document.createElement('a');
                //registerLink.href = 'register.html'; registerLink.textContent = 'ลงทะเบียน';
                registerLink.className = 'hover:text-blue-200 transition';
                authButtonsContainerFallback.appendChild(registerLink);
                navbar.appendChild(authButtonsContainerFallback);
            }
            if(navItemsThatRequireAuth) navItemsThatRequireAuth.forEach(item => item.style.display = 'none');
        }
    }

    async function handleLogout(event) {
        event.preventDefault();
        try {
            // ***** แก้ไขบรรทัดนี้ *****
            const response = await fetch('/logout', {
                method: 'POST',
                credentials: 'include'
            });

            const contentType = response.headers.get("content-type");
            let data;
            if (contentType && contentType.includes("application/json")) {
                data = await response.json();
            } else {
                const errorText = await response.text();
                console.error("Logout response not JSON:", errorText);
                throw new Error(`Server responded with non-JSON content (status: ${response.status}). Check backend /logout endpoint.`);
            }

            if (response.ok) {
                await updateNavbarBasedOnAuth();
                const currentPath = window.location.pathname;
                if (!['/', '/index.html', '/login.html', '/register.html'].some(p => currentPath.endsWith(p))) {
                    window.location.href = 'index.html';
                } else if (currentPath.endsWith('login.html') || currentPath.endsWith('register.html')) {
                    // Do nothing
                } else {
                    window.location.reload();
                }
            } else {
                alert(`Logout failed: ${data.error || response.statusText || 'Unknown error'}`);
            }
        } catch (error) {
            console.error('Logout error:', error);
            alert(error.message.includes("non-JSON") ? error.message : 'Logout failed due to a network or server error.');
        }
    }

    updateNavbarBasedOnAuth();
});
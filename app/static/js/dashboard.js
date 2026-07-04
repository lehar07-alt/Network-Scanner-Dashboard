// Sidebar toggle for mobile
const sidebarToggle = document.getElementById('sidebarToggle');
const sidebar = document.getElementById('sidebar');
if (sidebarToggle) {
    sidebarToggle.addEventListener('click', () => {
        sidebar.classList.toggle('show');
    });
}

// Dark mode toggle with persistence across page loads
const darkModeToggle = document.getElementById('darkModeToggle');
const body = document.body;

// On page load, restore saved preference
if (localStorage.getItem('theme') === 'dark') {
    body.classList.add('dark-mode');
}

if (darkModeToggle) {
    darkModeToggle.addEventListener('click', async () => {
        body.classList.toggle('dark-mode');
        const icon = darkModeToggle.querySelector('i');
        const isDark = body.classList.contains('dark-mode');

        if (isDark) {
            icon.classList.replace('fa-moon', 'fa-sun');
            localStorage.setItem('theme', 'dark');
        } else {
            icon.classList.replace('fa-sun', 'fa-moon');
            localStorage.setItem('theme', 'light');
        }

        try {
            const formData = new FormData();
            formData.append('theme', isDark ? 'dark' : 'light');
            const notifCheckbox = document.getElementById('emailNotif');
            if (notifCheckbox && notifCheckbox.checked) {
                formData.append('email_notifications', 'on');
            }
            await fetch("/settings/update-preferences", { method: 'POST', body: formData });
        } catch (err) {
            console.error('Failed to save theme preference:', err);
        }
    });
}

// Make any row with class "clickable-row" navigate to its data-href on click
document.addEventListener('click', (event) => {
    const row = event.target.closest('.clickable-row');
    if (row && row.dataset.href) {
        window.location.href = row.dataset.href;
    }
});
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
    darkModeToggle.addEventListener('click', () => {
        body.classList.toggle('dark-mode');
        const icon = darkModeToggle.querySelector('i');
        if (body.classList.contains('dark-mode')) {
            icon.classList.replace('fa-moon', 'fa-sun');
            localStorage.setItem('theme', 'dark');
        } else {
            icon.classList.replace('fa-sun', 'fa-moon');
            localStorage.setItem('theme', 'light');
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
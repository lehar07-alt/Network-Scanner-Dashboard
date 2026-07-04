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

// --- Global search with debounce ---
const searchInput = document.getElementById('globalSearchInput');
const searchDropdown = document.getElementById('searchDropdown');
let searchDebounceTimer = null;

if (searchInput) {
    searchInput.addEventListener('input', () => {
        const query = searchInput.value.trim();

        // Cancel any pending search — user is still typing
        clearTimeout(searchDebounceTimer);

        if (query.length < 2) {
            searchDropdown.classList.add('d-none');
            return;
        }

        // Wait 300ms after the user stops typing before actually searching
        searchDebounceTimer = setTimeout(async () => {
            try {
                const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
                const data = await response.json();
                renderSearchDropdown(data.results);
            } catch (err) {
                console.error('Search failed:', err);
            }
        }, 300);
    });

    // Hide dropdown when clicking elsewhere on the page
    document.addEventListener('click', (event) => {
        if (!event.target.closest('#searchForm')) {
            searchDropdown.classList.add('d-none');
        }
    });
}

function renderSearchDropdown(results) {
    const query = searchInput.value.trim();

    function highlight(text) {
        if (!text) return text;
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<strong>$1</strong>');
    }

    if (results.length === 0) {
        searchDropdown.innerHTML = '<div class="p-3 text-secondary small">No matches found</div>';
    } else {
        searchDropdown.innerHTML = results.map(device => `
            <a href="/devices/${device.id}" class="d-block p-2 text-decoration-none text-body border-bottom" style="border-color: var(--border-color) !important;">
                <div class="fw-semibold small">${highlight(device.ip_address)}</div>
                <div class="text-secondary" style="font-size:0.78rem;">${highlight(device.hostname)} · ${highlight(device.vendor)}</div>
            </a>
        `).join('');
    }
    searchDropdown.classList.remove('d-none');
}
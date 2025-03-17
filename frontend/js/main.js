// Theme Toggle Functionality
document.addEventListener('DOMContentLoaded', function() {
    const themeToggleBtn = document.getElementById('theme-toggle');
    const themeToggleDarkIcon = document.getElementById('theme-toggle-dark-icon');
    const themeToggleLightIcon = document.getElementById('theme-toggle-light-icon');

    // Change the icons inside the button based on previous settings
    if (localStorage.getItem('theme') === 'dark' || 
        (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        themeToggleLightIcon.classList.remove('hidden');
    } else {
        themeToggleDarkIcon.classList.remove('hidden');
    }

    // Toggle the theme
    themeToggleBtn.addEventListener('click', function() {
        // Toggle icons
        themeToggleDarkIcon.classList.toggle('hidden');
        themeToggleLightIcon.classList.toggle('hidden');

        // If is dark mode
        if (document.documentElement.classList.contains('dark')) {
            document.documentElement.classList.remove('dark');
            localStorage.setItem('theme', 'light');
        } else {
            document.documentElement.classList.add('dark');
            localStorage.setItem('theme', 'dark');
        }
    });
});

// Mobile Menu Functionality
document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');

    mobileMenuButton.addEventListener('click', function() {
        // Toggle the 'hidden' class
        mobileMenu.classList.toggle('hidden');

        // Toggle the menu button appearance
        const isOpen = !mobileMenu.classList.contains('hidden');
        mobileMenuButton.setAttribute('aria-expanded', isOpen);
    });

    // Close mobile menu when clicking outside
    document.addEventListener('click', function(event) {
        if (!mobileMenu.contains(event.target) && !mobileMenuButton.contains(event.target)) {
            mobileMenu.classList.add('hidden');
            mobileMenuButton.setAttribute('aria-expanded', 'false');
        }
    });
});

// Form Validation
function validateForm(formElement) {
    const inputs = formElement.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;

    inputs.forEach(input => {
        if (!input.value.trim()) {
            isValid = false;
            input.classList.add('border-red-500');
            
            // Add error message if it doesn't exist
            if (!input.nextElementSibling?.classList.contains('error-message')) {
                const errorMessage = document.createElement('p');
                errorMessage.className = 'text-red-500 text-sm mt-1 error-message';
                errorMessage.textContent = 'This field is required';
                input.parentNode.insertBefore(errorMessage, input.nextSibling);
            }
        } else {
            input.classList.remove('border-red-500');
            const errorMessage = input.nextElementSibling;
            if (errorMessage?.classList.contains('error-message')) {
                errorMessage.remove();
            }
        }
    });

    return isValid;
}

// File Upload Preview
function handleFileUpload(input, previewElement) {
    const file = input.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            if (file.type.startsWith('image/')) {
                previewElement.innerHTML = `<img src="${e.target.result}" class="max-h-48 mx-auto" alt="Preview">`;
            } else {
                previewElement.innerHTML = `
                    <div class="p-4 bg-gray-100 dark:bg-gray-700 rounded">
                        <p class="text-sm text-gray-600 dark:text-gray-300">${file.name}</p>
                        <p class="text-xs text-gray-500 dark:text-gray-400">${(file.size / 1024).toFixed(2)} KB</p>
                    </div>
                `;
            }
        };
        reader.readAsDataURL(file);
    }
}

// Calendar Functionality
class Calendar {
    constructor(container, options = {}) {
        this.container = container;
        this.options = {
            onDateSelect: options.onDateSelect || function() {},
            minDate: options.minDate || new Date(),
            maxDate: options.maxDate || new Date(new Date().setFullYear(new Date().getFullYear() + 1))
        };
        this.currentDate = new Date();
        this.selectedDate = null;
        this.render();
    }

    render() {
        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth();
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const daysInMonth = lastDay.getDate();
        const startingDay = firstDay.getDay();

        let calendarHTML = `
            <div class="calendar">
                <div class="flex justify-between items-center mb-4">
                    <button class="prev-month btn-secondary">&lt;</button>
                    <h3 class="text-lg font-semibold">${new Date(year, month).toLocaleDateString('default', { month: 'long', year: 'numeric' })}</h3>
                    <button class="next-month btn-secondary">&gt;</button>
                </div>
                <div class="calendar-grid">
                    ${['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => 
                        `<div class="text-center text-sm font-medium text-gray-500 dark:text-gray-400">${day}</div>`
                    ).join('')}
                    ${Array(startingDay).fill().map(() => 
                        `<div class="calendar-day opacity-50"></div>`
                    ).join('')}
                    ${Array(daysInMonth).fill().map((_, i) => {
                        const date = new Date(year, month, i + 1);
                        const isDisabled = date < this.options.minDate || date > this.options.maxDate;
                        const isSelected = this.selectedDate && date.toDateString() === this.selectedDate.toDateString();
                        return `
                            <div class="calendar-day ${isDisabled ? 'opacity-50 cursor-not-allowed' : ''} ${isSelected ? 'selected' : ''}"
                                 data-date="${date.toISOString()}"
                                 ${isDisabled ? 'disabled' : ''}>
                                ${i + 1}
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `;

        this.container.innerHTML = calendarHTML;

        // Event Listeners
        this.container.querySelector('.prev-month').addEventListener('click', () => this.previousMonth());
        this.container.querySelector('.next-month').addEventListener('click', () => this.nextMonth());
        this.container.querySelectorAll('.calendar-day[data-date]').forEach(day => {
            if (!day.hasAttribute('disabled')) {
                day.addEventListener('click', (e) => this.selectDate(new Date(e.target.dataset.date)));
            }
        });
    }

    previousMonth() {
        this.currentDate.setMonth(this.currentDate.getMonth() - 1);
        this.render();
    }

    nextMonth() {
        this.currentDate.setMonth(this.currentDate.getMonth() + 1);
        this.render();
    }

    selectDate(date) {
        this.selectedDate = date;
        this.options.onDateSelect(date);
        this.render();
    }
}

// Search and Filter Functionality
function initializeSearch(searchInput, items, options = {}) {
    const defaultOptions = {
        keys: ['textContent'],
        threshold: 0.3,
        ...options
    };

    searchInput.addEventListener('input', debounce(function(e) {
        const searchTerm = e.target.value.toLowerCase();
        
        items.forEach(item => {
            const searchableText = defaultOptions.keys.map(key => 
                key === 'textContent' ? item.textContent : item.getAttribute(key)
            ).join(' ').toLowerCase();

            const matches = searchableText.includes(searchTerm);
            item.style.display = matches ? '' : 'none';
        });
    }, 300));
}

// Utility Functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Lazy Loading Images
document.addEventListener('DOMContentLoaded', function() {
    const lazyImages = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                observer.unobserve(img);
            }
        });
    });

    lazyImages.forEach(img => imageObserver.observe(img));
}); 
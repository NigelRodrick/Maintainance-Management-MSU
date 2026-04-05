// MSU Maintenance System - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize form validation
    initializeFormValidation();
    
    // Initialize AJAX loading
    initializeAjaxLoading();
    
    // Initialize navigation
    initializeNavigation();
});

function initializeTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(event) {
    const tooltip = event.target.getAttribute('data-tooltip');
    const tooltipElement = document.createElement('div');
    tooltipElement.className = 'tooltip';
    tooltipElement.textContent = tooltip;
    tooltipElement.style.position = 'absolute';
    tooltipElement.style.background = '#333';
    tooltipElement.style.color = '#fff';
    tooltipElement.style.padding = '5px 10px';
    tooltipElement.style.borderRadius = '3px';
    tooltipElement.style.fontSize = '12px';
    tooltipElement.style.zIndex = '1000';
    
    document.body.appendChild(tooltipElement);
    
    const rect = event.target.getBoundingClientRect();
    tooltipElement.style.left = rect.left + 'px';
    tooltipElement.style.top = (rect.top - 30) + 'px';
}

function hideTooltip() {
    const tooltip = document.querySelector('.tooltip');
    if (tooltip) {
        tooltip.remove();
    }
}

function initializeFormValidation() {
    const forms = document.querySelectorAll('form[data-validate]');
    forms.forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
    });
}

function handleFormSubmit(event) {
    const form = event.target;
    const formData = new FormData(form);
    let isValid = true;
    
    // Validate required fields
    const requiredFields = form.querySelectorAll('[required]');
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            showFieldError(field, 'This field is required');
            isValid = false;
        } else {
            clearFieldError(field);
        }
    });
    
    // Validate email fields
    const emailFields = form.querySelectorAll('[type="email"]');
    emailFields.forEach(field => {
        if (field.value && !isValidEmail(field.value)) {
            showFieldError(field, 'Please enter a valid email address');
            isValid = false;
        } else {
            clearFieldError(field);
        }
    });
    
    if (!isValid) {
        event.preventDefault();
    }
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function showFieldError(field, message) {
    clearFieldError(field);
    
    const errorElement = document.createElement('div');
    errorElement.className = 'field-error';
    errorElement.style.color = '#dc3545';
    errorElement.style.fontSize = '12px';
    errorElement.style.marginTop = '5px';
    errorElement.textContent = message;
    
    field.parentNode.appendChild(errorElement);
    field.style.borderColor = '#dc3545';
}

function clearFieldError(field) {
    const errorElement = field.parentNode.querySelector('.field-error');
    if (errorElement) {
        errorElement.remove();
    }
    field.style.borderColor = '#ddd';
}

function initializeAjaxLoading() {
    const ajaxButtons = document.querySelectorAll('[data-ajax]');
    ajaxButtons.forEach(button => {
        button.addEventListener('click', handleAjaxClick);
    });
}

function handleAjaxClick(event) {
    const button = event.target;
    const url = button.getAttribute('data-ajax');
    
    if (url) {
        event.preventDefault();
        
        // Show loading state
        button.disabled = true;
        button.textContent = 'Loading...';
        
        // Simulate AJAX request
        setTimeout(() => {
            button.disabled = false;
            button.textContent = 'Complete';
            
            setTimeout(() => {
                button.textContent = 'Submit';
            }, 2000);
        }, 1500);
    }
}

function initializeNavigation() {
    const mobileMenuToggle = document.querySelector('[data-mobile-menu-toggle]');
    const mobileMenu = document.querySelector('[data-mobile-menu]');
    
    if (mobileMenuToggle && mobileMenu) {
        mobileMenuToggle.addEventListener('click', () => {
            mobileMenu.classList.toggle('active');
        });
    }
}

// Utility functions
function formatDate(date) {
    return new Date(date).toLocaleDateString();
}

function formatTime(time) {
    return new Date(time).toLocaleTimeString();
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.maxWidth = '300px';
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// API helpers
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    const finalOptions = { ...defaultOptions, ...options };
    
    try {
        const response = await fetch(url, finalOptions);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API request failed:', error);
        showNotification('An error occurred. Please try again.', 'error');
        throw error;
    }
}

// Form helpers
function serializeForm(form) {
    const formData = new FormData(form);
    const object = {};
    
    formData.forEach((value, key) => {
        object[key] = value;
    });
    
    return object;
}

// Confirmation helpers
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Loading helpers
function showLoading(element) {
    element.disabled = true;
    element.dataset.originalText = element.textContent;
    element.textContent = 'Loading...';
}

function hideLoading(element) {
    element.disabled = false;
    element.textContent = element.dataset.originalText || 'Submit';
}

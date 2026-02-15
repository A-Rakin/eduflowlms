// Main JavaScript file

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('.delete-confirm');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item?')) {
                e.preventDefault();
            }
        });
    });
});

// Progress tracking for video content
function trackVideoProgress(videoId, contentId) {
    const video = document.getElementById(videoId);

    video.addEventListener('ended', function() {
        fetch(`/api/progress/${contentId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log('Progress saved:', data);
        })
        .catch(error => {
            console.error('Error saving progress:', error);
        });
    });
}

// Quiz timer
class QuizTimer {
    constructor(timeLimit, elementId) {
        this.timeLimit = timeLimit * 60; // Convert to seconds
        this.element = document.getElementById(elementId);
        this.interval = null;
    }

    start() {
        this.interval = setInterval(() => {
            this.timeLimit--;

            const minutes = Math.floor(this.timeLimit / 60);
            const seconds = this.timeLimit % 60;

            this.element.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;

            if (this.timeLimit <= 0) {
                clearInterval(this.interval);
                document.getElementById('quiz-form').submit();
            }
        }, 1000);
    }

    stop() {
        if (this.interval) {
            clearInterval(this.interval);
        }
    }
}
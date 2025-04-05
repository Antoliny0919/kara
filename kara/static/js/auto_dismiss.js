window.addEventListener('DOMContentLoaded', () => {
    const alerts = document.querySelectorAll('.auto-dismiss');
    alerts.forEach(alert => {
        setTimeout(() => {
            // 10sec later slide up element(fade out)
            alert.classList.remove('animate-slide-down');
            alert.classList.add('animate-slide-up-fade');
        }, 10000);
    });
});

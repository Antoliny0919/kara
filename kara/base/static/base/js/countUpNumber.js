function animateCounter(element, target, duration = 2000) {
    const startTime = Date.now();
    const startValue = 0;

    function easeOutQuart(t) {
        return 1 - Math.pow(1 - t, 4);
    }

    function updateCounter() {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);

        const easedProgress = easeOutQuart(progress);
        const currentValue = Math.floor(startValue + (target - startValue) * easedProgress);

        element.textContent = currentValue.toLocaleString();

        if (progress < 1) {
            requestAnimationFrame(updateCounter);
        } else {
            element.textContent = target.toLocaleString();
        }
    }

    requestAnimationFrame(updateCounter);
}

function startCountUp() {
    // Only need to add the data-count attribute for the count up animation to work.
    // e.g. <div data-count="100000"(purpose)>0(initial)</div>
    const counters = document.querySelectorAll('[data-count]');
    counters.forEach((counter, index) => {
        const target = parseInt(counter.dataset.count);
        const duration = target > 1000000 ? 1000 : 500;

        setTimeout(() => {
            animateCounter(counter, target, duration);
        }, index * 200);
    });
}

function resetCounters() {
    const counters = document.querySelectorAll('[data-count]');
    counters.forEach(counter => {
        counter.textContent = '0';
    });
}

window.addEventListener('load', () => {
    setTimeout(startCountUp, 500);
});
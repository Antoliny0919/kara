window.addEventListener('load', function() {
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.5,
    }

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                if (entry.target.dataset.trigger === 'underline') {
                    entry.target.classList.replace('before:w-0', 'before:w-full');
                }
                else if (entry.target.dataset.trigger === 'counter') {
                    animateCounter(entry.target);
                    observer.unobserve(entry.target);
                }
                else if (entry.target.dataset.trigger === 'fade-in-down') {
                    entry.target.classList.replace('opacity-0', 'opacity-100');
                    entry.target.classList.replace('-translate-y-20', 'translate-y-0');
                }
            }
        })
    }, observerOptions)

    const underlineElements = document.querySelectorAll('[data-trigger="underline"]');
    underlineElements.forEach(element => {
        const color = element.dataset.underlineColor ?? 'kara-light';
        element.classList.add(
            'before:w-0',
            'before:content-[\'\']',
            'before:absolute',
            'before:top-[60%]',
            'before:left-0',
            'before:h-[40%]',
            'before:bg-gradient-to-r',
            `before:from-${color}`,
            `before:to-${color}`,
            'before:transition-[with]',
            'before:duration-[1s]',
            'before:ease-out',
            'before:-z-10',
        );
        observer.observe(element);
    });

    function animateCounter(element) {
        const startTime = Date.now();
        const startValue = parseInt(element.innerHTML);
        const target = parseInt(element.dataset.count);
        const duration = 3000;

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

    const counterElements = document.querySelectorAll('[data-trigger="counter"]');
    counterElements.forEach(element => {
        observer.observe(element);
    })

    const fadeInDownElements = document.querySelectorAll('[data-trigger="fade-in-down"]');
    fadeInDownElements.forEach(element => {
        element.classList.add('opacity-0', 'duration-[1s]', 'transition-all', '-translate-y-20');
        observer.observe(element);
    })
})

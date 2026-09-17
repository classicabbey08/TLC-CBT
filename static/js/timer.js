(function () {
    const timerEl = document.getElementById('timer-display');
    const formEl = document.getElementById('exam-form');
    if (!timerEl || !formEl) return;

    let secondsRemaining = parseInt(timerEl.dataset.secondsRemaining, 10) || 0;

    function render() {
        const minutes = Math.floor(secondsRemaining / 60);
        const seconds = secondsRemaining % 60;
        timerEl.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        if (secondsRemaining <= 60) {
            timerEl.classList.add('text-danger', 'fw-bold');
        }
    }

    render();

    const interval = setInterval(function () {
        secondsRemaining -= 1;
        if (secondsRemaining <= 0) {
            secondsRemaining = 0;
            render();
            clearInterval(interval);
            // Time's up on the client: auto-submit. The server
            // independently checks the real elapsed time regardless
            // of what gets posted here.
            formEl.submit();
            return;
        }
        render();
    }, 1000);
})();

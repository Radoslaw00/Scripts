document.addEventListener('mousemove', (e) => {
    const container = document.querySelector('.glass-container');
    const xAxis = (window.innerWidth / 2 - e.pageX) / 25;
    const yAxis = (window.innerHeight / 2 - e.pageY) / 25;
    
    container.style.transform = `rotateY(${xAxis}deg) rotateX(${yAxis}deg)`;
});

// Reset on mouse leave
document.addEventListener('mouseleave', () => {
    const container = document.querySelector('.glass-container');
    container.style.transform = `rotateY(0deg) rotateX(0deg)`;
    container.style.transition = 'all 0.5s ease';
});

document.addEventListener('mouseenter', () => {
    const container = document.querySelector('.glass-container');
    container.style.transition = 'none';
});

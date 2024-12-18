document.getElementById('colorModeButton').addEventListener('click', function() {
    const body = document.body;
    let newMode;
    if (body.classList.contains('monochromacy')) {
        body.classList.remove('monochromacy');
        body.classList.add('dichromacy');
        newMode = 'dichromacy';
    } else if (body.classList.contains('dichromacy')) {
        body.classList.remove('dichromacy');
        body.classList.add('trichromacy');
        newMode = 'trichromacy';
    } else if (body.classList.contains('trichromacy')) {
        body.classList.remove('trichromacy');
        newMode = 'normal';
    } else {
        body.classList.add('monochromacy');
        newMode = 'monochromacy';
    }
    localStorage.setItem('colorMode', newMode);
});

const savedMode = localStorage.getItem('colorMode');
if (savedMode) {
    document.body.classList.add(savedMode);
}

const style = document.createElement('style');
style.innerHTML = `
    .monochromacy * {
        filter: grayscale(100%);
    }
    .dichromacy * {
        filter: contrast(150%) saturate(200%);
    }
    .trichromacy * {
        filter: hue-rotate(90deg);
    }
    .normal * {
        filter: none;
    }
`;
document.head.appendChild(style);

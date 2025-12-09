document.addEventListener('DOMContentLoaded', () => {
    // Numero totale di slide nel corso
    const totalSlides = 16;

    // Recupera il numero della slide corrente dalla variabile globale definita nell'HTML
    const currentSlide = typeof slideNumero !== 'undefined' ? slideNumero : 1;

    const prevBtn = document.getElementById('nav-prev');
    const nextBtn = document.getElementById('nav-next');
    const menuBtn = document.getElementById('nav-menu');

    // Gestione pulsante precedente
    if (prevBtn) {
        if (currentSlide <= 1) {
            prevBtn.classList.add('disabled');
        } else {
            prevBtn.addEventListener('click', () => {
                window.location.href = `${currentSlide - 1}.html`;
            });
        }
    }

    // Gestione pulsante successivo
    if (nextBtn) {
        if (currentSlide >= totalSlides) {
            nextBtn.classList.add('disabled');
        } else {
            nextBtn.addEventListener('click', () => {
                window.location.href = `${currentSlide + 1}.html`;
            });
        }
    }

    // Gestione menu indice
    if (menuBtn) {
        menuBtn.addEventListener('click', () => {
            showSlideIndex();
        });
    }

    // Navigazione con tastiera
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowRight' || e.key === ' ') {
            if (currentSlide < totalSlides) {
                window.location.href = `${currentSlide + 1}.html`;
            }
        } else if (e.key === 'ArrowLeft') {
            if (currentSlide > 1) {
                window.location.href = `${currentSlide - 1}.html`;
            }
        } else if (e.key === 'Home') {
            window.location.href = '1.html';
        } else if (e.key === 'End') {
            window.location.href = `${totalSlides}.html`;
        }
    });

    // Funzione per mostrare l'indice delle slide
    function showSlideIndex() {
        const chapters = [
            { name: 'Intro: NTA', start: 1, end: 1 },
            { name: 'ARP Spoofing', start: 2, end: 2 },
            { name: 'ARP Scanning', start: 3, end: 3 },
            { name: 'WiFi DoS', start: 4, end: 4 },
            { name: 'Rogue AP', start: 5, end: 5 },
            { name: 'Fragmentation', start: 6, end: 6 },
            { name: 'IP Spoofing', start: 7, end: 7 },
            { name: 'IP TTL', start: 8, end: 8 },
            { name: 'TCP Handshake', start: 9, end: 9 },
            { name: 'TCP Hijacking', start: 10, end: 10 },
            { name: 'ICMP Tunneling', start: 11, end: 11 },
            { name: 'HTTP Enum', start: 12, end: 12 },
            { name: 'Strange Headers', start: 13, end: 13 },
            { name: 'XSS', start: 14, end: 14 },
            { name: 'SSL Attacks', start: 15, end: 15 },
            { name: 'DNS Traffic', start: 16, end: 16 }
        ];

        let indexHTML = '<div style="max-height: 70vh; overflow-y: auto;">';

        chapters.forEach(chapter => {
            indexHTML += `<div style="margin-bottom: 15px;">
                <strong style="color: #667eea; font-size: 1.1em;">${chapter.name}</strong>
                <div style="margin-left: 20px; margin-top: 5px;">`;

            for (let i = chapter.start; i <= chapter.end; i++) {
                const isCurrentSlide = i === currentSlide;
                const style = isCurrentSlide
                    ? 'color: #4CAF50; font-weight: bold;'
                    : 'color: #d0d0e0;';
                indexHTML += `<a href="${i}.html" style="${style} text-decoration: none; display: block; padding: 3px 0;">
                    ${isCurrentSlide ? '▶ ' : ''}Slide ${i}
                </a>`;
            }

            indexHTML += '</div></div>';
        });

        indexHTML += '</div>';
        indexHTML += `<div style="margin-top: 20px; text-align: center; color: #888;">
            Slide ${currentSlide} di ${totalSlides} | 
            Usa ← → per navigare | Home/End per inizio/fine
        </div>`;

        // Crea overlay
        const overlay = document.createElement('div');
        overlay.id = 'slide-index-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.9);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 2000;
        `;

        const modal = document.createElement('div');
        modal.style.cssText = `
            background: linear-gradient(135deg, #1a1f4d 0%, #0a0e27 100%);
            padding: 30px 40px;
            border-radius: 15px;
            max-width: 500px;
            width: 90%;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
        `;

        modal.innerHTML = `
            <h2 style="color: #fff; margin-bottom: 20px; text-align: center;">📚 Indice del Corso</h2>
            ${indexHTML}
            <button id="close-index" style="
                margin-top: 20px;
                width: 100%;
                padding: 12px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 1em;
                transition: background 0.3s;
            ">Chiudi (Esc)</button>
        `;

        overlay.appendChild(modal);
        document.body.appendChild(overlay);

        // Chiudi con click su overlay o pulsante
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                overlay.remove();
            }
        });

        document.getElementById('close-index').addEventListener('click', () => {
            overlay.remove();
        });

        // Chiudi con Escape
        const escHandler = (e) => {
            if (e.key === 'Escape') {
                overlay.remove();
                document.removeEventListener('keydown', escHandler);
            }
        };
        document.addEventListener('keydown', escHandler);
    }

    // Indicatore di progresso
    const progressIndicator = document.createElement('div');
    progressIndicator.style.cssText = `
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(255, 255, 255, 0.1);
        padding: 8px 20px;
        border-radius: 20px;
        color: #d0d0e0;
        font-size: 0.9em;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    `;
    progressIndicator.innerHTML = `Slide ${currentSlide} / ${totalSlides}`;
    document.body.appendChild(progressIndicator);

    // Gestione Spoiler
    document.body.addEventListener('click', (e) => {
        if (e.target.classList.contains('spoiler')) {
            e.target.classList.toggle('revealed');
        }
    });
});

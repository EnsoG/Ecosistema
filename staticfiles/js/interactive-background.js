document.addEventListener('DOMContentLoaded', function() {
    const canvas = document.createElement('canvas');
    // Insertamos el canvas al principio del body para asegurarnos que esté detrás de todo.
    document.body.prepend(canvas);
    const ctx = canvas.getContext('2d');

    // Estilos para que el canvas sea un fondo fijo
    canvas.style.position = 'fixed';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.style.zIndex = '-1'; // Lo ponemos detrás de todo el contenido

    let width = canvas.width = window.innerWidth;
    let height = canvas.height = window.innerHeight;

    window.addEventListener('resize', () => {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    });

    let particles = [];
    const mouse = {
        x: null,
        y: null,
    };

    // Eventos para el mouse y el dedo
    window.addEventListener('mousemove', (event) => {
        mouse.x = event.x;
        mouse.y = event.y;
        // Genera una partícula a la vez para un rastro más suave
        particles.push(new Particle(mouse.x, mouse.y));
    });
    window.addEventListener('touchmove', (event) => {
        if (event.touches.length > 0) {
            mouse.x = event.touches[0].clientX;
            mouse.y = event.touches[0].clientY;
            // Genera una partícula a la vez para un rastro más suave
            particles.push(new Particle(mouse.x, mouse.y));
        }
    });

    class Particle {
        constructor(x, y) {
            this.x = x;
            this.y = y;
            this.size = Math.random() * 3 + 1; // Tamaño de las partículas
            this.speedX = Math.random() * 1 - 0.5; // Velocidad aún más reducida para un efecto de suspensión
            this.speedY = Math.random() * 1 - 0.5;
            this.color = `rgba(142, 224, 0, ${Math.random() * 0.4 + 0.4})`;
            this.lifespan = Math.random() * 60 + 120; // Vida de la partícula mucho más larga
        }

        update() {
            this.x += this.speedX;
            this.y += this.speedY;
            if (this.size > 0.2) {
                this.size -= 0.02; // Se encogen mucho más lentamente para que duren más
            }
            this.lifespan--;
        }

        draw() {
            // La opacidad disminuye con la vida útil
            ctx.fillStyle = this.color;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    function animate() {
        ctx.clearRect(0, 0, width, height);
        for (let i = 0; i < particles.length; i++) {
            particles[i].update();
            particles[i].draw();
            // Si la partícula ha expirado, la eliminamos del array
            if (particles[i].lifespan <= 0 || particles[i].size <= 0.1) {
                particles.splice(i, 1);
                i--;
            }
        }
        requestAnimationFrame(animate);
    }
    animate();
});
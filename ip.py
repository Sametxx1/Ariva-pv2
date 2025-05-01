from flask import Flask, request, render_template_string, redirect
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from colorama import init, Fore, Style
from datetime import datetime
import threading
import queue
import os
import re
import subprocess

init()
console = Console()
app = Flask(__name__)
log_queue = queue.Queue()
visitor_count = 0
cloudflared_url = "Starting..."

def log_processor():
    global visitor_count, cloudflared_url
    table = Table(title="Ziyaretçi Kayıtları", title_style="bold purple", show_lines=True, border_style="bright_blue", header_style="bold white")
    table.add_column("⏰ Zaman", style="cyan", no_wrap=True, justify="center")
    table.add_column("🌐 IP Adresi", style="green", justify="center")
    table.add_column("📱 User-Agent", style="yellow", overflow="fold")
    table.add_column("🚀 Durum", style="magenta", justify="center")

    while True:
        try:
            timestamp, ip, user_agent = log_queue.get(timeout=1)
            table.add_row(timestamp, ip, user_agent, "[green]Aktif[/green]")
            console.print(Panel.fit(f"[bold cyan]🌌 Siber Dünya IP İzleyici 🌌[/bold cyan]", border_style="blue", subtitle=f"Ziyaretçi: {visitor_count} | Cloudflared Linkiniz: {cloudflared_url}", title_align="center"))
            console.print(table)
            console.print(f"{Fore.BLUE}[BILGI]{Style.RESET_ALL} Yeni ziyaret: {Fore.GREEN}{ip}{Style.RESET_ALL} ({Fore.YELLOW}{user_agent}{Style.RESET_ALL})")
            log_queue.task_done()
        except queue.Empty:
            pass

def get_client_ip():
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        ip = forwarded_for.split(',')[0].strip()
        if ip and ip != '127.0.0.1' and ip != '::1':
            return ip
    ip = request.remote_addr
    return ip if ip and ip != '127.0.0.1' and ip != '::1' else 'Unknown'

INDEX_HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌌 Siber Dünya 🌌</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css"/>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/css/all.min.css"/>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
        body {
            background: radial-gradient(circle at center, #1a1a3d 0%, #0d0d2b 100%);
            color: #fff;
            font-family: 'Poppins', sans-serif;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            margin: 0;
        }
        canvas {
            position: fixed;
            top: 0;
            left: 0;
            z-index: -1;
        }
        .container {
            text-align: center;
            padding: 2rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 20px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            transform: perspective(1000px) rotateX(5deg);
            transition: transform 0.5s ease;
            max-width: 90%;
            margin: 1rem;
        }
        .container:hover {
            transform: perspective(1000px) rotateX(0deg);
        }
        h1 {
            font-size: clamp(2rem, 8vw, 3.5rem);
            font-weight: 700;
            background: linear-gradient(90deg, #ff3cac, #784ba0, #2b86c5);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 20px rgba(255, 255, 255, 0.3);
            animation: glowText 3s ease-in-out infinite;
            margin-bottom: 1.5rem;
        }
        .icon {
            font-size: clamp(3rem, 10vw, 4.5rem);
            color: #ff3cac;
            margin-bottom: 1.5rem;
            filter: drop-shadow(0 0 15px rgba(255, 60, 172, 0.7));
            animation: floatIcon 4s ease-in-out infinite;
        }
        .lead {
            font-size: clamp(1rem, 4vw, 1.2rem);
            margin-bottom: 1rem;
        }
        .visitor-count {
            font-size: clamp(0.9rem, 3vw, 1rem);
            background: linear-gradient(90deg, #ff3cac, #784ba0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: pulse 2s infinite;
            margin-bottom: 2rem;
        }
        .btn-custom {
            background: linear-gradient(45deg, #ff3cac, #784ba0);
            border: none;
            padding: 1rem 3rem;
            font-size: clamp(1rem, 4vw, 1.2rem);
            font-weight: 600;
            border-radius: 50px;
            color: #fff;
            box-shadow: 0 8px 25px rgba(255, 60, 172, 0.5);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            width: 100%;
            max-width: 300px;
        }
        .btn-custom:hover {
            transform: translateY(-8px);
            box-shadow: 0 12px 30px rgba(255, 60, 172, 0.7);
        }
        .particle {
            position: absolute;
            width: 15px;
            height: 15px;
            background: radial-gradient(circle, rgba(255, 60, 172, 0.8), transparent);
            border-radius: 50%;
            animation: float 10s infinite ease-in-out;
            pointer-events: none;
        }
        .glow {
            position: absolute;
            width: 60px;
            height: 60px;
            background: radial-gradient(circle, rgba(255, 60, 172, 0.4), transparent);
            animation: glow 5s infinite alternate;
        }
        @media (max-width: 768px) {
            .container {
                padding: 1.5rem;
                margin: 0.5rem;
            }
            h1 {
                font-size: clamp(1.8rem, 7vw, 2.8rem);
            }
            .icon {
                font-size: clamp(2.5rem, 8vw, 3.5rem);
            }
            .btn-custom {
                padding: 0.8rem 2rem;
            }
        }
        @keyframes float {
            0% { transform: translateY(0) scale(1); opacity: 1; }
            50% { transform: translateY(-150vh) scale(0.6); opacity: 0.4; }
            100% { transform: translateY(-300vh) scale(0); opacity: 0; }
        }
        @keyframes glow {
            0% { transform: scale(1); opacity: 0.4; }
            100% { transform: scale(1.8); opacity: 0.8; }
        }
        @keyframes floatIcon {
            0% { transform: translateY(0); }
            50% { transform: translateY(-15px); }
            100% { transform: translateY(0); }
        }
        @keyframes glowText {
            0% { text-shadow: 0 0 10px rgba(255, 255, 255, 0.3); }
            50% { text-shadow: 0 0 30px rgba(255, 255, 255, 0.5); }
            100% { text-shadow: 0 0 10px rgba(255, 255, 255, 0.3); }
        }
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
    </style>
</head>
<body>
    <canvas id="stars"></canvas>
    <div class="container animate__animated animate__zoomIn">
        <i class="fas fa-rocket icon animate__animated"></i>
        <h1 class="animate__animated">🌌 Siber Dünya'ya Hoş Geldiniz! 🌌</h1>
        <p class="lead animate__animated animate__fadeInUp animate__delay-1s">Dinamik ve güvenli bir siber deneyim için hazır mısınız?</p>
        <p class="visitor-count animate__animated animate__fadeInUp animate__delay-1s">Toplam Ziyaretçi: {{ visitor_count }}</p>
        <a href="/redirect" class="btn btn-custom animate__animated animate__pulse animate__delay-2s animate__infinite">
            Siber Sohbete Katıl! 🚀
        </a>
    </div>
    <script>
        const canvas = document.getElementById('stars');
        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        const stars = [];
        const meteors = [];
        for (let i = 0; i < 100; i++) {
            stars.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                radius: Math.random() * 2,
                speed: Math.random() * 0.5 + 0.1
            });
        }
        for (let i = 0; i < 5; i++) {
            meteors.push({
                x: Math.random() * canvas.width,
                y: -50,
                length: Math.random() * 50 + 20,
                speed: Math.random() * 5 + 2
            });
        }
        function animate() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            stars.forEach(star => {
                ctx.beginPath();
                ctx.arc(star.x, star.y, star.radius, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
                ctx.fill();
                star.y += star.speed;
                if (star.y > canvas.height) star.y = 0;
            });
            meteors.forEach(meteor => {
                ctx.beginPath();
                ctx.moveTo(meteor.x, meteor.y);
                ctx.lineTo(meteor.x - meteor.length, meteor.y + meteor.length);
                ctx.strokeStyle = 'rgba(255, 255, 255, 0.5)';
                ctx.lineWidth = 2;
                ctx.stroke();
                meteor.y += meteor.speed;
                meteor.x -= meteor.speed * 0.5;
                if (meteor.y > canvas.height || meteor.x < 0) {
                    meteor.x = Math.random() * canvas.width;
                    meteor.y = -50;
                }
            });
            requestAnimationFrame(animate);
        }
        animate();
        function createParticle() {
            const particle = document.createElement('div');
            particle.classList.add(Math.random() > 0.5 ? 'particle' : 'glow');
            particle.style.left = Math.random() * 100 + 'vw';
            particle.style.animationDuration = Math.random() * 6 + 6 + 's';
            document.body.appendChild(particle);
            setTimeout(() => particle.remove(), 10000);
        }
        setInterval(createParticle, 100);
    </script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

REDIRECT_HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Yönlendiriliyorsunuz...</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
        body {
            background: linear-gradient(135deg, #1a1a3d 0%, #0d0d2b 100%);
            color: #fff;
            font-family: 'Poppins', sans-serif;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            margin: 0;
        }
        .container {
            text-align: center;
            padding: 2rem;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
            backdrop-filter: blur(10px);
            max-width: 90%;
            margin: 1rem;
        }
        h1 {
            font-size: clamp(1.5rem, 5vw, 2rem);
            background: linear-gradient(90deg, #ff3cac, #784ba0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
        }
        .spinner {
            font-size: 2.5rem;
            animation: spin 1s linear infinite;
        }
        p {
            font-size: clamp(0.9rem, 3vw, 1rem);
        }
        @media (max-width: 768px) {
            .container {
                padding: 1.5rem;
            }
            .spinner {
                font-size: 2rem;
            }
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <i class="fas fa-spinner spinner"></i>
        <h1>Siber Dünya Sohbet'e Yönlendiriliyorsunuz...</h1>
        <p>Lütfen bekleyin, Telegram'a gidiyorsunuz!</p>
    </div>
    <script>
        setTimeout(() => {
            window.location.href = 'https://t.me/siberdunyanizsohbet';
        }, 2000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    global visitor_count
    client_ip = get_client_ip()
    user_agent = request.headers.get('User-Agent', 'N/A')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    visitor_count += 1
    log_queue.put((timestamp, client_ip, user_agent))
    return render_template_string(INDEX_HTML, visitor_count=visitor_count)

@app.route('/redirect')
def redirect_to_telegram():
    return render_template_string(REDIRECT_HTML)

def capture_cloudflared_output():
    global cloudflared_url
    try:
        process = subprocess.Popen(
            ["cloudflared", "tunnel", "--url", "http://localhost:5000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        url_pattern = re.compile(r'https://[a-z0-9-]+\.trycloudflare\.com')
        for line in iter(process.stdout.readline, ''):
            console.print(f"[DEBUG] cloudflared: {line.strip()}")
            match = url_pattern.search(line)
            if match:
                cloudflared_url = match.group(0)
                console.print(f"[bold green]Cloudflared URL yakalandı: {cloudflared_url}[/bold green]")
                break
    except Exception as e:
        cloudflared_url = f"Error: {str(e)}"
        console.print(f"[bold red]Cloudflared hatası: {str(e)}[/bold red]")

if __name__ == '__main__':
    threading.Thread(target=capture_cloudflared_output, daemon=True).start()
    log_thread = threading.Thread(target=log_processor, daemon=True)
    log_thread.start()
    app.run(host='0.0.0.0', port=3131, debug=False)

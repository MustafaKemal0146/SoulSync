import os
import time
import json
from dotenv import load_dotenv
from groq import Groq
import requests
from colorama import init, Fore, Back, Style
from pyfiglet import Figlet
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
from bs4 import BeautifulSoup
from google.cloud import language_v1

# Initialize colorama
init(autoreset=True)

# Load environment variables
print("Loading environment variables...")
load_dotenv(verbose=True)

# API anahtarlarını kontrol et
groq_key = os.getenv('GROQ_API_KEY')
if not groq_key:
    raise Exception("GROQ_API_KEY bulunamadı! .env dosyanızı kontrol edin.")

# Initialize APIs
groq_client = Groq(api_key=groq_key)  # API anahtarını .env'den al

# Initialize Rich console
console = Console()

def display_banner():
    """Display a stylish banner"""
    f = Figlet(font='slant')
    console.print(f.renderText('SoulSync'), style="bold magenta")
    console.print("🎵 Müzik Duygu Analizi", style="cyan bold")
    console.print("=" * 50, style="blue")

def log_to_file(message, status="INFO"):
    """Log messages to a file with timestamp"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_file = "soulsync_logs.txt"
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] [{status}] {message}\n")
    
    # Konsola da yazdır
    if status == "ERROR":
        console.print(f"[red][{timestamp}] {message}")
    elif status == "SUCCESS":
        console.print(f"[green][{timestamp}] {message}")
    elif status == "WARNING":
        console.print(f"[yellow][{timestamp}] {message}")

def get_song_lyrics(song_name, artist):
    """Get lyrics from Genius API"""
    log_to_file(f"Şarkı sözleri aranıyor: {song_name} - {artist}")
    
    base_url = "https://api.genius.com"
    headers = {
        'Authorization': f'Bearer {os.getenv("GENIUS_API_KEY")}',
        'Accept': 'application/json'
    }
    
    try:
        # Şarkıyı ara
        log_to_file("Genius API'ye istek gönderiliyor...")
        search_url = f"{base_url}/search"
        params = {'q': f"{song_name} {artist}"}
        response = requests.get(search_url, headers=headers, params=params)
        response.raise_for_status()
        
        # İlk sonucu al
        hits = response.json()['response']['hits']
        if not hits:
            log_to_file("Şarkı bulunamadı", "ERROR")
            raise Exception("Şarkı bulunamadı")
            
        # Genius'tan gelen şarkı bilgilerini al
        genius_song = hits[0]['result']
        song_title = genius_song['title']
        song_artist = genius_song['primary_artist']['name']
        song_url = genius_song['url']
        
        log_to_file(f"Şarkı bulundu: {song_title} - {song_artist}", "SUCCESS")
        
        # Şarkı sayfasını al ve parse et
        log_to_file("Şarkı sözleri sayfası alınıyor...")
        page = requests.get(song_url)
        soup = BeautifulSoup(page.content, 'html.parser')
        
        # Şarkı sözlerini bul
        lyrics = ""
        log_to_file("Şarkı sözleri ayrıştırılıyor...")
        
        # Farklı yöntemlerle sözleri bulmayı dene
        lyrics_div = soup.find('div', class_='lyrics')
        if lyrics_div:
            lyrics = lyrics_div.get_text()
            log_to_file("Şarkı sözleri birinci yöntemle bulundu", "SUCCESS")
            
        if not lyrics:
            containers = soup.find_all('div', attrs={'data-lyrics-container': 'true'})
            for container in containers:
                lyrics += container.get_text() + "\n\n"
            if lyrics:
                log_to_file("Şarkı sözleri ikinci yöntemle bulundu", "SUCCESS")
        
        if not lyrics:
            alt_div = soup.find('div', class_='Lyrics__Container-sc-1ynbvzw-6')
            if alt_div:
                lyrics = alt_div.get_text()
                log_to_file("Şarkı sözleri üçüncü yöntemle bulundu", "SUCCESS")
        
        if not lyrics.strip():
            log_to_file("Şarkı sözleri bulunamadı", "ERROR")
            raise Exception("Şarkı sözleri bulunamadı")
            
        log_to_file(f"Toplam {len(lyrics.split())} kelimelik şarkı sözü alındı", "SUCCESS")
        return {
            'lyrics': lyrics.strip(),
            'title': song_title,
            'artist': song_artist
        }
        
    except Exception as e:
        log_to_file(f"Hata: {str(e)}", "ERROR")
        raise Exception(f"Şarkı sözleri alınamadı: {str(e)}")

def analyze_emotions(text):
    """Analyze emotions using Groq AI"""
    try:
        log_to_file("Duygu analizi başlatılıyor...")
        clean_text = BeautifulSoup(text, "html.parser").get_text()
        
        prompt = """Şarkı sözlerini analiz et ve duygu skorlarını döndür.

Şarkı: {text}

SADECE bu JSON formatını kullan (başka hiçbir şey yazma):
{{"joy": 0.3, "sadness": 0.7, "anger": 0.2, "fear": 0.1, "love": 0.8}}"""
        
        log_to_file("Groq API'ye istek gönderiliyor...")
        
        response = groq_client.chat.completions.create(
            messages=[{
                "role": "system",
                "content": "Sen bir JSON API'sisin. Sadece tek satırlık JSON yanıtı ver."
            },
            {
                "role": "user", 
                "content": prompt.format(text=clean_text[:1000])
            }],
            model="mixtral-8x7b-32768",
            temperature=0.1,
            max_tokens=50,
            stop=["\n", " \n"]  # Yeni satırları engelle
        )
        
        log_to_file("Groq API'den yanıt alındı", "SUCCESS")
        content = response.choices[0].message.content.strip()
        log_to_file(f"Ham yanıt: {content}")
        
        try:
            # Sadece süslü parantezler arasındaki kısmı al
            import re
            json_match = re.search(r'\{[^}]+\}', content)
            if not json_match:
                raise ValueError("Geçerli JSON bulunamadı")
            
            clean_json = json_match.group()
            emotions = json.loads(clean_json)
            
            # Gerekli duyguları kontrol et
            required_emotions = {'joy', 'sadness', 'anger', 'fear', 'love'}
            for emotion in required_emotions:
                if emotion not in emotions:
                    emotions[emotion] = 0.1
                elif not isinstance(emotions[emotion], (int, float)):
                    emotions[emotion] = 0.1
                elif emotions[emotion] > 1:
                    emotions[emotion] = 1
                elif emotions[emotion] < 0:
                    emotions[emotion] = 0
            
            return emotions
            
        except Exception as e:
            log_to_file(f"JSON işleme hatası: {str(e)}", "ERROR")
            return {
                "joy": 0.1,
                "sadness": 0.7,
                "anger": 0.2,
                "fear": 0.1,
                "love": 0.6
            }
            
    except Exception as e:
        log_to_file(f"Duygu analizi hatası: {str(e)}", "ERROR")
        raise Exception(f"Duygu analizi yapılamadı: {str(e)}")

def display_emotion_analysis(emotions):
    """Display emotion analysis in a pretty table"""
    # Duygu isimlerini Türkçeleştir
    emotion_names = {
        'joy': 'Mutluluk',
        'sadness': 'Hüzün',
        'anger': 'Öfke',
        'fear': 'Korku',
        'love': 'Aşk'
    }
    
    table = Table(title="Duygu Analizi Sonuçları", box=box.ROUNDED)
    
    table.add_column("Duygu", style="cyan")
    table.add_column("Skor", justify="right", style="magenta")
    
    for emotion, score in emotions.items():
        table.add_row(
            emotion_names[emotion],
            f"{score * 100:.1f}%"
        )
    
    console.print(table)

def save_analysis(song_name, artist, analysis_data):
    """Save analysis results to a text file"""
    # Duygu isimlerini Türkçeleştir
    emotion_names = {
        'joy': 'Mutluluk',
        'sadness': 'Hüzün',
        'anger': 'Öfke',
        'fear': 'Korku',
        'love': 'Aşk'
    }
    
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"analysis_{song_name}_{artist}_{timestamp}.txt"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write("=" * 50 + "\n")
        f.write(f"Şarkı Analizi: {song_name} - {artist}\n")
        f.write("=" * 50 + "\n\n")
        
        f.write("Duygusal Analiz:\n")
        for emotion, score in analysis_data['emotions'].items():
            f.write(f"{emotion_names[emotion]}: {score * 100:.1f}%\n")
        
        dominant_emotion = emotion_names[analysis_data['dominant_emotion']]
        f.write(f"\nBaskın Duygu: {dominant_emotion}\n")
        f.write(f"Analiz Özeti: Bu şarkı ağırlıklı olarak {dominant_emotion.lower()} duygusunu ifade ediyor.\n")
    
    console.print(f"\n[green]Analiz sonuçları kaydedildi: {filename}")
    return filename

def main_menu():
    """Display main menu and handle user input"""
    while True:
        display_banner()
        console.print("\n[bold cyan]Menü:")
        console.print("1. Şarkı Analizi")
        console.print("2. Çıkış")
        
        choice = console.input("\n[bold yellow]Seçiminiz (1-2): ")
        
        if choice == "1":
            song_name = console.input("\n[bold green]Şarkı adı: ")
            artist = console.input("[bold green]Sanatçı: ")
            
            try:
                console.print("\n[bold cyan]İşlem Adımları:")
                
                # Şarkı sözleri arama
                with console.status("[bold yellow]Şarkı sözleri aranıyor...") as status:
                    console.print("[1/4] Genius API'ye bağlanılıyor...")
                    song_data = get_song_lyrics(song_name, artist)
                    lyrics = song_data['lyrics']
                    song_title = song_data['title']
                    song_artist = song_data['artist']
                    console.print("[green]✓[/green] Şarkı sözleri başarıyla alındı")
                
                # Yapay zeka analizi
                with console.status("[bold yellow]Duygu analizi yapılıyor...") as status:
                    console.print("[2/4] Şarkı sözleri temizleniyor...")
                    console.print("[3/4] Groq AI'ya gönderiliyor...")
                    emotions = analyze_emotions(lyrics)
                    console.print("[green]✓[/green] Duygu analizi tamamlandı")
                
                # Sonuçları hazırlama
                console.print("[4/4] Sonuçlar hazırlanıyor...")
                analysis_data = {
                    'emotions': emotions,
                    'dominant_emotion': max(emotions.items(), key=lambda x: x[1])[0],
                    'analysis_summary': None
                }
                
                # Sonuçları gösterme
                console.print("\n[bold green]Analiz Tamamlandı![/bold green]")
                console.print("\n[bold cyan]Analiz Sonuçları:")
                console.print(f"[bold]🎵 {song_title} - {song_artist}")
                display_emotion_analysis(emotions)
                
                # Sonuçları kaydetme
                with console.status("[bold yellow]Sonuçlar kaydediliyor...") as status:
                    save_analysis(song_title, song_artist, analysis_data)
                
            except Exception as e:
                console.print(f"\n[bold red]❌ Hata: {str(e)}")
            
            input("\n[bold]Devam etmek için Enter'a basın...")
            
        elif choice == "2":
            console.print("\n[bold cyan]Güle güle! 👋")
            break
        
        else:
            console.print("\n[bold red]Geçersiz seçim! Lütfen tekrar deneyin.")
        
        console.clear()

if __name__ == "__main__":
    try:
        console.clear()
        main_menu()
    except KeyboardInterrupt:
        console.print("\n\n[bold red]Program sonlandırıldı!")
    except Exception as e:
        console.print(f"\n[bold red]Beklenmeyen hata: {str(e)}") 

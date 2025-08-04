# Telegram AutoPost Bot (Python)

Bot, belirli aralıklarla Telegram kanalına/grubuna otomatik mesaj gönderir,  
eski mesajları siler, admin kontrolü sağlar.

## Ortam Değişkenleri

- BOT_TOKEN: Bot token (BotFather’dan alınır)  
- ADMIN_ID: Admin Telegram kullanıcı ID’si  

## Komutlar

- /setchannel @kanaladi  
- /setinterval dakika  
- /setdays gün_sayisi  
- /addpost mesaj  
- /removepost mesaj_no  
- /startposting  
- /stopposting  

## Çalıştırma

```bash
pip install -r requirements.txt
python bot.py

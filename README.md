# AgroOC Holdings — server versiyasi

Bitta ma'lumot bazasi, ko'p foydalanuvchi. Har kim o'z PIN'i bilan kiradi,
kiritilgan ma'lumot hammada bir zumda ko'rinadi.

## 1. Render.com'ga qo'yish (bepul)

1. https://github.com — yangi **private repository** oching (masalan `agroos`).
2. Shu papkadagi hamma faylni o'sha repoga yuklang
   (`app.py`, `requirements.txt`, `render.yaml`, `static/app.html`).
3. https://render.com — ro'yxatdan o'ting → **New → Blueprint** → repoingizni tanlang.
   `render.yaml` o'zi hammasini sozlaydi.
4. 2–3 daqiqada manzil chiqadi: `https://agroos-xxxx.onrender.com`

**Muhim:** `render.yaml` da 1 GB disk yozilgan (`/var/data`) — ma'lumot shunda saqlanadi
va qayta ishga tushirilganda yo'qolmaydi. Bepul tarifda disk pullik bo'lsa,
`disk:` bo'limini o'chirib, `AGROOS_DB` ni `agroos.db` qilib qo'ying —
lekin unda Render ilovani qayta qurganda ma'lumot o'chadi, shuning uchun
haftada bir **Zaxira** oling.

## 2. Telefonga o'rnatish

Har bir xodim: manzilni brauzerda ochadi → PIN kiritadi →
**Ulashish → Bosh ekranga qo'shish**. Endi oddiy ilova kabi ochiladi.

## 3. Boshlang'ich PIN'lar — birinchi kirishdan keyin ALMASHTIRING

| Kim | Roli | PIN |
|---|---|---|
| Asqar | egasi | 1111 |
| Bobur | Qozog'iston baza | 2222 |
| Zuhriddin | Toshkent baza | 3333 |
| Akmal Karimov | Yem zavodi | 4444 |
| Xasan Toshpolatov | Ferma | 5555 |

PIN'ni almashtirish: avatarga bosing → **PIN o'zgartirish**.
Egasi boshqalarnikini ham almashtira oladi.

## 4. Qanday ishlaydi

- Har bir yozuv **0,6 soniyada** serverga ketadi — o'ng yuqorida "Saqlandi" chiqadi.
- Ilova har **12 soniyada** serverni tekshiradi; boshqa odam yozsa,
  ekran o'zi yangilanadi va "Falonchi ma'lumot kiritdi" deb chiqadi.
- Ikki kishi bir vaqtda yozsa — ikkalasining yozuvi ham saqlanadi
  (server birlashtiradi, hech biri yo'qolmaydi).
- Internet uzilsa — "Ulanish yo'q" chiqadi, ma'lumot telefonda turadi
  va ulanish tiklanganda o'zi ketadi.

## 5. Zaxira

- Ilovadan: **Zaxira olish** tugmasi (JSON fayl).
- Serverdan: `https://…/api/backup` — o'sha paytdagi to'liq holat.
- Server har 20-o'zgarishda o'zi ham ichki nusxa saqlaydi (oxirgi 50 tasi).

## 6. Yangilanish

Yangi versiya chiqsa — `static/app.html` ni almashtirib repoga yuklaysiz.
Render o'zi qayta quradi. **Hamma keyingi ochganda yangisini ko'radi**,
hech kim hech narsa o'rnatmaydi. Ma'lumot o'z joyida qoladi.

## 7. Xavfsizlik

- PIN'lar SHA-256 bilan saqlanadi, ochiq matnda emas.
- `SECRET_KEY` Render tomonidan avtomatik yaratiladi.
- Manzilni faqat o'z xodimlaringizga bering.
- Noto'g'ri PIN kiritilganda javob 0,6 soniya kechiktiriladi (terib topishga qarshi).

## 8. Ikonka

Ilova ikonkasi `static/icon-180.png`, `icon-192.png`, `icon-512.png` fayllarida.
Almashtirmoqchi bo'lsangiz — o'sha uch faylni yangi kvadrat PNG bilan almashtirib
repoga yuklang. Telefonda bosh ekrandan o'chirib qaytadan qo'shsangiz, yangisi chiqadi.

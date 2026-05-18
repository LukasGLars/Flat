# Flat – Landlord Mailer

Personaliserat mailskript för att kontakta privata hyresvärdar i Alingsås med omnejd.

## Filstruktur

```
Flat/
├── mailer.py          # Huvudskript
├── contacts.csv       # Kontaktlista med avsändningsstatus
├── template.txt       # Mailmall med ämnesrad och brödtext
├── .env               # Hemliga uppgifter (ingår ej i git)
├── .env.example       # Mall för .env
├── log.csv            # Automatiskt loggfilsskapas vid körning (ingår ej i git)
├── .gitignore
└── CLAUDE.md
```

## Flöde

1. `mailer.py` läser `.env` via `python-dotenv`.
2. `template.txt` parsas – första raden (`Ämne: ...`) blir subject, resten blir body.
3. `contacts.csv` läses in; rader med ifyllt `skickat_datum` hoppas över.
4. För varje väntande kontakt ersätts `{namn}`, `{ort}` och `{telefon}` i subject och body.
   - Om `telefon` saknas i CSV används `SENDER_PHONE` från `.env`.
5. Mailet skickas via Gmail SMTP SSL (port 465).
6. Vid lyckat utskick skrivs dagens datum (ISO 8601) till `skickat_datum` i CSV.
7. Varje försök loggas (datum, namn, email, OK/FEL) till `log.csv`.
8. Skriptet väntar 5 sekunder mellan utskick för att undvika spamfilter.

## Miljövariabler (.env)

| Variabel            | Beskrivning                              |
|---------------------|------------------------------------------|
| `GMAIL_USER`        | Din Gmail-adress                         |
| `GMAIL_APP_PASSWORD`| App-lösenord (inte ditt vanliga lösenord)|
| `SENDER_NAME`       | Avsändarnamn i mail-headern              |
| `SENDER_PHONE`      | Telefonnummer som fallback i malltext    |

Skapa ett Gmail App Password under:
**Google-konto → Säkerhet → Tvåstegsverifiering → Applösenord**

## Kom igång

Miljövariablerna sätts som secrets i din miljö (t.ex. GitHub Secrets eller Claude Code Secrets) – ingen `.env`-fil behövs.

```bash
# Kör skriptet (env-variabler måste vara satta i miljön)
python mailer.py
```

## contacts.csv – kolumner

| Kolumn          | Beskrivning                                      |
|-----------------|--------------------------------------------------|
| `namn`          | Fastighetsbolagets namn (används i hälsningsfras)|
| `email`         | Mottagarens e-postadress                         |
| `telefon`       | Telefonnummer (visas i mailsignaturen)            |
| `ort`           | Ort (används i ämnesrad och brödtext)            |
| `skickat_datum` | Fylls i automatiskt av skriptet (ISO-datum)      |
| `notering`      | Fri anteckning, påverkar inte körningen          |

Rader med ifyllt `skickat_datum` hoppas över vid nästa körning – säkert att köra om.

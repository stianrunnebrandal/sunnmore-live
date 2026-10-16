Sunnmøre Live – prototype med automatisk NFF-kalenderimport

Dette prosjektet er eit teknisk første steg. Det har:
- mobilvenleg kampoversikt
- datoveljar og navigering mellom datoar
- lenkjer til offisiell terminliste/resultat og tabell hos NFF
- ei kampvising som les data frå data/matches.json
- eit Python-skript som prøver å hente NFF si offentlege iCalendar-teneste og konvertere ho til JSON
- ein GitHub Actions-workflow som kan køyre synkronisering kvar sjette time etter at prosjektet er lagt i eit GitHub-repositorium og Actions er aktivert

VIKTIGE AVGRENSINGAR
- Eg fekk ikkje testa henting av kalendaren frå denne arbeidsøkta fordi nettverkstilgang til NFF-endepunktet ikkje var tilgjengeleg her. Scriptet må testast når det køyrer på ein nettverksvert.
- Kalenderfeeden er forventa å innehalde kalenderhendingar, ikkje nødvendigvis resultat, målscorarar, kort eller live-hendingar.
- Dette prosjektet viser aldri oppdikta resultat eller late-som-live-data.
- Før offentleg drift må NFF sine vilkår for automatisk uthenting og vidarebruk kontrollerast. At ein kalender er offentleg tilgjengeleg, er ikkje i seg sjølv eit juridisk løyve til all bruk.
- Ingen hosting er sett opp, og det finst ikkje ei offentleg nettadresse enno.

TEST LOKALT
1. Installer Python 3.10+.
2. Køyr: python scripts/sync_calendar.py
3. Opne sida via ein lokal webserver frå prosjektmappa, til dømes: python -m http.server 8000
4. Opne http://localhost:8000

Merk: Opnar du index.html direkte som file://, vil nettlesaren ofte blokkere lesing av data/matches.json.

AUTOMATISK OPPDATERING
Workflow-fila .github/workflows/update-calendar.yml er sett opp til å køyre kvar sjette time når prosjektet ligg i GitHub og Actions har rett tilgang til å skrive endra datafila. Workflowen oppdaterer data/matches.json i repoet. Publisering av nettsida må konfigurerast separat.

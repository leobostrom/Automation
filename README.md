# Automatisera skapandet av användare i både Active Directory och Linux
## Beskrivning
Vi har valt att göra uppgiften automatisera skapandet av användare och har valt att göra både för Linux och Windows Active Directory.

## Vårt mål
Vårt mål var att automatisera så mycket som möjligt för att skapa användare. Vår miljö är baserat på en skolmiljö och har därmed, två kategorier, Students och Staff där dessa två ska ha olika rättigheter, i Windows AD skapas de i olika OU:n och i Linux kommer dom i olika grupper.

Från början var vår ambition att både Linux och Active Directory skulle köras från samma skript men vi hade problem att implementera Ansible. Vi bestämde därefter att göra två olika versioner av programmet, en för Windows och en för Linux.
Python-scriptet frågar efter lite olika inputs, förnamn, efternamn, staff/student, och när man skapar staff, kopplar ett telefonnummer.
Tanken är att det scriptet ska köras på en dator i skolexpeditionen om det tillkommer nya elever eller nya medarbetare på skolan.

## Windows
### Funktioner
- Ett menysystem
- Input-prompts där man skriver personuppgifter och kategori.
- Genererar Powershell-kod baserat på inputs:en som sedan körs

### Hur det fungerar
Programmet börjar med att visa huvudmenyn där man kan välja 1 för att skapa en användare eller 2 för att avsluta. Trycker man 1 så frågar den sen efter förnamn, efternamn, om det är staff eller student. När man svarat på samtliga prompts händer följande:
1. Den läser av inputs:en och genererar två Powershell-strängar, en för skapandet av användaren i Windows Active Directory och en för att skapa en hemkatalog på den gemensamma filservern.
2. De två strängarna körs med hjälp av subprocess-modul som kan köra Powershell och därefter finns både användaren i AD:t och hemkatalogen på filservern.

## Linux
### Funktioner
- Ett menysystem
- Input-prompts där man skriver personuppgifter och kategori. 
- Genererer Yaml-fil med användare.

### Hur det fungerar
Programmet börjar med att visa huvudmenyn där man kan välja 1 för att skapa en användare eller 2 för att avsluta. Trycker man 1 så frågar den sen efter förnamn, efternamn, om det är staff eller student. När man svarat på samtliga prompts händer följande:
1. Den läser av inputs:en och genererar en Yaml-fil.
2. Ansible-Playbook körs med hjälp av en subprocess-modul och skapar användare i två olika Linux-system med användare från Yamel-filen. 
3. Felhantering görs av subprocess-modulen för att fånga upp eventuella fel från Ansible.

## To do
- [X] Implementera skapandet av användare och hemkatalog i Windows AD
- [X] Implementera Linux på ett smart sätt
- [ ] Felhantering av koden

## Credits
### MLM - Marcus, Leo & Martin

# Custom direct routing

Файлы в этой папке — пользовательские дополнения форка:

- `direct-domains.txt` — доменные суффиксы для DIRECT;
- `direct-processes.txt` — Windows-процессы для DIRECT в Mihomo.

Скрипт `scripts/apply-custom-rules.py` применяет их к профилям `DEFAULT` для
HAPP/INCY и к обоим шаблонам Mihomo. GitHub Actions запускает его перед
обновлением сгенерированных deeplink-файлов.

В HAPP/INCY нет правила по имени процесса, поэтому динамические IP игровых
серверов там покрываются только доменными правилами и существующим
`geoip:direct`. Для точного обхода VPN всего трафика CS2/Faceit используйте
Mihomo-профиль.

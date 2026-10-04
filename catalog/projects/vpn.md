# VPN

**Инфраструктура** · 🟢 работает — работает: xray, xray, wstunnel, stunnel4

AmneziaWG (Казахстан, 198) и Xray. Ключи выдаются по одному на устройство, хранятся только на сервере. Ключи клиентов (/root/amnezia-clients) никогда не выгружаются. MTProto-прокси Telegram (контейнер mtg) остановлен.

## Со слов владельца

- **Для чего:** сервер 198 (Алматы) — VPN и часть сайтов
- **Сейчас:** работает

## Что запущено

| Сервис | Сервер | Состояние | Порты | Память |
|---|---|---|---|---|
| xray | 198 | active | 2053, 2087, 8443 | 18.7 МБ |
| xray | 78 | active | 2053 | 16.6 МБ |
| wstunnel | 78 | active | 8087 | 6.2 МБ |
| stunnel4 | 78 | active | — | 2.0 МБ |
| 🐳 mtg | 78 | Exited (0) 11 days ago | — | — |

## Папки на серверах

- `198:/root/amneziawg-go` — 8.0 МБ, 122 файлов, изменена 2026-09-08, стек: go, docker
  - README: # Go Implementation of AmneziaWG · AmneziaWG is a contemporary version of the WireGuard protocol. It's a fork of WireGuard-Go and offers protection against detection by Deep Packet Inspection (DPI) systems. At the same time, it retains the simplified architecture and high performance of the original. · The precursor, WireGuard, is known for its efficiency but had issues with detection due to its d
- `198:/root/amneziawg-tools` — 1.9 МБ, 191 файлов, изменена 2026-09-08
  - README: # [wireguard-tools](https://git.zx2c4.com/wireguard-tools/about/) &mdash; tools for configuring [WireGuard](https://www.wireguard.com/) · This supplies the main userspace tooling for using and configuring WireGuard · tunnels, including the · [`awg(8)`](https://git.zx2c4.com/wireguard-tools/about/src/man/wg.8) and · [`awg-quick(8)`](https://git.zx2c4.com/wireguard-tools/about/src/man/wg-quick.8) · 
- `78:/opt/amnezia` — —, 0 файлов, изменена —
- `198:/root/amnezia-clients` — 9.1 КБ, 14 файлов, изменена 2026-10-04

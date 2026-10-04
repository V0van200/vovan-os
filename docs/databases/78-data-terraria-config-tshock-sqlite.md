# /data/terraria/config/tshock.sqlite (сервер 78, sqlite)

Проект: Terraria Server. Размер: 88.0 КБ.

## GroupList — 8 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| GroupName | TEXT |  | PK |
| Parent | TEXT |  |  |
| Commands | TEXT |  |  |
| ChatColor | TEXT |  |  |
| Prefix | TEXT |  |  |
| Suffix | TEXT |  |  |

## ItemBans — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| ItemName | TEXT |  | PK |
| AllowedGroups | TEXT |  |  |

## PlayerBans — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| TicketNumber | INTEGER |  | PK |
| Identifier | TEXT |  |  |
| Reason | TEXT |  |  |
| BanningUser | TEXT |  |  |
| Date | BIGINT |  |  |
| Expiration | BIGINT |  |  |

## ProjectileBans — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| ProjectileID | INTEGER |  | PK |
| AllowedGroups | TEXT |  |  |

## Regions — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| Id | INTEGER |  | PK |
| X1 | INTEGER |  |  |
| Y1 | INTEGER |  |  |
| width | INTEGER |  |  |
| height | INTEGER |  |  |
| RegionName | TEXT |  |  |
| WorldID | TEXT |  |  |
| UserIds | TEXT |  |  |
| Protected | INTEGER |  |  |
| Groups | TEXT |  |  |
| Owner | TEXT |  |  |
| Z | INTEGER |  |  |

## RememberedPos — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| Name | TEXT |  | PK |
| IP | TEXT |  |  |
| X | INTEGER |  |  |
| Y | INTEGER |  |  |
| WorldID | TEXT |  |  |

## Research — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| WorldId | INTEGER |  |  |
| PlayerId | INTEGER |  |  |
| ItemId | INTEGER |  |  |
| AmountSacrificed | INTEGER |  |  |
| TimeSacrificed | DATETIME |  |  |

## TileBans — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| TileId | INTEGER |  | PK |
| AllowedGroups | TEXT |  |  |

## Users — 1 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| ID | INTEGER |  | PK |
| Username | TEXT |  |  |
| Password | TEXT |  |  |
| UUID | TEXT |  |  |
| Usergroup | TEXT |  |  |
| Registered | TEXT |  |  |
| LastAccessed | TEXT |  |  |
| KnownIPs | TEXT |  |  |

## Warps — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| Id | INTEGER |  | PK |
| WarpName | TEXT |  |  |
| X | INTEGER |  |  |
| Y | INTEGER |  |  |
| WorldID | TEXT |  |  |
| Private | TEXT |  |  |

## tsCharacter — 1 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| Account | INTEGER |  | PK |
| Health | INTEGER |  |  |
| MaxHealth | INTEGER |  |  |
| Mana | INTEGER |  |  |
| MaxMana | INTEGER |  |  |
| Inventory | TEXT |  |  |
| extraSlot | INTEGER |  |  |
| spawnX | INTEGER |  |  |
| spawnY | INTEGER |  |  |
| skinVariant | INTEGER |  |  |
| hair | INTEGER |  |  |
| hairDye | INTEGER |  |  |
| hairColor | INTEGER |  |  |
| pantsColor | INTEGER |  |  |
| shirtColor | INTEGER |  |  |
| underShirtColor | INTEGER |  |  |
| shoeColor | INTEGER |  |  |
| hideVisuals | INTEGER |  |  |
| skinColor | INTEGER |  |  |
| eyeColor | INTEGER |  |  |
| questsCompleted | INTEGER |  |  |
| usingBiomeTorches | INTEGER |  |  |
| happyFunTorchTime | INTEGER |  |  |
| unlockedBiomeTorches | INTEGER |  |  |
| currentLoadoutIndex | INTEGER |  |  |
| ateArtisanBread | INTEGER |  |  |
| usedAegisCrystal | INTEGER |  |  |
| usedAegisFruit | INTEGER |  |  |
| usedArcaneCrystal | INTEGER |  |  |
| usedGalaxyPearl | INTEGER |  |  |
| usedGummyWorm | INTEGER |  |  |
| usedAmbrosia | INTEGER |  |  |
| unlockedSuperCart | INTEGER |  |  |
| enabledSuperCart | INTEGER |  |  |
| deathsPVE | INTEGER |  |  |
| deathsPVP | INTEGER |  |  |
| voiceVariant | INTEGER |  |  |
| voicePitchOffset | REAL |  |  |
| team | INTEGER |  |  |

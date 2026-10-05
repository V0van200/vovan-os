# /var/lib/kabluk/kabluk.sqlite (сервер 78, sqlite)

Проект: Каблуковск / Kabluk. Размер: 1.1 МБ.

## accounts — 21 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | TEXT |  | PK |
| owner_type | TEXT | да |  |
| owner_id | TEXT | да |  |
| city_id | TEXT | да |  |
| balance | INTEGER | да |  |
| allow_negative | INTEGER | да |  |
| created_at | INTEGER | да |  |

## actions — 486 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | TEXT | да | PK |
| player_id | TEXT | да |  → players.id |
| kind | TEXT | да |  |
| created_at | INTEGER | да |  |

## apartments — 2 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | TEXT | да | PK |
| owner_id | TEXT | да |  → players.id |
| bought_at | INTEGER | да |  |

## business_stats — 1 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| business_id | TEXT | да | PK → businesses.id |
| day | TEXT | да | PK |
| produced | INTEGER | да |  |
| sold | INTEGER | да |  |
| revenue | INTEGER | да |  |
| moved | INTEGER | да |  |

## businesses — 1 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | TEXT |  | PK |
| city_id | TEXT | да |  |
| type | TEXT | да |  |
| owner_id | TEXT | да |  → players.id |
| parcel_id | TEXT |  |  → parcels.id |
| account_id | TEXT | да |  → accounts.id |
| level | INTEGER | да |  |
| last_cycle_at | INTEGER | да |  |
| created_at | INTEGER | да |  |
| carry | INTEGER | да |  |
| staff | INTEGER | да |  |
| wage_at | INTEGER | да |  |
| shift_from | INTEGER | да |  |
| shift_until | INTEGER | да |  |
| shift_ready_at | INTEGER | да |  |
| npc_at | INTEGER | да |  |

## chain_jobs — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| player_id | TEXT |  | PK → players.id |
| job | TEXT | да |  |
| since | INTEGER | да |  |
| shifts | INTEGER | да |  |
| earned | INTEGER | да |  |

## chain_license — 2 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| player_id | TEXT |  | PK → players.id |
| stage | TEXT | да |  |
| qids | TEXT |  |  |
| step | INTEGER | да |  |
| drive_at | INTEGER | да |  |
| fails | INTEGER | да |  |
| last_fail_at | INTEGER | да |  |
| paid | INTEGER | да |  |
| issued_at | INTEGER |  |  |

## chain_stock — 3 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| place | TEXT | да | PK |
| item | TEXT | да | PK |
| qty | INTEGER | да |  |
| cap | INTEGER | да |  |
| at | INTEGER | да |  |

## chain_vehicle — 2 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| player_id | TEXT |  | PK → players.id |
| kind | TEXT | да |  |
| since | INTEGER | да |  |

## city_auto_lots — 20 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| lot_key | TEXT |  | PK |
| building_id | TEXT | да |  → city_buildings.id |
| road_id | TEXT | да |  |

## city_buildings — 28 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | TEXT |  | PK |
| kind | TEXT | да |  |
| x | REAL | да |  |
| z | REAL | да |  |
| rotation | INTEGER | да |  |
| status | TEXT | да |  |
| built_at | INTEGER | да |  |
| built_by | TEXT |  |  → players.id |

## city_lots — 9 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| building_id | TEXT |  | PK → city_buildings.id |
| level | INTEGER | да |  |
| bad | INTEGER | да |  |
| updated_at | INTEGER | да |  |

## city_roads — 1 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| building_id | TEXT | да | PK |
| points | TEXT | да |  |
| length | REAL | да |  |
| cost | INTEGER | да |  |
| upkeep | INTEGER | да |  |

## city_roles — 1 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| role | TEXT |  | PK |
| player_id | TEXT |  |  → players.id |
| since | INTEGER | да |  |

## city_zone_cells — 96 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| cell_id | TEXT |  | PK |
| zone | TEXT | да |  |
| painted_at | INTEGER | да |  |

## contributions — 68 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| action_id | TEXT | да | PK → actions.id |
| player_id | TEXT | да |  → players.id |
| amount | INTEGER | да |  |
| created_at | INTEGER | да |  |

## coop_jobs — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | TEXT | да | PK |
| owner_id | TEXT | да |  → players.id |
| partner_id | TEXT | да |  → players.id |
| owner_done | INTEGER | да |  |
| partner_done | INTEGER | да |  |
| status | TEXT | да |  |
| settlement | TEXT |  |  |
| created_at | INTEGER | да |  |

## coop_queue — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| player_id | TEXT | да | PK → players.id |
| joined_at | INTEGER | да |  |

## deposits — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | TEXT |  | PK |
| player_id | TEXT | да |  → players.id |
| account_id | TEXT | да |  → accounts.id |
| amount | INTEGER | да |  |
| rate_bps | INTEGER | да |  |
| term_days | INTEGER | да |  |
| matures_at | INTEGER | да |  |
| status | TEXT | да |  |
| created_at | INTEGER | да |  |

## econ_jobs — 21 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| key | TEXT |  | PK |
| done_at | INTEGER | да |  |
| result | TEXT |  |  |

## econ_policy — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| key | TEXT |  | PK |
| value | INTEGER | да |  |
| updated_at | INTEGER | да |  |
| updated_by | TEXT |  |  |

## economy_assert — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| ok | INTEGER | да |  |

## economy_context — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| tx_id | TEXT | да |  |
| reason | TEXT | да |  |

## economy_types — 11 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| type | TEXT |  | PK |
| capacity | INTEGER | да |  |

## events — 151 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | TEXT | да | PK |
| player_id | TEXT | да |  → players.id |
| message | TEXT | да |  |
| created_at | INTEGER | да |  |

## freight_orders — 3 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | TEXT |  | PK |
| player_id | TEXT | да |  → players.id |
| item | TEXT | да |  |
| qty | INTEGER | да |  |
| from_id | TEXT | да |  |
| to_id | TEXT | да |  |
| dist | REAL | да |  |
| pay | INTEGER | да |  |
| energy | INTEGER | да |  |
| status | TEXT | да |  |
| created_at | INTEGER | да |  |
| finished_at | INTEGER |  |  |

## gig_orders — 32 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | TEXT |  | PK |
| player_id | TEXT | да |  → players.id |
| kind | TEXT | да |  |
| from_id | TEXT | да |  |
| to_id | TEXT | да |  |
| dist | REAL | да |  |
| pay | INTEGER | да |  |
| energy | INTEGER | да |  |
| status | TEXT | да |  |
| created_at | INTEGER | да |  |
| picked_at | INTEGER |  |  |
| finished_at | INTEGER |  |  |

## guide_claims — 32 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| player_id | TEXT | да | PK → players.id |
| task_id | TEXT | да | PK |
| claimed_at | INTEGER | да |  |

## guide_prefs — 16 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| player_id | TEXT | да | PK → players.id |
| task_id | TEXT | да | PK |
| mode | TEXT | да |  |
| updated_at | INTEGER | да |  |

## inventory — 2 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| business_id | TEXT | да | PK → businesses.id |
| resource | TEXT | да | PK |
| qty | INTEGER | да |  |

## ledger — 512 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| tx_id | TEXT | да |  |
| account_id | TEXT | да |  → accounts.id |
| delta | INTEGER | да |  |
| reason | TEXT | да |  |
| ref | TEXT |  |  |
| created_at | INTEGER | да |  |

## loan_payments — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| key | TEXT |  | PK |
| loan_id | TEXT | да |  → loans.id |
| due | INTEGER | да |  |
| paid | INTEGER | да |  |
| created_at | INTEGER | да |  |

## loans — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | TEXT |  | PK |
| player_id | TEXT | да |  → players.id |
| principal | INTEGER | да |  |
| remaining | INTEGER | да |  |
| rate_bps | INTEGER | да |  |
| term_days | INTEGER | да |  |
| overdue | INTEGER | да |  |
| status | TEXT | да |  |
| created_at | INTEGER | да |  |
| updated_at | INTEGER | да |  |

## parcels — 19 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | TEXT |  | PK |
| city_id | TEXT | да |  |
| owner_id | TEXT |  |  → players.id |
| price | INTEGER | да |  |
| bought_at | INTEGER |  |  |

## pc_actions — 146 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | TEXT |  | PK |
| owner_id | TEXT | да |  |
| created_at | INTEGER | да |  |

## pc_cities — 1 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| owner_id | TEXT |  | PK |
| nickname | TEXT | да |  |
| data | TEXT | да |  |
| population | INTEGER | да |  |
| level | INTEGER | да |  |
| revision | INTEGER | да |  |
| last_at | INTEGER | да |  |
| created_at | INTEGER | да |  |

## player_energy — 2 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| player_id | TEXT |  | PK → players.id |
| energy | REAL | да |  |
| at | INTEGER | да |  |

## player_meta — 4 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| player_id | TEXT |  | PK → players.id |
| phone | TEXT | да |  |
| daily_at | INTEGER | да |  |
| streak | INTEGER | да |  |
| created_at | INTEGER | да |  |

## players — 4 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | TEXT | да | PK |
| nickname | TEXT | да |  |
| nick_key | TEXT | да |  |
| color | TEXT | да |  |
| money | INTEGER | да |  |
| xp | INTEGER | да |  |
| quest | INTEGER | да |  |
| items | TEXT | да |  |
| choices | TEXT | да |  |
| love | INTEGER | да |  |
| self | INTEGER | да |  |
| house | INTEGER | да |  |
| revision | INTEGER | да |  |
| x | REAL | да |  |
| z | REAL | да |  |
| angle | REAL | да |  |
| last_seen | INTEGER | да |  |
| last_action | INTEGER | да |  |
| job_at | INTEGER | да |  |
| ready_at | INTEGER | да |  |
| work_quest | TEXT |  |  |
| emote | TEXT |  |  |
| emote_until | INTEGER | да |  |
| created_at | INTEGER | да |  |
| reputation | INTEGER | да |  |
| plot | INTEGER | да |  |
| training | INTEGER | да |  |
| harvest_at | INTEGER | да |  |
| zone | TEXT | да |  |
| laptop | INTEGER | да |  |
| furniture | TEXT | да |  |
| desktop | TEXT | да |  |
| profession | TEXT | да |  |
| council_at | INTEGER | да |  |
| cash | INTEGER | да |  |
| bank | INTEGER | да |  |
| appearance | TEXT | да |  |

## projects — 1 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | TEXT | да | PK |
| owner_id | TEXT | да |  → players.id |
| title | TEXT | да |  |
| code | TEXT | да |  |
| revision | INTEGER | да |  |
| updated_at | INTEGER | да |  |

## service_jobs — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | TEXT | да | PK |
| player_id | TEXT | да |  → players.id |
| site | TEXT | да |  |
| role | TEXT | да |  |
| stage | INTEGER | да |  |
| ready_at | INTEGER | да |  |
| expires_at | INTEGER | да |  |
| status | TEXT | да |  |
| pay | INTEGER | да |  |
| earned | INTEGER | да |  |
| created_at | INTEGER | да |  |
| finished_at | INTEGER |  |  |

## shop_prices — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| business_id | TEXT | да | PK → businesses.id |
| resource | TEXT | да | PK |
| price | INTEGER | да |  |
| carry | REAL | да |  |

## stock_ledger — 12 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| warehouse | TEXT | да |  |
| resource | TEXT | да |  |
| delta | INTEGER | да |  |
| tx_id | TEXT | да |  |
| reason | TEXT | да |  |
| created_at | INTEGER | да |  |

## stock_policies — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| business_id | TEXT | да | PK → businesses.id |
| resource | TEXT | да | PK |
| target | INTEGER | да |  |

## supply_events — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| order_id | TEXT | да |  → supply_orders.id |
| actor_id | TEXT | да |  |
| status | TEXT | да |  |
| created_at | INTEGER | да |  |

## supply_offers — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| business_id | TEXT | да | PK → businesses.id |
| resource | TEXT | да | PK |
| price | INTEGER | да |  |
| active | INTEGER | да |  |
| updated_at | INTEGER | да |  |

## supply_orders — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | TEXT |  | PK |
| from_id | TEXT | да |  → businesses.id |
| to_id | TEXT | да |  → businesses.id |
| buyer_id | TEXT | да |  → players.id |
| resource | TEXT | да |  |
| qty | INTEGER | да |  |
| unit_price | INTEGER | да |  |
| freight | INTEGER | да |  |
| tax | INTEGER | да |  |
| tax_bps | INTEGER | да |  |
| distance | INTEGER | да |  |
| escrow_id | TEXT | да |  → accounts.id |
| courier_id | TEXT |  |  → players.id |
| status | TEXT | да |  |
| version | INTEGER | да |  |
| created_at | INTEGER | да |  |
| updated_at | INTEGER | да |  |

## tax_charges — 1 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| key | TEXT |  | PK |
| player_id | TEXT | да |  → players.id |
| amount | INTEGER | да |  |
| paid | INTEGER | да |  |
| created_at | INTEGER | да |  |
| paid_at | INTEGER |  |  |

## wallet_movements — 10 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | TEXT |  | PK |
| player_id | TEXT | да |  |
| delta | INTEGER | да |  |
| created_at | INTEGER | да |  |

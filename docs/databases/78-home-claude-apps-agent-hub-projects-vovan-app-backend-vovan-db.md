# /home/claude/apps/agent-hub/projects/vovan-app/backend/vovan.db (сервер 78, sqlite)

Проект: Vovan App. Размер: 648.0 КБ.

## activity_log — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| user_id | INTEGER | да |  |
| event_type | TEXT | да |  |
| description | TEXT |  |  |
| coins_delta | INTEGER |  |  |
| created_at | TEXT |  |  |

## app_access — 7 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| user_id | INTEGER | да |  → users.user_id |
| app_key | TEXT | да |  |
| granted_by | INTEGER |  |  |
| granted_at | TEXT |  |  |

## app_settings — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| key | TEXT |  | PK |
| value | TEXT | да |  |
| updated_at | TIMESTAMP |  |  |

## apps — 7 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| key | TEXT | да |  |
| name | TEXT | да |  |
| description | TEXT |  |  |
| icon | TEXT |  |  |
| price | INTEGER |  |  |
| is_active | INTEGER |  |  |
| sort_order | INTEGER |  |  |

## bunker_players — 6 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| room_id | INTEGER | да |  |
| user_id | INTEGER | да |  |
| display_name | TEXT | да |  |
| avatar | TEXT |  |  |
| card | TEXT |  |  |
| is_alive | INTEGER |  |  |
| action_used | INTEGER |  |  |
| joined_at | TIMESTAMP |  |  |

## bunker_rooms — 2 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| code | TEXT | да |  |
| name | TEXT | да |  |
| host_id | INTEGER | да |  |
| status | TEXT |  |  |
| phase | INTEGER |  |  |
| catastrophe | TEXT |  |  |
| bunker_capacity | INTEGER |  |  |
| bunker_years | INTEGER |  |  |
| is_public | INTEGER |  |  |
| events_log | TEXT |  |  |
| shield_active | INTEGER |  |  |
| game_mode | TEXT |  |  |
| win_condition | TEXT |  |  |
| bunker_cards | TEXT |  |  |
| active_player_idx | INTEGER |  |  |
| created_at | TIMESTAMP |  |  |

## bunker_votes — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| room_id | INTEGER | да |  |
| phase | INTEGER | да |  |
| voter_id | INTEGER | да |  |
| target_id | INTEGER | да |  |

## changelog_wishes — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| version | TEXT | да |  |
| text | TEXT | да |  |
| created_at | INTEGER |  |  |

## channel_messages — 2 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| channel_id | INTEGER | да |  → server_channels.id |
| user_id | INTEGER | да |  → users.user_id |
| text | TEXT | да |  |
| created_at | TEXT |  |  |
| pinned | INTEGER |  |  |
| media_url | TEXT |  |  |
| media_type | TEXT |  |  |
| file_name | TEXT |  |  |

## chat_settings — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| user_id | INTEGER |  | PK |
| chat_id | INTEGER |  | PK |
| muted | INTEGER |  |  |
| tg_notifications | INTEGER |  |  |

## coin_transactions — 36 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| user_id | INTEGER | да |  |
| amount | INTEGER | да |  |
| balance_after | INTEGER | да |  |
| tx_type | TEXT | да |  |
| description | TEXT | да |  |
| by_user_id | INTEGER |  |  |
| is_flagged | INTEGER |  |  |
| created_at | TEXT |  |  |

## cosmetics — 30 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| type | TEXT | да |  |
| name | TEXT | да |  |
| description | TEXT |  |  |
| rarity | INTEGER |  |  |
| unlock_type | TEXT |  |  |
| unlock_value | INTEGER |  |  |
| config | TEXT |  |  |
| preview_color | TEXT |  |  |
| sort_order | INTEGER |  |  |

## daily_poll_votes — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| poll_id | INTEGER | да |  → daily_polls.id |
| user_id | INTEGER | да |  |
| option_idx | INTEGER | да |  |
| voted_at | TEXT |  |  |

## daily_polls — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| question | TEXT | да |  |
| options_json | TEXT | да |  |
| poll_date | TEXT | да |  |
| created_by | INTEGER |  |  |
| created_at | TEXT |  |  |

## daily_task_completions — 34 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| user_id | INTEGER | да |  |
| task_def_id | INTEGER | да |  |
| completed_date | TEXT | да |  |
| completed_at | TIMESTAMP |  |  |

## daily_task_defs — 5 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| title | TEXT | да |  |
| description | TEXT |  |  |
| reward_coins | INTEGER |  |  |
| task_type | TEXT |  |  |
| icon | TEXT |  |  |
| is_active | INTEGER |  |  |

## dm_reactions — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| message_id | INTEGER | да |  |
| user_id | INTEGER | да |  |
| emoji | TEXT | да |  |
| created_at | TIMESTAMP |  |  |

## email_verifications — 5 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| email | TEXT | да |  |
| code | TEXT | да |  |
| purpose | TEXT |  |  |
| username | TEXT |  |  |
| display_name | TEXT |  |  |
| password_hash | TEXT |  |  |
| attempts | INTEGER |  |  |
| expires_at | TEXT | да |  |
| consumed_at | TEXT |  |  |
| created_at | TEXT |  |  |

## event_rsvp — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| user_id | INTEGER | да | PK |
| event_id | INTEGER | да | PK |
| status | TEXT | да |  |

## follows — 3 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| follower_id | INTEGER | да | PK |
| following_id | INTEGER | да | PK |
| created_at | TIMESTAMP |  |  |

## gifts — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| name | TEXT | да |  |
| description | TEXT |  |  |
| image_url | TEXT |  |  |
| category | TEXT |  |  |
| rarity | INTEGER |  |  |
| cost | INTEGER | да |  |
| created_at | TIMESTAMP |  |  |
| model_url | TEXT |  |  |

## group_events — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| creator_id | INTEGER | да |  → users.user_id |
| group_id | INTEGER |  |  |
| title | TEXT | да |  |
| description | TEXT |  |  |
| location | TEXT |  |  |
| event_date | TEXT | да |  |
| event_time | TEXT |  |  |
| created_at | TIMESTAMP |  |  |

## group_members — 18 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| group_id | INTEGER | да |  → groups.id |
| user_id | INTEGER | да |  → users.user_id |
| role | TEXT |  |  |
| joined_at | TIMESTAMP |  |  |

## group_read_positions — 6 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| user_id | INTEGER | да | PK |
| group_id | INTEGER | да | PK |
| last_read_msg_id | INTEGER |  |  |

## groups — 7 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| name | TEXT | да |  |
| description | TEXT |  |  |
| avatar | TEXT |  |  |
| slug | TEXT |  |  |
| type | TEXT | да |  |
| password | TEXT |  |  |
| created_by | INTEGER | да |  → users.user_id |
| created_at | TIMESTAMP |  |  |
| is_server | INTEGER |  |  |
| color | TEXT |  |  |
| invite_token | TEXT |  |  |
| is_channel | INTEGER |  |  |

## habit_logs — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| habit_id | INTEGER | да |  → habits.id |
| user_id | INTEGER | да |  |
| log_date | TEXT | да |  |

## habits — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| user_id | INTEGER | да |  → users.user_id |
| title | TEXT | да |  |
| emoji | TEXT |  |  |
| color | TEXT |  |  |
| created_at | TEXT |  |  |

## mafia_game_log — 18 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| room_id | INTEGER | да |  |
| round_number | INTEGER |  |  |
| phase | TEXT | да |  |
| event_type | TEXT | да |  |
| actor_id | INTEGER |  |  |
| target_id | INTEGER |  |  |
| data | TEXT |  |  |
| created_at | TIMESTAMP |  |  |

## mafia_players — 4 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| room_id | INTEGER | да |  |
| user_id | INTEGER | да |  |
| display_name | TEXT | да |  |
| avatar | TEXT |  |  |
| role | TEXT |  |  |
| team | TEXT |  |  |
| is_alive | INTEGER |  |  |
| is_muted | INTEGER |  |  |
| is_speaking_allowed | INTEGER |  |  |
| night_action_done | INTEGER |  |  |
| night_action_target | INTEGER |  |  |
| night_blocked | INTEGER |  |  |
| death_night | INTEGER |  |  |
| joined_at | TIMESTAMP |  |  |

## mafia_rooms — 4 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| code | TEXT | да |  |
| name | TEXT | да |  |
| host_id | INTEGER | да |  |
| voice_mode | TEXT |  |  |
| status | TEXT |  |  |
| phase | TEXT |  |  |
| night_number | INTEGER |  |  |
| day_number | INTEGER |  |  |
| current_acting_role | TEXT |  |  |
| settings | TEXT |  |  |
| is_public | INTEGER |  |  |
| created_at | TIMESTAMP |  |  |

## mafia_votes — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| room_id | INTEGER | да |  |
| voter_id | INTEGER | да |  |
| target_id | INTEGER | да |  |
| day_number | INTEGER | да |  |
| created_at | TIMESTAMP |  |  |

## message_reactions — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| message_id | INTEGER | да |  |
| user_id | INTEGER | да |  |
| emoji | TEXT | да |  |
| created_at | TIMESTAMP |  |  |

## messages — 1 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| group_id | INTEGER |  |  → groups.id |
| user_id | INTEGER | да |  → users.user_id |
| text | TEXT | да |  |
| created_at | TIMESTAMP |  |  |
| attachment_type | TEXT |  |  |
| attachment_url | TEXT |  |  |
| attachment_data | TEXT |  |  |

## permissions — 24 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| key | TEXT | да |  |
| name | TEXT | да |  |
| category | TEXT | да |  |
| description | TEXT |  |  |
| level | INTEGER |  |  |

## poll_options — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| poll_id | INTEGER | да |  → polls.id |
| text | TEXT | да |  |

## poll_votes — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| poll_id | INTEGER | да |  → polls.id |
| option_id | INTEGER | да |  → poll_options.id |
| user_id | INTEGER | да |  |

## polls — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| group_id | INTEGER |  |  |
| message_id | INTEGER |  |  |
| question | TEXT | да |  |
| created_by | INTEGER | да |  |
| created_at | TIMESTAMP |  |  |

## post_comments — 2 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| post_id | INTEGER | да |  |
| author_id | INTEGER | да |  |
| text | TEXT | да |  |
| created_at | TEXT |  |  |
| is_deleted | INTEGER |  |  |

## post_likes — 3 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| post_id | INTEGER | да | PK |
| user_id | INTEGER | да | PK |
| liked_at | TEXT |  |  |

## post_reactions — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| post_id | INTEGER | да |  |
| user_id | INTEGER | да |  |
| emoji | TEXT | да |  |
| created_at | TEXT |  |  |

## posts — 2 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| author_id | INTEGER | да |  |
| text | TEXT |  |  |
| image_url | TEXT |  |  |
| created_at | TEXT |  |  |
| likes_count | INTEGER |  |  |
| is_deleted | INTEGER |  |  |
| is_pinned | INTEGER |  |  |
| moderation_status | TEXT |  |  |
| comments_count | INTEGER |  |  |
| images | TEXT |  |  |
| action_buttons | TEXT |  |  |
| poll_id | INTEGER |  |  |
| video_url | TEXT |  |  |

## private_chats — 5 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| user1_id | INTEGER | да |  |
| user2_id | INTEGER | да |  |
| created_at | TIMESTAMP |  |  |

## private_messages — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| chat_id | INTEGER | да |  → private_chats.id |
| sender_id | INTEGER | да |  |
| text | TEXT |  |  |
| is_read | INTEGER |  |  |
| attachment_type | TEXT |  |  |
| attachment_url | TEXT |  |  |
| attachment_data | TEXT |  |  |
| created_at | TIMESTAMP |  |  |

## profile_customization — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| user_id | INTEGER |  | PK |
| bio | TEXT |  |  |
| status | TEXT |  |  |
| accent_color | TEXT |  |  |
| updated_at | TIMESTAMP |  |  |

## role_permissions — 6 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| role_id | INTEGER |  | PK → roles.id |
| perm_key | TEXT |  | PK → permissions.key |

## roles — 2 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| name | TEXT | да |  |
| emoji | TEXT | да |  |
| color | TEXT | да |  |
| description | TEXT |  |  |
| created_at | TIMESTAMP |  |  |

## server_bans — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| server_id | INTEGER | да | PK |
| user_id | INTEGER | да | PK |
| banned_by | INTEGER | да |  |
| reason | TEXT |  |  |
| banned_at | DATETIME |  |  |

## server_categories — 8 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| server_id | INTEGER | да |  → groups.id |
| name | TEXT | да |  |
| position | INTEGER |  |  |

## server_channels — 14 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| server_id | INTEGER | да |  → groups.id |
| category_id | INTEGER |  |  → server_categories.id |
| name | TEXT | да |  |
| type | TEXT |  |  |
| position | INTEGER |  |  |
| created_at | TEXT |  |  |

## server_invites — 6 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| code | TEXT | да |  |
| server_id | INTEGER | да |  → groups.id |
| created_by | INTEGER | да |  |
| max_uses | INTEGER |  |  |
| uses | INTEGER |  |  |
| expires_at | TEXT |  |  |
| created_at | TEXT |  |  |

## server_member_roles — 11 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| server_id | INTEGER | да |  → groups.id |
| user_id | INTEGER | да |  |
| role_id | INTEGER | да |  → server_roles.id |

## server_poll_options — 2 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| poll_id | INTEGER | да |  |
| text | TEXT | да |  |
| emoji | TEXT |  |  |
| position | INTEGER |  |  |

## server_poll_votes — 1 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| poll_id | INTEGER | да | PK |
| option_id | INTEGER | да | PK |
| user_id | INTEGER | да | PK |
| voted_at | DATETIME |  |  |

## server_polls — 1 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| channel_id | INTEGER | да |  |
| user_id | INTEGER | да |  |
| question | TEXT | да |  |
| multi_answer | INTEGER |  |  |
| expires_at | DATETIME |  |  |
| created_at | DATETIME |  |  |

## server_roles — 12 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| server_id | INTEGER | да |  → groups.id |
| name | TEXT | да |  |
| color | TEXT |  |  |
| is_owner | INTEGER |  |  |
| is_admin | INTEGER |  |  |
| can_manage_channels | INTEGER |  |  |
| can_manage_members | INTEGER |  |  |
| can_send_messages | INTEGER |  |  |
| position | INTEGER |  |  |
| can_view_channels | INTEGER |  |  |
| can_manage_roles | INTEGER |  |  |
| can_view_audit_log | INTEGER |  |  |
| can_manage_server | INTEGER |  |  |
| can_create_invite | INTEGER |  |  |
| can_change_nickname | INTEGER |  |  |
| can_manage_nicknames | INTEGER |  |  |
| can_kick_members | INTEGER |  |  |
| can_ban_members | INTEGER |  |  |
| can_timeout_members | INTEGER |  |  |
| can_upload_media | INTEGER |  |  |
| can_send_in_threads | INTEGER |  |  |
| can_create_public_threads | INTEGER |  |  |
| can_create_private_threads | INTEGER |  |  |
| can_embed_links | INTEGER |  |  |
| can_add_reactions | INTEGER |  |  |
| can_use_external_emojis | INTEGER |  |  |
| can_use_external_stickers | INTEGER |  |  |
| can_mention_everyone | INTEGER |  |  |
| can_manage_messages | INTEGER |  |  |
| can_pin_messages | INTEGER |  |  |
| can_bypass_slowmode | INTEGER |  |  |
| can_manage_threads | INTEGER |  |  |
| can_read_message_history | INTEGER |  |  |
| can_send_tts | INTEGER |  |  |
| can_send_voice_messages | INTEGER |  |  |
| can_create_polls | INTEGER |  |  |
| is_displayed_separately | INTEGER |  |  |
| is_mentionable | INTEGER |  |  |

## server_timeouts — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| server_id | INTEGER | да | PK |
| user_id | INTEGER | да | PK |
| timed_out_by | INTEGER | да |  |
| expires_at | DATETIME | да |  |
| reason | TEXT |  |  |

## sessions — 29 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| token | TEXT |  | PK |
| user_id | INTEGER | да |  |
| created_at | TEXT |  |  |
| expires_at | TEXT |  |  |
| user_agent | TEXT |  |  |
| revoked | INTEGER |  |  |

## stream_rsvp — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| stream_id | INTEGER | да |  → streams.id |
| user_id | INTEGER | да |  |
| rsvped_at | TEXT |  |  |

## streams — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| title | TEXT | да |  |
| description | TEXT |  |  |
| platform | TEXT |  |  |
| stream_url | TEXT |  |  |
| starts_at | TEXT | да |  |
| created_by | INTEGER |  |  |
| is_cancelled | INTEGER |  |  |
| created_at | TEXT |  |  |

## system_messages — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| text | TEXT | да |  |
| sent_by | INTEGER |  |  |
| sent_at | TIMESTAMP |  |  |

## user_cosmetics — 6 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| user_id | INTEGER | да |  |
| cosmetic_id | INTEGER | да |  |
| acquired_at | TIMESTAMP |  |  |

## user_equipped — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| user_id | INTEGER |  | PK |
| frame_id | INTEGER |  |  |
| name_color_id | INTEGER |  |  |
| badge_id | INTEGER |  |  |
| theme_id | INTEGER |  |  |

## user_gifts — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| user_id | INTEGER | да |  → users.user_id |
| gift_id | INTEGER | да |  → gifts.id |
| received_at | TIMESTAMP |  |  |

## user_notes — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| user_id | INTEGER | да |  → users.user_id |
| title | TEXT | да |  |
| content | TEXT |  |  |
| tags | TEXT |  |  |
| pinned | INTEGER |  |  |
| created_at | TIMESTAMP |  |  |
| updated_at | TIMESTAMP |  |  |

## user_notification_reads — 3 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| user_id | INTEGER |  | PK |
| last_read_at | TEXT |  |  |

## user_permission_overrides — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| user_id | INTEGER | да | PK |
| perm_key | TEXT |  | PK → permissions.key |
| enabled | INTEGER | да |  |

## user_privacy_settings — 3 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| user_id | INTEGER |  | PK |
| phone_visibility | TEXT |  |  |
| last_seen | TEXT |  |  |
| profile_photo | TEXT |  |  |
| bio_visibility | TEXT |  |  |
| forwards | TEXT |  |  |
| calls | TEXT |  |  |
| messages | TEXT |  |  |
| gifts | TEXT |  |  |
| birthday | TEXT |  |  |
| birthday_visibility | TEXT |  |  |
| updated_at | TIMESTAMP |  |  |
| discoverable | INTEGER |  |  |
| show_in_leaderboard | INTEGER |  |  |
| search_by_username | INTEGER |  |  |

## user_roles — 1 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| user_id | INTEGER |  | PK → users.user_id |
| role_id | INTEGER | да |  → roles.id |
| assigned_at | TIMESTAMP |  |  |
| assigned_by | INTEGER |  |  |

## user_settings — 1 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| user_id | INTEGER |  | PK → users.user_id |
| tg_notifications | INTEGER |  |  |
| sound_vibration | INTEGER |  |  |
| quiet_start | TEXT |  |  |
| quiet_end | TEXT |  |  |
| keywords | TEXT |  |  |
| notify_channel_sub | INTEGER |  |  |

## user_streaks — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| user_id | INTEGER |  | PK |
| streak | INTEGER |  |  |
| last_task_date | TEXT |  |  |

## user_tasks — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| user_id | INTEGER | да |  → users.user_id |
| title | TEXT | да |  |
| description | TEXT |  |  |
| due_date | TEXT |  |  |
| due_time | TEXT |  |  |
| priority | INTEGER |  |  |
| done | INTEGER |  |  |
| repeat | TEXT |  |  |
| created_at | TIMESTAMP |  |  |

## user_xp — 13 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| user_id | INTEGER |  | PK |
| total_xp | INTEGER | да |  |
| level | INTEGER | да |  |
| updated_at | TEXT |  |  |

## users — 15 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| user_id | INTEGER |  | PK |
| username | TEXT |  |  |
| first_name | TEXT |  |  |
| balance | INTEGER |  |  |
| profile_image | TEXT |  |  |
| rank | TEXT |  |  |
| joined_at | TIMESTAMP |  |  |
| is_deleted | INTEGER |  |  |
| deleted_at | TEXT |  |  |
| email | TEXT |  |  |
| password_hash | TEXT |  |  |
| auth_source | TEXT |  |  |
| last_active | TEXT |  |  |
| boosted | INTEGER |  |  |
| banned | INTEGER |  |  |
| is_hidden | INTEGER |  |  |
| boost_expires | TEXT |  |  |
| showcase_gifts | TEXT |  |  |
| email_verified | INTEGER |  |  |
| email_verified_at | TEXT |  |  |
| messages | INTEGER |  |  |
| last_earn | INTEGER |  |  |
| shorts_enabled | INTEGER |  |  |

## video_likes — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| video_id | INTEGER | да |  |
| user_id | INTEGER | да |  |
| created_at | TEXT |  |  |

## video_variants — 5 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| video_id | INTEGER | да |  → videos.id |
| quality | TEXT | да |  |
| height | INTEGER | да |  |
| hls_url | TEXT |  |  |
| file_size | INTEGER |  |  |
| status | TEXT |  |  |
| created_at | TEXT |  |  |

## video_views — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| video_id | INTEGER | да |  |
| user_id | INTEGER | да |  |
| watched_at | TEXT |  |  |

## videos — 2 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| user_id | INTEGER | да |  |
| title | TEXT |  |  |
| description | TEXT |  |  |
| original_url | TEXT |  |  |
| thumbnail_url | TEXT |  |  |
| duration | REAL |  |  |
| width | INTEGER |  |  |
| height | INTEGER |  |  |
| file_size | INTEGER |  |  |
| status | TEXT |  |  |
| source | TEXT |  |  |
| created_at | TEXT |  |  |
| likes_count | INTEGER |  |  |
| views_count | INTEGER |  |  |
| is_deleted | INTEGER |  |  |

## weekly_task_completions — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| user_id | INTEGER | да |  |
| task_id | INTEGER | да |  |
| week_key | TEXT | да |  |
| completed_at | TEXT |  |  |

## weekly_tasks — 0 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| title | TEXT | да |  |
| description | TEXT |  |  |
| icon | TEXT |  |  |
| reward_coins | INTEGER |  |  |
| task_type | TEXT |  |  |
| is_active | INTEGER |  |  |

## xp_log — 37 строк

| Поле | Тип | Обязательное | Ключ |
|---|---|---|---|
| id | INTEGER |  | PK |
| user_id | INTEGER | да |  |
| amount | INTEGER | да |  |
| reason | TEXT | да |  |
| created_at | TEXT |  |  |

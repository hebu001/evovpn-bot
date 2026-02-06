
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

#############################
# 1. Переменная "row_width" отвечает за количество кнопок в ряду.
# 2. .add(*buttons) добавит кнопки, автоматически раскладывая по рядам согласно row_width.
# 3. Чтобы намеренно разместить кнопки в одной строке, передайте их одной группой в .add().
#############################

# Стартовое меню (перенос с ReplyKeyboardMarkup)
async def fun_klav_start(user, NAME_VPN_CONFIG):
    klav = InlineKeyboardMarkup(row_width=2)  # теперь по 2 кнопки в ряд

    if not user.isGetTestKey:
        klav.add(
            InlineKeyboardButton(
                text=user.lang.get('but_test_key'),
                callback_data='buttons:but_test_key'
            )
        )

    klav.add(
        InlineKeyboardButton(text=user.lang.get('but_my_keys'), callback_data='buttons:but_my_keys'),
        InlineKeyboardButton(text=user.lang.get('but_connect'), callback_data='buttons:but_connect'),
        InlineKeyboardButton(text=user.lang.get('but_change_location'), callback_data='buttons:but_change_location'),
        InlineKeyboardButton(text=user.lang.get('but_ref'), callback_data='buttons:but_ref'),
        InlineKeyboardButton(text=user.lang.get('but_partner'), callback_data='buttons:but_partner'),
        InlineKeyboardButton(text=user.lang.get('but_help'), callback_data='buttons:but_help'),
    )

    return klav

# Покупка дней
async def fun_klav_buy_days(user):
    klav = InlineKeyboardMarkup(row_width=1)
    for button in user.buttons_days:
        klav.add(InlineKeyboardButton(text=button, callback_data=f'buttons:{button}:znach'))
    klav.add(InlineKeyboardButton(text=user.lang.get('but_back_main'), callback_data='buttons:but_main'))
    return klav

# Описание/о нас
async def fun_klav_desription(user, but_instagram):
    # Оригинал: row_width=1, порядок: but_tarif -> (but_pravila_sogl, but_pravila_politic, but_pravila_refaund) -> instagram -> but_main
    klav = InlineKeyboardMarkup(row_width=1)
    klav.add(InlineKeyboardButton(text=user.lang.get('but_tarif'), callback_data='buttons:but_tarif'))
    klav2 = InlineKeyboardMarkup(row_width=3)  # локальная укладка в одну строку из трёх, как в исходнике через одну .add(...)
    
    # Но InlineKeyboardMarkup не комбинируется, поэтому просто добавим тремя в один .add на основном klav
    klav.add(
        InlineKeyboardButton(text=user.lang.get('but_pravila_sogl'), callback_data='buttons:but_pravila_sogl'),
        InlineKeyboardButton(text=user.lang.get('but_pravila_politic'), callback_data='buttons:but_pravila_politic'),
        InlineKeyboardButton(text=user.lang.get('but_pravila_refaund'), callback_data='buttons:but_pravila_refaund'),
    )
    klav.add(InlineKeyboardButton(text=but_instagram, callback_data='buttons:but_instagram'))
    klav.add(InlineKeyboardButton(text=user.lang.get('but_back_main'), callback_data='buttons:but_main'))
    return klav

# Опрос
async def fun_klav_opros(user):
    # Оригинал: row_width=2, две кнопки в один ряд + main
    klav = InlineKeyboardMarkup(row_width=2)
    klav.add(
        InlineKeyboardButton(text=user.lang.get('but_opros_super'), callback_data='buttons:but_opros_super'),
        InlineKeyboardButton(text=user.lang.get('but_opros_good'), callback_data='buttons:but_opros_good'),
    )
    klav.add(InlineKeyboardButton(text=user.lang.get('but_back_main'), callback_data='buttons:but_main'))
    return klav

# Промокоды/продление
async def fun_klav_promo(user):
    # Оригинал: по одному в строке, затем main
    klav = InlineKeyboardMarkup(row_width=1)
    klav.add(InlineKeyboardButton(text=user.lang.get('but_create_key'), callback_data='buttons:but_create_key'))
    klav.add(InlineKeyboardButton(text=user.lang.get('but_prodlit_key'), callback_data='buttons:but_prodlit_key'))
    klav.add(InlineKeyboardButton(text=user.lang.get('but_back_main'), callback_data='buttons:but_main'))
    return klav

# Отмена платежа
async def fun_klav_cancel_pay(user):
    klav = InlineKeyboardMarkup(row_width=1)
    klav.add(InlineKeyboardButton(text=user.lang.get('but_cancel_pay'), callback_data='buttons:but_cancel_pay'))
    return klav

# Подключение (список вариантов + назад/в меню)
async def fun_klav_podkl(user, buttons_podkl):
    klav = InlineKeyboardMarkup(row_width=3)
    for button in buttons_podkl:
        klav.add(InlineKeyboardButton(text=button, callback_data=f'buttons:{button}:znach'))
    klav.add(
        InlineKeyboardButton(text=user.lang.get('but_back_help'), callback_data='buttons:but_back_help'),
        InlineKeyboardButton(text=user.lang.get('but_main'), callback_data='buttons:but_main'),
    )
    return klav

# Как установить (по наличию флагов)
async def fun_klav_how_install(user, HELP_VLESS, HELP_WIREGUARD, HELP_OUTLINE, HELP_PPTP):
    klav = InlineKeyboardMarkup(row_width=2)
    if HELP_VLESS:
        klav.add(InlineKeyboardButton(text=user.lang.get('but_how_podkl_vless'), callback_data='buttons:but_how_podkl_vless'))
    if HELP_WIREGUARD:
        klav.add(InlineKeyboardButton(text=user.lang.get('but_how_podkl_WG'), callback_data='buttons:but_how_podkl_WG'))
    if HELP_OUTLINE:
        klav.add(InlineKeyboardButton(text=user.lang.get('but_how_podkl_Outline'), callback_data='buttons:but_how_podkl_Outline'))
    if HELP_PPTP:
        klav.add(InlineKeyboardButton(text=user.lang.get('but_how_podkl_pptp'), callback_data='buttons:but_how_podkl_pptp'))
    klav.add(InlineKeyboardButton(text=user.lang.get('but_back_help'), callback_data='buttons:but_back_help'))
    return klav

# Выбор протокола
async def fun_klav_select_protocol(user, PR_VLESS, PR_WIREGUARD, PR_OUTLINE, PR_PPTP):
    klav = InlineKeyboardMarkup(row_width=2)
    if PR_VLESS:
        klav.add(InlineKeyboardButton(text=user.lang.get('but_select_vless'), callback_data='buttons:but_select_vless'))
    if PR_WIREGUARD:
        klav.add(InlineKeyboardButton(text=user.lang.get('but_select_WG'), callback_data='buttons:but_select_WG'))
    if PR_OUTLINE:
        klav.add(InlineKeyboardButton(text=user.lang.get('but_select_Outline'), callback_data='buttons:but_select_Outline'))
    if PR_PPTP:
        klav.add(InlineKeyboardButton(text=user.lang.get('but_select_pptp'), callback_data='buttons:but_select_pptp'))
    klav.add(InlineKeyboardButton(text=user.lang.get('but_back_main'), callback_data='buttons:but_main'))
    return klav

# Подключение без кнопки "назад"
async def fun_klav_podkl_no_back(user, buttons_podkl):
    klav = InlineKeyboardMarkup(row_width=3)
    for button in buttons_podkl:
        klav.add(InlineKeyboardButton(text=button, callback_data=f'buttons:{button}:znach'))
    klav.add(InlineKeyboardButton(text=user.lang.get('but_back_main'), callback_data='buttons:but_my_keys'))
    return klav

# Помощь
async def fun_klav_help(user):
    # Оригинал: row_width=1; две правовые в одну .add(...)
    klav = InlineKeyboardMarkup(row_width=1)
    klav.add(InlineKeyboardButton(text=user.lang.get('but_change_app'), callback_data=f'buttons:but_change_app'))
    klav.add(InlineKeyboardButton(text=user.lang.get('but_how_podkl'), callback_data='buttons:but_how_podkl'))
    klav.add(InlineKeyboardButton(text=user.lang.get('but_no_work_vpn'), callback_data='buttons:but_no_work_vpn'))
    klav.add(InlineKeyboardButton(text=user.lang.get('but_manager'), callback_data='buttons:but_manager'))
    klav.add(
        InlineKeyboardButton(text=user.lang.get('but_polz_sogl'), callback_data='buttons:but_polz_sogl'),
        InlineKeyboardButton(text=user.lang.get('but_pravila'), callback_data='buttons:but_pravila'),
    )
    klav.add(InlineKeyboardButton(text=user.lang.get('but_back_main'), callback_data='buttons:but_main'))
    return klav

# Донаты
async def fun_klav_donats(user):
    klav = InlineKeyboardMarkup(row_width=3)
    for button in user.buttons_Donate:
        klav.add(InlineKeyboardButton(text=button, callback_data=f'buttons:{button}:znach'))
    klav.add(
        InlineKeyboardButton(text=user.lang.get('but_donaters'), callback_data='buttons:but_donaters'),
        InlineKeyboardButton(text=user.lang.get('but_back_main'), callback_data='buttons:but_main'),
    )
    return klav

# Продление/новый ключ
async def fun_klav_buy_ustr(user):
    klav = InlineKeyboardMarkup(row_width=1)
    klav.add(InlineKeyboardButton(text=user.lang.get('but_prodlit'), callback_data='buttons:but_prodlit'))
    klav.add(InlineKeyboardButton(text=user.lang.get('but_new_key'), callback_data='buttons:but_new_key'))
    klav.add(InlineKeyboardButton(text=user.lang.get('but_back_main'), callback_data='buttons:but_main'))
    return klav

# Партнёрка
async def fun_klav_partner(user):
    klav = InlineKeyboardMarkup(row_width=1)
    klav.add(InlineKeyboardButton(text=user.lang.get('but_zaprosi'), callback_data='buttons:but_zaprosi'))
    klav.add(InlineKeyboardButton(text=user.lang.get('but_back_main'), callback_data='buttons:but_main'))
    return klav

# Запросы
async def fun_klav_zaprosi(user):
    klav = InlineKeyboardMarkup(row_width=2)
    klav.add(InlineKeyboardButton(text=user.lang.get('but_zaprosi_add'), callback_data='buttons:but_zaprosi_add'))
    klav.add(InlineKeyboardButton(text=user.lang.get('but_partner'), callback_data='buttons:but_partner'))
    return klav

# Оплата смены протокола
async def fun_klav_pay_change_protocol(user):
    klav = InlineKeyboardMarkup(row_width=1)
    klav.add(InlineKeyboardButton(text=user.lang.get('but_pay_change_protocol'), callback_data='buttons:but_pay_change_protocol'))
    klav.add(InlineKeyboardButton(text=user.lang.get('but_back_main'), callback_data='buttons:but_main'))
    return klav

# Смена протокола
async def fun_klav_change_protocol(user):
    klav = InlineKeyboardMarkup(row_width=1)
    klav.add(InlineKeyboardButton(text=user.lang.get('but_change_protocol'), callback_data='buttons:but_change_protocol'))
    klav.add(InlineKeyboardButton(text=user.lang.get('but_back_main'), callback_data='buttons:but_main'))
    return klav

# Оплата смены локаций
async def fun_klav_pay_change_locations(user):
    klav = InlineKeyboardMarkup(row_width=1)
    klav.add(InlineKeyboardButton(text=user.lang.get('but_pay_change_locations'), callback_data='buttons:but_pay_change_locations'))
    klav.add(InlineKeyboardButton(text=user.lang.get('but_back_main'), callback_data='buttons:but_main'))
    return klav

# Смена локаций
async def fun_klav_change_locations(user):
    klav = InlineKeyboardMarkup(row_width=1)
    klav.add(InlineKeyboardButton(text=user.lang.get('but_change_location'), callback_data='buttons:but_change_location'))
    klav.add(InlineKeyboardButton(text=user.lang.get('but_back_main'), callback_data='buttons:but_main'))
    return klav

# Выбор языка (в исходнике уже был Inline)
async def fun_klav_select_languages(LANG):
    klav = InlineKeyboardMarkup(row_width=1)
    for lang in LANG:
        klav.add(InlineKeyboardButton(text=f'🔹{lang}', callback_data=f'lang:{lang}'))
    return klav

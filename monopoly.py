"""
Property Tycoon — game logic (Monopoly-inspired, original content)
All names, board, and card text are original to avoid trademark issues.
"""
import random
import time

# ─── BOARD DEFINITION ──────────────────────────────────────────────────────────
# rent[0] = base rent, rent[1-4] = 1-4 houses, rent[5] = hotel
BOARD = [
    {'pos': 0,  'name': 'Départ',              'type': 'go'},
    {'pos': 1,  'name': 'Rue des Sables',      'type': 'property', 'color': 'brown',  'price': 60,  'rent': [2,  10,  30,  90,  160, 250], 'house_cost': 50,  'mortgage': 30},
    {'pos': 2,  'name': 'Caisse',              'type': 'community_chest'},
    {'pos': 3,  'name': 'Rue du Limon',        'type': 'property', 'color': 'brown',  'price': 60,  'rent': [4,  20,  60,  180, 320, 450], 'house_cost': 50,  'mortgage': 30},
    {'pos': 4,  'name': 'Taxe sur le revenu',  'type': 'tax',      'amount': 200},
    {'pos': 5,  'name': 'Gare du Nord',        'type': 'railway',  'price': 200, 'mortgage': 100},
    {'pos': 6,  'name': 'Rue de l\'Aube',      'type': 'property', 'color': 'cyan',   'price': 100, 'rent': [6,  30,  90,  270, 400, 550], 'house_cost': 50,  'mortgage': 50},
    {'pos': 7,  'name': 'Chance',              'type': 'chance'},
    {'pos': 8,  'name': 'Rue du Brouillard',   'type': 'property', 'color': 'cyan',   'price': 100, 'rent': [6,  30,  90,  270, 400, 550], 'house_cost': 50,  'mortgage': 50},
    {'pos': 9,  'name': 'Rue du Ciel',         'type': 'property', 'color': 'cyan',   'price': 120, 'rent': [8,  40,  100, 300, 450, 600], 'house_cost': 50,  'mortgage': 60},
    {'pos': 10, 'name': 'Prison',              'type': 'jail'},
    {'pos': 11, 'name': 'Rue des Pins',        'type': 'property', 'color': 'pink',   'price': 140, 'rent': [10, 50,  150, 450, 625, 750], 'house_cost': 100, 'mortgage': 70},
    {'pos': 12, 'name': 'Cie Électrique',      'type': 'utility',  'price': 150, 'mortgage': 75},
    {'pos': 13, 'name': 'Rue des Chênes',      'type': 'property', 'color': 'pink',   'price': 140, 'rent': [10, 50,  150, 450, 625, 750], 'house_cost': 100, 'mortgage': 70},
    {'pos': 14, 'name': 'Rue des Érables',     'type': 'property', 'color': 'pink',   'price': 160, 'rent': [12, 60,  180, 500, 700, 900], 'house_cost': 100, 'mortgage': 80},
    {'pos': 15, 'name': 'Gare de l\'Est',      'type': 'railway',  'price': 200, 'mortgage': 100},
    {'pos': 16, 'name': 'Rue des Orangers',    'type': 'property', 'color': 'orange', 'price': 180, 'rent': [14, 70,  200, 550, 750, 950], 'house_cost': 100, 'mortgage': 90},
    {'pos': 17, 'name': 'Caisse',              'type': 'community_chest'},
    {'pos': 18, 'name': 'Rue des Citrons',     'type': 'property', 'color': 'orange', 'price': 180, 'rent': [14, 70,  200, 550, 750, 950], 'house_cost': 100, 'mortgage': 90},
    {'pos': 19, 'name': 'Rue des Mandarines',  'type': 'property', 'color': 'orange', 'price': 200, 'rent': [16, 80,  220, 600, 800, 1000],'house_cost': 100, 'mortgage': 100},
    {'pos': 20, 'name': 'Parc Gratuit',        'type': 'free_parking'},
    {'pos': 21, 'name': 'Rue des Roses',       'type': 'property', 'color': 'red',    'price': 220, 'rent': [18, 90,  250, 700, 875, 1050],'house_cost': 150, 'mortgage': 110},
    {'pos': 22, 'name': 'Chance',              'type': 'chance'},
    {'pos': 23, 'name': 'Rue des Tulipes',     'type': 'property', 'color': 'red',    'price': 220, 'rent': [18, 90,  250, 700, 875, 1050],'house_cost': 150, 'mortgage': 110},
    {'pos': 24, 'name': 'Rue des Dahlias',     'type': 'property', 'color': 'red',    'price': 240, 'rent': [20, 100, 300, 750, 925, 1100],'house_cost': 150, 'mortgage': 120},
    {'pos': 25, 'name': 'Gare du Sud',         'type': 'railway',  'price': 200, 'mortgage': 100},
    {'pos': 26, 'name': 'Rue des Étoiles',     'type': 'property', 'color': 'yellow', 'price': 260, 'rent': [22, 110, 330, 800, 975, 1150],'house_cost': 150, 'mortgage': 130},
    {'pos': 27, 'name': 'Rue de la Lune',      'type': 'property', 'color': 'yellow', 'price': 260, 'rent': [22, 110, 330, 800, 975, 1150],'house_cost': 150, 'mortgage': 130},
    {'pos': 28, 'name': 'Cie des Eaux',        'type': 'utility',  'price': 150, 'mortgage': 75},
    {'pos': 29, 'name': 'Rue du Soleil',       'type': 'property', 'color': 'yellow', 'price': 280, 'rent': [24, 120, 360, 850, 1025, 1200],'house_cost': 150, 'mortgage': 140},
    {'pos': 30, 'name': 'Allez en Prison',     'type': 'go_to_jail'},
    {'pos': 31, 'name': 'Rue des Diamants',    'type': 'property', 'color': 'green',  'price': 300, 'rent': [26, 130, 390, 900, 1100, 1275],'house_cost': 200, 'mortgage': 150},
    {'pos': 32, 'name': 'Rue des Rubis',       'type': 'property', 'color': 'green',  'price': 300, 'rent': [26, 130, 390, 900, 1100, 1275],'house_cost': 200, 'mortgage': 150},
    {'pos': 33, 'name': 'Caisse',              'type': 'community_chest'},
    {'pos': 34, 'name': 'Rue des Émeraudes',   'type': 'property', 'color': 'green',  'price': 320, 'rent': [28, 150, 450, 1000, 1200, 1400],'house_cost': 200, 'mortgage': 160},
    {'pos': 35, 'name': 'Gare de l\'Ouest',    'type': 'railway',  'price': 200, 'mortgage': 100},
    {'pos': 36, 'name': 'Chance',              'type': 'chance'},
    {'pos': 37, 'name': 'Rue des Palais',      'type': 'property', 'color': 'blue',   'price': 350, 'rent': [35, 175, 500, 1100, 1300, 1500],'house_cost': 200, 'mortgage': 175},
    {'pos': 38, 'name': 'Taxe de luxe',        'type': 'tax',      'amount': 100},
    {'pos': 39, 'name': 'Rue des Châteaux',    'type': 'property', 'color': 'blue',   'price': 400, 'rent': [50, 200, 600, 1400, 1700, 2000],'house_cost': 200, 'mortgage': 200},
]

# Pre-built lookups
COLOR_GROUPS = {}
for _s in BOARD:
    if _s['type'] == 'property':
        COLOR_GROUPS.setdefault(_s['color'], []).append(_s['pos'])

RAILWAY_POSITIONS = [s['pos'] for s in BOARD if s['type'] == 'railway']
UTILITY_POSITIONS = [s['pos'] for s in BOARD if s['type'] == 'utility']

PLAYER_COLORS  = ['#e74c3c', '#3498db', '#2ecc71', '#f1c40f', '#9b59b6', '#e67e22']
PLAYER_TOKENS  = ['🔴', '🔵', '🟢', '🟡', '🟣', '🟠']

# ─── CARD DECKS ────────────────────────────────────────────────────────────────
CHANCE_CARDS = [
    {'text': 'Avancez jusqu\'au Départ. Recevez 200€.',                        'action': 'goto',              'value': 0,  'collect_go': True},
    {'text': 'Avancez à la gare la plus proche. Payez le double si possédée.', 'action': 'goto_railway_near'},
    {'text': 'Avancez jusqu\'à la Cie Électrique.',                            'action': 'goto',              'value': 12},
    {'text': 'La banque vous verse un dividende de 50€.',                      'action': 'collect',           'value': 50},
    {'text': 'Votre crédit est excellent. Recevez 150€.',                      'action': 'collect',           'value': 150},
    {'text': 'Payez des frais d\'école : 150€.',                               'action': 'pay',               'value': 150},
    {'text': 'Reculez de 3 cases.',                                            'action': 'move',              'value': -3},
    {'text': 'Allez directement en Prison.',                                   'action': 'jail'},
    {'text': 'Réparations : 25€/maison, 100€/hôtel.',                         'action': 'repairs',           'house': 25, 'hotel': 100},
    {'text': 'Amende pour excès de vitesse : 15€.',                           'action': 'pay',               'value': 15},
    {'text': 'Avancez jusqu\'à Rue des Palais.',                               'action': 'goto',              'value': 37},
    {'text': 'Avancez jusqu\'à Rue des Châteaux.',                             'action': 'goto',              'value': 39},
    {'text': 'Carte « Sortez de Prison » gratuitement.',                       'action': 'jail_free'},
    {'text': 'Tous les joueurs vous paient 50€.',                              'action': 'collect_from_all',  'value': 50},
    {'text': 'Avancez à la Gare de l\'Est.',                                   'action': 'goto',              'value': 15},
    {'text': 'Avancez à la Gare du Sud.',                                      'action': 'goto',              'value': 25},
]

COMMUNITY_CHEST_CARDS = [
    {'text': 'Avancez jusqu\'au Départ. Recevez 200€.',                         'action': 'goto',             'value': 0,  'collect_go': True},
    {'text': 'Erreur bancaire en votre faveur. Recevez 200€.',                  'action': 'collect',          'value': 200},
    {'text': 'Frais médicaux : payez 50€.',                                     'action': 'pay',              'value': 50},
    {'text': 'Recevez votre salaire annuel : 100€.',                            'action': 'collect',          'value': 100},
    {'text': 'Facture d\'hôpital : payez 100€.',                                'action': 'pay',              'value': 100},
    {'text': 'C\'est votre anniversaire ! Chaque joueur vous donne 10€.',       'action': 'collect_from_all', 'value': 10},
    {'text': 'Héritage : recevez 100€.',                                        'action': 'collect',          'value': 100},
    {'text': 'Remboursement d\'impôt : recevez 20€.',                           'action': 'collect',          'value': 20},
    {'text': 'Carte « Sortez de Prison » gratuitement.',                        'action': 'jail_free'},
    {'text': 'Allez directement en Prison.',                                    'action': 'jail'},
    {'text': 'Amende : payez 10€.',                                             'action': 'pay',              'value': 10},
    {'text': 'Honoraires de consultant : recevez 25€.',                         'action': 'collect',          'value': 25},
    {'text': 'Vente d\'actions : recevez 45€.',                                 'action': 'collect',          'value': 45},
    {'text': 'Frais de scolarité : payez 150€.',                                'action': 'pay',              'value': 150},
    {'text': 'Réparations : 40€/maison et 115€/hôtel.',                        'action': 'repairs',          'house': 40, 'hotel': 115},
    {'text': 'Prix de beauté (2e place) : recevez 10€.',                        'action': 'collect',          'value': 10},
]

# ─── HELPERS ───────────────────────────────────────────────────────────────────

def _add_log(game, text, player_idx):
    color = game['players'][player_idx]['color'] if player_idx is not None else '#aaaaaa'
    game['log'].append({'text': text, 'color': color})
    if len(game['log']) > 60:
        game['log'] = game['log'][-60:]

def _active_players(game):
    return [i for i, p in enumerate(game['players']) if not p['bankrupt']]

def _owns_color_group(game, player_idx, color):
    positions = COLOR_GROUPS.get(color, [])
    return all(
        game['property_owners'].get(p) == player_idx
        for p in positions
    )

def _railway_rent(game, owner_idx):
    owned = sum(1 for pos in RAILWAY_POSITIONS if game['property_owners'].get(pos) == owner_idx)
    return [0, 25, 50, 100, 200][min(owned, 4)]

def _utility_rent(game, owner_idx, dice_total):
    owned = sum(1 for pos in UTILITY_POSITIONS if game['property_owners'].get(pos) == owner_idx)
    multiplier = 10 if owned == 2 else 4
    return dice_total * multiplier

def get_rent(game, pos, dice_total=0):
    space = BOARD[pos]
    owner_idx = game['property_owners'].get(pos)
    if owner_idx is None:
        return 0
    if game['property_mortgaged'].get(pos, False):
        return 0
    if space['type'] == 'railway':
        return _railway_rent(game, owner_idx)
    if space['type'] == 'utility':
        return _utility_rent(game, owner_idx, dice_total)
    # Regular property
    houses = game['property_houses'].get(pos, 0)
    rent = space['rent'][houses]
    if houses == 0 and _owns_color_group(game, owner_idx, space['color']):
        rent *= 2
    return rent

def _goto_jail(game, player_idx):
    p = game['players'][player_idx]
    p['position'] = 10
    p['in_jail'] = True
    p['jail_turns'] = 0
    _add_log(game, f"{p['token']} {p['name']} est envoyé en Prison !", player_idx)

def _advance_to(game, player_idx, target_pos, collect_go=True):
    p = game['players'][player_idx]
    current = p['position']
    if collect_go and target_pos < current:
        p['money'] += 200
        _add_log(game, f"{p['token']} {p['name']} passe par Départ → +200€", player_idx)
    p['position'] = target_pos

# ─── GAME FACTORY ──────────────────────────────────────────────────────────────

def new_monopoly_game(host_username, room_id):
    chance_deck = list(range(len(CHANCE_CARDS)))
    random.shuffle(chance_deck)
    community_deck = list(range(len(COMMUNITY_CHEST_CARDS)))
    random.shuffle(community_deck)
    return {
        'room_id': room_id,
        'status': 'waiting',
        'host': host_username,
        'players': [],
        'current_player_idx': 0,
        'phase': 'roll',
        'dice': [0, 0],
        'double_count': 0,
        'rolled_this_turn': False,
        'property_owners': {},
        'property_houses': {},
        'property_mortgaged': {},
        'deck_chance': chance_deck,
        'deck_community': community_deck,
        'log': [],
        'pending_trade': None,
        'start_time': None,
        'winner': None,
    }

# ─── PLAYER MANAGEMENT ─────────────────────────────────────────────────────────

def add_player(game, username, sid):
    if len(game['players']) >= 6:
        return False, 'La partie est pleine (max 6 joueurs).'
    if game['status'] != 'waiting':
        return False, 'La partie a déjà commencé.'
    idx = len(game['players'])
    game['players'].append({
        'name': username,
        'sid': sid,
        'money': 1500,
        'position': 0,
        'in_jail': False,
        'jail_turns': 0,
        'has_jail_free': False,
        'bankrupt': False,
        'color': PLAYER_COLORS[idx],
        'token': PLAYER_TOKENS[idx],
    })
    return True, idx

def start_game(game):
    if len(game['players']) < 2:
        return False, 'Il faut au moins 2 joueurs pour commencer.'
    game['status'] = 'playing'
    game['start_time'] = time.time()
    game['current_player_idx'] = 0
    game['phase'] = 'roll'
    first = game['players'][0]
    _add_log(game, f"🎮 La partie commence ! C'est à {first['token']} {first['name']} de jouer.", None)
    return True, None

# ─── CORE GAME ACTIONS ─────────────────────────────────────────────────────────

def roll_dice():
    return random.randint(1, 6), random.randint(1, 6)

def process_roll(game, player_idx, d1, d2):
    """Process a dice roll. Returns list of event dicts."""
    events = []
    p = game['players'][player_idx]
    total = d1 + d2
    is_double = d1 == d2

    game['dice'] = [d1, d2]
    game['rolled_this_turn'] = True

    _add_log(game, f"{p['token']} {p['name']} lance les dés : {d1} + {d2} = {total}", player_idx)
    events.append({'type': 'dice', 'dice': [d1, d2], 'player': player_idx})

    # ── Jail handling ──────────────────────────────────────────────────────────
    if p['in_jail']:
        if is_double:
            p['in_jail'] = False
            p['jail_turns'] = 0
            _add_log(game, f"{p['token']} {p['name']} sort de Prison avec un double !", player_idx)
            events.append({'type': 'jail_release', 'player': player_idx})
            # Fall through to normal move
        else:
            p['jail_turns'] += 1
            if p['jail_turns'] >= 3:
                # Force pay fine after 3 failed rolls
                p['money'] -= 50
                p['in_jail'] = False
                p['jail_turns'] = 0
                _add_log(game, f"{p['token']} {p['name']} paie 50€ (3 tours en Prison).", player_idx)
                events.append({'type': 'jail_fine', 'player': player_idx})
                # Fall through to move
            else:
                _add_log(game, f"{p['token']} {p['name']} reste en Prison (tour {p['jail_turns']}/3).", player_idx)
                events.append({'type': 'jail_stay', 'player': player_idx, 'turn': p['jail_turns']})
                game['phase'] = 'end'
                return events

    else:
        # Track doubles outside jail
        if is_double:
            game['double_count'] += 1
            if game['double_count'] >= 3:
                _goto_jail(game, player_idx)
                game['double_count'] = 0
                game['phase'] = 'end'
                events.append({'type': 'jail', 'player': player_idx, 'reason': 'three_doubles'})
                return events
        else:
            game['double_count'] = 0

    # ── Move player ────────────────────────────────────────────────────────────
    old_pos = p['position']
    new_pos = (old_pos + total) % 40

    # Passing GO (but not landing exactly on it via advance_to)
    if new_pos < old_pos or (old_pos == 0 and total > 0):
        p['money'] += 200
        _add_log(game, f"{p['token']} {p['name']} passe par Départ → +200€", player_idx)
        events.append({'type': 'collect_go', 'player': player_idx})

    p['position'] = new_pos
    events.append({'type': 'move', 'player': player_idx, 'position': new_pos})

    # ── Land on space ─────────────────────────────────────────────────────────
    landing_events = _process_landing(game, player_idx, total)
    events.extend(landing_events)

    # Double → roll again (unless jailed during this turn)
    if is_double and not p['in_jail'] and game['phase'] != 'end':
        game['phase'] = 'roll'
        _add_log(game, f"{p['token']} {p['name']} a fait un double ! Lancez à nouveau.", player_idx)
        events.append({'type': 'double', 'player': player_idx})
    elif game['phase'] not in ('end',):
        game['phase'] = 'action'

    return events

def _process_landing(game, player_idx, dice_total):
    events = []
    p = game['players'][player_idx]
    pos = p['position']
    space = BOARD[pos]

    stype = space['type']

    if stype == 'go':
        pass  # 200€ already handled in roll

    elif stype == 'go_to_jail':
        _goto_jail(game, player_idx)
        game['phase'] = 'end'
        events.append({'type': 'jail', 'player': player_idx})

    elif stype == 'tax':
        amount = space['amount']
        p['money'] -= amount
        _add_log(game, f"{p['token']} {p['name']} paie {amount}€ de taxes.", player_idx)
        events.append({'type': 'tax', 'player': player_idx, 'amount': amount})
        events.extend(_check_bankruptcy(game, player_idx, None))

    elif stype in ('property', 'railway', 'utility'):
        owner_idx = game['property_owners'].get(pos)
        if owner_idx is None:
            price = space['price']
            _add_log(game, f"{p['token']} {p['name']} arrive sur {space['name']} (à vendre : {price}€).", player_idx)
            events.append({'type': 'can_buy', 'player': player_idx, 'position': pos, 'price': price})
        elif owner_idx == player_idx:
            _add_log(game, f"{p['token']} {p['name']} arrive sur sa propre propriété.", player_idx)
        elif game['property_mortgaged'].get(pos, False):
            _add_log(game, f"{p['token']} {p['name']} arrive sur {space['name']} (hypothéquée — pas de loyer).", player_idx)
        else:
            owner = game['players'][owner_idx]
            if owner['bankrupt']:
                pass
            else:
                rent = get_rent(game, pos, dice_total)
                p['money'] -= rent
                owner['money'] += rent
                _add_log(game, f"{p['token']} {p['name']} paie {rent}€ de loyer à {owner['token']} {owner['name']}.", player_idx)
                events.append({'type': 'rent', 'player': player_idx, 'owner': owner_idx, 'amount': rent})
                events.extend(_check_bankruptcy(game, player_idx, owner_idx))

    elif stype == 'chance':
        events.extend(_draw_chance(game, player_idx, dice_total))

    elif stype == 'community_chest':
        events.extend(_draw_community(game, player_idx, dice_total))

    elif stype in ('jail', 'free_parking'):
        pass  # Just visiting / free parking

    return events

def _draw_chance(game, player_idx, dice_total):
    events = []
    if not game['deck_chance']:
        game['deck_chance'] = list(range(len(CHANCE_CARDS)))
        random.shuffle(game['deck_chance'])
    card_idx = game['deck_chance'].pop(0)
    card = CHANCE_CARDS[card_idx]
    p = game['players'][player_idx]
    _add_log(game, f"🃏 Chance : « {card['text']} »", player_idx)
    events.append({'type': 'card', 'deck': 'chance', 'text': card['text'], 'player': player_idx})
    events.extend(_apply_card(game, player_idx, card, dice_total))
    return events

def _draw_community(game, player_idx, dice_total):
    events = []
    if not game['deck_community']:
        game['deck_community'] = list(range(len(COMMUNITY_CHEST_CARDS)))
        random.shuffle(game['deck_community'])
    card_idx = game['deck_community'].pop(0)
    card = COMMUNITY_CHEST_CARDS[card_idx]
    p = game['players'][player_idx]
    _add_log(game, f"📦 Caisse : « {card['text']} »", player_idx)
    events.append({'type': 'card', 'deck': 'community', 'text': card['text'], 'player': player_idx})
    events.extend(_apply_card(game, player_idx, card, dice_total))
    return events

def _apply_card(game, player_idx, card, dice_total):
    events = []
    p = game['players'][player_idx]
    action = card['action']

    if action == 'collect':
        p['money'] += card['value']

    elif action == 'pay':
        p['money'] -= card['value']
        events.extend(_check_bankruptcy(game, player_idx, None))

    elif action == 'goto':
        _advance_to(game, player_idx, card['value'], card.get('collect_go', False))
        events.append({'type': 'move', 'player': player_idx, 'position': p['position']})
        events.extend(_process_landing(game, player_idx, dice_total))

    elif action == 'goto_railway_near':
        current = p['position']
        nearest = min(RAILWAY_POSITIONS, key=lambda r: (r - current) % 40)
        passing_go = (nearest - current) % 40 < current or nearest < current
        _advance_to(game, player_idx, nearest, passing_go)
        events.append({'type': 'move', 'player': player_idx, 'position': nearest})
        # Double rent if owned
        owner_idx = game['property_owners'].get(nearest)
        if owner_idx is not None and owner_idx != player_idx:
            rent = _railway_rent(game, owner_idx) * 2
            game['players'][owner_idx]['money'] += rent
            p['money'] -= rent
            _add_log(game, f"{p['token']} {p['name']} paie {rent}€ de loyer double à {game['players'][owner_idx]['name']}.", player_idx)
            events.extend(_check_bankruptcy(game, player_idx, owner_idx))
        else:
            events.extend(_process_landing(game, player_idx, dice_total))

    elif action == 'move':
        new_pos = (p['position'] + card['value']) % 40
        p['position'] = new_pos
        events.append({'type': 'move', 'player': player_idx, 'position': new_pos})
        events.extend(_process_landing(game, player_idx, dice_total))

    elif action == 'jail':
        _goto_jail(game, player_idx)
        game['phase'] = 'end'

    elif action == 'jail_free':
        p['has_jail_free'] = True

    elif action == 'repairs':
        total_houses = sum(1 for pos, h in game['property_houses'].items()
                           if game['property_owners'].get(pos) == player_idx and h < 5)
        total_hotels = sum(1 for pos, h in game['property_houses'].items()
                           if game['property_owners'].get(pos) == player_idx and h == 5)
        cost = total_houses * card['house'] + total_hotels * card['hotel']
        p['money'] -= cost
        if cost > 0:
            _add_log(game, f"{p['token']} {p['name']} paie {cost}€ de réparations.", player_idx)
        events.extend(_check_bankruptcy(game, player_idx, None))

    elif action == 'collect_from_all':
        amount = card['value']
        for i, other in enumerate(game['players']):
            if i != player_idx and not other['bankrupt']:
                other['money'] -= amount
                p['money'] += amount

    return events

def _check_bankruptcy(game, player_idx, creditor_idx):
    events = []
    p = game['players'][player_idx]
    if p['money'] >= 0:
        return events

    # Calculate total liquidation value
    total_assets = p['money']
    for pos, owner in game['property_owners'].items():
        if owner == player_idx:
            total_assets += BOARD[pos].get('mortgage', 0)
            total_assets += game['property_houses'].get(pos, 0) * (BOARD[pos].get('house_cost', 0) // 2)

    if total_assets >= 0:
        return events  # Can survive by mortgaging/selling

    # Bankrupt
    p['bankrupt'] = True
    _add_log(game, f"💀 {p['token']} {p['name']} est en faillite !", player_idx)
    events.append({'type': 'bankrupt', 'player': player_idx})

    # Transfer properties to creditor or back to bank
    for pos in list(game['property_owners'].keys()):
        if game['property_owners'][pos] == player_idx:
            if creditor_idx is not None:
                game['property_owners'][pos] = creditor_idx
                game['property_houses'].pop(pos, None)
                game['property_mortgaged'].pop(pos, None)
            else:
                del game['property_owners'][pos]
                game['property_houses'].pop(pos, None)
                game['property_mortgaged'].pop(pos, None)

    if creditor_idx is not None and p['money'] > 0:
        game['players'][creditor_idx]['money'] += p['money']
    p['money'] = 0

    # Check game over
    active = _active_players(game)
    if len(active) == 1:
        winner_idx = active[0]
        winner = game['players'][winner_idx]
        game['status'] = 'finished'
        game['winner'] = winner_idx
        game['phase'] = 'finished'
        _add_log(game, f"🏆 {winner['token']} {winner['name']} remporte la partie !", winner_idx)
        events.append({'type': 'game_over', 'winner': winner_idx, 'winner_name': winner['name']})

    return events

# ─── PLAYER ACTIONS ────────────────────────────────────────────────────────────

def buy_property(game, player_idx):
    p = game['players'][player_idx]
    pos = p['position']
    space = BOARD[pos]
    if space['type'] not in ('property', 'railway', 'utility'):
        return False, 'Cette case n\'est pas achetable.'
    if game['property_owners'].get(pos) is not None:
        return False, 'Cette propriété est déjà vendue.'
    if p['money'] < space['price']:
        return False, f'Pas assez d\'argent (prix : {space["price"]}€).'
    p['money'] -= space['price']
    game['property_owners'][pos] = player_idx
    _add_log(game, f"{p['token']} {p['name']} achète {space['name']} pour {space['price']}€.", player_idx)
    return True, None

def build_house(game, player_idx, pos):
    if pos < 0 or pos >= len(BOARD):
        return False, 'Position invalide.'
    space = BOARD[pos]
    if space['type'] != 'property':
        return False, 'Impossible de construire ici.'
    if game['property_owners'].get(pos) != player_idx:
        return False, 'Vous ne possédez pas cette propriété.'
    if game['property_mortgaged'].get(pos, False):
        return False, 'Cette propriété est hypothéquée.'
    if not _owns_color_group(game, player_idx, space['color']):
        return False, 'Vous devez posséder tout le groupe de couleur.'
    current = game['property_houses'].get(pos, 0)
    if current >= 5:
        return False, 'Il y a déjà un hôtel sur cette propriété.'
    # Even build rule
    color_positions = COLOR_GROUPS[space['color']]
    min_houses = min(game['property_houses'].get(cp, 0) for cp in color_positions)
    if current > min_houses:
        return False, 'Construisez d\'abord sur les autres propriétés du groupe.'
    cost = space['house_cost']
    if game['players'][player_idx]['money'] < cost:
        return False, f'Pas assez d\'argent (coût : {cost}€).'
    game['players'][player_idx]['money'] -= cost
    game['property_houses'][pos] = current + 1
    label = 'hôtel' if current + 1 == 5 else 'maison'
    _add_log(game, f"{game['players'][player_idx]['token']} {game['players'][player_idx]['name']} construit 1 {label} sur {space['name']}.", player_idx)
    return True, None

def sell_house(game, player_idx, pos):
    if pos < 0 or pos >= len(BOARD):
        return False, 'Position invalide.'
    space = BOARD[pos]
    if game['property_owners'].get(pos) != player_idx:
        return False, 'Vous ne possédez pas cette propriété.'
    current = game['property_houses'].get(pos, 0)
    if current == 0:
        return False, 'Pas de maison à vendre sur cette propriété.'
    color_positions = COLOR_GROUPS.get(space['color'], [])
    max_houses = max(game['property_houses'].get(cp, 0) for cp in color_positions)
    if current < max_houses:
        return False, 'Vendez d\'abord sur les propriétés avec le plus de maisons.'
    refund = space['house_cost'] // 2
    game['players'][player_idx]['money'] += refund
    new_count = current - 1
    if new_count == 0:
        game['property_houses'].pop(pos, None)
    else:
        game['property_houses'][pos] = new_count
    label = 'hôtel' if current == 5 else 'maison'
    _add_log(game, f"{game['players'][player_idx]['token']} {game['players'][player_idx]['name']} vend 1 {label} de {space['name']} (+{refund}€).", player_idx)
    return True, None

def mortgage_property(game, player_idx, pos):
    if game['property_owners'].get(pos) != player_idx:
        return False, 'Vous ne possédez pas cette propriété.'
    if game['property_mortgaged'].get(pos, False):
        return False, 'Propriété déjà hypothéquée.'
    if game['property_houses'].get(pos, 0) > 0:
        return False, 'Vendez d\'abord toutes les maisons.'
    space = BOARD[pos]
    value = space['mortgage']
    game['players'][player_idx]['money'] += value
    game['property_mortgaged'][pos] = True
    _add_log(game, f"{game['players'][player_idx]['token']} {game['players'][player_idx]['name']} hypothèque {space['name']} (+{value}€).", player_idx)
    return True, None

def unmortgage_property(game, player_idx, pos):
    if game['property_owners'].get(pos) != player_idx:
        return False, 'Vous ne possédez pas cette propriété.'
    if not game['property_mortgaged'].get(pos, False):
        return False, 'Cette propriété n\'est pas hypothéquée.'
    space = BOARD[pos]
    cost = int(space['mortgage'] * 1.1)
    if game['players'][player_idx]['money'] < cost:
        return False, f'Pas assez d\'argent (coût : {cost}€).'
    game['players'][player_idx]['money'] -= cost
    game['property_mortgaged'][pos] = False
    _add_log(game, f"{game['players'][player_idx]['token']} {game['players'][player_idx]['name']} déhypothèque {space['name']} (-{cost}€).", player_idx)
    return True, None

def pay_jail_fine(game, player_idx):
    p = game['players'][player_idx]
    if not p['in_jail']:
        return False, 'Vous n\'êtes pas en Prison.'
    if p['money'] < 50:
        return False, 'Pas assez d\'argent (50€ requis).'
    p['money'] -= 50
    p['in_jail'] = False
    p['jail_turns'] = 0
    _add_log(game, f"{p['token']} {p['name']} paie 50€ pour sortir de Prison.", player_idx)
    return True, None

def use_jail_free_card(game, player_idx):
    p = game['players'][player_idx]
    if not p['in_jail']:
        return False, 'Vous n\'êtes pas en Prison.'
    if not p['has_jail_free']:
        return False, 'Pas de carte « Sortez de Prison ».'
    p['in_jail'] = False
    p['jail_turns'] = 0
    p['has_jail_free'] = False
    _add_log(game, f"{p['token']} {p['name']} utilise sa carte « Sortez de Prison ».", player_idx)
    return True, None

def end_turn(game, player_idx):
    active = _active_players(game)
    if len(active) <= 1:
        return
    if player_idx not in active:
        active_idx = 0
    else:
        active_idx = active.index(player_idx)
    next_active_idx = (active_idx + 1) % len(active)
    game['current_player_idx'] = active[next_active_idx]
    game['phase'] = 'roll'
    game['rolled_this_turn'] = False
    game['double_count'] = 0
    next_p = game['players'][game['current_player_idx']]
    _add_log(game, f"🎲 Au tour de {next_p['token']} {next_p['name']}.", None)

# ─── SERIALIZATION ─────────────────────────────────────────────────────────────

def get_public_state(game):
    """Return a JSON-serializable snapshot of the game state."""
    return {
        'status': game['status'],
        'phase': game['phase'],
        'current_player_idx': game['current_player_idx'],
        'dice': game['dice'],
        'rolled_this_turn': game['rolled_this_turn'],
        'players': [
            {k: v for k, v in p.items() if k != 'sid'}
            for p in game['players']
        ],
        'property_owners':    {str(k): v for k, v in game['property_owners'].items()},
        'property_houses':    {str(k): v for k, v in game['property_houses'].items()},
        'property_mortgaged': {str(k): v for k, v in game['property_mortgaged'].items()},
        'log': game['log'],
        'winner': game['winner'],
        'pending_trade': game['pending_trade'],
        'host': game['host'],
    }

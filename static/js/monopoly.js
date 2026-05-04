/* =========================================================
   PROPERTY TYCOON — monopoly.js
   ========================================================= */

// ─── STATE ────────────────────────────────────────────────
var socket = io();
var gameState    = null;
var myPlayerIdx  = null;   // set after join/create
var myCardQueue  = [];     // cards waiting to be shown
var showingCard  = false;

// Color map for board rendering
var COLOR_MAP = {
    brown:   '#8B4513', cyan:   '#87CEEB', pink:    '#FF69B4',
    orange:  '#FFA500', red:    '#FF4444', yellow:  '#FFD700',
    green:   '#228B22', blue:   '#0000CD', railway: '#333333',
    utility: '#777777'
};

// ─── SOCKET EVENTS ────────────────────────────────────────

socket.on('connect', function() {
    // Join the room (server rejects gracefully if already joined or game started)
    socket.emit('mono_join', { room_id: ROOM_ID });
    socket.emit('mono_get_state', { room_id: ROOM_ID });
});

socket.on('mono_state', function(state) {
    gameState = state;
    render();
});

socket.on('mono_created', function(data) {
    // Already on game page — no redirect needed
});

socket.on('mono_joined', function(data) {
    myPlayerIdx = data.player_idx;
    saveMyIdx();
});

socket.on('mono_events', function(data) {
    (data.events || []).forEach(function(ev) {
        if (ev.type === 'card') {
            myCardQueue.push(ev);
            if (!showingCard) showNextCard();
        }
    });
});

socket.on('mono_error', function(data) {
    showToast('⚠️ ' + data.msg, '#e74c3c');
});

socket.on('mono_chat_msg', function(data) {
    appendChat(data.user, data.msg);
});

// ─── SESSION STORAGE FOR MY IDX ───────────────────────────

function saveMyIdx() {
    if (myPlayerIdx !== null)
        sessionStorage.setItem('mono_idx_' + ROOM_ID, myPlayerIdx);
}

function loadMyIdx() {
    var v = sessionStorage.getItem('mono_idx_' + ROOM_ID);
    if (v !== null) myPlayerIdx = parseInt(v);
}

loadMyIdx();

// ─── MAIN RENDER ──────────────────────────────────────────

function render() {
    if (!gameState) return;

    // Identify myself if still unknown
    if (myPlayerIdx === null) {
        var me = gameState.players.findIndex(function(p) { return p.name === MY_USERNAME; });
        if (me >= 0) { myPlayerIdx = me; saveMyIdx(); }
    }

    if (gameState.status === 'waiting') {
        showWaiting();
    } else {
        showGame();
    }
}

// ─── WAITING ROOM ─────────────────────────────────────────

function showWaiting() {
    document.getElementById('waiting-room').classList.remove('hidden');
    document.getElementById('game-screen').classList.add('hidden');

    var list = document.getElementById('player-list');
    list.innerHTML = gameState.players.map(function(p, i) {
        var isHost = (p.name === gameState.host);
        return '<div class="player-item">' +
               '<span class="player-token">' + p.token + '</span>' +
               '<span class="player-item-name">' + escHtml(p.name) + '</span>' +
               (isHost ? '<span class="player-item-badge">HÔTE</span>' : '') +
               '</div>';
    }).join('');

    var isHost = (MY_USERNAME === gameState.host);
    var startArea = document.getElementById('start-area');
    var waitMsg   = document.getElementById('waiting-msg');
    if (isHost && gameState.players.length >= 2) {
        startArea.classList.remove('hidden');
        waitMsg.classList.add('hidden');
    } else if (isHost) {
        startArea.classList.add('hidden');
        waitMsg.textContent = 'En attente d\'au moins un autre joueur… (' + gameState.players.length + '/6)';
    } else {
        startArea.classList.add('hidden');
        waitMsg.textContent = 'En attente que l\'hôte démarre la partie…';
    }
}

function startGame() {
    socket.emit('mono_start', { room_id: ROOM_ID });
}

// ─── GAME SCREEN ──────────────────────────────────────────

function showGame() {
    document.getElementById('waiting-room').classList.add('hidden');
    document.getElementById('game-screen').classList.remove('hidden');

    if (gameState.status === 'finished' && gameState.winner !== null) {
        showWinner();
    }

    renderBoard();
    renderSidePanel();
    renderLog();
    renderActions();
    renderTrade();
}

// ─── BOARD RENDERING ──────────────────────────────────────

function renderBoard() {
    // Place tokens on cells
    BOARD_DATA.forEach(function(space) {
        var tokensEl  = document.getElementById('tokens-' + space.pos);
        var housesEl  = document.getElementById('houses-' + space.pos);
        var cell      = document.getElementById('cell-' + space.pos);
        if (!tokensEl) return;

        // Clear
        tokensEl.innerHTML = '';
        if (housesEl) housesEl.innerHTML = '';

        // Tokens
        gameState.players.forEach(function(p) {
            if (p.position === space.pos) {
                var span = document.createElement('span');
                span.className = 'board-token';
                span.textContent = p.token;
                span.title = p.name;
                tokensEl.appendChild(span);
            }
        });

        // Houses / hotel
        if (housesEl) {
            var h = parseInt(gameState.property_houses[space.pos] || 0);
            if (h === 5) {
                var hel = document.createElement('span');
                hel.className = 'hotel-icon'; hel.textContent = '🏨';
                housesEl.appendChild(hel);
            } else {
                for (var i = 0; i < h; i++) {
                    var hel2 = document.createElement('span');
                    hel2.className = 'house-icon'; hel2.textContent = '🏠';
                    housesEl.appendChild(hel2);
                }
            }
        }

        // Owner overlay tint
        var ownerIdx = gameState.property_owners[space.pos];
        if (ownerIdx !== undefined && ownerIdx !== null) {
            var owner = gameState.players[ownerIdx];
            cell.style.boxShadow = 'inset 0 0 0 2px ' + owner.color;
        } else {
            cell.style.boxShadow = '';
        }

        // Mortgaged
        if (gameState.property_mortgaged[space.pos]) {
            cell.classList.add('mortgaged');
        } else {
            cell.classList.remove('mortgaged');
        }
    });

    // Center info
    var dice = gameState.dice;
    var d1 = diceEmoji(dice[0]);
    var d2 = diceEmoji(dice[1]);
    document.getElementById('center-dice').textContent = d1 + ' ' + d2;

    var cur = gameState.players[gameState.current_player_idx];
    if (cur) {
        document.getElementById('center-turn').textContent =
            cur.token + ' ' + cur.name + ' joue';
    }
}

function diceEmoji(n) {
    return ['', '⚀', '⚁', '⚂', '⚃', '⚄', '⚅'][n] || '🎲';
}

// ─── SIDE PANEL ───────────────────────────────────────────

function renderSidePanel() {
    // My status
    var myStatus = document.getElementById('my-status');
    if (myPlayerIdx !== null && gameState.players[myPlayerIdx]) {
        var me = gameState.players[myPlayerIdx];
        var pos = BOARD_DATA[me.position];
        myStatus.innerHTML =
            '<div class="status-money">' + me.money + '€</div>' +
            '<div class="status-pos">' + me.token + ' Case ' + me.position +
            ' — ' + escHtml(pos ? pos.name : '') + '</div>' +
            (me.in_jail ? '<div style="color:#e74c3c;font-weight:700;">🔒 EN PRISON (tour ' + me.jail_turns + '/3)</div>' : '') +
            (me.has_jail_free ? '<div style="color:#f9ca24;">🃏 Carte Sortie Prison</div>' : '') +
            (me.bankrupt ? '<div style="color:#e74c3c;">💀 EN FAILLITE</div>' : '');
    } else {
        myStatus.innerHTML = '<span style="color:#888;">Spectateur</span>';
    }

    // Players
    var pp = document.getElementById('players-panel');
    pp.innerHTML = gameState.players.map(function(p, i) {
        var isActive = (i === gameState.current_player_idx);
        var cls = 'player-row' +
            (isActive ? ' active-player' : '') +
            (p.bankrupt ? ' bankrupt-player' : '');
        var pos = BOARD_DATA[p.position];
        return '<div class="' + cls + '" style="border-left:3px solid ' + p.color + ';">' +
               '<span class="pr-token">' + p.token + '</span>' +
               '<span class="pr-name">' + escHtml(p.name) + '</span>' +
               '<span class="pr-money">' + p.money + '€</span>' +
               '</div>';
    }).join('');

    // My properties
    var mpp = document.getElementById('my-props-panel');
    if (myPlayerIdx !== null) {
        var myProps = [];
        for (var pos2 in gameState.property_owners) {
            if (parseInt(gameState.property_owners[pos2]) === myPlayerIdx) {
                myProps.push(parseInt(pos2));
            }
        }
        if (!myProps.length) {
            mpp.innerHTML = '<p style="color:#888;font-size:12px;">Aucune propriété.</p>';
        } else {
            myProps.sort(function(a,b){return a-b;});
            mpp.innerHTML = myProps.map(function(pos3) {
                var sp = BOARD_DATA[pos3];
                if (!sp) return '';
                var color = sp.color ? (COLOR_MAP[sp.color] || '#aaa') : '#888';
                var h = parseInt(gameState.property_houses[pos3] || 0);
                var isMort = gameState.property_mortgaged[pos3];
                var detail = isMort ? 'hypothéquée' : (h === 5 ? '🏨 hôtel' : (h > 0 ? h + ' 🏠' : ''));
                return '<div class="my-prop-item' + (isMort ? ' prop-mortgaged' : '') + '" onclick="showPropActions(' + pos3 + ')">' +
                       '<div class="prop-dot" style="background:' + color + '"></div>' +
                       '<span class="prop-name">' + escHtml(sp.name) + '</span>' +
                       '<span class="prop-detail">' + detail + '</span>' +
                       '</div>' +
                       '<div id="prop-actions-' + pos3 + '" class="prop-mgmt hidden"></div>';
            }).join('');
        }
    }
}

function showPropActions(pos) {
    // Toggle prop action panel
    var el = document.getElementById('prop-actions-' + pos);
    if (!el) return;
    var isHidden = el.classList.contains('hidden');

    // Hide all others first
    document.querySelectorAll('.prop-mgmt').forEach(function(e) {
        e.classList.add('hidden'); e.innerHTML = '';
    });

    if (!isHidden) return;

    var sp = BOARD_DATA[pos];
    if (!sp) return;
    var h = parseInt(gameState.property_houses[pos] || 0);
    var isMort = !!gameState.property_mortgaged[pos];
    var me = gameState.players[myPlayerIdx];
    var isMyTurn = (myPlayerIdx === gameState.current_player_idx);

    var btns = '';
    if (!isMort) {
        if (sp.type === 'property') {
            var canBuild = me && me.money >= sp.house_cost && h < 5;
            btns += '<button style="background:#27ae60;color:#fff;" onclick="buildHouse(' + pos + ')">🏠 +Maison ' + sp.house_cost + '€</button>';
            if (h > 0) {
                var refund = Math.floor(sp.house_cost / 2);
                btns += '<button style="background:#e67e22;color:#fff;" onclick="sellHouseOn(' + pos + ')">🔨 -Maison +' + refund + '€</button>';
            }
        }
        btns += '<button style="background:#c0392b;color:#fff;" onclick="mortgageProp(' + pos + ')">💸 Hypothéquer +' + sp.mortgage + '€</button>';
    } else {
        var unmortCost = Math.round(sp.mortgage * 1.1);
        btns += '<button style="background:#2980b9;color:#fff;" onclick="unmortgageProp(' + pos + ')">🔓 Déhypothéquer -' + unmortCost + '€</button>';
    }

    el.innerHTML = '<div class="prop-btns">' + btns + '</div>';
    el.classList.remove('hidden');
}

// ─── ACTION BUTTONS ───────────────────────────────────────

function renderActions() {
    var btns = document.getElementById('action-btns');
    if (!btns) return;

    var isMyTurn = (myPlayerIdx !== null && myPlayerIdx === gameState.current_player_idx);
    var phase = gameState.phase;
    var me = myPlayerIdx !== null ? gameState.players[myPlayerIdx] : null;
    var html = '';

    if (isMyTurn && gameState.status === 'playing') {
        if (phase === 'roll') {
            if (me && me.in_jail) {
                html += '<button class="btn-jail" onclick="payJail()">💸 Payer 50€ (Prison)</button>';
                if (me.has_jail_free) {
                    html += '<button class="btn-jail" onclick="useJailFree()">🃏 Carte Prison</button>';
                }
                html += '<button class="btn-roll" onclick="rollDice()">🎲 Tenter le double</button>';
            } else {
                html += '<button class="btn-roll" onclick="rollDice()">🎲 LANCER LES DÉS</button>';
            }
        }
        if (phase === 'action') {
            // Check if can buy current cell
            var curPos = me ? me.position : -1;
            var sp = BOARD_DATA[curPos];
            if (sp && ['property','railway','utility'].includes(sp.type)) {
                var ownerIdx = gameState.property_owners[curPos];
                if (ownerIdx === undefined || ownerIdx === null) {
                    html += '<button class="btn-buy" onclick="buyProp()">🏠 ACHETER ' + sp.name + ' (' + sp.price + '€)</button>';
                }
            }
            html += '<button class="btn-end" onclick="endTurn()">✅ FIN DE TOUR</button>';
        }
        if (phase === 'end') {
            html += '<button class="btn-end" onclick="endTurn()">✅ FIN DE TOUR</button>';
        }
    } else if (myPlayerIdx !== null && gameState.status === 'playing') {
        var cur2 = gameState.players[gameState.current_player_idx];
        html += '<div style="color:#888;font-size:13px;">En attente de ' +
                (cur2 ? cur2.token + ' ' + escHtml(cur2.name) : '...') + '…</div>';
    }

    // Trade button (available to all active players anytime)
    if (myPlayerIdx !== null && me && !me.bankrupt && gameState.status === 'playing') {
        var otherActive = gameState.players.some(function(p, i) {
            return i !== myPlayerIdx && !p.bankrupt;
        });
        if (otherActive) {
            html += '<button class="btn-trade" onclick="openTrade()">🤝 PROPOSER ÉCHANGE</button>';
        }
    }

    btns.innerHTML = html;
}

// ─── SOCKET ACTIONS ───────────────────────────────────────

function rollDice() {
    socket.emit('mono_roll', { room_id: ROOM_ID });
}

function buyProp() {
    socket.emit('mono_buy', { room_id: ROOM_ID });
}

function endTurn() {
    socket.emit('mono_end_turn', { room_id: ROOM_ID });
}

function payJail() {
    socket.emit('mono_pay_jail', { room_id: ROOM_ID });
}

function useJailFree() {
    socket.emit('mono_use_jail_free', { room_id: ROOM_ID });
}

function buildHouse(pos) {
    socket.emit('mono_build', { room_id: ROOM_ID, pos: pos });
}

function sellHouseOn(pos) {
    socket.emit('mono_sell_house', { room_id: ROOM_ID, pos: pos });
}

function mortgageProp(pos) {
    socket.emit('mono_mortgage', { room_id: ROOM_ID, pos: pos });
}

function unmortgageProp(pos) {
    socket.emit('mono_unmortgage', { room_id: ROOM_ID, pos: pos });
}

// ─── TRADE ────────────────────────────────────────────────

function openTrade() {
    if (!gameState || myPlayerIdx === null) return;
    var modal = document.getElementById('trade-modal');

    // Populate target select
    var sel = document.getElementById('trade-to');
    sel.innerHTML = '';
    gameState.players.forEach(function(p, i) {
        if (i !== myPlayerIdx && !p.bankrupt) {
            var opt = document.createElement('option');
            opt.value = i;
            opt.textContent = p.token + ' ' + p.name;
            sel.appendChild(opt);
        }
    });

    // My properties to offer
    var offerDiv = document.getElementById('trade-offer-props');
    offerDiv.innerHTML = buildPropCheckboxes(myPlayerIdx, 'offer-prop-');

    // Reset request props (will update on target change)
    updateRequestProps();

    sel.onchange = updateRequestProps;
    modal.classList.remove('hidden');
}

function updateRequestProps() {
    var sel = document.getElementById('trade-to');
    if (!sel) return;
    var toIdx = parseInt(sel.value);
    var reqDiv = document.getElementById('trade-req-props');
    reqDiv.innerHTML = buildPropCheckboxes(toIdx, 'req-prop-');
}

function buildPropCheckboxes(playerIdx, prefix) {
    var html = '';
    for (var pos in gameState.property_owners) {
        if (parseInt(gameState.property_owners[pos]) === playerIdx) {
            var sp = BOARD_DATA[parseInt(pos)];
            if (!sp) continue;
            var color = sp.color ? (COLOR_MAP[sp.color] || '#aaa') : '#888';
            html += '<label class="prop-check-item">' +
                    '<input type="checkbox" id="' + prefix + pos + '" value="' + pos + '">' +
                    '<span style="width:10px;height:10px;background:' + color +
                    ';border-radius:50%;display:inline-block;"></span>' +
                    escHtml(sp.name) +
                    '</label>';
        }
    }
    return html || '<p style="color:#888;font-size:11px;">Aucune propriété.</p>';
}

function closeTrade() {
    document.getElementById('trade-modal').classList.add('hidden');
}

function sendTradeOffer() {
    var toIdx = parseInt(document.getElementById('trade-to').value);
    var offerMoney  = parseInt(document.getElementById('trade-offer-money').value) || 0;
    var reqMoney    = parseInt(document.getElementById('trade-req-money').value)   || 0;
    var offerProps  = getChecked('offer-prop-');
    var reqProps    = getChecked('req-prop-');

    socket.emit('mono_trade_offer', {
        room_id: ROOM_ID,
        to_idx: toIdx,
        offer_money: offerMoney,
        offer_props: offerProps,
        request_money: reqMoney,
        request_props: reqProps,
    });
    closeTrade();
}

function getChecked(prefix) {
    var results = [];
    document.querySelectorAll('input[id^="' + prefix + '"]:checked').forEach(function(el) {
        results.push(parseInt(el.value));
    });
    return results;
}

function renderTrade() {
    var trade = gameState.pending_trade;
    var incoming = document.getElementById('incoming-trade-modal');

    if (!trade || myPlayerIdx === null) {
        incoming.classList.add('hidden');
        return;
    }

    if (trade.to !== myPlayerIdx) {
        incoming.classList.add('hidden');
        return;
    }

    // Show incoming trade
    var fromP = gameState.players[trade.from];
    var desc = '';
    if (trade.offer_money > 0) desc += fromP.name + ' offre <strong>' + trade.offer_money + '€</strong><br>';
    if (trade.offer_props.length) {
        desc += fromP.name + ' offre : ';
        desc += trade.offer_props.map(function(p) {
            return escHtml(BOARD_DATA[p] ? BOARD_DATA[p].name : p);
        }).join(', ') + '<br>';
    }
    if (trade.request_money > 0) desc += fromP.name + ' demande <strong>' + trade.request_money + '€</strong><br>';
    if (trade.request_props.length) {
        desc += fromP.name + ' demande : ';
        desc += trade.request_props.map(function(p) {
            return escHtml(BOARD_DATA[p] ? BOARD_DATA[p].name : p);
        }).join(', ') + '<br>';
    }
    document.getElementById('incoming-trade-desc').innerHTML = desc || 'Pas de détails.';
    incoming.classList.remove('hidden');
}

function respondTrade(accept) {
    socket.emit('mono_trade_respond', { room_id: ROOM_ID, accept: accept });
    document.getElementById('incoming-trade-modal').classList.add('hidden');
}

// ─── GAME LOG ─────────────────────────────────────────────

function renderLog() {
    var logEl = document.getElementById('game-log');
    if (!logEl || !gameState.log) return;
    logEl.innerHTML = gameState.log.slice().reverse().map(function(entry) {
        return '<div class="log-entry" style="color:' + entry.color + '">' +
               escHtml(entry.text) + '</div>';
    }).join('');
}

// ─── CARD POPUP ───────────────────────────────────────────

function showNextCard() {
    if (!myCardQueue.length) { showingCard = false; return; }
    // Only show cards for ourselves (or all events since we don't know which player drew)
    var ev = myCardQueue.shift();
    showingCard = true;

    var icon  = ev.deck === 'chance' ? '🃏' : '📦';
    var label = ev.deck === 'chance' ? 'CHANCE' : 'CAISSE DE COMMUNAUTÉ';
    document.getElementById('card-popup-type').textContent = icon + ' ' + label;
    document.getElementById('card-popup-text').textContent = ev.text;
    document.getElementById('card-popup').classList.remove('hidden');
}

function closeCard() {
    document.getElementById('card-popup').classList.add('hidden');
    showingCard = false;
    if (myCardQueue.length) {
        setTimeout(showNextCard, 300);
    }
}

// ─── WINNER ───────────────────────────────────────────────

function showWinner() {
    var overlay = document.getElementById('winner-overlay');
    if (!overlay || overlay.classList.contains('shown')) return;
    overlay.classList.add('shown');
    overlay.classList.remove('hidden');

    var winIdx = gameState.winner;
    var winner = gameState.players[winIdx];
    var isMe   = (winIdx === myPlayerIdx);

    document.getElementById('winner-icon').textContent  = winner.token;
    document.getElementById('winner-title').textContent = isMe ? '🏆 VOUS AVEZ GAGNÉ !' : winner.name + ' a gagné !';
    document.getElementById('winner-sub').textContent   = 'Félicitations à ' + winner.name + ' !';
}

// ─── CHAT ─────────────────────────────────────────────────

function sendChat() {
    var inp = document.getElementById('chat-input');
    var msg = inp.value.trim();
    if (!msg) return;
    socket.emit('mono_chat', { room_id: ROOM_ID, msg: msg });
    inp.value = '';
}

function appendChat(user, msg) {
    var el = document.getElementById('chat-messages');
    var div = document.createElement('div');
    div.className = 'chat-msg';
    div.innerHTML = '<span class="chat-user">' + escHtml(user) + '</span>: ' + escHtml(msg);
    el.appendChild(div);
    el.scrollTop = el.scrollHeight;
}

// ─── TOAST ────────────────────────────────────────────────

function showToast(msg, color) {
    var el = document.getElementById('toast');
    if (!el) {
        el = document.createElement('div');
        el.id = 'toast';
        el.style.cssText = 'position:fixed;bottom:24px;left:50%;transform:translateX(-50%);' +
            'padding:12px 24px;border-radius:10px;font-size:14px;font-weight:700;' +
            'z-index:9999;transition:opacity 0.4s;box-shadow:0 4px 20px rgba(0,0,0,0.4);';
        document.body.appendChild(el);
    }
    el.style.background = color || '#2d2d2d';
    el.style.color = '#fff';
    el.textContent = msg;
    el.style.opacity = '1';
    clearTimeout(el._t);
    el._t = setTimeout(function() { el.style.opacity = '0'; }, 3500);
}

// ─── HELPERS ──────────────────────────────────────────────

function escHtml(s) {
    return String(s)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

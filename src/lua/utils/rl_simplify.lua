-- RL environment simplification (FINAL CLEAN VERSION)

-- Allowed jokers
local ALLOWED_JOKER_LIST = {
    "j_joker",
    "j_lusty_joker",
    "j_jolly"
}

------------------------------------------------------------------
-- Check if joker allowed
------------------------------------------------------------------
local function is_allowed(card)
    if not card or not card.config then return false end
    local key = card.config.center_key
    for _, k in ipairs(ALLOWED_JOKER_LIST) do
        if k == key then return true end
    end
    return false
end

------------------------------------------------------------------
-- Get missing jokers (avoid duplicates)
------------------------------------------------------------------
local function get_missing_jokers(existing)
    local present = {}

    for _, c in ipairs(existing) do
        if c.config and c.config.center_key then
            present[c.config.center_key] = true
        end
    end

    local available = {}
    for _, key in ipairs(ALLOWED_JOKER_LIST) do
        if not present[key] then
            table.insert(available, key)
        end
    end

    return available
end

------------------------------------------------------------------
-- FORCE SHOP CONTENT
------------------------------------------------------------------
local function enforce_shop()
    if not G or G.STATE ~= G.STATES.SHOP then return end

    --------------------------------------------------------------
    -- JOKERS
    --------------------------------------------------------------
    if G.shop_jokers and G.shop_jokers.cards then

        -- Remove disallowed jokers
        for i = #G.shop_jokers.cards, 1, -1 do
            local card = G.shop_jokers.cards[i]
            if not is_allowed(card) then
                card:remove()
                table.remove(G.shop_jokers.cards, i)
            end
        end

        -- Refill with allowed jokers (no duplicates)
        while #G.shop_jokers.cards < 2 do
            local available = get_missing_jokers(G.shop_jokers.cards)
            if #available == 0 then break end

            local key = available[math.random(#available)]
            local new = create_card("Joker", G.shop_jokers, nil, nil, nil, nil, key)

            if new then
                G.shop_jokers:emplace(new)
            end
        end
    end

    --------------------------------------------------------------
    -- REMOVE BOOSTERS / PACKS
    --------------------------------------------------------------
    if G.shop_booster and G.shop_booster.cards then
        for i = #G.shop_booster.cards, 1, -1 do
            local c = G.shop_booster.cards[i]
            c:remove()
            table.remove(G.shop_booster.cards, i)
        end
    end

    --------------------------------------------------------------
    -- REMOVE CONSUMABLES (tarot / planet / spectral)
    --------------------------------------------------------------
    if G.shop_consumables and G.shop_consumables.cards then
        for i = #G.shop_consumables.cards, 1, -1 do
            local c = G.shop_consumables.cards[i]
            c:remove()
            table.remove(G.shop_consumables.cards, i)
        end
    end

    --------------------------------------------------------------
    -- REMOVE VOUCHERS
    --------------------------------------------------------------
    if G.shop_vouchers and G.shop_vouchers.cards then
        for i = #G.shop_vouchers.cards, 1, -1 do
            local c = G.shop_vouchers.cards[i]
            c:remove()
            table.remove(G.shop_vouchers.cards, i)
        end
    end
end

------------------------------------------------------------------
-- HOOK GAME LOOP 
------------------------------------------------------------------
local orig_update = Game.update
function Game:update(dt)
    orig_update(self, dt)
    enforce_shop()
end

------------------------------------------------------------------
-- FORCE HEART DECK
------------------------------------------------------------------
local orig_start_run = Game.start_run
function Game:start_run(...)
    orig_start_run(self, ...)

    G.E_MANAGER:add_event(Event({
        trigger = "condition",
        blocking = false,
        func = function()
            if not G.deck or not G.deck.cards then return false end

            for _, card in pairs(G.deck.cards) do
                if card.config and card.config.card then
                    card:change_suit("Hearts")
                end
            end

            return true
        end,
    }))
end

------------------------------------------------------------------
-- For deterministic randomness for RL:
------------------------------------------------------------------
-- math.randomseed(123)

------------------------------------------------------------------
sendInfoMessage("RL SIMPLIFY FINAL (JOKERS + NO VOUCHERS + HEARTS)", "BB.RL")
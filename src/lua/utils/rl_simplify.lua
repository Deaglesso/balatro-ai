-- RL environment simplification

local ALLOWED_JOKER_LIST = {
    "j_joker",
    "j_lusty_joker",
    "j_jolly"
}

local function is_allowed_key(key)
    for _, k in ipairs(ALLOWED_JOKER_LIST) do
        if k == key then return true end
    end
    return false
end

local function is_allowed(card)
    if not card or not card.config then return false end
    return is_allowed_key(card.config.center_key)
end

local function enforce_shop()
    if not G or G.STATE ~= G.STATES.SHOP then return end

    if G.shop_jokers and G.shop_jokers.cards then
        for i = #G.shop_jokers.cards, 1, -1 do
            if not is_allowed(G.shop_jokers.cards[i]) then
                G.shop_jokers.cards[i]:remove()
                table.remove(G.shop_jokers.cards, i)
            end
        end
    end

    if G.shop_booster and G.shop_booster.cards then
        for i = #G.shop_booster.cards, 1, -1 do
            G.shop_booster.cards[i]:remove()
            table.remove(G.shop_booster.cards, i)
        end
    end

    if G.shop_consumables and G.shop_consumables.cards then
        for i = #G.shop_consumables.cards, 1, -1 do
            G.shop_consumables.cards[i]:remove()
            table.remove(G.shop_consumables.cards, i)
        end
    end

    if G.shop_vouchers and G.shop_vouchers.cards then
        for i = #G.shop_vouchers.cards, 1, -1 do
            G.shop_vouchers.cards[i]:remove()
            table.remove(G.shop_vouchers.cards, i)
        end
    end
end

local orig_update = Game.update
function Game:update(dt)
    orig_update(self, dt)
    enforce_shop()
end

-- Intercept shop card creation and replace disallowed jokers
local orig_create_card_for_shop = create_card_for_shop
function create_card_for_shop(area, forced_tag)
    local card = orig_create_card_for_shop(area, forced_tag)
    if card and card.ability and card.ability.set == "Joker" then
        if not is_allowed_key(card.config.center_key) then
            local replace_key = ALLOWED_JOKER_LIST[math.random(#ALLOWED_JOKER_LIST)]
            card:set_ability(G.P_CENTERS[replace_key])
        end
    end
    return card
end

local orig_start_run = Game.start_run
function Game:start_run(...)
    orig_start_run(self, ...)

    -- Force all deck cards to Hearts
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

sendInfoMessage("RL SIMPLIFY (JOKERS + NO VOUCHERS + HEARTS)", "BB.RL")
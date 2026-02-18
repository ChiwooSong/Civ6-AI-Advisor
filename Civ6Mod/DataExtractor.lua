-- DataExtractor.lua (Fixes for Lua API)

print("DataExtractor: Script Loaded")

function GetSafeYields(playerID)
    local pPlayer = Players[playerID]
    if not pPlayer then return {} end

    -- Treasury (Gold)
    local gold = 0
    local goldPerTurn = 0
    if pPlayer:GetTreasury() then
        gold = pPlayer:GetTreasury():GetGoldBalance()
        goldPerTurn = pPlayer:GetTreasury():GetGoldYield() - pPlayer:GetTreasury():GetTotalMaintenance()
    end

    -- Science
    local science = 0
    if pPlayer:GetTechs() then
        science = pPlayer:GetTechs():GetScienceYield()
    end

    -- Culture
    local culture = 0
    if pPlayer:GetCulture() then
        culture = pPlayer:GetCulture():GetCultureYield()
    end
    
    -- Faith
    local faith = 0
    if pPlayer:GetReligion() then
        faith = pPlayer:GetReligion():GetFaithBalance()
    end

    return {
        science = science,
        culture = culture,
        gold = gold,
        gold_per_turn = goldPerTurn,
        faith = faith
    }
end

function GetSafeCities(playerID)
    local pPlayer = Players[playerID]
    local cities = {}
    if not pPlayer then return cities end
    
    local pCities = pPlayer:GetCities()
    if pCities then
        for i, pCity in pCities:Members() do
            table.insert(cities, {
                name = pCity:GetName(),
                population = pCity:GetPopulation()
            })
        end
    end
    return cities
end

function OnTurnBegin()
    -- 안전하게 Local Player ID 가져오기
    local playerID = Game.GetLocalPlayer()
    if playerID == -1 or playerID == nil then return end

    print("DataExtractor: Processing Turn " .. tostring(Game.GetCurrentGameTurn()))
    
    local civName = "Unknown"
    local leaderName = "Unknown"
    
    if PlayerConfigurations then
        local pConfig = PlayerConfigurations[playerID]
        if pConfig then
            civName = pConfig:GetCivilizationTypeName()
            leaderName = pConfig:GetLeaderTypeName()
        end
    end

    local data = {
        header = {
            turn = Game.GetCurrentGameTurn(),
            playerID = playerID,
            civilization = civName,
            leader = leaderName
        },
        yields = GetSafeYields(playerID),
        cities = GetSafeCities(playerID)
    }

    -- JSON 직렬화
    local function serialize(t)
        local s = "{"
        for k, v in pairs(t) do
            s = s .. '"' .. k .. '":'
            if type(v) == "table" then
                s = s .. serialize(v)
            elseif type(v) == "string" then
                s = s .. '"' .. v .. '"'
            elseif type(v) == "number" then
                s = s .. tostring(v)
            else
                s = s .. '"unknown"'
            end
            s = s .. ","
        end
        if s:sub(-1) == "," then s = s:sub(1, -2) end
        return s .. "}"
    end

    local status, json_output = pcall(serialize, data)
    if status then
        print("[CIV6_AI_DATA] " .. json_output)
    else
        print("DataExtractor Error: Serialization failed")
    end
end

-- 이벤트 리스너 등록
-- Events.LocalPlayerTurnBegin이 가장 안전함
Events.LocalPlayerTurnBegin.Add(OnTurnBegin)

print("DataExtractor: Listeners Registered")

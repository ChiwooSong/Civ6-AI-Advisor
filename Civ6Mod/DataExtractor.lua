-- DataExtractor.lua
-- Phase 3.1: Robust Data Collection (Error Handling Added)

print("DataExtractor: Script Loaded (v2.1)")

-- --- Helper Functions for Safe API Access ---

function GetSafeYields(playerID)
    local pPlayer = Players[playerID]
    if not pPlayer then return {} end

    local function get_yields_inner()
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

    local status, result = pcall(get_yields_inner)
    if status then return result else return {} end
end

function GetCurrentResearch(playerID)
    local function get_research_inner()
        local pPlayer = Players[playerID]
        if not pPlayer or not pPlayer:GetTechs() then return "None" end
        
        local pTechs = pPlayer:GetTechs()
        
        -- Try GetActiveTech first
        local techID = -1
        if pTechs.GetActiveTech then
            techID = pTechs:GetActiveTech()
        elseif pTechs.GetResearchingTech then
            techID = pTechs:GetResearchingTech() -- Alternative API
        end
        
        if techID == -1 then return "None" end
        
        local techInfo = GameInfo.Technologies[techID]
        if techInfo then
            return techInfo.Name
        end
        return "Unknown Tech (" .. tostring(techID) .. ")"
    end

    local status, result = pcall(get_research_inner)
    if status then return result else return "Unknown (Error)" end
end

function GetCurrentCivic(playerID)
    local function get_civic_inner()
        local pPlayer = Players[playerID]
        if not pPlayer or not pPlayer:GetCulture() then return "None" end
        
        local pCulture = pPlayer:GetCulture()
        
        local civicID = -1
        if pCulture.GetProgressingCivic then
            civicID = pCulture:GetProgressingCivic()
        end
        
        if civicID == -1 then return "None" end
        
        local civicInfo = GameInfo.Civics[civicID]
        if civicInfo then
            return civicInfo.Name
        end
        return "Unknown Civic (" .. tostring(civicID) .. ")"
    end

    local status, result = pcall(get_civic_inner)
    if status then return result else return "Unknown (Error)" end
end

function GetActivePolicies(playerID)
    local function get_policies_inner()
        local pPlayer = Players[playerID]
        if not pPlayer or not pPlayer:GetCulture() then return {} end
        
        local pCulture = pPlayer:GetCulture()
        local numSlots = pCulture:GetNumPolicySlots()
        local policies = {}
        
        for i = 0, numSlots - 1 do
            local policyID = pCulture:GetSlotPolicy(i)
            if policyID ~= -1 then
                local policyInfo = GameInfo.Policies[policyID]
                if policyInfo then
                    table.insert(policies, policyInfo.Name)
                end
            end
        end
        return policies
    end

    local status, result = pcall(get_policies_inner)
    if status then return result else return {} end
end

function GetCityProduction(pCity)
    local function get_prod_inner()
        if not pCity then return "Idle (No City)" end
        local buildQueue = pCity:GetBuildQueue()
        if not buildQueue then return "Idle (No Queue)" end
        
        -- Try CurrentlyBuilding() first (if available)
        if buildQueue.CurrentlyBuilding then
            local name = buildQueue:CurrentlyBuilding()
            if name and name ~= "" then return name end
        end

        local hash = 0
        if buildQueue.GetCurrentProductionTypeHash then
            hash = buildQueue:GetCurrentProductionTypeHash()
        end
        
        if hash == 0 then return "Idle (Hash 0)" end
        
        -- Try Units
        if GameInfo.Units then
            for row in GameInfo.Units() do
                if row.Hash == hash then return "Unit: " .. row.Name end
            end
        end
        -- Try Buildings
        if GameInfo.Buildings then
            for row in GameInfo.Buildings() do
                if row.Hash == hash then return "Building: " .. row.Name end
            end
        end
        -- Try Districts
        if GameInfo.Districts then
            for row in GameInfo.Districts() do
                if row.Hash == hash then return "District: " .. row.Name end
            end
        end
        -- Try Projects
        if GameInfo.Projects then
            for row in GameInfo.Projects() do
                if row.Hash == hash then return "Project: " .. row.Name end
            end
        end
        
        return "Unknown (Hash: " .. tostring(hash) .. ")"
    end

    local status, result = pcall(get_prod_inner)
    if status then return result else return "Unknown (Error)" end
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
                population = pCity:GetPopulation(),
                production = GetCityProduction(pCity)
            })
        end
    end
    return cities
end

-- --- Main Event Handler ---

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
        research = {
            active_tech = GetCurrentResearch(playerID),
            active_civic = GetCurrentCivic(playerID)
        },
        policies = GetActivePolicies(playerID),
        cities = GetSafeCities(playerID)
    }

    -- JSON 직렬화 (재귀적 테이블 처리)
    local function serialize(t)
        local s = "{"
        local first = true
        for k, v in pairs(t) do
            if not first then s = s .. "," end
            first = false
            
            s = s .. '"' .. k .. '":'
            if type(v) == "table" then
                local isArray = (#v > 0)
                if isArray then
                    s = s .. "["
                    for i, val in ipairs(v) do
                        if i > 1 then s = s .. "," end
                        if type(val) == "string" then s = s .. '"' .. val .. '"'
                        elseif type(val) == "number" then s = s .. tostring(val)
                        elseif type(val) == "table" then s = s .. serialize(val)
                        else s = s .. '"unknown"' end
                    end
                    s = s .. "]"
                else
                    s = s .. serialize(v)
                end
            elseif type(v) == "string" then
                local safe_str = v:gsub('"', '\\"'):gsub('\n', '\\n')
                s = s .. '"' .. safe_str .. '"'
            elseif type(v) == "number" then
                s = s .. tostring(v)
            else
                s = s .. '"unknown"'
            end
        end
        return s .. "}"
    end

    local status, json_output = pcall(serialize, data)
    if status then
        print("[CIV6_AI_DATA] " .. json_output)
    else
        print("DataExtractor Error: Serialization failed")
    end
end

Events.LocalPlayerTurnBegin.Add(OnTurnBegin)

print("DataExtractor: Listeners Registered (v2.1)")

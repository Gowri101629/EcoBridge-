const state = {
  mode: "ai",
  city: "",
  selectedCrop: "",
  cities: [],
  crops: [],
  demandRows: [],
  farmers: [],
  climateRisk: null,
  offlineMode: false,
  currentUser: null
};

const OFFLINE_CITIES = [
  { city: "Bengaluru", state_name: "Karnataka", market_name: "Yeshwanthpur APMC" },
  { city: "Pune", state_name: "Maharashtra", market_name: "Pune Gultekdi Market" },
  { city: "Coimbatore", state_name: "Tamil Nadu", market_name: "Uzhavar Sandhai" },
  { city: "Hyderabad", state_name: "Telangana", market_name: "Bowenpally Market" },
  { city: "Delhi", state_name: "Delhi", market_name: "Azadpur Mandi" }
];

const OFFLINE_CROPS = [
  ["Tomato", "Vegetable", "kg", 1], ["Onion", "Vegetable", "kg", 1], ["Potato", "Vegetable", "kg", 1],
  ["Brinjal", "Vegetable", "kg", 1], ["Okra", "Vegetable", "kg", 1], ["Cabbage", "Vegetable", "kg", 1],
  ["Cauliflower", "Vegetable", "kg", 1], ["Carrot", "Vegetable", "kg", 1], ["Beetroot", "Vegetable", "kg", 1],
  ["Spinach", "Leafy", "bunch", 1], ["Coriander", "Leafy", "bunch", 1], ["Methi", "Leafy", "bunch", 1],
  ["Cucumber", "Vegetable", "kg", 1], ["Bottle Gourd", "Vegetable", "kg", 1], ["Bitter Gourd", "Vegetable", "kg", 1],
  ["Pumpkin", "Vegetable", "kg", 1], ["Green Chili", "Vegetable", "kg", 1], ["Capsicum", "Vegetable", "kg", 1],
  ["Banana", "Fruit", "dozen", 1], ["Mango", "Fruit", "kg", 1], ["Papaya", "Fruit", "kg", 1],
  ["Guava", "Fruit", "kg", 1], ["Pomegranate", "Fruit", "kg", 1], ["Watermelon", "Fruit", "kg", 1],
  ["Muskmelon", "Fruit", "kg", 1], ["Rice", "Cereal", "kg", 0], ["Wheat", "Cereal", "kg", 0],
  ["Maize", "Cereal", "kg", 0], ["Ragi", "Millet", "kg", 1], ["Bajra", "Millet", "kg", 1],
  ["Jowar", "Millet", "kg", 1], ["Foxtail Millet", "Millet", "kg", 1], ["Little Millet", "Millet", "kg", 1],
  ["Tur Dal", "Pulse", "kg", 1], ["Moong Dal", "Pulse", "kg", 1], ["Urad Dal", "Pulse", "kg", 1],
  ["Chana", "Pulse", "kg", 1], ["Groundnut", "Oilseed", "kg", 1], ["Sesame", "Oilseed", "kg", 1],
  ["Sunflower", "Oilseed", "kg", 0], ["Mustard", "Oilseed", "kg", 0], ["Soybean", "Oilseed", "kg", 0],
  ["Turmeric", "Spice", "kg", 1], ["Ginger", "Spice", "kg", 1], ["Coriander Seed", "Spice", "kg", 1],
  ["Cumin", "Spice", "kg", 1], ["Fenugreek Seed", "Spice", "kg", 1], ["Coconut", "Plantation", "piece", 0],
  ["Sugarcane", "Cash Crop", "ton", 0], ["Cotton", "Cash Crop", "kg", 0]
].map((c, i) => ({ crop_id: i + 1, crop_name: c[0], category: c[1], preferred_unit: c[2], is_organic_priority: c[3] }));

const climateByCity = {
  Bengaluru: { risk: "Heat stress with irregular rain windows", actions: ["Use drip irrigation and mulching.", "Increase compost use.", "Use pest traps after sudden rain."] },
  Pune: { risk: "Dry spells and hot afternoons", actions: ["Adopt staggered sowing.", "Use short-duration varieties.", "Store rainwater."] },
  Coimbatore: { risk: "Variable rain and pest pressure", actions: ["Improve drainage.", "Use bio-input pest management.", "Rotate with pulses."] },
  Hyderabad: { risk: "High summer temperatures", actions: ["Use mulched beds.", "Choose drought-tolerant rotations.", "Increase soil organic matter."] },
  Delhi: { risk: "Heatwave and sudden weather swings", actions: ["Shift sowing windows.", "Protect topsoil with residue cover.", "Use precise irrigation."] }
};

const citySelect = document.getElementById("citySelect");
const modeSelect = document.getElementById("modeSelect");
const cityButtons = document.getElementById("cityButtons");
const modeBanner = document.getElementById("modeBanner");
const summaryCards = document.getElementById("summaryCards");
const catalogSectionRows = document.getElementById("catalogueRows");
const priceRows = document.getElementById("priceRows");
const allCropRows = document.getElementById("allCropRows"); // Still available in Catalog View 

const currentCrop = document.getElementById("currentCrop");
const soilType = document.getElementById("soilType");
const rotationBtn = document.getElementById("rotationBtn");
const rotationOutput = document.getElementById("rotationOutput");
const climateOutput = document.getElementById("climateOutput");
const beginnerGuide = document.getElementById("beginnerGuide");

// AI Chat elements
const aiSections = document.getElementById("aiSections");
const questionInput = document.getElementById("questionInput");
const voiceBtn = document.getElementById("voiceBtn");
const askBtn = document.getElementById("askBtn");
const voiceStatus = document.getElementById("voiceStatus");
const aiAnswer = document.getElementById("aiAnswer");

// Form elements
const farmerForm = document.getElementById("farmerForm");
const farmerStatus = document.getElementById("farmerStatus");
const farmerAdminRows = document.getElementById("farmerAdminRows");
const farmerName = document.getElementById("farmerName");
const farmerSoil = document.getElementById("farmerSoil");
const farmerExp = document.getElementById("farmerExp");
const farmerEmail = document.getElementById("farmerEmail");
const farmerPhone = document.getElementById("farmerPhone");
const farmerCrops = document.getElementById("farmerCrops");

// UI Sections / Tabs
const loginPage = document.getElementById("loginPage");
const signupPage = document.getElementById("signupPage");
const homePage = document.getElementById("homePage");

// Home Display Items
const farmerNameDisplay = document.getElementById("farmerNameDisplay");
const farmerLocationDisplay = document.getElementById("farmerLocationDisplay");
const farmerExpDisplay = document.getElementById("farmerExpDisplay");

function seededInt(key, low, high) {
  let hash = 0;
  for (let i = 0; i < key.length; i += 1) {
    hash = (hash * 31 + key.charCodeAt(i)) >>> 0;
  }
  const span = high - low + 1;
  return low + (hash % span);
}

function todayDate() {
  return new Date().toISOString().slice(0, 10);
}

function getOfflineFarmers() {
  const raw = localStorage.getItem("farmbridge_farmers");
  return raw ? JSON.parse(raw) : [];
}

function setOfflineFarmers(rows) {
  localStorage.setItem("farmbridge_farmers", JSON.stringify(rows));
}

async function apiGet(url) {
  if (state.offlineMode) {
    if (url === "/api/cities") return { cities: OFFLINE_CITIES };
    if (url === "/api/crops") return { count: OFFLINE_CROPS.length, crops: OFFLINE_CROPS };
    if (url.startsWith("/api/cities/") && url.includes("/demand")) {
      const u = new URL(url, "https://x.local");
      const city = decodeURIComponent(url.split("/")[3]);
      const cropIdQuery = u.searchParams.get("crop_id");
      const market = OFFLINE_CITIES.find((c) => c.city === city)?.market_name || "Market";
      let crops = OFFLINE_CROPS.map((crop) => {
        const score = seededInt(`${city}:${crop.crop_name}:score`, 48, 97);
        const price = seededInt(`${city}:${crop.crop_name}:price`, 20, 180);
        const premium = crop.is_organic_priority ? seededInt(`${city}:${crop.crop_name}:prem`, 8, 35) : 0;
        return {
          ...crop,
          demand_score: score,
          average_price_inr: price,
          organic_profit_pct: premium,
          city,
          market_name: market,
          last_updated: todayDate()
        };
      }).sort((a, b) => {
        if (a.is_organic_priority !== b.is_organic_priority) return b.is_organic_priority - a.is_organic_priority;
        return b.demand_score - a.demand_score;
      });
      if (cropIdQuery) {
        crops = crops.filter((c) => String(c.crop_id) === String(cropIdQuery));
      }
      return { city, count: crops.length, crops };
    }
    if (url === "/api/farmers") {
      const rows = getOfflineFarmers().map((f) => ({
        full_name: f.full_name,
        city: f.city,
        soil_type: f.soil_type,
        farming_experience_years: f.farming_experience_years,
        email: f.email,
        phone: f.phone
      }));
      return { farmers: rows };
    }
    return {};
  }

  const response = await fetch(url);
  if (!response.ok) throw new Error(`GET ${url} failed`);
  return response.json();
}

async function apiPost(url, payload) {
  if (state.offlineMode) {
    if (url === "/api/farmers") {
      const rows = getOfflineFarmers();
      const farmer = { ...payload, farmer_id: Date.now() };
      rows.push(farmer);
      setOfflineFarmers(rows);
      return { message: "farmer created", farmer_id: farmer.farmer_id };
    }
    if (url === "/api/ai/ask") {
      return { answer: localAiAnswer(payload.question || "", payload.city || state.city), provider: "offline" };
    }
    return { message: "offline ok" };
  }

  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || `POST ${url} failed`);
  return data;
}

function localAiAnswer(question, city) {
  const top = state.demandRows.find((row) => row.is_organic_priority) || state.demandRows[0];
  const q = question.toLowerCase();
  if (q.includes("which crop") || q.includes("demand")) {
    return `In ${city}, prioritize ${top.crop_name}. Demand score is ${Number(top.demand_score).toFixed(1)} and average price is ₹${Number(top.average_price_inr).toFixed(0)}. Organic cultivation can improve profit margin.`;
  }
  if (q.includes("climate")) {
    const c = climateByCity[city] || climateByCity.Bengaluru;
    return `Climate risk in ${city}: ${c.risk}. Immediate adaptation: ${c.actions[0]} ${c.actions[1]}`;
  }
  return `For ${city}, use sustainable practices: compost, crop rotation, and water-efficient irrigation. Start small, track weekly profit, and scale crops with higher demand.`;
}

async function init() {
  try {
    const [citiesRes, cropsRes] = await Promise.all([apiGet("/api/cities"), apiGet("/api/crops")]);
    state.cities = citiesRes.cities;
    state.crops = cropsRes.crops;
  } catch (error) {
    console.error("Falling back to local data...", error);
    state.offlineMode = true;
    const citiesRes = await apiGet("/api/cities");
    const cropsRes = await apiGet("/api/crops");
    state.cities = citiesRes.cities;
    state.crops = cropsRes.crops;
  }

  state.city = state.cities[0]?.city || "Bengaluru";
  setupCityControls();
  setupCropSelect();
  bindEvents();
  await loadCityData();
  renderAll();
}

function setupCityControls() {
  citySelect.innerHTML = state.cities.map((item) => `<option value="${item.city}">${item.city}</option>`).join("");
  citySelect.value = state.city;
  renderCityButtons();
}

function renderCityButtons() {
  cityButtons.innerHTML = state.cities
    .map((item) => `<button type="button" class="chip ${item.city === state.city ? "active" : ""}" data-city="${item.city}">${item.city}</button>`)
    .join("");
  cityButtons.querySelectorAll("button[data-city]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      state.city = btn.dataset.city;
      state.selectedCrop = "";
      citySelect.value = state.city;
      renderCityButtons();
      await loadCityData();
      renderAll();
    });
  });
}

function setupCropSelect() {
  currentCrop.innerHTML = state.crops.map((crop) => `<option value="${crop.crop_name}">${crop.crop_name}</option>`).join("");
}

function bindEvents() {
  citySelect.addEventListener("change", async () => {
    state.city = citySelect.value;
    state.selectedCrop = "";
    renderCityButtons();
    await loadCityData();
    renderAll();
  });
  modeSelect.addEventListener("change", () => {
    state.mode = modeSelect.value;
    renderMode();
  });
  askBtn.addEventListener("click", answerQuestion);
  voiceBtn.addEventListener("click", startVoiceInput);
  rotationBtn.addEventListener("click", renderRotation);
  farmerForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    await saveFarmer();
  });
}

async function loadCityData() {
  const climateCropParam = state.selectedCrop ? `&crop_name=${encodeURIComponent(state.selectedCrop)}` : "";
  const [demandRes, climateRes] = await Promise.all([
    apiGet(`/api/cities/${encodeURIComponent(state.city)}/demand?organic_first=true`),
    state.offlineMode
      ? Promise.resolve(null)
      : apiGet(`/api/climate-risk?city=${encodeURIComponent(state.city)}${climateCropParam}`)
  ]);
  state.demandRows = demandRes.crops;
  state.climateRisk = climateRes;
}

async function loadFarmerRegistry() {
  const farmersRes = await apiGet("/api/farmers");
  state.farmers = farmersRes.farmers || [];
}

function renderAll() {
  renderMode();
  renderSummary();
  renderAllCropsTable();
  renderCatalogue();
  renderPrices();
  renderClimate();
  renderBeginnerGuide();
  renderRotation();
  renderFarmerRegistry();
}

function selectedDemandRows() {
  if (!state.selectedCrop) return [];
  return state.demandRows.filter((row) => row.crop_name === state.selectedCrop);
}

function renderSummary() {
  if (!state.selectedCrop) {
    summaryCards.innerHTML = "<p class=\"hint\">Select a crop to view demand, market price, and organic profit details.</p>";
    return;
  }
  const row = selectedDemandRows()[0];
  if (!row) {
    summaryCards.innerHTML = "<p class=\"hint\">No data found for selected crop in this city.</p>";
    return;
  }
  const premium = row.is_organic_priority ? `+${Number(row.organic_profit_pct).toFixed(1)}%` : "Not prioritized";
  summaryCards.innerHTML = `
    <article class="summary-card"><p>Crop</p><h3>${row.crop_name}</h3></article>
    <article class="summary-card"><p>Demand Score</p><h3>${Number(row.demand_score).toFixed(1)}</h3></article>
    <article class="summary-card"><p>Avg Market Price</p><h3>₹${Number(row.average_price_inr).toFixed(0)}</h3></article>
    <article class="summary-card"><p>Organic Profit</p><h3>${premium}</h3></article>`;
}

function renderAllCropsTable() {
  // Update tabular view in the Catalog Tab
  allCropRows.innerHTML = state.demandRows.map((row) => {
    const organic = row.is_organic_priority ? "Yes" : "No";
    return `
      <tr>
        <td>${row.crop_name}</td>
        <td>${row.category}</td>
        <td>${Number(row.demand_score).toFixed(1)}</td>
        <td>₹${Number(row.average_price_inr).toFixed(0)}</td>
        <td>${organic}</td>
        <td><button type="button" class="mini-btn select-crop-btn" data-crop="${row.crop_name}">Select</button></td>
      </tr>`;
  }).join("");

  allCropRows.querySelectorAll(".select-crop-btn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      // Find full row data
      const cropNameBtn = btn.dataset.crop;
      state.selectedCrop = cropNameBtn;

      // Navigate logically to Catalog Top to view details
      switchTab('viewCatalog');
      window.scrollTo(0, 0);

      await loadCityData();
      renderAll();
    });
  });

}

function renderMode() {
  const aiEnabled = state.mode === "ai";
  aiSections.classList.toggle("hidden", !aiEnabled);
}

function renderCatalogue() {
  const rows = selectedDemandRows();
  if (rows.length === 0) {
    catalogSectionRows.innerHTML = "<tr><td colspan=\"6\">Select a crop to view catalogue details.</td></tr>";
    return;
  }
  catalogSectionRows.innerHTML = rows.map((row) => {
    const cropType = row.is_organic_priority ? "Organic Priority" : "Standard";
    const premium = row.is_organic_priority ? `+${Number(row.organic_profit_pct).toFixed(1)}%` : "-";
    return `<tr><td>${row.crop_name}</td><td>${cropType}</td><td>${Number(row.demand_score).toFixed(1)}</td><td>₹${Number(row.average_price_inr).toFixed(0)}/${row.preferred_unit}</td><td>${premium}</td><td>${row.market_name}</td></tr>`;
  }).join("");
}

function renderPrices() {
  const rows = selectedDemandRows();
  if (rows.length === 0) {
    priceRows.innerHTML = "<tr><td colspan=\"7\">Select a crop to view pricing board.</td></tr>";
    return;
  }
  priceRows.innerHTML = rows.map((row) => {
    const modal = Number(row.average_price_inr);
    const min = Math.max(1, modal - Math.round(modal * 0.12));
    const max = modal + Math.round(modal * 0.12);
    const trend = row.demand_score >= 80 ? "Up" : row.demand_score >= 65 ? "Stable" : "Down";
    return `<tr><td>${row.last_updated}</td><td>${row.market_name}</td><td>${row.crop_name}</td><td>₹${min}</td><td><strong>₹${modal.toFixed(0)}</strong></td><td>₹${max}</td><td>${trend}</td></tr>`;
  }).join("");
}

function renderClimate() {
  if (state.climateRisk) {
    const list = state.climateRisk.actions.map((a) => `<li>${a}</li>`).join("");
    climateOutput.innerHTML = `
      <p><strong>Provider:</strong> ${state.climateRisk.provider}</p>
      <p><strong>Risk Level:</strong> ${state.climateRisk.risk_level} (${state.climateRisk.risk_score}/100)</p>
      <p><strong>Summary:</strong> ${state.climateRisk.summary}</p>
      <p><strong>Adaptation actions:</strong></p>
      <ul>${list}</ul>`;
    return;
  }
  const climate = climateByCity[state.city] || climateByCity.Bengaluru;
  climateOutput.innerHTML = `<p><strong>Risk:</strong> ${climate.risk}</p><p><strong>Adaptation actions:</strong></p><ul>${climate.actions.map((a) => `<li>${a}</li>`).join("")}</ul>`;
}

function renderFarmerRegistry() {
  if (!state.farmers.length) {
    farmerAdminRows.innerHTML = "<tr><td colspan=\"6\">No farmers registered yet.</td></tr>";
    return;
  }
  farmerAdminRows.innerHTML = state.farmers
    .map(
      (f) => `<tr>
        <td>${f.full_name || "-"}</td>
        <td>${f.city || "-"}</td>
        <td>${f.soil_type || "-"}</td>
        <td>${f.farming_experience_years ?? "-"}</td>
        <td>${f.email || "-"}</td>
        <td>${f.phone || "-"}</td>
      </tr>`
    )
    .join("");
}

function renderBeginnerGuide() {
  const top = selectedDemandRows()[0] || state.demandRows.find((row) => row.is_organic_priority) || state.demandRows[0];
  if (!top) return;
  beginnerGuide.innerHTML = `<p><strong>Step 1:</strong> Start with 10-20% of land.</p><p><strong>Step 2:</strong> Improve soil with compost and bio-inputs.</p><p><strong>Step 3:</strong> In ${state.city}, start with <strong>${top.crop_name}</strong> (demand ${Number(top.demand_score).toFixed(1)}).</p><p><strong>Step 4:</strong> Sell directly to improve farmer margin.</p><p><strong>Step 5:</strong> Track cost-profit weekly and scale.</p>`;
}

function rotationPlan(crop, soil) {
  const plans = { Tomato: ["Cowpea", "Ragi", "Onion"], Onion: ["Moong Dal", "Groundnut", "Tomato"], Rice: ["Black Gram", "Sesame", "Rice"], Banana: ["Green Manure", "Turmeric", "Banana"], Groundnut: ["Jowar", "Moong Dal", "Groundnut"] };
  const soilAdvice = { loamy: "Loamy soil supports diverse rotation.", clay: "Clay soil benefits from legumes.", sandy: "Sandy soil needs mulch and legumes.", black: "Black soil performs well with pulse rotations." };
  return { sequence: plans[crop] || ["Legume", "Millet", crop], why: soilAdvice[soil] || soilAdvice.loamy, benefit: "Improves soil fertility and reduces pest recurrence." };
}

function renderRotation() {
  const plan = rotationPlan(currentCrop.value, soilType.value);
  rotationOutput.innerHTML = `<p><strong>Recommended Rotation:</strong> ${plan.sequence.join(" -> ")}</p><p><strong>Why:</strong> ${plan.why}</p><p><strong>Expected Benefit:</strong> ${plan.benefit}</p>`;
}

async function answerQuestion() {
  if (state.mode !== "ai") {
    aiAnswer.innerHTML = "<p>AI Mode is OFF. Switch to AI Mode for assistant answers.</p>";
    return;
  }
  const question = questionInput.value.trim();
  if (!question) {
    aiAnswer.innerHTML = "<p>Enter a farming-related question first.</p>";
    return;
  }
  aiAnswer.innerHTML = "<p>Generating answer...</p>";
  try {
    const response = await apiPost("/api/ai/ask", {
      question,
      city: state.city,
      crop_name: state.selectedCrop || currentCrop.value || null,
      soil_type: soilType.value || null,
      experience_years: Number(farmerExp.value || 1)
    });
    aiAnswer.innerHTML = `<p>${response.answer}</p><p class="hint">Provider: ${response.provider}</p>`;
  } catch (error) {
    aiAnswer.innerHTML = `<p>AI request failed: ${error.message}</p>`;
  }
}

function startVoiceInput() {
  if (state.mode !== "ai") {
    voiceStatus.textContent = "Voice assistant is disabled in Regular Mode.";
    return;
  }
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    voiceStatus.textContent = "Voice input is not supported in this browser. Use Chrome or Edge.";
    return;
  }
  const recognition = new SpeechRecognition();
  recognition.lang = "en-IN";
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;
  voiceStatus.textContent = "Listening... ask your farming question.";
  recognition.onresult = (event) => {
    questionInput.value = event.results[0][0].transcript;
    voiceStatus.textContent = "Voice captured. Click 'Get AI Answer'.";
  };
  recognition.onerror = () => { voiceStatus.textContent = "Voice recognition error. Try again."; };
  recognition.start();
}

async function saveFarmer() {
  const crops = farmerCrops.value.split(",").map((x) => x.trim()).filter(Boolean);
  if (!farmerEmail.value.trim() && !farmerPhone.value.trim()) {
    farmerStatus.textContent = "Provide at least one contact: email or phone.";
    return;
  }
  const selectedCity = state.cities.find((item) => item.city === state.city);
  const payload = {
    full_name: farmerName.value.trim(),
    city: state.city,
    state_name: selectedCity?.state_name || "",
    soil_type: farmerSoil.value,
    farming_experience_years: Number(farmerExp.value),
    email: farmerEmail.value.trim() || null,
    phone: farmerPhone.value.trim() || null,
    crops_harvested: crops,
    season_label: "Current Season",
    harvested_quantity: 100
  };
  try {
    const result = await apiPost("/api/farmers", payload);
    farmerStatus.textContent = `Saved farmer profile successfully. Farmer ID: ${result.farmer_id}`;
    farmerForm.reset();
    farmerExp.value = 1;
    farmerSoil.value = "Loamy";
    await loadCityData();
    await loadFarmerRegistry();
    renderAll();
  } catch (error) {
    farmerStatus.textContent = `Failed to save farmer profile: ${error.message}`;
  }
}

// ----------------------------------------------------
// UI Logic: Forms, Auth & Tabs 
// ----------------------------------------------------
function showSignup() {
  loginPage.style.display = "none";
  signupPage.style.display = "block";
}

function showLogin() {
  signupPage.style.display = "none";
  loginPage.style.display = "block";
}

function login(btn) {
  const inputEl = document.getElementById("loginInput").value;
  btn.innerHTML = '<div class="loader"></div>';
  btn.disabled = true;

  setTimeout(() => {
    loginPage.style.display = "none";
    homePage.style.display = "block";
    btn.innerHTML = 'Login';
    btn.disabled = false;

    // Check if the user exists in our registry
    const existingFarmer = state.farmers.find(f => f.email === inputEl || f.phone === inputEl || f.full_name === inputEl);
    if (existingFarmer) {
      state.currentUser = existingFarmer;
      farmerNameDisplay.textContent = existingFarmer.full_name || "-";
      farmerLocationDisplay.textContent = existingFarmer.city || "-";
      farmerExpDisplay.textContent = (existingFarmer.farming_experience_years || "0") + " Years";

      // Populate profile edit form and show harvested crops
      farmerName.value = existingFarmer.full_name || "";
      farmerEmail.value = existingFarmer.email || "";
      farmerPhone.value = existingFarmer.phone || "";
      farmerExp.value = existingFarmer.farming_experience_years || "1";
      const wrapper = document.getElementById("harvestedCropsWrapper");
      if (wrapper) wrapper.style.display = "block";
      farmerSubmit.textContent = "Update Profile";

      // Auto-set the city logic 
      if (existingFarmer.city) {
        state.city = existingFarmer.city;
        citySelect.value = state.city;
      }
    } else {
      farmerNameDisplay.textContent = inputEl || "Guest Farmer";
      farmerLocationDisplay.textContent = state.city;
      farmerExpDisplay.textContent = "N/A";

      // Reset profile edit form
      farmerName.value = "";
      farmerEmail.value = "";
      farmerPhone.value = "";
      const wrapper = document.getElementById("harvestedCropsWrapper");
      if (wrapper) wrapper.style.display = "none";
      farmerSubmit.textContent = "Register Profile";
    }

    // Reload UI state with logged-in user city 
    loadCityData().then(() => {
      setupCityControls();
      renderAll();
    });

  }, 1000);
}

function signup(btn) {
  btn.innerHTML = '<div class="loader"></div>';
  btn.disabled = true;

  let nameVal = document.getElementById("signupName").value;
  let locVal = document.getElementById("signupLocation").value;
  let expVal = document.getElementById("signupExperience").value || "1";
  let phoneVal = document.getElementById("signupPhone").value;

  const payload = {
    full_name: nameVal || "New Farmer",
    city: locVal || state.city,
    state_name: "",
    soil_type: "Loamy",
    farming_experience_years: Number(expVal),
    email: null,
    phone: phoneVal || null,
    crops_harvested: [],
    season_label: "Current Season",
    harvested_quantity: 0
  };

  // Create asynchronously and log in 
  apiPost("/api/farmers", payload).then(res => {
    return loadFarmerRegistry();
  }).then(() => {
    signupPage.style.display = "none";
    homePage.style.display = "block";
    btn.innerHTML = 'Create Account';
    btn.disabled = false;

    state.currentUser = payload;
    farmerNameDisplay.textContent = payload.full_name;
    farmerLocationDisplay.textContent = payload.city;
    farmerExpDisplay.textContent = payload.farming_experience_years + " Years";

    state.city = payload.city;
    citySelect.value = state.city;
    loadCityData().then(() => {
      setupCityControls();
      renderAll();
    });
  }).catch(err => {
    console.error("Signup error", err);
    btn.innerHTML = 'Error! Try Again';
    btn.disabled = false;
  });
}

function switchTab(viewId) {
  // Hide all sections
  document.querySelectorAll('.view-section').forEach(el => {
    el.style.display = 'none';
  });
  // Show target
  const target = document.getElementById(viewId);
  if (target) {
    target.style.display = 'block';
  }
}

async function boot() {
  await init();
  await loadFarmerRegistry();
  renderFarmerRegistry();
}

boot();

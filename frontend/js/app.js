// SimpleNutri Web Application Coordinator
document.addEventListener('DOMContentLoaded', () => {
  // App State
  const state = {
    currentTab: 'tab-cycle',
    lastPeriodDate: localStorage.getItem('sn_period_date') || getYesterdayDate(),
    cycleLength: parseInt(localStorage.getItem('sn_cycle_length') || '28', 10),
    pantry: JSON.parse(localStorage.getItem('sn_pantry') || '["ragi", "moong_dal", "palak", "onion", "turmeric"]'),
    selectedRecipes: JSON.parse(localStorage.getItem('sn_selected_recipes') || '["ragi_dosa", "palak_moong_dal"]'),
    currentPhase: null,
    foods: [],
    categories: [],
    cuisines: [],
    dietTypes: []
  };

  function getYesterdayDate() {
    const d = new Date();
    d.setDate(d.getDate() - 3);
    return d.toISOString().split('T')[0];
  }

  // DOM Elements
  const periodDateInput = document.getElementById('period-date');
  const cycleLenInput = document.getElementById('cycle-len');
  const cycleLenVal = document.getElementById('cycle-len-val');
  const calcCycleBtn = document.getElementById('calc-cycle-btn');
  const phaseResultContainer = document.getElementById('phase-result-container');
  
  const foodsGrid = document.getElementById('foods-grid');
  const foodSearchInput = document.getElementById('food-search-input');
  const foodSearchBtn = document.getElementById('food-search-btn');
  const filterCategory = document.getElementById('filter-category');
  const filterCuisine = document.getElementById('filter-cuisine');
  const filterDiet = document.getElementById('filter-diet');
  const filterTag = document.getElementById('filter-tag');

  const pantryCountBadge = document.getElementById('pantry-count-badge');
  const pantryAddInput = document.getElementById('pantry-add-input');
  const pantryAddBtn = document.getElementById('pantry-add-btn');
  const pantryItemsList = document.getElementById('pantry-items-list');
  const quickPantryTags = document.getElementById('quick-pantry-tags');
  const rankedRecipesList = document.getElementById('ranked-recipes-list');

  const shoppingListContainer = document.getElementById('shopping-list-container');
  const copyShoppingBtn = document.getElementById('copy-shopping-btn');
  const clearShoppingBtn = document.getElementById('clear-shopping-btn');

  const foodModal = document.getElementById('food-modal');
  const modalContent = document.getElementById('modal-content');
  const closeModalBtn = document.getElementById('close-modal-btn');

  const apiOutputBox = document.getElementById('api-output-box');
  const responseStatusBadge = document.getElementById('response-status-badge');

  // Initialize Inputs
  periodDateInput.value = state.lastPeriodDate;
  cycleLenInput.value = state.cycleLength;
  cycleLenVal.textContent = state.cycleLength;

  // Tab Navigation
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
      
      btn.classList.add('active');
      const target = btn.getAttribute('data-tab');
      document.getElementById(target).classList.add('active');
      state.currentTab = target;

      if (target === 'tab-foods' && state.foods.length === 0) {
        fetchFoods();
      } else if (target === 'tab-kitchen') {
        renderPantry();
        fetchRankedRecipes();
      } else if (target === 'tab-shopping') {
        renderShoppingList();
      }
    });
  });

  // Cycle Length slider
  cycleLenInput.addEventListener('input', (e) => {
    cycleLenVal.textContent = e.target.value;
    state.cycleLength = parseInt(e.target.value, 10);
    localStorage.setItem('sn_cycle_length', state.cycleLength);
  });

  periodDateInput.addEventListener('change', (e) => {
    state.lastPeriodDate = e.target.value;
    localStorage.setItem('sn_period_date', state.lastPeriodDate);
  });

  // Calculate Cycle Phase
  async function calculatePhase() {
    try {
      calcCycleBtn.textContent = "Calculating...";
      const res = await fetch('/api/v1/cycle/estimate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          last_period_start: state.lastPeriodDate,
          cycle_length_days: state.cycleLength
        })
      });
      if (!res.ok) throw new Error("API error calculating phase");
      const data = await res.json();
      state.currentPhase = data;
      renderPhaseResult(data);
    } catch (err) {
      console.warn("Falling back to client-side cycle calculation", err);
      // Fallback local calculation
      const start = new Date(state.lastPeriodDate);
      const now = new Date();
      const diff = Math.floor((now - start) / (1000 * 60 * 60 * 24));
      const day = (diff < 0 ? 1 : (diff % state.cycleLength) + 1);
      
      let phaseId = "menstrual", phaseName = "Menstrual Phase";
      if (day > 5 && day <= 13) { phaseId = "follicular"; phaseName = "Follicular Phase"; }
      else if (day > 13 && day <= 16) { phaseId = "ovulatory"; phaseName = "Ovulatory Phase"; }
      else if (day > 16) { phaseId = "luteal"; phaseName = "Luteal Phase"; }

      state.currentPhase = {
        estimated_cycle_day: day,
        phase_id: phaseId,
        phase_name: phaseName,
        phase_day_range: `Day ${day} of ${state.cycleLength}`,
        description: "Personalized focus for hormone balance, satiety, and micronutrient replenishment.",
        priority_nutrients: [
          { nutrient_name: "Iron", biological_role: "Replenishes hemoglobin losses and supports cellular respiration.", top_food_sources: ["Cheera", "Spinach", "Ragi", "Bajra"] },
          { nutrient_name: "Magnesium", biological_role: "Relaxes smooth muscle tissue and promotes restorative sleep.", top_food_sources: ["Pumpkin Seeds", "Almonds", "Moong Dal"] },
          { nutrient_name: "Vitamin C", biological_role: "Enhances iron absorption rate and supports antioxidant defenses.", top_food_sources: ["Amla", "Tomatoes", "Papaya"] }
        ],
        dietary_tips: [
          "Focus on nutrient-dense whole grains like millets (Ragi, Bajra) and pulses.",
          "Combine iron-rich leafy greens with a touch of vitamin C (amla or lemon).",
          "Ensure steady hydration with warm broths and soothing herbal teas."
        ]
      };
      renderPhaseResult(state.currentPhase);
    } finally {
      calcCycleBtn.textContent = "Calculate Nutritional Focus";
    }
  }

  calcCycleBtn.addEventListener('click', calculatePhase);

  function renderPhaseResult(phase) {
    phaseResultContainer.style.display = 'block';
    phaseResultContainer.innerHTML = `
      <div class="phase-header-row">
        <div class="phase-title-group">
          <span class="pill-badge">Current Estimated Phase</span>
          <h2>${phase.phase_name}</h2>
          <p style="color: var(--text-secondary); margin-top: 4px;">${phase.description}</p>
        </div>
        <div class="phase-day-badge">
          Day ${phase.estimated_cycle_day} (${phase.phase_day_range})
        </div>
      </div>

      <h3 style="color: white; margin-bottom: 12px; font-size: 1.15rem;">Priority Nutrients & Biological Role</h3>
      <div class="nutrients-grid">
        ${phase.priority_nutrients.map(n => `
          <div class="nutrient-card">
            <h4>${n.nutrient_name}</h4>
            <p>${n.biological_role}</p>
            <div class="sources-list">
              <strong>Top Sources:</strong> ${n.top_food_sources.join(', ')}
            </div>
          </div>
        `).join('')}
      </div>

      <div style="background: rgba(11, 15, 25, 0.5); padding: 18px; border-radius: var(--radius-sm); border: 1px solid var(--border-color); margin-top: 18px;">
        <h4 style="color: var(--accent-warning); margin-bottom: 8px;">💡 Evidence-Based Nutrition Tips</h4>
        <ul style="padding-left: 20px; color: var(--text-secondary); font-size: 0.9rem;">
          ${phase.dietary_tips.map(t => `<li style="margin-bottom: 4px;">${t}</li>`).join('')}
        </ul>
      </div>
    `;
  }

  // Food Database Filters & Listing
  async function loadTaxonomies() {
    try {
      const [catRes, cuiRes, dietRes] = await Promise.all([
        fetch('/api/v1/categories'),
        fetch('/api/v1/cuisines'),
        fetch('/api/v1/diet-types')
      ]);
      if (catRes.ok) {
        state.categories = await catRes.json();
        filterCategory.innerHTML = '<option value="">All Categories</option>' +
          state.categories.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
      }
      if (cuiRes.ok) {
        state.cuisines = await cuiRes.json();
        filterCuisine.innerHTML = '<option value="">All Cuisines</option>' +
          state.cuisines.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
      }
      if (dietRes.ok) {
        state.dietTypes = await dietRes.json();
        filterDiet.innerHTML = '<option value="">All Diets</option>' +
          state.dietTypes.map(d => `<option value="${d.id}">${d.name}</option>`).join('');
      }
    } catch (e) {
      console.warn("Could not load taxonomies", e);
    }
  }

  async function fetchFoods() {
    foodsGrid.innerHTML = '<div style="color: var(--text-muted); grid-column: 1/-1; text-align: center; padding: 40px;">Loading foods...</div>';
    
    const params = new URLSearchParams({ page: '1', page_size: '40' });
    if (filterCategory.value) params.append('category', filterCategory.value);
    if (filterCuisine.value) params.append('cuisine', filterCuisine.value);
    if (filterDiet.value) params.append('diet', filterDiet.value);
    if (filterTag.value) params.append('tag', filterTag.value);

    try {
      const res = await fetch(`/api/v1/foods?${params.toString()}`);
      const data = await res.json();
      state.foods = data.items || [];
      renderFoodsGrid(state.foods);
    } catch (e) {
      foodsGrid.innerHTML = '<div style="color: #ef4444; grid-column: 1/-1; text-align: center;">Failed to load foods from API</div>';
    }
  }

  function renderFoodsGrid(foodsList) {
    if (!foodsList || foodsList.length === 0) {
      foodsGrid.innerHTML = '<div style="color: var(--text-muted); grid-column: 1/-1; text-align: center; padding: 40px;">No foods found matching filters.</div>';
      return;
    }

    foodsGrid.innerHTML = foodsList.map(food => {
      const n = food.nutrition || {};
      return `
        <div class="food-card" data-food-id="${food.id}">
          <div class="food-card-top">
            <span class="food-category-tag">${food.category.replace('_', ' ')}</span>
            <h3>${food.name}</h3>
            <div class="food-aliases">${food.aliases && food.aliases.length > 0 ? food.aliases.slice(0, 3).join(', ') : 'Canonical item'}</div>
          </div>
          <div class="food-card-bottom">
            <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 6px;">
              Per 100g: <strong>${n.energy_kcal ? Math.round(n.energy_kcal) + ' kcal' : '—'}</strong> | 
              Protein: <strong>${n.protein_g ? n.protein_g + 'g' : '—'}</strong>
            </div>
            <div class="nutrient-pills">
              ${n.iron_mg ? `<span class="pill ${n.iron_mg > 3 ? 'highlight' : ''}">Fe ${n.iron_mg}mg</span>` : ''}
              ${n.calcium_mg ? `<span class="pill ${n.calcium_mg > 100 ? 'highlight' : ''}">Ca ${n.calcium_mg}mg</span>` : ''}
              ${n.magnesium_mg ? `<span class="pill ${n.magnesium_mg > 100 ? 'highlight' : ''}">Mg ${n.magnesium_mg}mg</span>` : ''}
              ${n.fiber_g ? `<span class="pill ${n.fiber_g > 8 ? 'highlight' : ''}">Fiber ${n.fiber_g}g</span>` : ''}
            </div>
          </div>
        </div>
      `;
    }).join('');

    // Attach click listeners to open food detail modal
    document.querySelectorAll('.food-card').forEach(card => {
      card.addEventListener('click', () => {
        const fid = card.getAttribute('data-food-id');
        openFoodModal(fid);
      });
    });
  }

  // Food Search
  async function searchFoods() {
    const q = foodSearchInput.value.trim();
    if (!q) {
      fetchFoods();
      return;
    }
    try {
      const res = await fetch(`/api/v1/foods/search?q=${encodeURIComponent(q)}`);
      const data = await res.json();
      renderFoodsGrid(data);
    } catch (e) {
      console.warn("Search failed", e);
    }
  }

  foodSearchBtn.addEventListener('click', searchFoods);
  foodSearchInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') searchFoods(); });
  filterCategory.addEventListener('change', fetchFoods);
  filterCuisine.addEventListener('change', fetchFoods);
  filterDiet.addEventListener('change', fetchFoods);
  filterTag.addEventListener('change', fetchFoods);

  // Food Modal
  async function openFoodModal(foodId) {
    foodModal.classList.add('open');
    modalContent.innerHTML = '<div style="text-align: center; padding: 40px;">Loading nutrition detail...</div>';
    try {
      const res = await fetch(`/api/v1/foods/${foodId}`);
      if (!res.ok) throw new Error("Food detail not found");
      const f = await res.json();
      const n = f.nutrition || {};
      modalContent.innerHTML = `
        <span class="pill-badge" style="margin-bottom: 8px;">${f.category.replace('_', ' ')}</span>
        <h2 style="color: white; font-family: var(--font-display); margin-bottom: 6px;">${f.name}</h2>
        <p style="color: var(--text-muted); font-size: 0.9rem; margin-bottom: 16px;">
          <strong>Aliases:</strong> ${f.aliases && f.aliases.length > 0 ? f.aliases.join(', ') : 'None'}
        </p>

        <h4 style="color: var(--accent-primary); margin-bottom: 10px;">Authoritative Nutrition Profile (Per 100g)</h4>
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; background: rgba(11, 15, 25, 0.6); padding: 14px; border-radius: var(--radius-sm); font-size: 0.88rem;">
          <div>Energy: <strong>${n.energy_kcal ?? '—'} kcal</strong></div>
          <div>Protein: <strong>${n.protein_g ?? '—'} g</strong></div>
          <div>Carbohydrates: <strong>${n.carbohydrate_g ?? '—'} g</strong></div>
          <div>Fat: <strong>${n.fat_g ?? '—'} g</strong></div>
          <div>Dietary Fiber: <strong>${n.fiber_g ?? '—'} g</strong></div>
          <div>Iron: <strong>${n.iron_mg ?? '—'} mg</strong></div>
          <div>Calcium: <strong>${n.calcium_mg ?? '—'} mg</strong></div>
          <div>Magnesium: <strong>${n.magnesium_mg ?? '—'} mg</strong></div>
          <div>Zinc: <strong>${n.zinc_mg ?? '—'} mg</strong></div>
          <div>Potassium: <strong>${n.potassium_mg ?? '—'} mg</strong></div>
          <div>Folate (B9): <strong>${n.folate_ug ?? '—'} ug</strong></div>
          <div>Vitamin C: <strong>${n.vitamin_c_mg ?? '—'} mg</strong></div>
          <div>Vitamin A: <strong>${n.vitamin_a_ug ?? '—'} ug</strong></div>
          <div>Vitamin B6: <strong>${n.vitamin_b6_mg ?? '—'} mg</strong></div>
        </div>

        <h4 style="color: var(--accent-info); margin: 18px 0 8px;">Provenance & Citation</h4>
        <div style="font-size: 0.8rem; color: var(--text-secondary);">
          ${f.sources && f.sources.length > 0 ? f.sources.map(s => `
            <div style="margin-bottom: 6px;">
              <strong>${s.name}</strong> (${s.version || ''}) — ${s.basis || ''}<br>
              <span style="color: var(--text-muted);">${s.license_status || ''}</span>
            </div>
          `).join('') : 'Canonical Project Dataset'}
        </div>

        <div style="margin-top: 20px; display: flex; gap: 10px;">
          <button class="btn btn-primary btn-sm" onclick="addToPantry('${f.id}')">+ Add to My Kitchen</button>
        </div>
      `;
    } catch (e) {
      modalContent.innerHTML = '<div style="color: #ef4444;">Failed to load detail</div>';
    }
  }

  closeModalBtn.addEventListener('click', () => foodModal.classList.remove('open'));
  foodModal.addEventListener('click', (e) => {
    if (e.target === foodModal) foodModal.classList.remove('open');
  });

  // Global helper for pantry add
  window.addToPantry = function(foodId) {
    if (!state.pantry.includes(foodId)) {
      state.pantry.push(foodId);
      localStorage.setItem('sn_pantry', JSON.stringify(state.pantry));
      renderPantry();
      foodModal.classList.remove('open');
      alert(`Added to Kitchen Pantry!`);
    } else {
      alert(`Already in your Kitchen Pantry.`);
    }
  };

  // Kitchen Pantry & Recipe Matcher
  const quickItems = [
    { id: "ragi", name: "Ragi" },
    { id: "moong_dal", name: "Moong Dal" },
    { id: "urad_dal", name: "Urad Dal" },
    { id: "rice", name: "Rice" },
    { id: "palak", name: "Spinach (Palak)" },
    { id: "cheera", name: "Cheera (Amaranth)" },
    { id: "tomato", name: "Tomato" },
    { id: "onion", name: "Onion" },
    { id: "ginger", name: "Ginger" },
    { id: "garlic", name: "Garlic" },
    { id: "coconut_oil", name: "Coconut Oil" },
    { id: "ghee", name: "Ghee" },
    { id: "oats", name: "Oats" },
    { id: "chia_seeds", name: "Chia Seeds" },
    { id: "curd", name: "Curd/Yogurt" },
    { id: "almonds", name: "Almonds" },
    { id: "chickpea", name: "Chickpeas" },
    { id: "sweet_potato", name: "Sweet Potato" },
    { id: "beetroot", name: "Beetroot" }
  ];

  function renderQuickTags() {
    quickPantryTags.innerHTML = quickItems.map(item => `
      <span class="quick-tag-chip" data-id="${item.id}">+ ${item.name}</span>
    `).join('');

    quickPantryTags.querySelectorAll('.quick-tag-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        const id = chip.getAttribute('data-id');
        if (!state.pantry.includes(id)) {
          state.pantry.push(id);
          saveAndRefreshPantry();
        }
      });
    });
  }

  function renderPantry() {
    pantryCountBadge.textContent = `${state.pantry.length} items`;
    if (state.pantry.length === 0) {
      pantryItemsList.innerHTML = '<div style="color: var(--text-muted); font-size: 0.85rem; padding: 12px 0;">Your pantry is currently empty. Use the quick tags or search above to add items.</div>';
      return;
    }

    pantryItemsList.innerHTML = state.pantry.map(id => `
      <div class="pantry-item">
        <span style="text-transform: capitalize;">${id.replace(/_/g, ' ')}</span>
        <button class="pantry-item-del" data-del-id="${id}">&times;</button>
      </div>
    `).join('');

    pantryItemsList.querySelectorAll('.pantry-item-del').forEach(btn => {
      btn.addEventListener('click', () => {
        const delId = btn.getAttribute('data-del-id');
        state.pantry = state.pantry.filter(x => x !== delId);
        saveAndRefreshPantry();
      });
    });
  }

  function saveAndRefreshPantry() {
    localStorage.setItem('sn_pantry', JSON.stringify(state.pantry));
    renderPantry();
    fetchRankedRecipes();
  }

  const pantryDropdown = document.getElementById('pantry-autocomplete-dropdown');
  let autocompleteTimer = null;

  if (pantryDropdown) {
    pantryAddInput.addEventListener('input', (e) => {
      const q = e.target.value.trim();
      clearTimeout(autocompleteTimer);
      if (!q || q.length < 2) {
        pantryDropdown.classList.remove('open');
        pantryDropdown.innerHTML = '';
        return;
      }

      autocompleteTimer = setTimeout(async () => {
        try {
          const res = await fetch(`/api/v1/ingredients/autocomplete?q=${encodeURIComponent(q)}&limit=8`);
          if (!res.ok) return;
          const items = await res.json();
          if (items.length === 0) {
            pantryDropdown.classList.remove('open');
            return;
          }

          pantryDropdown.innerHTML = items.map(item => `
            <div class="autocomplete-item" data-id="${item.id}" data-name="${item.name}">
              <div>
                <span class="autocomplete-item-name">${item.name}</span>
                ${item.matched_alias ? `<span class="autocomplete-item-alias">(${item.matched_alias})</span>` : ''}
              </div>
              <span class="autocomplete-item-cat">${item.category ? item.category.replace('_', ' ') : ''}</span>
            </div>
          `).join('');

          pantryDropdown.classList.add('open');

          pantryDropdown.querySelectorAll('.autocomplete-item').forEach(el => {
            el.addEventListener('click', () => {
              const fid = el.getAttribute('data-id');
              if (!state.pantry.includes(fid)) {
                state.pantry.push(fid);
                saveAndRefreshPantry();
              }
              pantryAddInput.value = '';
              pantryDropdown.classList.remove('open');
              pantryDropdown.innerHTML = '';
            });
          });
        } catch (err) {
          console.warn('Autocomplete fetch failed', err);
        }
      }, 200);
    });

    document.addEventListener('click', (e) => {
      if (!pantryAddInput.contains(e.target) && !pantryDropdown.contains(e.target)) {
        pantryDropdown.classList.remove('open');
      }
    });
  }

  pantryAddBtn.addEventListener('click', () => {
    const val = pantryAddInput.value.trim().toLowerCase().replace(/\s+/g, '_');
    if (val && !state.pantry.includes(val)) {
      state.pantry.push(val);
      pantryAddInput.value = '';
      if (pantryDropdown) {
        pantryDropdown.classList.remove('open');
        pantryDropdown.innerHTML = '';
      }
      saveAndRefreshPantry();
    }
  });

  async function fetchRankedRecipes() {
    rankedRecipesList.innerHTML = '<div style="color: var(--text-muted); padding: 20px; text-align: center;">Calculating matching recipes...</div>';
    
    const targetTags = state.currentPhase ? state.currentPhase.recommended_tags : ["iron", "calcium", "magnesium"];

    try {
      const res = await fetch('/api/v1/recommendations/recipes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          available_food_ids: state.pantry,
          target_tags: targetTags
        })
      });
      const ranked = await res.json();
      renderRankedRecipes(ranked);
    } catch (e) {
      rankedRecipesList.innerHTML = '<div style="color: #ef4444;">Failed to rank recipes</div>';
    }
  }

  function renderRankedRecipes(recipesList) {
    if (!recipesList || recipesList.length === 0) {
      rankedRecipesList.innerHTML = '<div style="color: var(--text-muted); padding: 20px;">No recipes found.</div>';
      return;
    }

    rankedRecipesList.innerHTML = recipesList.map(item => {
      const r = item.recipe;
      const isSelected = state.selectedRecipes.includes(r.id);
      const is100 = item.match_percentage === 100;
      return `
        <div class="ranked-recipe-card">
          <div class="recipe-card-header">
            <div>
              <span style="font-size: 0.72rem; text-transform: uppercase; color: var(--accent-info); font-weight: 700;">
                ${(r.cuisine || 'Global').replace(/_/g, ' ')}
              </span>
              <h4 style="font-size: 1.15rem; color: white; margin: 2px 0 6px;">${r.name}</h4>
              <p style="font-size: 0.85rem; color: var(--text-secondary);">${r.description || ''}</p>
            </div>
            <span class="match-badge ${is100 ? 'match-100' : 'match-partial'}">
              ${Math.round(item.match_percentage)}% Match
            </span>
          </div>

          <div style="font-size: 0.8rem; color: var(--text-secondary); margin: 8px 0;">
            <strong>Ingredients (${r.ingredients.length}):</strong> ${r.ingredients.map(i => i.food_name || i.food_id).join(', ')}
          </div>

          <div class="missing-items-row">
            ${item.missing_ingredients.length === 0 ? 
              '<span style="color: var(--accent-primary); font-weight: 600;">✓ You have all ingredients in your kitchen!</span>' :
              `<span>Missing (${item.missing_ingredients.length}):</span> ` + item.missing_ingredients.map(m => `<span class="missing-chip">${m.food_name || m.food_id} (${m.quantity}${m.unit})</span>`).join('')
            }
          </div>

          <div style="margin-top: 14px; display: flex; justify-content: flex-end;">
            <button class="btn btn-sm ${isSelected ? 'btn-secondary' : 'btn-primary'} toggle-recipe-btn" data-recipe-id="${r.id}">
              ${isSelected ? '✓ Included in Shopping List' : '+ Add to Shopping Plan'}
            </button>
          </div>
        </div>
      `;
    }).join('');

    rankedRecipesList.querySelectorAll('.toggle-recipe-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const rid = btn.getAttribute('data-recipe-id');
        if (state.selectedRecipes.includes(rid)) {
          state.selectedRecipes = state.selectedRecipes.filter(x => x !== rid);
        } else {
          state.selectedRecipes.push(rid);
        }
        localStorage.setItem('sn_selected_recipes', JSON.stringify(state.selectedRecipes));
        fetchRankedRecipes();
      });
    });
  }

  // Shopping List
  async function renderShoppingList() {
    shoppingListContainer.innerHTML = '<div style="color: var(--text-muted); padding: 40px; text-align: center;">Calculating missing grocery items...</div>';
    
    if (state.selectedRecipes.length === 0) {
      shoppingListContainer.innerHTML = `
        <div style="text-align: center; padding: 40px; color: var(--text-muted);">
          <p>You have not selected any recipes yet.</p>
          <button class="btn btn-primary btn-sm" style="margin-top: 12px;" onclick="document.getElementById('nav-kitchen-btn').click();">
            Browse Kitchen & Recipes
          </button>
        </div>
      `;
      return;
    }

    try {
      const res = await fetch('/api/v1/recommendations/shopping-list', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          selected_recipe_ids: state.selectedRecipes,
          kitchen_inventory_food_ids: state.pantry
        })
      });
      const data = await res.json();
      
      if (!data.items || data.items.length === 0) {
        shoppingListContainer.innerHTML = `
          <div style="text-align: center; padding: 40px; color: var(--accent-primary);">
            <h3>🎉 No purchases needed!</h3>
            <p style="color: var(--text-secondary); margin-top: 6px;">Your kitchen pantry already contains 100% of the ingredients required for all ${data.selected_recipe_count} selected recipes.</p>
          </div>
        `;
        return;
      }

      shoppingListContainer.innerHTML = `
        <div style="margin-bottom: 16px; font-size: 0.9rem; color: var(--text-secondary);">
          Consolidated shopping needs for <strong>${data.selected_recipe_count} recipes</strong> (${data.total_missing_items} unique ingredients to buy):
        </div>
        ${data.items.map((item, idx) => `
          <div class="shopping-item-row" id="shop-row-${idx}">
            <div class="shopping-item-left">
              <input type="checkbox" class="shopping-checkbox" id="check-${idx}">
              <label for="check-${idx}" style="cursor: pointer;">
                <strong style="color: white; font-size: 0.95rem;">${item.food_name}</strong>
                <span style="font-size: 0.8rem; color: var(--text-muted); margin-left: 6px;">[${(item.category || 'general').replace(/_/g, ' ')}]</span>
              </label>
            </div>
            <div style="font-weight: 700; color: var(--accent-primary); font-size: 0.95rem;">
              ${item.quantity} ${item.unit}
            </div>
          </div>
        `).join('')}
      `;

      // Checkbox strikethrough
      shoppingListContainer.querySelectorAll('.shopping-checkbox').forEach(cb => {
        cb.addEventListener('change', (e) => {
          const row = e.target.closest('.shopping-item-row');
          if (e.target.checked) {
            row.style.opacity = '0.4';
            row.style.textDecoration = 'line-through';
          } else {
            row.style.opacity = '1';
            row.style.textDecoration = 'none';
          }
        });
      });

    } catch (e) {
      shoppingListContainer.innerHTML = '<div style="color: #ef4444;">Failed to generate shopping list</div>';
    }
  }

  // Copy shopping list to clipboard
  copyShoppingBtn.addEventListener('click', async () => {
    try {
      const res = await fetch('/api/v1/recommendations/shopping-list', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          selected_recipe_ids: state.selectedRecipes,
          kitchen_inventory_food_ids: state.pantry
        })
      });
      const data = await res.json();
      if (!data.items || data.items.length === 0) {
        alert("No missing items to copy!");
        return;
      }
      const text = "🛒 SimpleNutri Shopping List:\n" +
        data.items.map(i => `• ${i.food_name}: ${i.quantity} ${i.unit}`).join('\n');
      await navigator.clipboard.writeText(text);
      alert("Shopping list copied to clipboard!");
    } catch (e) {
      alert("Could not copy list.");
    }
  });

  clearShoppingBtn.addEventListener('click', () => {
    if (confirm("Clear all selected recipes from shopping plan?")) {
      state.selectedRecipes = [];
      localStorage.setItem('sn_selected_recipes', JSON.stringify(state.selectedRecipes));
      renderShoppingList();
    }
  });

  // API Explorer Testing
  document.querySelectorAll('.test-api-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const endpoint = btn.getAttribute('data-endpoint');
      responseStatusBadge.textContent = "Executing...";
      responseStatusBadge.className = "badge";
      apiOutputBox.textContent = `Sending GET request to ${endpoint}...`;
      
      try {
        const start = performance.now();
        const res = await fetch(endpoint);
        const duration = Math.round(performance.now() - start);
        const json = await res.json();
        
        responseStatusBadge.textContent = `Status: ${res.status} OK (${duration}ms)`;
        responseStatusBadge.className = "badge match-100";
        apiOutputBox.textContent = JSON.stringify(json, null, 2);
      } catch (err) {
        responseStatusBadge.textContent = "Request Failed";
        responseStatusBadge.className = "badge";
        apiOutputBox.textContent = String(err);
      }
    });
  });

  // Initial Boot
  loadTaxonomies();
  calculatePhase();
  renderQuickTags();
});

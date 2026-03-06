# FarmBridge - Easy Run Options

## Option 1 (No backend, easiest)
- Open this file directly in browser:
  - `/Users/gowrimahesh/Documents/Playground/web/index.html`
- App auto-switches to **OFFLINE MODE**.
- Works without Python/Node/backend.
- Includes 50 crops, 5 cities, demand sorting, city click view, farmer registration (saved in browser localStorage), AI fallback answers, voice input, crop rotation, and climate advice.
- Crop-first flow is enforced: crop data appears only after selecting a crop.
- All crops table is always visible (city-wise ranked), with one-click crop selection for filtered sections.

## Option 2 (Full backend mode)
```bash
cd /Users/gowrimahesh/Documents/Playground
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
python3 backend/server.py
```
Open: http://127.0.0.1:9000

If backend is unavailable, frontend still works in offline mode automatically.

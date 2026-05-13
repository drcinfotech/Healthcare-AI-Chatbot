# Contributing

Thanks for your interest in improving the Healthcare AI Chatbot demo! Here's how to get set up and what we look for in contributions.

## ⚠️ Healthcare-specific contribution rules

Because this is a healthcare demo, contributions touching anything safety-related are held to a higher bar:

1. **Never weaken the safety layer.** If you change `backend/app/safety.py`, you must add tests covering your change.
2. **Every medical-info response must include a `DisclaimerBlock`.** Tests enforce this.
3. **The bot never diagnoses.** Handlers should suggest professional consultation, not conclude what's wrong.
4. **No real medication, doctor, brand, or patient names.** All sample data must be fictional. The `test_no_real_brand_names_in_data` test enforces this.
5. **Be cautious with new emergency keywords.** False positives (over-routing to hotlines) are acceptable; false negatives (missing an emergency) are not. When in doubt, route to the hotline.

## Development setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate           # Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest                              # run tests
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Vite proxies `/api/*` to `http://localhost:8000`, so as long as both servers run on default ports, you're set.

## Adding a new intent

Three places to edit:

**1.** `backend/app/intents.py` — add an `IntentSpec`:
```python
IntentSpec(
    "diet_advice",
    patterns=[r"\b(diet|nutrition|meal\s+plan|what\s+should\s+i\s+eat)\b"],
    keywords=["diet", "nutrition", "meal plan"],
),
```

**2.** `backend/app/chatbot.py` — add a handler:
```python
def _handle_diet_advice(_c, _session):
    return [
        _text("I can share general nutrition guidance, but for personalized diet advice, a registered dietitian or your doctor is the best source."),
        _disclaimer("This is general wellness information only and isn't tailored to your specific health conditions."),
    ], ["Find a dietitian", "Diabetes-friendly meals", "Heart-healthy diet"]

# in ChatbotEngine.respond's handler_map:
"diet_advice": lambda: _handle_diet_advice(c, session),
```

**3.** `backend/test_chatbot.py` — add a test:
```python
def test_intent_diet():
    assert classify("what should I eat for diabetes").intent == "diet_advice"
```

**(Optional)** `frontend/src/components/Blocks.jsx` — only if you're introducing a new block *type*. Existing intents that return text/doctors/medications/etc. need no frontend changes.

## Adding a new block type

1. Add the Pydantic model in `backend/app/models.py`
2. Add a builder helper in `backend/app/chatbot.py`
3. Add a renderer component in `frontend/src/components/Blocks.jsx`
4. Register the renderer in the `Block` dispatcher at the bottom of that file

## Testing

```bash
cd backend
pytest -v
```

All 31+ tests should pass. New features need new tests, especially anything touching safety.

## Code style

- Python: keep functions small, document non-obvious logic
- React: functional components only, Tailwind for styling, no global CSS except `index.css`
- No new dependencies without good reason — every package adds attack surface and maintenance load

## Pull requests

- One topic per PR
- Reference any related issue
- Include test coverage for new behavior
- Update README if you change the public-facing API

### Чеклист перед пушем новой фичи

1. Создай новую ветку от `main`:
   `git checkout -b feat/your-feature-name`

2. Прогони тесты, форматирование, линтер и проверку типов по всему проекту:
   - `pytest -v`
   - `ruff format .`
   - `ruff check . --fix`
   - `mypy app/`

3. Закоммить и отправь ветку в репозиторий:
   - `git add .`
   - `git commit -m "feat: your commit message"`
   - `git push -u origin feat/your-feature-name`

# Reviews & Baselines — <iteration_id>

## Requirements Baseline (Design Input)
- [ ] Выбранные US/UC/NFR перечислены в 01_vision.md
- [ ] Для каждого US есть хотя бы один AT в acceptance.md
- [ ] traceability.md заполнен минимум до "US → AT"
- [ ] Проведён walkthrough (async в issue/PR): scope понятен, противоречий нет

Sign-off: @<you>  Date: YYYY-MM-DD

## Design Baseline (Design Output)
- [ ] 04_architecture.md описывает компоненты + потоки + контракты
- [ ] Все ключевые решения вынесены в ADR (если есть tradeoffs)
- [ ] traceability.md связывает US/UC/NFR → Design → AT
- [ ] Проведён walkthrough дизайна

Sign-off: @<you>  Date: YYYY-MM-DD

## Validation Baseline
- [ ] acceptance.md покрывает весь scope
- [ ] Определён способ прогона AT (ручной/авто) и где смотреть результаты (CI/runbook)
- [ ] Проведена inspection-стадия для критичных PR: тесты зелёные, дефекты исправлены

Sign-off: @<you>  Date: YYYY-MM-DD

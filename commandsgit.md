# Git команды для проекта

## Отправить изменения на GitHub

```bash
git add -A                           # добавить все изменения
git commit -m "описание что изменил" # зафиксировать
git push                             # отправить на GitHub
```

Добавить только конкретный файл:

```bash
git add bot.py
git commit -m "fix: исправил оплату"
git push
```

## Посмотреть что изменилось

```bash
git status           # какие файлы изменены
git diff             # что именно изменилось (построчно)
git log --oneline    # история коммитов
```

## Откатиться к предыдущей версии

Откатить один файл (не весь проект):

```bash
git checkout HEAD~1 -- bot.py        # вернуть bot.py на 1 коммит назад
git commit -m "revert: откатил bot.py"
git push
```

Откатить весь проект на 1 коммит назад (сохранив историю):

```bash
git revert HEAD                      # создаёт новый коммит, отменяющий последний
git push
```

Откатить на конкретный коммит (по хэшу из `git log --oneline`):

```bash
git revert abc1234                   # отменить конкретный коммит
git push
```

## После обновления кода — пересобрать бота

```bash
docker compose up -d --build
```

## Полный цикл: изменил -> залил -> пересобрал

```bash
git add -A && git commit -m "описание" && git push && docker compose up -d --build
```

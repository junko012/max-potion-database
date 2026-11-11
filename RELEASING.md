# Releasing `pokemon.db`

1. Update the data and `CHANGELOG.md`.
2. Pick the version (see `VERSIONING.md`). Same schema → keep `S`, move `AAAA.MM.R` forward. Breaking change → `S+1`.
3. Stamp it: `python scripts/set_version.py database/pokemon.db <S> <AAAA.MM.R>`
4. Validate: `python scripts/validate_db.py database/pokemon.db`
5. Commit, then tag and push: `git tag db-v<S>.<AAAA.MM.R> && git push origin master db-v<S>.<AAAA.MM.R>`
6. The `Release database` workflow validates again (tag must match the version inside the file) and publishes
   `pokemon.db`, `pokemon.db.gz` and `pokemon.db.sha256`.
7. In the app repo (`max-potion`): `python scripts/update-db-lock.py <S>.<AAAA.MM.R>`, commit `db.lock`.

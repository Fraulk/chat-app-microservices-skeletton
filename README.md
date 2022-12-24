
⚠ pour le service d'auth en local: il vous faut node 18+

(avec nvm: `nvm install --lts`)

1. `make npm-install-spa`
2. `make npm-install-auth`
3. `make build-frontend`
4. `docker compose up`

Steps for updating code on front:
1. `/spa/www> npm run build`
2. `/spa/www> docker compose build frontend`
3. Exit containers at project's root and restart with `docker compose up`

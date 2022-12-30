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

## Connexion à l'API

Pour se connecter à l'API de chat, un client peut envoyer une requête WebSocket à l'adresse suivante :

```
ws://<host>/chat/ws
```

## Authentification

Afin d'accéder à l'API, un client doit fournir un jeton d'authentification JWT valide dans un cookie nommé "session". Ce jeton doit être signé avec la clé secrète définie dans l'environnement de l'API (`JWT_SECRET`).

## Envoi de messages

Pour envoyer un message de chat, le client peut envoyer un message texte au format JSON suivant :

```json
{
  "message": "<message>"
}
```

Où `<message>` est le message à envoyer.

## Réception de messages

Lorsqu'un nouveau message de chat est envoyé par un autre client, l'API envoie un message texte au format JSON suivant :

```json
{
  "type": "new_message",
  "id": "<message_id>",
  "client": "<client_id>",
  "message": "<message>",
  "reaction": [
    {
      "reaction": "<reaction>",
      "client": [
        "<client_id_1>",
        "<client_id_2>",
        ...
      ]
    },
    ...
  ],
  "date": "<date>"
}

```

Où :

- `<message_id>` est l'identifiant unique du message.
- `<client_id>` est l'identifiant du client qui a envoyé le message.
- `<message>` est le contenu du message.
- `<reaction>` est le type de réaction au message (par exemple, "like" ou "dislike").
- `<client_id_1>`, `<client_id_2>`, etc. sont les identifiants des clients qui ont réagi au message.
- `<date>` est la date d'envoi du message au format ISO 8601.

## Réactions aux messages

Pour réagir à un message de chat, le client peut envoyer un message texte au format JSON suivant :

```json
{
  "reaction": "<reaction>",
  "id": "<message_id>"
}
```

Où `<reaction>` est le type de réaction au message (par exemple, "like" ou "dislike") et `<message_id>` est l'identifiant unique du message auquel réagir.

Si le client a déjà réagi au message, sa réaction sera retirée. Si le client n'a pas encore réagi au message, sa réaction sera ajoutée.

## Déconnexion

Pour se déconnecter de l'API, le client peut fermer la connexion WebSocket. L'API retirera alors la connexion du client du gestionnaire de connexions et ne diffusera plus de messages au client.

# Ghosted API

Backend for the [Ghosted Website](https://github.com/Kodex-Tech/ghosted_frontend) powered by Flask.


## Setup
### 1) clone code
```bash
git clone https://github.com/Kodex-Tech/ghosted_api.git
cd ghosted_api
```

### 2) install deps
```bash
pip install -r requirements.txt
```

### 2) run server
```bash
python app.py
```

**if no `PORT` environment variable is set the api will serve on port `2500`**

## Endpoins

### Token Data
`GET /api/token?token=<user_token_here>`

*replace `<user_token_here>` with the user's token*

**Response**
```json
{
        "username": username,
        "id": id,
        "verified": verified,
        "premium_type": type,
        "email": email,
        "phone": phone,
        "avatar": avatar,
        "mfa_authentication": mfa,
        "account_created": created,
        "language": language,
        "has_nitro": hasNitro,
        "days_left": days_left if hasNitro else 0,
        "billing_info": billing_info,
        "connections": connections,
        "premium_guilds": boosted_servers,
        "relationships": friends

    }
```

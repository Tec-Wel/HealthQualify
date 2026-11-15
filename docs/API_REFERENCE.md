![Build & extend documentation](assets/category-build.svg)

[← **Documentation home**](README.md) &nbsp; / &nbsp; **Build & extend**

# HTTP API reference — local secure alpha

> **What you'll learn:** Authenticate against the local alpha API, inspect available endpoints, and understand role permissions.

**On this page:** [Start and authenticate](#start-and-authenticate) · [Endpoint catalog (from implementation)](#endpoint-catalog-from-implementation) · [Practical example: register a synthetic system](#practical-example-register-a-synthetic-system) · [Error behavior and boundaries](#error-behavior-and-boundaries)

---

**Status:** implemented local developer-alpha interface in `healthqualify/secure_api.py`. Base URL: `http://127.0.0.1:8877`. Not public, multi-tenant, production, HIPAA-ready, or a regulated approval service.

## Start and authenticate

```bash
python -m healthqualify.appcli --db demo.db init
python -m healthqualify.appcli --db demo.db bootstrap-admin admin_owner
python -m healthqualify.appcli --db demo.db serve
```

Bootstrap prompts for a password (12+ chars) without passing it as an argument. Start the server in a dedicated terminal. On your **own local machine**, use an API client to POST:

```http
POST /login HTTP/1.1
Host: 127.0.0.1:8877
Content-Type: application/json

{"username":"admin_owner","password":"REPLACE_IN_LOCAL_CLIENT"}
```

Response 200: `{"access_token":"<opaque>","token_type":"Bearer","expires_in":3600}`. Treat tokens as secrets. For all protected routes, send `Authorization: Bearer <opaque>`. `POST /logout` revokes the presented token.

## Endpoint catalog (from implementation)

| Method | Path | Permission | Body / response |
| --- | --- | --- | --- |
| GET | `/health` | Public localhost | `{"status":"ok","type":"secure-alpha","regulated":false}` |
| POST | `/login` | Public localhost | `username,password` → token |
| POST | `/logout` | Authenticated read | → `{"revoked":true}` |
| POST | `/users` | admin `users` | `username,password,role` → 201 user |
| POST | `/systems` | admin/validator `write` | `name,intended_use` → 201 system |
| GET | `/systems` | All roles `read` | Array of systems |
| POST | `/protocols` | admin/validator `write` | `system_id,payload` → 201 v0.2 draft |
| GET | `/protocols` | All roles | Array of protocol records |
| POST | `/baselines` | admin/qa `baseline` | `protocol_id,rationale` → baselined event |
| POST | `/runs` | admin/validator `execute` | `protocol_id` → 201 synthetic run |
| GET | `/runs` | All roles | Array of runs |
| GET | `/deviations` | All roles | Array of findings |
| GET | `/audit` | admin/qa `audit` | Array of audit events |
| GET | `/frameworks` | All roles | Regulatory guidance catalog |

**Important:** all POST routes accept JSON objects, with a 1 MiB input-body limit. New protocols must be **v0.2** JSON (not strict v0.3 standalone protocols). The authenticated principal supplies the actor identity; do not trust a user-specified author property.

## Practical example: register a synthetic system

With your token already stored in a local shell variable (do not commit it):

```bash
curl -sS -X POST http://127.0.0.1:8877/systems \
  -H "Authorization: Bearer $HQ_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"name":"Synthetic LIS","intended_use":"Offline training fixture only"}'
curl -sS http://127.0.0.1:8877/systems -H "Authorization: Bearer $HQ_TOKEN"
```

The returned system ID is a UUID. For protocol creation, copy `examples/synthetic_lis_v2/protocol.json`, replace `system.id` with this UUID, and submit the whole parsed JSON object as the `payload`. Reviewers must differ from authors. Baseline events are developer records, not electronic signatures.

## Error behavior and boundaries

| Status | Meaning |
| --- | --- |
| 200/201 | Successful read/write |
| 400 | Invalid JSON, body size or invalid request data |
| 403 | Missing, invalid, expired authentication or insufficient role |
| 404 | Unknown route or missing reference |
| 500 | Server error; details intentionally not leaked |

The service has `Cache-Control: no-store`, `X-Content-Type-Options: nosniff`, and restrictive CSP headers. It does **not** provide TLS, rate limiting, SSO/MFA, protected operational storage, or tenant isolation. Don't expose it to a network or send real PHI. API errors are not evidence of clinical system failure.

See [Integration](INTEGRATION_GUIDE.md), [Security model](SECURITY_MODEL.md), and [CLI reference](CLI_REFERENCE.md).

---

### Continue exploring

[developer architecture](DEVELOPER_ARCHITECTURE.md) · [cli reference](CLI_REFERENCE.md) · [All guides](README.md) · [Project homepage](../README.md)

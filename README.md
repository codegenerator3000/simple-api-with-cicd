# Simple app as warm-up

Entites:
- Market
- City
- Street


Use-Cases:
- Get cities
- Get streets in a city
- Add a market on a street
- Get markets by street, city, and/or open status (1 or 0)

## Diagrams

```mermaid
erDiagram
    CITY ||--o{ STREET : contains
    STREET ||--o{ MARKET : has

    CITY {
        int id PK
        string name
    }
    STREET {
        int id PK
        string name
        int city_id FK
    }
    MARKET {
        int id PK
        string name
        int street_id FK
        string house_number
        time opening_time
        time closing_time
    }
```

Open status (1 or 0) is derived from `opening_time`/`closing_time`, not stored.

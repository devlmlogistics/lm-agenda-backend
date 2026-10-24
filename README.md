# LM Agenda Backend

Flask/Gunicorn API for the LM Driver Agenda testing environment.

Run database migrations before the first deployment:

```sh
python manage_agenda.py migrate
```

Run retention cleanup daily:

```sh
python manage_agenda.py cleanup
```

Testing URL: `https://nocobase.stdc.cl`

## Transport dashboard

The dashboard endpoint is available at `GET /dashboard/transportes`. It requires the
`X-Dashboard-Key` header and accepts an optional `date=YYYY-MM-DD` query parameter.
When no date is supplied, it returns today's and future in-progress transports in
`America/Los_Angeles`; a selected past date also includes completed transports.

Set a dashboard-only secret in `DASHBOARD_KEY`. Keep it different from
`SUPERVISOR_KEY` and share it only in the dashboard URL used by the monitoring
operator (the frontend removes the key from the visible URL after loading it).


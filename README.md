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


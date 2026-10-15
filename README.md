# Company Website

A small corporate website built with Django, plus a management panel I wrote from scratch so the person running the site never has to touch HTML or CSS.

I built it for the common case: a company that wants a clean site with a blog and a portfolio, and wants to change the colors, fonts, pictures and footer links without calling a developer. It is deliberately plain Django: function and class views, ordinary forms and templates, SQLite, a little vanilla JavaScript. No REST framework, no frontend build step, no Django Admin.

## What it does

**The public site**
- Home, About Us, Articles (list and detail), Our Work (portfolio), Contact Us, and proper 403/404/500 pages
- Responsive layout that works on phones, tablets and desktops
- Everything visitors read is in English

**The panel at `/manage/`**
- **Dashboard** with quick counts and the latest messages
- **Articles**: draft or published, slug, short description, featured image, SEO title and meta description. Each article can carry images, video and audio
- **Portfolio**: add, edit, hide or delete projects, each with an image and an optional link
- **Website content**: hero text, intro, services, about page, contact texts, footer text
- **Appearance**: colors, fonts (you can upload your own), text sizes, spacing, hero and image settings. Changes show up on the site straight away, no restart needed
- **Navigation & footer**: menu links, footer columns and links, with order and on/off switches
- **Contact messages**: read them, reply to them, mark them, delete them
- **Account**: change your password, log out

**Restoring defaults.** On the Appearance page there is a "Restore default values" box. Tick only what you want back to the original (colors, fonts, text sizes, layout, image sizes and shapes, or the site pictures) and the rest stays exactly as you left it.

## Replying to messages

When someone fills in the contact form, the message is saved. In the panel you open it, write your answer and press **Send Reply**. The visitor gets an email with your reply and a copy of what they originally wrote.

The order matters here: your reply is saved first, and only then is the email sent. If sending fails (wrong password, no connection, whatever), you see the error, nothing is lost, the message does not get marked as replied, and you can just press the button again.

The visitor's address is only ever used as the recipient. The "from" address comes from your settings, and anything the visitor typed is escaped before it goes into the HTML email.

## Getting it running

You need Python 3.10 or newer.

```bash
python -m venv venv
venv\Scripts\activate              # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt

copy .env.example .env             # macOS/Linux: cp .env.example .env
```

Open `.env` and fill it in (see the next section), then:

```bash
python manage.py makemigrations site_module article_module contact_module portfolio_module
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo
python manage.py runserver
```

The site is at http://127.0.0.1:8000/ and the panel at http://127.0.0.1:8000/manage/. Sign in with the account you made with `createsuperuser`. Any user with "staff status" can get in.

A few notes on those commands:
- The migration files are not included in the download. `makemigrations` creates them on your machine the first time, and you should keep them in version control afterwards.
- `seed_demo` is optional. It adds a menu, a footer, three placeholder services, four sample articles and six sample portfolio items with pictures, so you are not staring at an empty site. It never overwrites anything you changed, and you can run it again whenever you like.
- Delete or edit the sample content from the panel as soon as you have real content.

## The `.env` file

Secrets live in `.env`, which is never committed (it is in `.gitignore`). `.env.example` shows every setting with placeholder values.

For a local run you only need two lines:

```
DJANGO_DEBUG=True
DJANGO_SECRET_KEY=any-long-random-string
```

You can generate a proper key with:

```bash
python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"
```

If `DJANGO_DEBUG` is `True` and you leave the key out, the site still starts with a throwaway development key. With `DJANGO_DEBUG=False` it refuses to start without a real one, on purpose.

### Email

Replies go out through SMTP. For Gmail:

```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=you@gmail.com
EMAIL_HOST_PASSWORD=your-16-letter-app-password
DEFAULT_FROM_EMAIL=you@gmail.com
```

Gmail will not accept your normal password here. Turn on 2-step verification, then create an **App password** in your Google account and use that, written without spaces. No `.env` quotes, no spaces around `=`. Restart the server after editing `.env`; it is only read at startup.

If you just want to click through the screens without a mail account, add this line and replies will be printed in the terminal instead of delivered:

```
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

## Tests

```bash
python manage.py test
```

There are tests for who can reach the panel, the article life cycle (draft, publish, unpublish, delete), hidden portfolio items, link and color validation, the contact form and its spam trap, sending a reply, a failed send, and restoring defaults. I wrote them alongside the code, but I could not run them on the machine where the code was written, so treat the first run as a real check and not a formality. If something fails, that is a bug worth fixing.

## What's where

```
config/            settings, root URLs
home_module/       Home, About, error pages
article_module/    articles and their media, public article pages
portfolio_module/  portfolio items, public portfolio pages
contact_module/    contact form and stored messages
site_module/       site texts, services, theme, menu, footer, fonts,
                   the "restore defaults" logic and the seed_demo command
manage_module/     the /manage/ panel: forms, views, URLs
utils/             validators and the email sending helper
templates/ static/
static/default_images/   the neutral placeholder pictures (made by tools/make_default_images.py)
```

## Safety, briefly

- `/manage/` needs a signed-in staff user. Anonymous visitors are sent to the login page, signed-in non-staff users get a 403
- Every form that changes data uses CSRF protection; logout and publish/unpublish are POST-only
- Uploads are checked for extension and size (images 5 MB, video 100 MB, audio 30 MB, fonts 2 MB), and fonts are also checked by their file signature
- Menu, footer and button links must be a site path, an anchor, or start with `http://`, `https://`, `mailto:` or `tel:`. `javascript:` and friends are rejected
- Colors must be real hex values and sizes stay inside sane ranges, so a typo cannot wreck the layout
- Secrets only come from the environment, never from the code

## Putting it on a real server

- `DJANGO_DEBUG=False`, a long random `DJANGO_SECRET_KEY`, and your domain in `DJANGO_ALLOWED_HOSTS` and `DJANGO_CSRF_TRUSTED_ORIGINS` (with `https://`)
- Run `python manage.py collectstatic` and have your web server serve `/static/` from `staticfiles/` and `/media/` from `uploads/`. Django serves `/media/` by itself only in debug mode
- Back up `db.sqlite3` and the `uploads/` folder together. They belong to each other

## Known limits

- Article and portfolio text is plain text with line breaks. There is no rich-text editor on purpose, to keep things simple and safe
- The sample pictures are generated shapes, not photos. Swap them for your own
- SQLite is fine for a company site of this size. If you outgrow it, switching the `DATABASES` setting to PostgreSQL is the usual next step
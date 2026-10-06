# CinemaVerse

CinemaVerse displays South Indian film reviews and saves them in MongoDB database `cinemaverse`, collection `reviews`.

## Run locally on Windows

Start MongoDB Community Server, then run these commands from the project folder:

```bat
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe server.py
```

Open http://127.0.0.1:8000. To inspect local data in Compass, connect to `mongodb://127.0.0.1:27017`.

## Deploy on Vercel

Vercel cannot connect to MongoDB running only on your computer. Use MongoDB Atlas for the live database.

1. Create an Atlas cluster and a database user with a strong password.
2. In Atlas Network Access, allow connections from Vercel. For a small test deployment, `0.0.0.0/0` allows network access from Vercel; protect the database with a strong, least-privilege database user and never expose its password in browser code or GitHub.
3. Copy the Atlas connection string. Replace its password placeholder with the database user's password, URL-encoding special characters as needed. The URI should include the database name, for example `mongodb+srv://USER:PASSWORD@CLUSTER.mongodb.net/cinemaverse?retryWrites=true&w=majority`.
4. Import this GitHub repository into Vercel. Use the repository root and no build command; Vercel serves the HTML and deploys `api/movies.py` as the `/api/movies` function.
5. In Vercel project **Settings → Environment Variables**, add `MONGODB_URI` with the Atlas connection string and `MONGODB_DATABASE` with `cinemaverse`. Apply them to Production (and Preview if needed), save, and redeploy.
6. Open the deployed site and add a review. In Compass, connect using the same Atlas URI to see the live `cinemaverse.reviews` documents. The local Compass connection and Atlas are separate databases.

The API seeds the South Indian starter reviews when the Atlas collection is first accessed and is empty. Local SQLite data is not committed to GitHub; import it separately into Atlas if you need those exact local records.

## Git safety

`.gitignore` excludes the local virtual environment, SQLite database, Vercel project link, and `.env` files. Never commit database credentials. The local server uses `mongodb://127.0.0.1:27017` by default; set `MONGODB_URI` in the environment to override it.

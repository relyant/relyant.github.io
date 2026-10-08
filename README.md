<div align="center">

  <img src="logo.png" alt="Logo" width="150" height="auto" />

  # Personal Journal
  
  <p>
    <strong>A static site built with Jekyll, hosted on GitHub Pages, and managed via a built-in admin app.</strong>
  </p>

</div>

---

### 🚀 How it Works

Posts, images and the vessel location are managed through the built-in
admin app at **/admin/** (works in any browser on Linux and Android).
It talks directly to the GitHub API with a fine-grained personal
access token and commits straight to `main`; GitHub Pages rebuilds
automatically.

1. **Write:** open `/admin/` → *Neuer Post*, write markdown, drop in
   images (auto-resized to 1920px and converted to WebP), publish.
2. **Move:** update the boat's position under *Position* — fields,
   map picker or GPS.
3. **Publish:** GitHub Pages builds the site on every push.

**Directory Structure:**
- `_posts/`: Jekyll posts (written by the admin app)
- `assets/`: images, patches and PDFs
- `assets/tiles/`: self-hosted OSM map tiles (see `scripts/fetch_tiles.py`)
- `admin/`: the admin app
- `specs/`: boat specifications

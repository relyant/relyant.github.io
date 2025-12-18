<div align="center">

  <img src="logo.png" alt="Logo" width="150" height="auto" />

  # Personal Journal
  
  <p>
    <strong>A static site built with Jekyll, hosted on GitHub Pages, and updated via GitJournal.</strong>
  </p>

  <p>
    <a href="https://github.com/YOUR_USERNAME/YOUR_REPO/actions">
      <img src="https://img.shields.io/github/actions/workflow/status/YOUR_USERNAME/YOUR_REPO/publish-journal.yml?label=Journal%20Bot&style=for-the-badge" alt="Bot Status" />
    </a>
    <a href="https://YOUR_CUSTOM_DOMAIN.com">
      <img src="https://img.shields.io/website?label=website&style=for-the-badge&url=https%3A%2F%2FYOUR_CUSTOM_DOMAIN.com" alt="Website Check" />
    </a>
  </p>

</div>

---

### 🚀 How it Works

This repository is fully automated. I write posts on my phone using **GitJournal**, and a GitHub Action handles the rest.

1.  **Draft:** I save a new entry. It uploads detailed `YYYY-MM-DD.md` files to the `_incoming/` folder.
2.  **Process:** The **Journal Bot** wakes up (waits 30s for sync), formats the file, and moves it to `_posts/`.
3.  **Publish:** GitHub Pages builds the site and pushes it live.

**Directory Structure:**
- `_incoming/`: Raw entries from my phone.
- `_posts/`: Processed Jekyll posts.
- `assets/`: Images and media.

# 🎮 Retro-Modern 3D PyGame Web Arcade Suite

A premium, high-performance 3D retro arcade cabinet selection interface and dashboard. This portfolio is built using **React, Vite, and Three.js (React Three Fiber)** and hosts **16 classic arcade games** written in Python (PyGame) and compiled to WebAssembly via **Pygbag**.

The suite includes real-time telemetry metrics, automated high score syncing between desktop and web builds, and immersive retro styling (neon glows, CRT scanlines, responsive controls).

---

## 🚀 Live Demo & Publication

The project is structured to run directly on **GitHub Pages**. Once activated, it serves:
1. **3D Arcade Dashboard**: The main entry point at the root URL.
2. **Interactive WebAssembly PyGame ROMs**: Loaded dynamically via iframe inside the virtual 3D monitor.

---

## ✨ Features

- **Procedural 3D Cabinet**: Rendered dynamically using Three.js primitives to maximize performance (60 FPS) and avoid loading latency.
- **Dynamic Physics & Lighting**: Implements wiggling joysticks, pulsing marquee headers, ambient neon spotlights, and category-themed cabinet colors (e.g., cyan for action, pink for shooter).
- **Glassmorphic Telemetry HUD**: A retro sidebar dashboard showing simulated cabinet vitals (CPU load, GPU temperature, memory utilization, active session playtime).
- **Personal Best Score Tracking**: Automatic high score persistence using:
  - **Desktop (Local)**: Saves to a shared `high_scores.json` file.
  - **Web (GitHub Pages)**: Saves to browser `localStorage` and listens to game frame messages via `postMessage`.
- **Celebration Confetti**: Triggers colorful particle explosions on the dashboard when a new high score is registered.
- **16 Classic Games**: Includes fully playable retro games like *Neon Pac-Man, Space Dodge, Cyber Platformer, Car Racing, Tetris, Snake, Asteroids, Lander, Minesweeper, Breakout, Pong, checkers, Space Invader, Galaxy Fight, and 2048*.

---

## 🛠️ Tech Stack

- **Dashboard Core**: React 19, TypeScript, Vite.
- **3D Graphics Engine**: Three.js, React Three Fiber (R3F), `@react-three/drei`.
- **Styling & UI**: Vanilla CSS (specifically optimized for LightningCSS minification, glassmorphic filters, and neon glowing animations).
- **Game Engine**: Python 3, PyGame Community Edition.
- **Web Compilation**: Pygbag (Emscripten / WebAssembly compiler).

---

## 📂 Project Structure

```text
├── arcade-3d/            # React + Three.js source code
│   ├── src/
│   │   ├── components/   # Procedural 3D Cabinet component
│   │   ├── App.tsx       # Main dashboard layout, state & postMessage score listener
│   │   └── App.css       # Semantic neon styling & layouts
│   └── vite.config.ts    # Configured with relative base path ('./')
├── assets/               # Production assets (built React application)
├── dist/                 # Self-contained packaged production bundle (dashboard + 16 Wasm ROMs)
├── index.html            # Entry point for the 3D Arcade Console (production build)
├── main.py               # Desktop Python Arcade Launcher (Tkinter/Pygame)
├── build_all.py          # Automated build script (compiles games to Wasm & patches CDN references)
├── arcade_api.py         # Scoring API bridge (handles local file writes or web postMessage)
├── [Game Directories]/   # Individual Python PyGame repositories (e.g. Tetris, Space_Dodge, etc.)
└── README.md             # Project documentation
```

---

## 🏃‍♂️ How to Run Locally

### Option 1: Desktop Python Launcher
You can run the full arcade suite natively on your desktop using the Python launcher. It automatically aggregates high scores and updates them in real-time as you play and close games.

1. Ensure you have python installed.
2. Run the main launcher:
   ```bash
   python main.py
   ```
3. Use the arrow keys or GUI to select and launch any game.

### Option 2: 3D Web Dashboard (Development Mode)
To run the React + Three.js application in development mode:

1. Navigate to the `arcade-3d/` directory:
   ```bash
   cd arcade-3d
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
4. Open the displayed local URL (usually `http://localhost:5173`) in your browser.

### Option 3: Local Production Server
To preview the production-compiled version (dashboard + Wasm games) exactly as it will appear on GitHub Pages:

1. Start a local HTTP server at the root directory:
   ```bash
   python -m http.server 8000
   ```
2. Navigate to `http://localhost:8000` in your web browser.

---

## ⚙️ Compilation & Build Automation

If you modify the Python source code of any game and want to recompile it to WebAssembly for the web dashboard:

1. Compile all games with production CDN links and package them:
   ```bash
   python build_all.py --prod --package
   ```
2. Rebuild the React app:
   ```bash
   cd arcade-3d
   npm run build
   ```
3. Copy the built contents from `arcade-3d/dist/assets/` to the root `assets/` directory and update the root `index.html` references if the JS/CSS hashes changed. (The `build_all.py --package` command automatically bundles everything into the `dist/` folder).

---

## 🌐 How to Deploy to GitHub Pages

Since the repository is already pre-built and configured with relative paths at the root, hosting it takes under a minute:

1. Go to your repository on GitHub: `https://github.com/[Your-Username]/PyGame_Projects`.
2. Click on the **Settings** tab at the top.
3. On the left sidebar, click on **Pages** (under Code and automation).
4. Under **Build and deployment**:
   - **Source**: Select **Deploy from a branch**.
   - **Branch**: Select **`main`** and set the folder to **`/ (root)`**.
5. Click **Save**.
6. Within 1-2 minutes, GitHub Pages will deploy your site. You will see a live URL at the top of the page (e.g., `https://[Your-Username].github.io/PyGame_Projects/`). Open it to enjoy your 3D Web Arcade!

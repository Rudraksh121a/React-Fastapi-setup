import os
import subprocess
from pathlib import Path
import textwrap
import json

def main():
    print("⚡ Welcome to FastAPI + React setup wizard ⚡\n")

    # Get project name
    project_name = input("👉 Enter project name (default: myapp): ").strip() or "myapp"
    project_dir = Path(project_name)
    project_dir.mkdir(exist_ok=True)

    # --- Backend setup ---
    backend_dir = project_dir / "backend"
    backend_dir.mkdir(exist_ok=True)

    (backend_dir / "main.py").write_text(textwrap.dedent("""\
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware

        app = FastAPI()

        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        @app.get("/api/hello")
        def read_root():
            return {"message": "Hello from FastAPI backend 🚀"}
    """))
    print("✅ Backend created successfully!\n")

    # --- Frontend setup (interactive) ---
    print("⚙️ Launching React/Vite setup wizard...\n")
    subprocess.run(
        ["npx", "create-launcher"],
        cwd=project_dir,
        check=True,
        stdin=None,
        stdout=None,
        stderr=None
    )

    # --- Detect frontend folder ---
    # find the first folder created inside the project directory
    created_dirs = [d for d in project_dir.iterdir() if d.is_dir() and d.name != "backend"]
    if not created_dirs:
        print("❌ Could not detect frontend folder. Please check the create-launcher output.")
        return
    frontend_dir = created_dirs[0]

    print(f"\n✅ Detected frontend directory: {frontend_dir.name}")

    # --- Modify frontend to connect to backend ---
    app_file = frontend_dir / "src" / "App.jsx"
    if not app_file.exists():
        # fallback for TS or different structure
        app_file = frontend_dir / "src" / "App.tsx"

    if app_file.exists():
        app_file.write_text(textwrap.dedent("""\
            import { useEffect, useState } from 'react'
            

            function App() {
              const [message, setMessage] = useState('Connecting to backend...')

              useEffect(() => {
                fetch('http://localhost:8000/api/hello')
                  .then(res => res.json())
                  .then(data => setMessage(data.message))
                  .catch(() => setMessage('❌ Backend not reachable'))
              }, [])

              return (
                <div style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  height: '100vh',
                  fontFamily: 'sans-serif'
                }}>
                  <h1>⚡ FastAPI + React ⚡</h1>
                  <p>{message}</p>
                </div>
              )
            }

            export default App
        """))
        print("✅ Updated frontend App.jsx to show FastAPI + React message.")
    else:
        print("⚠️ Could not find App.jsx or App.tsx to modify automatically.")

    # --- Add Vite proxy if vite.config.ts or vite.config.js exists ---
    vite_config = None
    for config_name in ["vite.config.ts", "vite.config.js"]:
        config_path = frontend_dir / config_name
        if config_path.exists():
            vite_config = config_path
            break

    if vite_config:
        vite_config.write_text(textwrap.dedent("""\
            import { defineConfig } from 'vite'
            import react from '@vitejs/plugin-react'

            export default defineConfig({
              plugins: [react()],
              server: {
                proxy: {
                  '/api': 'http://localhost:8000',
                },
              },
            })
        """))
        print("✅ Added Vite proxy to forward /api to FastAPI backend.")

    print(textwrap.dedent(f"""
    🎉 All done!

    ▶ Start backend:
        cd {project_name}/backend
        uvicorn main:app --reload

    ▶ Start frontend:
        cd {project_name}/{frontend_dir.name}
        npm run dev

    Then open http://localhost:5173 in your browser 🚀
    """))


if __name__ == "__main__":
    main()

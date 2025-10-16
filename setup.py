import os
import subprocess
from pathlib import Path
import textwrap

def main():
    print("Welcome to FastAPI + React setup wizard\n")

    # --- Project setup ---
    project_name = input("Enter project name (default: myapp): ").strip() or "myapp"
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
            return {"message": "Hello from FastAPI backend"}
    """))
    (backend_dir / "requirements.txt").write_text("fastapi\nuvicorn\n")
    print("Backend created successfully!\n")

    # --- Frontend setup ---
    print("Launching React/Vite setup wizard...\n")

    # Try create-launcher, fallback to Vite
    try:
        subprocess.run(["npx", "create-launcher"], cwd=project_dir, check=True)
    except subprocess.CalledProcessError:
        print("create-launcher failed, falling back to Vite...")
        subprocess.run(
            ["npm", "create", "vite@latest", "frontend", "--", "--template", "react"],
            cwd=project_dir,
            check=True
        )

    # --- Detect frontend folder ---
    frontend_dir = None
    for d in project_dir.iterdir():
        if d.is_dir() and d.name != "backend":
            frontend_dir = d
            break

    if not frontend_dir:
        print("Could not detect frontend folder. Check the output of the setup.")
        return

    print(f"\nDetected frontend directory: {frontend_dir.name}")

    # --- Update App.jsx / App.tsx ---
    app_file = frontend_dir / "src" / "App.jsx"
    if not app_file.exists():
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
                  .catch(() => setMessage('Backend not reachable'))
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
                  <h1>FastAPI + React</h1>
                  <p>{message}</p>
                </div>
              )
            }

            export default App
        """))
        print("Updated frontend App.jsx to connect to backend.")
    else:
        print("Could not find App.jsx or App.tsx.")

    # --- Add Vite proxy ---
    vite_config = None
    for cfg in ["vite.config.ts", "vite.config.js"]:
        cfg_path = frontend_dir / cfg
        if cfg_path.exists():
            vite_config = cfg_path
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
        print("Added Vite proxy to forward /api to backend.")

    print(textwrap.dedent(f"""
    Setup complete!

    ▶ Start backend:
       cd {project_name}/backend
       pip install -r requirements.txt
       uvicorn main:app --reload

    ▶ Start frontend:
       cd {project_name}/{frontend_dir.name}
       npm install
       npm run dev

    Open http://localhost:5173 in your browser
    """))

if __name__ == "__main__":
    main()

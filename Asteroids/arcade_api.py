import platform
import json
import os

def submit_score(game_name, score):
    """
    Submits a high score.
    - Web (Emscripten): Posts a JSON string message to the parent window.
    - Desktop: Appends/updates the score in a local high_scores.json file.
    """
    score = int(score)
    print(f"[Arcade API] Submitting score for '{game_name}': {score}")
    
    if platform.system() == "Emscripten":
        try:
            import js
            payload = {
                "type": "ARCADE_SCORE",
                "game": game_name,
                "score": score
            }
            # Post message to parent window running the iframe
            js.window.parent.postMessage(json.dumps(payload), "*")
            print("[Arcade API] Sent score to web parent.")
        except Exception as e:
            print("[Arcade API] Failed to send score to web parent:", e)
    else:
        # Desktop Mode: Write to shared high_scores.json in the parent directory
        # Since games usually run inside their subdirectories (e.g., 'Tetris/'),
        # the root workspace directory is one level up (..).
        # We also check the current directory just in case it's run from the root.
        paths_to_try = [
            os.path.join("..", "high_scores.json"),
            "high_scores.json"
        ]
        
        target_path = None
        for p in paths_to_try:
            # If the parent directory contains main.py, it's the root workspace
            dir_name = os.path.dirname(p) or "."
            if os.path.exists(os.path.join(dir_name, "main.py")) or os.path.exists("main.py"):
                target_path = p
                break
        
        if not target_path:
            target_path = os.path.join("..", "high_scores.json")
            
        try:
            scores = {}
            if os.path.exists(target_path):
                try:
                    with open(target_path, "r") as f:
                        scores = json.load(f)
                except Exception:
                    scores = {}
                    
            current_high = scores.get(game_name, 0)
            if score > current_high:
                scores[game_name] = score
                with open(target_path, "w") as f:
                    json.dump(scores, f, indent=4)
                print(f"[Arcade API] Saved new desktop high score to {target_path}")
            else:
                print(f"[Arcade API] Score {score} did not beat high score {current_high}")
        except Exception as e:
            print("[Arcade API] Failed to write desktop high score:", e)

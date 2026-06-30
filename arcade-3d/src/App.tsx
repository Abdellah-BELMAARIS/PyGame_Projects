import React, { useState, useEffect, useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import * as THREE from 'three';
import { 
  Play, 
  Cpu, 
  Gamepad2, 
  Clock, 
  RotateCw, 
  Trophy, 
  X, 
  Activity, 
  Thermometer, 
  Layers,
  Search
} from 'lucide-react';
import { Cabinet3D } from './components/Cabinet3D';
import { VirtualGamepad } from './components/VirtualGamepad';
import './App.css';

// Game Database (All 16 Cabinet Classics)
interface Game {
  name: string;
  path: string;
  dir: string;
  cat: string;
  desc: string;
  keys: string;
}

const GAMES: Game[] = [
  {
    name: "Tetris",
    path: "Tetris/main.py",
    dir: "Tetris",
    cat: "PUZZLE",
    desc: "Neon Cyberpunk Tetris featuring soft/hard drop, hold queue, next queue preview, ghost landing projection, and visual line clear explosions.",
    keys: "Arrows (Move/Rotate), Space (Hard Drop), C/Shift (Hold)"
  },
  {
    name: "Space Dodge",
    path: "Space_Dodge/main.py",
    dir: "Space_Dodge",
    cat: "SURVIVAL",
    desc: "Pilot a glowing vector spaceship. Dodge rotating orange meteorites falling in dynamic orbits, leave thruster flame trails, and survive.",
    keys: "Left/Right Arrows (or A/D to steer)"
  },
  {
    name: "Pong",
    path: "pong/main.py",
    dir: "pong",
    cat: "RETRO",
    desc: "Cyberpunk Neon Pong. Deflect a glowing ball that leaves a fading particle path, trigger screen-shakes on scores, and fight with physics.",
    keys: "P1: W/S keys | P2: Up/Down Arrow keys"
  },
  {
    name: "Snake",
    path: "snake/main.py",
    dir: "snake",
    cat: "RETRO",
    desc: "Classic Arcade Neon Snake. Munch glowing food pellets, spawn particle trails, avoid crashing into grid borders or your own growing tail.",
    keys: "Arrow Keys (or WASD to steer)"
  },
  {
    name: "Car Racing",
    path: "Car_Racing/main.py",
    dir: "Car_Racing",
    cat: "RACING",
    desc: "High speed racing. Steer, accelerate, drift on track boundaries, and cross the finish line before a smart computer-controlled opponent.",
    keys: "Arrow Keys (Steer/Drive)"
  },
  {
    name: "Space Invader",
    path: "Space_invader/main.py",
    dir: "Space_invader",
    cat: "SHOOTER",
    desc: "Classic shoot-'em-up. Lead your fighter against descending squadrons of alien spaceships, fire yellow laser bolts, and dodge enemy pulses.",
    keys: "Arrow Keys (Move), Space (Shoot Lasers)"
  },
  {
    name: "Galaxy Fight",
    path: "Galaxy_Fight/main.py",
    dir: "Galaxy_Fight",
    cat: "VERSUS",
    desc: "Local 2-player spaceship dogfight. Shoot lasers across the middle divider barrier and deplete your opponent's health shields to win.",
    keys: "P1: WASD + L-Ctrl (Shoot) | P2: Arrows + R-Ctrl"
  },
  {
    name: "2048",
    path: "2048/main.py",
    dir: "2048",
    cat: "PUZZLE",
    desc: "Strategic math puzzle. Slide tiles across a grid to merge matching numbers and unlock the legendary 2048 tile without getting grid-locked.",
    keys: "Arrow Keys (Slide Tiles in four directions)"
  },
  {
    name: "Platformer",
    path: "Platformer/main.py",
    dir: "Platformer",
    cat: "ACTION",
    desc: "Physics 2D platformer. Run across floating platforms as Mask Dude, perform double jumps, and time your moves to dodge glowing fire traps.",
    keys: "Left/Right Arrows (Move), Space (Double Jump)"
  },
  {
    name: "Checkers",
    path: "checkers/main.py",
    dir: "checkers",
    cat: "BOARD",
    desc: "Classic board game of checkers. Plan your moves, jump over opponent tokens to capture them, crown your pieces, and wipe the board.",
    keys: "Mouse Click (Select and move checkers pieces)"
  },
  {
    name: "Neon Asteroids",
    path: "Asteroids/main.py",
    dir: "Asteroids",
    cat: "SURVIVAL",
    desc: "Classic vector space survival. Blast giant radioactive asteroids that shatter into smaller fragments, manage shield cores, and steer against high-speed impacts.",
    keys: "UP (Thrust), Left/Right (Rotate), Space (Fire Lasers)"
  },
  {
    name: "Neon Pac-Man",
    path: "Pacman/main.py",
    dir: "Pacman",
    cat: "RETRO",
    desc: "Munch glowing dot pellets in a cybernetic grid maze, avoid colorful AI-controlled ghosts, and eat power pills to trigger high-score counter hunts.",
    keys: "Arrow Keys (Steer Pacman through maze paths)"
  },
  {
    name: "Flappy Neon",
    path: "Flappy/main.py",
    dir: "Flappy",
    cat: "ACTION",
    desc: "High-speed flight avoidance. Tap to flap your glowing vector bird through moving hazard pipe gates, spawn trailing sparks, and test your split-second reflexes.",
    keys: "Space / UP Arrow / Left Mouse Click (Flap)"
  },
  {
    name: "Neon Lander",
    path: "Lander/main.py",
    dir: "Lander",
    cat: "SURVIVAL",
    desc: "Lunar module gravity descent simulator. Burn fuel thrusters to slow your vertical falling speed, balance roll angle, and perform soft touchdowns on glowing cyan pads.",
    keys: "UP (Thrust), Left/Right (Rotate Capsule)"
  },
  {
    name: "Neon Minesweeper",
    path: "Minesweeper/main.py",
    dir: "Minesweeper",
    cat: "PUZZLE",
    desc: "Tactical radioactive hazard sweeper. Scan cells on a glowing 10x10 matrix, flag mine coordinates, and perform safe sweeps in bright neon spark bursts.",
    keys: "Left Click (Uncover Cell) | Right Click (Flag Mine)"
  },
  {
    name: "Neon Breakout",
    path: "Breakout/main.py",
    dir: "Breakout",
    cat: "ACTION",
    desc: "Explosive brick-blasting arena. Launch glowing vector balls at armoured and explosive brick matrices, grab power-ups to trigger multi-ball cores and laser cannons.",
    keys: "Left/Right Arrows or A/D (Paddle), Space / Click (Laser Fire)"
  }
];

// Helper to determine game category color in CSS
const getCSSCategoryColor = (cat: string) => {
  switch (cat.toUpperCase()) {
    case 'RETRO':
    case 'BOARD':
      return 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10';
    case 'PUZZLE':
      return 'text-amber-400 border-amber-500/30 bg-amber-500/10';
    case 'SURVIVAL':
      return 'text-orange-500 border-orange-500/30 bg-orange-500/10';
    case 'SHOOTER':
    case 'VERSUS':
      return 'text-pink-500 border-pink-500/30 bg-pink-500/10';
    case 'ACTION':
    default:
      return 'text-sky-400 border-sky-500/30 bg-sky-500/10';
  }
};

// 3D Background Particles / Starfield Component
const Starfield: React.FC = () => {
  const pointsRef = useRef<THREE.Points>(null);
  const count = 300;
  const positions = useRef(new Float32Array(count * 3));

  useEffect(() => {
    for (let i = 0; i < count; i++) {
      positions.current[i * 3] = (Math.random() - 0.5) * 15;
      positions.current[i * 3 + 1] = (Math.random() - 0.5) * 15;
      positions.current[i * 3 + 2] = (Math.random() - 0.5) * 15;
    }
  }, []);

  useFrame(({ clock }) => {
    if (pointsRef.current) {
      pointsRef.current.rotation.y = clock.getElapsedTime() * 0.02;
      pointsRef.current.rotation.x = clock.getElapsedTime() * 0.01;
    }
  });

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          args={[positions.current, 3]}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.06}
        color="#c084fc"
        transparent
        opacity={0.6}
        sizeAttenuation
      />
    </points>
  );
};

// Camera Controller Component for zoom transitions
interface CameraControllerProps {
  isLaunching: boolean;
  isActive: boolean;
}

const CameraController: React.FC<CameraControllerProps> = ({ isLaunching, isActive }) => {
  useFrame((state) => {
    if (isActive || isLaunching) {
      // Smoothly zoom in close to the screen coordinates
      state.camera.position.lerp(new THREE.Vector3(0, 0.58, 1.05), 0.08);
      state.camera.lookAt(0, 0.58, 0);
    } else {
      // Normal orbit camera position
      state.camera.position.lerp(new THREE.Vector3(0, 1.2, 4.0), 0.04);
    }
  });
  return null;
};

// 3D Glowing Neon Floor Component
const NeonFloor: React.FC<{ color: string }> = ({ color }) => {
  return (
    <group position={[0, -2.2, 0]}>
      {/* Grid helper with glow */}
      <gridHelper args={[20, 20, color, '#121324']} position={[0, 0.01, 0]} />
      {/* Dark floor plate */}
      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[30, 30]} />
        <meshStandardMaterial color="#04050a" roughness={0.9} metalness={0.2} />
      </mesh>
    </group>
  );
};

export default function App() {
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [isLaunching, setIsLaunching] = useState(false);
  const [isActive, setIsActive] = useState(false);
  const [autoRotate, setAutoRotate] = useState(true);
  const [highScores, setHighScores] = useState<Record<string, number>>({});
  const [stats, setStats] = useState({
    playedCount: 0,
    activeTime: 0,
    cpuLoad: 24,
    gpuTemp: 45,
    memoryUsed: 1.8,
  });

  // Mobile-specific states
  const [isMobile, setIsMobile] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeCategory, setActiveCategory] = useState('ALL');
  const [isDetailOpen, setIsDetailOpen] = useState(false);
  const [flagMode, setFlagMode] = useState(false);
  const [showStatsModal, setShowStatsModal] = useState(false);

  const iframeRef = useRef<HTMLIFrameElement>(null);
  const flagModeRef = useRef(false);

  useEffect(() => {
    flagModeRef.current = flagMode;
  }, [flagMode]);

  // Mobile viewport detection
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 1024 || /Mobi|Android|iPhone|iPad/i.test(navigator.userAgent));
    };
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const selectedGame = GAMES[selectedIndex];

  // Resolve dev/prod paths to local WASM builds of games
  const getGameIframeUrl = (gameDir: string) => {
    const isDev = import.meta.env.DEV;
    return isDev ? `../${gameDir}/build/web/index.html` : `./${gameDir}/build/web/index.html`;
  };

  // Keyboard Event Dispatcher for virtual gamepad
  const sendKeyEvent = (key: string, type: 'keydown' | 'keyup') => {
    if (!iframeRef.current) return;
    try {
      const iframe = iframeRef.current;
      const targetWindow = iframe.contentWindow;
      if (!targetWindow) return;
      const targetDoc = targetWindow.document;

      const keyMappings: Record<string, { key?: string; code: string; keyCode: number }> = {
        'ArrowUp': { code: 'ArrowUp', keyCode: 38 },
        'ArrowDown': { code: 'ArrowDown', keyCode: 40 },
        'ArrowLeft': { code: 'ArrowLeft', keyCode: 37 },
        'ArrowRight': { code: 'ArrowRight', keyCode: 39 },
        'Space': { key: ' ', code: 'Space', keyCode: 32 },
        'KeyW': { key: 'w', code: 'KeyW', keyCode: 87 },
        'KeyS': { key: 's', code: 'KeyS', keyCode: 83 },
        'KeyA': { key: 'a', code: 'KeyA', keyCode: 65 },
        'KeyD': { key: 'd', code: 'KeyD', keyCode: 68 },
        'KeyC': { key: 'c', code: 'KeyC', keyCode: 67 },
        'Shift': { code: 'ShiftLeft', keyCode: 16 },
        'Control': { code: 'ControlLeft', keyCode: 17 },
        'ControlLeft': { code: 'ControlLeft', keyCode: 17 },
        'ControlRight': { code: 'ControlRight', keyCode: 17 },
        'KeyR': { key: 'r', code: 'KeyR', keyCode: 82 }
      };

      const mapping = keyMappings[key] || { key, code: key, keyCode: 0 };
      const eventKey = mapping.key !== undefined ? mapping.key : key;

      const event = new KeyboardEvent(type, {
        key: eventKey,
        code: mapping.code,
        keyCode: mapping.keyCode,
        which: mapping.keyCode,
        bubbles: true,
        cancelable: true,
        view: targetWindow as any
      });

      targetDoc.dispatchEvent(event);
      if (targetDoc.activeElement) {
        targetDoc.activeElement.dispatchEvent(event);
      }
    } catch (err) {
      console.error("Failed to send key event:", err);
    }
  };

  // Iframe loaded callback: sets focus and intercepts Minesweeper right-clicks
  const handleIframeLoad = () => {
    if (!iframeRef.current) return;
    const iframe = iframeRef.current;
    try {
      const iframeWindow = iframe.contentWindow;
      const iframeDoc = iframeWindow?.document;
      if (!iframeDoc) return;

      // Focus the iframe so it captures keyboard events immediately
      iframeWindow.focus();

      // Intercept clicks in Minesweeper to simulate right clicks for flagging
      if (selectedGame.dir === 'Minesweeper') {
        const handleMouseDown = (e: MouseEvent) => {
          if (flagModeRef.current && e.button === 0) {
            e.preventDefault();
            e.stopPropagation();

            const clientX = e.clientX;
            const clientY = e.clientY;

            // Dispatch right-click mousedown
            const rightDown = new MouseEvent('mousedown', {
              bubbles: true,
              cancelable: true,
              view: iframeWindow as any,
              button: 2,
              buttons: 2,
              clientX,
              clientY,
              screenX: e.screenX,
              screenY: e.screenY
            });
            e.target?.dispatchEvent(rightDown);

            // Dispatch right-click mouseup
            const rightUp = new MouseEvent('mouseup', {
              bubbles: true,
              cancelable: true,
              view: iframeWindow as any,
              button: 2,
              buttons: 0,
              clientX,
              clientY,
              screenX: e.screenX,
              screenY: e.screenY
            });
            e.target?.dispatchEvent(rightUp);
          }
        };

        iframeDoc.addEventListener('mousedown', handleMouseDown, true);
        iframeDoc.addEventListener('contextmenu', (e) => e.preventDefault());
      }
    } catch (err) {
      console.error("Failed to setup iframe event interception:", err);
    }
  };

  // Load High Scores and Telemetry on boot
  useEffect(() => {
    // 1. Fetch desktop high scores from parent directory JSON (if available)
    const loadDesktopScores = async () => {
      try {
        const response = await fetch(import.meta.env.DEV ? '../high_scores.json' : './high_scores.json');
        if (response.ok) {
          const data = await response.json();
          setHighScores((prev) => ({ ...prev, ...data }));
        }
      } catch (e) {
        console.log("Could not load desktop high scores:", e);
      }
    };
    loadDesktopScores();

    // 2. Load web high scores from localStorage
    try {
      const saved = localStorage.getItem('arcade_high_scores_v2');
      if (saved) {
        const data = JSON.parse(saved);
        setHighScores((prev) => ({ ...prev, ...data }));
      }
    } catch (e) {}

    // 3. Load stats telemetry
    try {
      const savedStats = localStorage.getItem('arcade_stats');
      if (savedStats) {
        const data = JSON.parse(savedStats);
        setStats((prev) => ({
          ...prev,
          playedCount: data.gamesPlayed || 0,
        }));
      }
    } catch (e) {}

    // Telemetry updates loop
    const telemetryInterval = setInterval(() => {
      setStats((prev) => ({
        ...prev,
        activeTime: prev.activeTime + 1,
        cpuLoad: Math.floor(18 + Math.random() * 12),
        gpuTemp: Math.floor(40 + Math.random() * 8),
        memoryUsed: parseFloat((1.6 + Math.random() * 0.4).toFixed(1)),
      }));
    }, 1000);

    return () => clearInterval(telemetryInterval);
  }, []);

  // Score message listener from game iframes
  useEffect(() => {
    const handleScoreMessage = (e: MessageEvent) => {
      try {
        const data = typeof e.data === 'string' ? JSON.parse(e.data) : e.data;
        if (data && data.type === 'ARCADE_SCORE' && data.game && typeof data.score === 'number') {
          // Record score
          setHighScores((prev) => {
            const currentHigh = prev[data.game] || 0;
            if (data.score > currentHigh) {
              const updated = { ...prev, [data.game]: data.score };
              
              // Save to localStorage
              localStorage.setItem('arcade_high_scores_v2', JSON.stringify(updated));
              
              // Trigger CSS Confetti Celebration!
              triggerConfettiCelebration();
              return updated;
            }
            return prev;
          });

          // Update telemetry count
          setStats((prev) => {
            const updatedPlayed = prev.playedCount + 1;
            // Save to localStorage arcade_stats
            try {
              const savedStats = localStorage.getItem('arcade_stats') || '{}';
              const parsed = JSON.parse(savedStats);
              parsed.gamesPlayed = updatedPlayed;
              parsed.lastPlayed = data.game;
              localStorage.setItem('arcade_stats', JSON.stringify(parsed));
            } catch(err){}
            return { ...prev, playedCount: updatedPlayed };
          });
        }
      } catch (err) {}
    };

    window.addEventListener('message', handleScoreMessage);
    return () => window.removeEventListener('message', handleScoreMessage);
  }, []);

  const triggerConfettiCelebration = () => {
    const container = document.getElementById('confetti-container');
    if (!container) return;
    container.innerHTML = '';
    
    // Spawn 80 confetti elements with random speeds and colors
    for (let i = 0; i < 80; i++) {
      const conf = document.createElement('div');
      conf.className = 'confetti-piece';
      conf.style.left = `${Math.random() * 100}%`;
      conf.style.backgroundColor = ['#3B82F6', '#A855F7', '#EC4899', '#10B981', '#F97316'][Math.floor(Math.random() * 5)];
      conf.style.transform = `rotate(${Math.random() * 360}deg)`;
      conf.style.animationDelay = `${Math.random() * 0.4}s`;
      conf.style.animationDuration = `${1.2 + Math.random() * 1.5}s`;
      container.appendChild(conf);
    }
  };

  // Launching transition
  const handleLaunchGame = () => {
    if (isLaunching || isActive) return;
    setIsLaunching(true);
    setAutoRotate(false);
    setIsDetailOpen(false); // Close mobile detail panel if open
    
    // Simulate zooming into screen before showing iframe overlay
    setTimeout(() => {
      setIsActive(true);
      setIsLaunching(false);
    }, 1200);
  };

  const handleCloseGame = () => {
    setIsActive(false);
    setAutoRotate(true);
  };

  // Format active time to human readable
  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}m ${s}s`;
  };

  const currentNeonColor = (() => {
    switch (selectedGame.cat.toUpperCase()) {
      case 'RETRO':
      case 'BOARD':
        return '#00ff66';
      case 'PUZZLE':
        return '#ffcc00';
      case 'SURVIVAL':
        return '#ff3300';
      case 'SHOOTER':
      case 'VERSUS':
        return '#ff0077';
      case 'ACTION':
      default:
        return '#00ccff';
    }
  })();

  const CATEGORIES = ['ALL', 'RETRO', 'PUZZLE', 'SURVIVAL', 'SHOOTER', 'VERSUS', 'ACTION', 'BOARD'];

  const filteredGames = GAMES.filter((game) => {
    const matchesCategory = activeCategory === 'ALL' || game.cat.toUpperCase() === activeCategory;
    const matchesSearch =
      game.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      game.desc.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  // =====================================================================
  // MOBILE RENDER VIEW
  // =====================================================================
  if (isMobile) {
    return (
      <div className="flex flex-col h-screen w-screen bg-cabinet-dark font-sans antialiased text-gray-100 select-none relative overflow-hidden">
        
        {/* Confetti container inside gameplay */}
        <div id="confetti-container" className="absolute inset-0 z-50 pointer-events-none overflow-hidden"></div>

        {/* Mobile Header (Only visible when game is not active) */}
        {!isActive && (
          <header className="px-4 py-3 flex items-center justify-between border-b border-white/5 bg-slate-950/40 backdrop-blur-md z-10">
            <div className="flex items-center space-x-2.5">
              <div className="w-8 h-8 rounded-lg bg-gradient-arcade flex items-center justify-center shadow-md">
                <Gamepad2 className="w-4.5 h-4.5 text-white" />
              </div>
              <span className="font-extrabold text-base tracking-wider text-white">
                NEON<span className="text-neon-blue">ARCADE</span>
              </span>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowStatsModal(true)}
                className="p-1.5 rounded-lg border border-white/5 bg-white/2 hover:bg-white/5 text-gray-300"
              >
                <Activity className="w-4 h-4 text-neon-blue" />
              </button>
              <a
                href="https://abdellah-belmaaris.github.io/"
                className="text-[9px] px-2 py-1.5 rounded-md border border-white/10 text-gray-400 font-bold uppercase tracking-wider"
              >
                Portfolio
              </a>
            </div>
          </header>
        )}

        {/* Mobile Dashboard (Games Grid + Search) */}
        {!isActive && (
          <main className="flex-1 overflow-y-auto p-4 space-y-4 pb-12">
            {/* Search input */}
            <div className="relative">
              <Search className="absolute left-3 top-2.5 w-4 h-4 text-gray-500" />
              <input
                type="text"
                placeholder="Search retro classics..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-slate-900/60 border border-white/5 rounded-xl py-2 pl-9 pr-4 text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:border-neon-blue transition-all"
              />
            </div>

            {/* Category pills */}
            <div className="flex gap-2 overflow-x-auto pb-1 -mx-1 px-1 scrollbar-none">
              {CATEGORIES.map((cat) => {
                const active = cat === activeCategory;
                return (
                  <button
                    key={cat}
                    onClick={() => setActiveCategory(cat)}
                    className={`text-[10px] px-3 py-1.5 rounded-lg border font-bold uppercase tracking-wide whitespace-nowrap transition-all ${
                      active
                        ? 'bg-gradient-arcade border-transparent text-white shadow-neon-blue-sm'
                        : 'bg-white/2 border-white/5 text-gray-400'
                    }`}
                  >
                    {cat}
                  </button>
                );
              })}
            </div>

            {/* Game Cards Grid */}
            <div className="grid grid-cols-2 gap-3">
              {filteredGames.map((game) => {
                const originalIndex = GAMES.findIndex((g) => g.name === game.name);
                const isSelected = originalIndex === selectedIndex;
                
                // Fetch category colors
                let borderGlow = 'border-white/5 shadow-none';
                if (isSelected) {
                  if (game.cat === 'PUZZLE') borderGlow = 'border-amber-500/80 shadow-[0_0_10px_rgba(251,191,36,0.25)]';
                  else if (game.cat === 'SURVIVAL') borderGlow = 'border-orange-500/80 shadow-[0_0_10px_rgba(249,115,22,0.25)]';
                  else if (game.cat === 'RETRO' || game.cat === 'BOARD') borderGlow = 'border-emerald-500/80 shadow-[0_0_10px_rgba(52,211,153,0.25)]';
                  else if (game.cat === 'SHOOTER' || game.cat === 'VERSUS') borderGlow = 'border-pink-500/80 shadow-[0_0_10px_rgba(236,72,153,0.25)]';
                  else borderGlow = 'border-sky-500/80 shadow-[0_0_10px_rgba(56,189,248,0.25)]';
                }

                return (
                  <button
                    key={game.name}
                    onClick={() => {
                      setSelectedIndex(originalIndex);
                      setIsDetailOpen(true);
                    }}
                    className={`p-3 rounded-xl border bg-slate-900/40 text-left flex flex-col justify-between h-32 transition-all duration-300 ${borderGlow}`}
                  >
                    <div>
                      <div className="flex justify-between items-start mb-1.5">
                        <span className={`text-[8px] px-1.5 py-0.5 rounded border font-black tracking-wide ${getCSSCategoryColor(game.cat)}`}>
                          {game.cat}
                        </span>
                        {highScores[game.name] && (
                          <Trophy className="w-3.5 h-3.5 text-yellow-500" />
                        )}
                      </div>
                      <h3 className="font-extrabold text-sm text-white tracking-tight line-clamp-1">
                        {game.name}
                      </h3>
                      <p className="text-[10px] text-gray-400 line-clamp-2 leading-relaxed mt-1 font-light">
                        {game.desc}
                      </p>
                    </div>

                    <div className="text-[9px] text-gray-500 font-mono flex justify-between items-center w-full pt-1.5 border-t border-white/5">
                      <span>HI SCORE:</span>
                      <span className="text-yellow-400 font-bold">
                        {highScores[game.name] !== undefined ? highScores[game.name] : '0'}
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>

            {filteredGames.length === 0 && (
              <div className="text-center py-12 text-gray-500 text-xs">
                No games found matching "{searchQuery}"
              </div>
            )}
          </main>
        )}

        {/* Mobile Game Details Bottom Drawer */}
        {isDetailOpen && !isActive && (
          <div className="absolute inset-0 z-40 bg-black/60 backdrop-blur-sm flex items-end">
            <div className="w-full bg-slate-950 border-t border-white/10 rounded-t-2xl p-5 space-y-4 max-h-[85vh] overflow-y-auto animate-slide-up">
              <div className="flex justify-between items-center">
                <span className={`text-xs px-2 py-0.5 rounded border font-bold ${getCSSCategoryColor(selectedGame.cat)}`}>
                  {selectedGame.cat}
                </span>
                <button
                  onClick={() => setIsDetailOpen(false)}
                  className="p-1 rounded-full bg-white/5 text-gray-400 active:text-white"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div>
                <h2 className="font-black text-2xl text-white tracking-tight mb-1.5">{selectedGame.name}</h2>
                <p className="text-xs text-gray-300 leading-relaxed font-light">{selectedGame.desc}</p>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-xl border border-white/5 bg-white/2">
                  <span className="block text-[9px] text-gray-500 font-bold uppercase tracking-wider mb-1">High Score</span>
                  <span className="font-mono text-base font-black text-yellow-400">
                    {highScores[selectedGame.name] !== undefined ? highScores[selectedGame.name].toLocaleString() : 'No record'}
                  </span>
                </div>
                <div className="p-3 rounded-xl border border-white/5 bg-white/2">
                  <span className="block text-[9px] text-gray-500 font-bold uppercase tracking-wider mb-1">Cabinet Keys</span>
                  <span className="font-mono text-[9px] text-gray-300 block truncate">{selectedGame.keys}</span>
                </div>
              </div>

              <button
                onClick={handleLaunchGame}
                className="w-full py-3.5 rounded-xl bg-gradient-arcade font-black tracking-wider text-sm shadow-arcade text-white active:scale-95 transition-all flex items-center justify-center gap-2"
              >
                <Play className="w-4 h-4 fill-white" /> LAUNCH GAME
              </button>
            </div>
          </div>
        )}

        {/* Mobile Stats Modal */}
        {showStatsModal && (
          <div className="absolute inset-0 z-50 bg-black/70 backdrop-blur-md flex items-center justify-center p-4">
            <div className="w-full max-w-sm bg-slate-950 border border-white/10 rounded-2xl p-5 space-y-4">
              <div className="flex justify-between items-center pb-2 border-b border-white/5">
                <span className="flex items-center gap-1.5 text-xs font-bold text-gray-300">
                  <Activity className="w-4 h-4 text-neon-blue" /> CABINET DIAGNOSTICS
                </span>
                <button
                  onClick={() => setShowStatsModal(false)}
                  className="text-gray-500 hover:text-white"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="space-y-3">
                <div className="flex justify-between items-center text-xs">
                  <span className="text-gray-500 font-medium">Cabinet Status:</span>
                  <span className="text-emerald-400 font-bold flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span> ONLINE
                  </span>
                </div>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-gray-500 font-medium">CPU Core Load:</span>
                  <span className="text-gray-300 font-semibold">{stats.cpuLoad}%</span>
                </div>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-gray-500 font-medium">GPU Temperature:</span>
                  <span className="text-gray-300 font-semibold">{stats.gpuTemp}°C</span>
                </div>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-gray-500 font-medium">Memory Allocation:</span>
                  <span className="text-gray-300 font-semibold">{stats.memoryUsed} GB</span>
                </div>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-gray-500 font-medium">Total Session Playtime:</span>
                  <span className="text-gray-300 font-semibold">{formatTime(stats.activeTime)}</span>
                </div>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-gray-500 font-medium">Games Fired Up:</span>
                  <span className="text-gray-300 font-semibold">{stats.playedCount}</span>
                </div>
              </div>

              <button
                onClick={() => setShowStatsModal(false)}
                className="w-full py-2.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-white font-bold text-xs transition-all"
              >
                DISMISS DIAGNOSTICS
              </button>
            </div>
          </div>
        )}

        {/* Mobile Gameplay View */}
        {isActive && (
          <div className="absolute inset-0 z-45 bg-black flex flex-col justify-between h-full w-full mobile-gameplay-layout">
            {/* Gameplay Header */}
            <div className="flex justify-between items-center px-4 py-2 bg-slate-950 border-b border-white/5 shrink-0 z-20">
              <div className="flex items-center gap-2">
                <Gamepad2 className="w-4 h-4 text-neon-blue" />
                <h2 className="font-extrabold text-sm text-white tracking-wide uppercase">
                  {selectedGame.name}
                </h2>
              </div>
              <button
                onClick={handleCloseGame}
                className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 text-gray-300 active:text-white active:bg-neon-pink/20 active:border-neon-pink/30 transition-all text-[10px] font-bold"
              >
                <X className="w-3.5 h-3.5" /> CLOSE CABINET
              </button>
            </div>

            {/* Game Screen Area */}
            <div className="flex-1 bg-black relative flex items-center justify-center overflow-hidden game-iframe-container">
              <div className="absolute inset-0 scanline-overlay pointer-events-none z-10"></div>
              <iframe
                ref={iframeRef}
                src={getGameIframeUrl(selectedGame.dir)}
                onLoad={handleIframeLoad}
                className="w-full h-full border-none z-0 absolute inset-0"
                title={selectedGame.name}
                allowFullScreen
              />
            </div>

            {/* Virtual Gamepad Area */}
            <div className="shrink-0 bg-slate-950 border-t border-white/5 p-2 flex items-center justify-center select-none touch-none virtual-gamepad-wrapper">
              <VirtualGamepad
                gameDir={selectedGame.dir}
                sendKeyEvent={sendKeyEvent}
                flagMode={flagMode}
                setFlagMode={setFlagMode}
              />
            </div>
          </div>
        )}

        {/* Mobile Loading Overlay */}
        {isLaunching && (
          <div className="absolute inset-0 z-50 pointer-events-none flex items-center justify-center bg-slate-950 animate-fade-dark">
            <div className="text-center">
              <div className="text-[10px] font-mono font-bold tracking-[0.4em] text-neon-blue mb-3.5 uppercase animate-pulse">
                LOADING RETRO ROM
              </div>
              <div className="w-40 h-1 bg-white/10 rounded-full overflow-hidden mx-auto">
                <div className="h-full bg-gradient-arcade w-full animate-loader"></div>
              </div>
            </div>
          </div>
        )}

      </div>
    );
  }

  // =====================================================================
  // DESKTOP RENDER VIEW (ORIGINAL 3D CABINET)
  // =====================================================================
  return (
    <div className="flex h-screen w-screen overflow-hidden bg-cabinet-dark font-sans antialiased text-gray-100 select-none relative">
      
      {/* ========================================== */}
      {/* 3D CANVAS BACKGROUND */}
      {/* ========================================== */}
      <div className="absolute inset-0 z-0">
        <Canvas camera={{ position: [0, 1.2, 4.0], fov: 50 }}>
          <ambientLight intensity={0.65} />
          {/* Neon Spotlight shining down onto the cabinet */}
          <spotLight
            position={[0, 4, 2]}
            angle={0.5}
            penumbra={0.9}
            intensity={2.2}
            castShadow
            color={currentNeonColor}
          />
          <pointLight position={[-3, 2, -1]} intensity={0.5} color="#8b5cf6" />
          <pointLight position={[3, 2, -1]} intensity={0.5} color="#ec4899" />
          
          <Cabinet3D category={selectedGame.cat} isLaunching={isLaunching} />
          
          <Starfield />
          <NeonFloor color={currentNeonColor} />
          
          <CameraController isLaunching={isLaunching} isActive={isActive} />
          
          <OrbitControls
            enableZoom={!isActive && !isLaunching}
            enablePan={false}
            autoRotate={autoRotate}
            autoRotateSpeed={0.65}
            minDistance={3}
            maxDistance={7}
            maxPolarAngle={Math.PI / 2 - 0.05}
          />
        </Canvas>
      </div>

      {/* ========================================== */}
      {/* LEFT SIDE PANEL: GAME ROSTER */}
      {/* ========================================== */}
      <div className={`absolute left-0 top-0 bottom-0 w-80 z-10 transition-transform duration-500 p-5 flex flex-col justify-between border-r border-white/5 bg-slate-950/40 backdrop-blur-xl ${isActive || isLaunching ? '-translate-x-full' : 'translate-x-0'}`}>
        
        {/* Header Branding */}
        <div>
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <div className="w-9 h-9 rounded-xl bg-gradient-arcade flex items-center justify-center shadow-lg">
                <Gamepad2 className="w-5 h-5 text-white" />
              </div>
              <span className="font-extrabold text-lg tracking-wider text-white">
                NEON<span className="text-neon-blue">ARCADE</span>
              </span>
            </div>
            <a
              href="https://abdellah-belmaaris.github.io/"
              className="text-[10px] px-2 py-1 rounded-md border border-white/10 text-gray-400 hover:text-white hover:border-neon-blue transition-all font-bold uppercase tracking-wider"
              id="back-to-portfolio-link"
            >
              PORTFOLIO
            </a>
          </div>

          {/* Scrollable Game List */}
          <div className="space-y-2 h-[calc(100vh-270px)] overflow-y-auto pr-1">
            {GAMES.map((game, i) => {
              const active = i === selectedIndex;
              return (
                <button
                  key={game.name}
                  onClick={() => setSelectedIndex(i)}
                  className={`w-full flex items-center justify-between p-3 rounded-xl border transition-all duration-300 text-left ${
                    active
                      ? 'bg-white/5 border-neon-blue shadow-neon-blue-sm'
                      : 'bg-white/2 border-white/5 hover:bg-white/5 hover:border-white/10'
                  }`}
                >
                  <div className="flex items-center space-x-3 truncate">
                    <div className={`w-2 h-2 rounded-full ${
                      active ? 'bg-neon-blue animate-pulse' : 'bg-gray-600'
                    }`} />
                    <span className={`font-semibold text-sm truncate ${active ? 'text-neon-blue' : 'text-gray-300'}`}>
                      {game.name}
                    </span>
                  </div>
                  <span className={`text-[10px] px-2 py-0.5 rounded-md border font-bold uppercase tracking-wide ${getCSSCategoryColor(game.cat)}`}>
                    {game.cat}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        {/* System Telemetry Module */}
        <div className="p-4 rounded-xl border border-white/5 bg-white/2 backdrop-blur-md">
          <div className="flex items-center justify-between mb-3 pb-2 border-b border-white/5 text-xs font-bold text-gray-400">
            <span className="flex items-center gap-1.5"><Activity className="w-3 h-3 text-neon-blue" /> CABINET HEALTH</span>
            <span className="text-emerald-400 flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span> ONLINE</span>
          </div>
          <div className="grid grid-cols-2 gap-3 text-[10px]">
            <div className="flex items-center gap-1.5">
              <Cpu className="w-3.5 h-3.5 text-pink-500" />
              <div>
                <span className="block text-gray-500 font-bold uppercase">CPU CORE</span>
                <span className="text-gray-300 font-semibold">{stats.cpuLoad}%</span>
              </div>
            </div>
            <div className="flex items-center gap-1.5">
              <Thermometer className="w-3.5 h-3.5 text-amber-500" />
              <div>
                <span className="block text-gray-500 font-bold uppercase">GPU TEMP</span>
                <span className="text-gray-300 font-semibold">{stats.gpuTemp}°C</span>
              </div>
            </div>
            <div className="flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5 text-sky-500" />
              <div>
                <span className="block text-gray-500 font-bold uppercase">MEMORY</span>
                <span className="text-gray-300 font-semibold">{stats.memoryUsed} GB</span>
              </div>
            </div>
            <div className="flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-neon-green" />
              <div>
                <span className="block text-gray-500 font-bold uppercase">PLAYTIME</span>
                <span className="text-gray-300 font-semibold">{formatTime(stats.activeTime)}</span>
              </div>
            </div>
          </div>
        </div>

      </div>

      {/* ========================================== */}
      {/* RIGHT SIDE PANEL: DETAILS CARD */}
      {/* ========================================== */}
      <div className={`absolute right-0 top-0 bottom-0 w-[420px] z-10 transition-transform duration-500 p-5 flex flex-col justify-between border-l border-white/5 bg-slate-950/40 backdrop-blur-xl ${isActive || isLaunching ? 'translate-x-full' : 'translate-x-0'}`}>
        
        {/* Game Details Area */}
        <div className="space-y-4">
          <div>
            <h1 className="font-extrabold text-3xl tracking-tight text-white mb-2 leading-tight">
              {selectedGame.name}
            </h1>
            <span className={`inline-block text-xs px-2.5 py-1 rounded-md border font-bold uppercase tracking-wide ${getCSSCategoryColor(selectedGame.cat)}`}>
              {selectedGame.cat}
            </span>
          </div>

          <div className="space-y-1.5">
            <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider">Description</h3>
            <p className="text-sm text-gray-300 leading-relaxed font-light">
              {selectedGame.desc}
            </p>
          </div>

          <div className="space-y-2">
            <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider">Cabinet Deck Controls</h3>
            <div className="p-4 rounded-xl border border-white/5 bg-black/30 backdrop-blur-md">
              <p className="text-xs text-gray-300 font-medium leading-relaxed font-mono">
                {selectedGame.keys}
              </p>
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex items-center gap-1.5 text-xs font-bold text-gray-400 uppercase tracking-wider"><Trophy className="w-4 h-4 text-yellow-500" /> High Score</div>
            <div className="p-4 rounded-xl border border-white/5 bg-gradient-to-r from-black/40 to-black/10 flex items-center justify-between">
              <span className="text-xs text-gray-400">PERSONAL BEST:</span>
              <span className="font-mono font-black text-xl text-yellow-400">
                {highScores[selectedGame.name] !== undefined 
                  ? highScores[selectedGame.name].toLocaleString() 
                  : 'No record yet'}
              </span>
            </div>
          </div>
        </div>

        {/* Controls & Launcher */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <button
              onClick={() => setAutoRotate(!autoRotate)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-bold transition-all ${
                autoRotate 
                  ? 'border-neon-blue-fade text-neon-blue bg-neon-blue-fade' 
                  : 'border-white/10 text-gray-400'
              }`}
            >
              <RotateCw className="w-3.5 h-3.5" /> Orbit Auto-Rotation
            </button>

            <div className="text-right text-[10px] font-semibold text-gray-500 uppercase">
              CORES IN CABINET: {GAMES.length}
            </div>
          </div>

          {/* Launch Button */}
          <button
            onClick={handleLaunchGame}
            className="w-full py-3 rounded-xl bg-gradient-arcade bg-gradient-arcade-hover transition-all duration-300 flex items-center justify-center gap-2 font-black tracking-wider text-sm shadow-arcade hover:scale-[1.02] active:scale-[0.98] text-white"
          >
            <Play className="w-4 h-4 fill-white" /> LAUNCH CABINET
          </button>
        </div>

      </div>

      {/* ========================================== */}
      {/* 3D ZOOM LAUNCHING OVERLAY */}
      {/* ========================================== */}
      {isLaunching && (
        <div className="absolute inset-0 z-20 pointer-events-none flex items-center justify-center bg-black/0 animate-fade-dark">
          <div className="text-center">
            <div className="text-xs font-mono font-bold tracking-[0.4em] text-neon-blue mb-2 uppercase animate-pulse">
              LOADING RETRO ROM
            </div>
            <div className="w-48 h-1 bg-white/10 rounded-full overflow-hidden mx-auto">
              <div className="h-full bg-gradient-arcade w-full animate-loader"></div>
            </div>
          </div>
        </div>
      )}

      {/* ========================================== */}
      {/* FULLSCREEN RETRO GAMEPLAY OVERLAY */}
      {/* ========================================== */}
      {isActive && (
        <div className="absolute inset-0 z-30 flex flex-col items-center justify-center p-4 bg-overlay-dark backdrop-blur-md border border-white/10 shadow-2xl">
          {/* Confetti container inside gameplay */}
          <div id="confetti-container" className="absolute inset-0 z-40 pointer-events-none overflow-hidden"></div>
          
          <div className="w-full max-w-6xl h-full flex flex-col justify-between">
            {/* Header Control Bar */}
            <div className="flex justify-between items-center pb-3 border-b border-white/5 mb-4">
              <div className="flex items-center gap-3">
                <Gamepad2 className="w-5 h-5 text-neon-blue" />
                <h2 className="font-extrabold text-lg text-white font-sans tracking-wide uppercase">
                  {selectedGame.name}
                </h2>
              </div>
              <button
                onClick={handleCloseGame}
                className="flex items-center gap-1 px-4 py-2 rounded-xl bg-white/5 hover-bg-neon-pink-fade hover-border-neon-pink-fade border border-white/10 hover:text-white transition-all text-xs font-semibold text-gray-300"
              >
                <X className="w-4 h-4" /> CLOSE CABINET
              </button>
            </div>

            {/* Embed PyGame WebAssembly Iframe */}
            <div className="flex-1 rounded-2xl border-arcade-screen overflow-hidden bg-black shadow-arcade-screen-inner relative">
              {/* Scanlines overlay effect */}
              <div className="absolute inset-0 scanline-overlay pointer-events-none z-10"></div>
              
              <iframe
                ref={iframeRef}
                src={getGameIframeUrl(selectedGame.dir)}
                onLoad={handleIframeLoad}
                className="w-full h-full border-none z-0"
                title={selectedGame.name}
                allowFullScreen
              />
            </div>

            {/* Footer Control Hints */}
            <div className="pt-3 flex justify-between items-center text-[10px] font-bold text-gray-500 uppercase tracking-widest font-mono mt-2">
              <span>CONTROLS: {selectedGame.keys}</span>
              <span className="text-neon-blue flex items-center gap-1.5"><Activity className="w-3 h-3 text-neon-blue" /> CORE INTEGRATION LIVE</span>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}

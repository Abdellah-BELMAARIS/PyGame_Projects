import React from 'react';
import { ArrowUp, ArrowDown, ArrowLeft, ArrowRight, ShieldAlert, Zap } from 'lucide-react';

interface VirtualGamepadProps {
  gameDir: string;
  sendKeyEvent: (key: string, type: 'keydown' | 'keyup') => void;
  flagMode: boolean;
  setFlagMode: (mode: boolean) => void;
}

export const VirtualGamepad: React.FC<VirtualGamepadProps> = ({
  gameDir,
  sendKeyEvent,
  flagMode,
  setFlagMode
}) => {
  // Helper to handle button press
  const handlePress = (key: string, type: 'keydown' | 'keyup') => {
    sendKeyEvent(key, type);
  };

  // Common button attributes for touch responsiveness
  const buttonProps = (key: string) => ({
    onPointerDown: (e: React.PointerEvent) => {
      e.preventDefault();
      handlePress(key, 'keydown');
    },
    onPointerUp: (e: React.PointerEvent) => {
      e.preventDefault();
      handlePress(key, 'keyup');
    },
    onPointerLeave: (e: React.PointerEvent) => {
      e.preventDefault();
      handlePress(key, 'keyup');
    },
    onPointerCancel: (e: React.PointerEvent) => {
      e.preventDefault();
      handlePress(key, 'keyup');
    }
  });

  // Render D-pad
  const renderDPad = (directions: { up: boolean; down: boolean; left: boolean; right: boolean }) => {
    return (
      <div className="relative w-36 h-36 rounded-full bg-slate-900/90 border-4 border-slate-800 shadow-[0_0_15px_rgba(0,0,0,0.5)] flex items-center justify-center select-none touch-none">
        {/* Center core */}
        <div className="w-12 h-12 rounded-full bg-slate-850 border border-slate-800 z-10 shadow-inner"></div>

        {/* Up Arrow */}
        {directions.up && (
          <button
            {...buttonProps('ArrowUp')}
            className="absolute top-1 left-12 w-12 h-10 flex items-center justify-center text-gray-400 active:text-neon-blue active:scale-95 transition-all outline-none"
            aria-label="Up"
          >
            <ArrowUp className="w-6 h-6 fill-current" />
          </button>
        )}

        {/* Down Arrow */}
        {directions.down && (
          <button
            {...buttonProps('ArrowDown')}
            className="absolute bottom-1 left-12 w-12 h-10 flex items-center justify-center text-gray-400 active:text-neon-blue active:scale-95 transition-all outline-none"
            aria-label="Down"
          >
            <ArrowDown className="w-6 h-6 fill-current" />
          </button>
        )}

        {/* Left Arrow */}
        {directions.left && (
          <button
            {...buttonProps('ArrowLeft')}
            className="absolute left-1 top-12 w-10 h-12 flex items-center justify-center text-gray-400 active:text-neon-blue active:scale-95 transition-all outline-none"
            aria-label="Left"
          >
            <ArrowLeft className="w-6 h-6 fill-current" />
          </button>
        )}

        {/* Right Arrow */}
        {directions.right && (
          <button
            {...buttonProps('ArrowRight')}
            className="absolute right-1 top-12 w-10 h-12 flex items-center justify-center text-gray-400 active:text-neon-blue active:scale-95 transition-all outline-none"
            aria-label="Right"
          >
            <ArrowRight className="w-6 h-6 fill-current" />
          </button>
        )}
      </div>
    );
  };

  // Layout selection based on game
  const normalizedDir = gameDir.toLowerCase();

  // 1. Minesweeper Layout
  if (normalizedDir === 'minesweeper') {
    return (
      <div className="w-full flex items-center justify-center gap-6 p-4 select-none">
        <button
          onClick={() => setFlagMode(!flagMode)}
          className={`flex items-center gap-2 px-6 py-3 rounded-xl border-2 font-bold text-sm transition-all duration-300 ${
            flagMode
              ? 'bg-neon-pink/20 border-neon-pink text-neon-pink shadow-[0_0_15px_rgba(255,0,119,0.3)]'
              : 'bg-neon-blue/20 border-neon-blue text-neon-blue shadow-[0_0_15px_rgba(0,204,255,0.3)]'
          }`}
        >
          {flagMode ? <ShieldAlert className="w-5 h-5 animate-pulse" /> : <Zap className="w-5 h-5" />}
          MODE: {flagMode ? 'FLAG MINES' : 'SWEEP CELLS'}
        </button>
        <button
          {...buttonProps('KeyR')}
          className="px-6 py-3 rounded-xl border border-white/10 bg-slate-800 hover:bg-slate-700 text-white font-bold text-sm active:scale-95 transition-all"
        >
          RESET (R)
        </button>
      </div>
    );
  }

  // 2. Pong Layout (2-Player Local Splitscreen)
  if (normalizedDir === 'pong') {
    return (
      <div className="w-full flex justify-between items-center px-8 py-4 select-none touch-none">
        {/* Player 1 Controls (Left) */}
        <div className="flex flex-col gap-3">
          <span className="text-[9px] text-gray-500 font-bold tracking-wider text-center uppercase">P1 (W/S)</span>
          <div className="flex flex-col gap-2">
            <button
              {...buttonProps('KeyW')}
              className="w-16 h-16 rounded-2xl bg-slate-800 border border-white/10 flex items-center justify-center text-gray-300 active:bg-neon-blue/20 active:border-neon-blue active:text-neon-blue active:scale-90 transition-all outline-none"
            >
              W
            </button>
            <button
              {...buttonProps('KeyS')}
              className="w-16 h-16 rounded-2xl bg-slate-800 border border-white/10 flex items-center justify-center text-gray-300 active:bg-neon-blue/20 active:border-neon-blue active:text-neon-blue active:scale-90 transition-all outline-none"
            >
              S
            </button>
          </div>
        </div>

        {/* Player 2 Controls (Right) */}
        <div className="flex flex-col gap-3">
          <span className="text-[9px] text-gray-500 font-bold tracking-wider text-center uppercase">P2 (ARROWS)</span>
          <div className="flex flex-col gap-2">
            <button
              {...buttonProps('ArrowUp')}
              className="w-16 h-16 rounded-2xl bg-slate-800 border border-white/10 flex items-center justify-center text-gray-300 active:bg-neon-pink/20 active:border-neon-pink active:text-neon-pink active:scale-90 transition-all outline-none"
            >
              <ArrowUp className="w-6 h-6" />
            </button>
            <button
              {...buttonProps('ArrowDown')}
              className="w-16 h-16 rounded-2xl bg-slate-800 border border-white/10 flex items-center justify-center text-gray-300 active:bg-neon-pink/20 active:border-neon-pink active:text-neon-pink active:scale-90 transition-all outline-none"
            >
              <ArrowDown className="w-6 h-6" />
            </button>
          </div>
        </div>
      </div>
    );
  }

  // 3. Galaxy Fight Layout (2-Player Splitscreen)
  if (normalizedDir === 'galaxy_fight') {
    return (
      <div className="w-full flex justify-between items-center px-4 py-2 select-none touch-none">
        {/* Player 1 (Left Side) */}
        <div className="flex items-center gap-4">
          <div className="flex flex-col gap-1 items-center">
            <span className="text-[8px] text-gray-500 font-bold uppercase">P1 Steering</span>
            <div className="grid grid-cols-3 gap-1">
              <div></div>
              <button {...buttonProps('KeyW')} className="w-10 h-10 rounded-lg bg-slate-800 text-xs active:bg-neon-blue/20 active:scale-90 transition-all">W</button>
              <div></div>
              <button {...buttonProps('KeyA')} className="w-10 h-10 rounded-lg bg-slate-800 text-xs active:bg-neon-blue/20 active:scale-90 transition-all">A</button>
              <button {...buttonProps('KeyS')} className="w-10 h-10 rounded-lg bg-slate-800 text-xs active:bg-neon-blue/20 active:scale-90 transition-all">S</button>
              <button {...buttonProps('KeyD')} className="w-10 h-10 rounded-lg bg-slate-800 text-xs active:bg-neon-blue/20 active:scale-90 transition-all">D</button>
            </div>
          </div>
          <button
            {...buttonProps('Control')}
            className="w-14 h-14 rounded-full bg-neon-blue border border-white/20 text-white font-bold text-xs active:scale-90 transition-all shadow-lg"
          >
            FIRE (Ctrl)
          </button>
        </div>

        {/* Player 2 (Right Side) */}
        <div className="flex items-center gap-4">
          <button
            {...buttonProps('ControlRight')}
            className="w-14 h-14 rounded-full bg-neon-pink border border-white/20 text-white font-bold text-xs active:scale-90 transition-all shadow-lg"
          >
            FIRE (Ctrl)
          </button>
          <div className="flex flex-col gap-1 items-center">
            <span className="text-[8px] text-gray-500 font-bold uppercase">P2 Steering</span>
            <div className="grid grid-cols-3 gap-1">
              <div></div>
              <button {...buttonProps('ArrowUp')} className="w-10 h-10 rounded-lg bg-slate-800 text-xs active:bg-neon-pink/20 active:scale-90 transition-all">↑</button>
              <div></div>
              <button {...buttonProps('ArrowLeft')} className="w-10 h-10 rounded-lg bg-slate-800 text-xs active:bg-neon-pink/20 active:scale-90 transition-all">←</button>
              <button {...buttonProps('ArrowDown')} className="w-10 h-10 rounded-lg bg-slate-800 text-xs active:bg-neon-pink/20 active:scale-90 transition-all">↓</button>
              <button {...buttonProps('ArrowRight')} className="w-10 h-10 rounded-lg bg-slate-800 text-xs active:bg-neon-pink/20 active:scale-90 transition-all">→</button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // 4. Tetris Layout
  if (normalizedDir === 'tetris') {
    return (
      <div className="w-full flex justify-between items-center px-6 py-4 select-none touch-none">
        {/* D-Pad on Left */}
        {renderDPad({ up: true, down: true, left: true, right: true })}

        {/* Action Buttons on Right */}
        <div className="flex gap-4 items-center mr-2">
          <div className="flex flex-col items-center gap-1">
            <button
              {...buttonProps('KeyC')}
              className="w-14 h-14 rounded-full bg-slate-800 border border-white/10 flex items-center justify-center font-bold text-gray-300 text-sm active:scale-90 active:bg-slate-700 transition-all outline-none shadow-md"
            >
              HOLD
            </button>
            <span className="text-[9px] text-gray-500 font-bold uppercase">C key</span>
          </div>
          <div className="flex flex-col items-center gap-1">
            <button
              {...buttonProps('Space')}
              className="w-18 h-18 rounded-full bg-gradient-arcade border border-white/20 flex items-center justify-center font-black text-white text-base active:scale-90 active:brightness-110 transition-all outline-none shadow-arcade"
            >
              DROP
            </button>
            <span className="text-[9px] text-gray-500 font-bold uppercase">Space</span>
          </div>
        </div>
      </div>
    );
  }

  // 5. Flappy Layout (Giant Button)
  if (normalizedDir === 'flappy') {
    return (
      <div className="w-full flex items-center justify-center p-6 select-none touch-none">
        <button
          {...buttonProps('Space')}
          className="w-40 py-6 rounded-2xl bg-gradient-arcade border border-white/20 flex items-center justify-center font-black text-white text-xl shadow-arcade active:scale-95 active:brightness-110 transition-all outline-none"
        >
          FLAP (Space)
        </button>
      </div>
    );
  }

  // 6. Checkers Layout (No controls needed)
  if (normalizedDir === 'checkers') {
    return (
      <div className="w-full flex items-center justify-center p-4 select-none text-center">
        <p className="text-xs text-gray-400 font-bold uppercase tracking-wider animate-pulse">
          Tap pieces on the board to select and move them.
        </p>
      </div>
    );
  }

  // 7. Space Dodge (Left/Right only)
  if (normalizedDir === 'space_dodge') {
    return (
      <div className="w-full flex justify-center gap-12 p-6 select-none touch-none">
        <button
          {...buttonProps('ArrowLeft')}
          className="w-20 h-20 rounded-2xl bg-slate-800 border-2 border-white/10 flex items-center justify-center text-gray-300 active:bg-neon-blue/20 active:border-neon-blue active:text-neon-blue active:scale-90 transition-all outline-none shadow-lg"
          aria-label="Left"
        >
          <ArrowLeft className="w-10 h-10" />
        </button>
        <button
          {...buttonProps('ArrowRight')}
          className="w-20 h-20 rounded-2xl bg-slate-800 border-2 border-white/10 flex items-center justify-center text-gray-300 active:bg-neon-blue/20 active:border-neon-blue active:text-neon-blue active:scale-90 transition-all outline-none shadow-lg"
          aria-label="Right"
        >
          <ArrowRight className="w-10 h-10" />
        </button>
      </div>
    );
  }

  // 8. General D-pad Layouts
  // Asteroids / Lander: Left, Right, Up (Thrust) + Action A (Space)
  const isAsteroidsOrLander = normalizedDir === 'asteroids' || normalizedDir === 'lander';
  // Space Invader / Breakout / Platformer: Left, Right + Action A (Space)
  const isHorizontalShooterOrPlatformer = normalizedDir === 'space_invader' || normalizedDir === 'breakout' || normalizedDir === 'platformer';
  // Full D-pad: Snake, Car Racing, 2048, Pacman
  const isFullDPad = normalizedDir === 'snake' || normalizedDir === 'car_racing' || normalizedDir === '2048' || normalizedDir === 'pacman';

  const needsActionA = isAsteroidsOrLander || isHorizontalShooterOrPlatformer || normalizedDir === 'space_invader' || normalizedDir === 'breakout' || normalizedDir === 'platformer';

  return (
    <div className="w-full flex justify-between items-center px-6 py-4 select-none touch-none">
      {/* Left side: D-pad */}
      {renderDPad({
        up: isFullDPad || isAsteroidsOrLander,
        down: isFullDPad,
        left: true,
        right: true
      })}

      {/* Right side: Action Button */}
      {needsActionA ? (
        <div className="flex flex-col items-center gap-1 mr-2">
          <button
            {...buttonProps('Space')}
            className="w-20 h-20 rounded-full bg-gradient-arcade border border-white/20 flex items-center justify-center font-black text-white text-lg active:scale-90 active:brightness-110 transition-all outline-none shadow-arcade"
          >
            {normalizedDir === 'platformer' ? 'JUMP' : normalizedDir === 'space_invader' || normalizedDir === 'breakout' || normalizedDir === 'asteroids' ? 'FIRE' : 'THRUST'}
          </button>
          <span className="text-[9px] text-gray-500 font-bold uppercase">Space</span>
        </div>
      ) : (
        <div className="w-20 h-20"></div> // Spacer
      )}
    </div>
  );
};

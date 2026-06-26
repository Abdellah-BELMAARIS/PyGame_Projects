import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface Cabinet3DProps {
  category: string;
  isLaunching: boolean;
}

export const Cabinet3D: React.FC<Cabinet3DProps> = ({ category, isLaunching }) => {
  const joystick1Ref = useRef<THREE.Group>(null);
  const joystick2Ref = useRef<THREE.Group>(null);
  const marqueeRef = useRef<THREE.Mesh>(null);
  const screenRef = useRef<THREE.Mesh>(null);

  // Map categories to neon colors
  const getCategoryColor = (cat: string) => {
    switch (cat.toUpperCase()) {
      case 'RETRO':
      case 'BOARD':
        return '#00ff66'; // neon green
      case 'PUZZLE':
        return '#ffcc00'; // neon gold
      case 'SURVIVAL':
        return '#ff3300'; // neon orange/red
      case 'SHOOTER':
      case 'VERSUS':
        return '#ff0077'; // neon pink
      case 'ACTION':
      default:
        return '#00ccff'; // neon cyan
    }
  };

  const neonColor = getCategoryColor(category);

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();

    // Animate joysticks to look alive
    if (joystick1Ref.current) {
      joystick1Ref.current.rotation.x = Math.sin(t * 4) * 0.15;
      joystick1Ref.current.rotation.z = Math.cos(t * 3.5) * 0.12;
    }
    if (joystick2Ref.current) {
      joystick2Ref.current.rotation.x = Math.cos(t * 3) * 0.12;
      joystick2Ref.current.rotation.z = Math.sin(t * 4.5) * 0.15;
    }

    // Pulse marquee glow
    if (marqueeRef.current) {
      const material = marqueeRef.current.material as THREE.MeshBasicMaterial;
      if (material) {
        material.opacity = 0.75 + Math.sin(t * 8) * 0.15;
      }
    }

    // Pulse screen glow slightly
    if (screenRef.current) {
      const material = screenRef.current.material as THREE.MeshStandardMaterial;
      if (material && material.emissiveIntensity !== undefined) {
        material.emissiveIntensity = isLaunching 
          ? 2.5 + Math.sin(t * 20) * 0.5 
          : 0.8 + Math.sin(t * 3) * 0.15;
      }
    }
  });

  return (
    <group position={[0, -0.5, 0]}>
      {/* ========================================== */}
      {/* CABINET MAIN BODY & BASE */}
      {/* ========================================== */}
      {/* Bottom Base pedestal */}
      <mesh position={[0, -1.4, 0]}>
        <boxGeometry args={[1.5, 0.4, 1.2]} />
        <meshStandardMaterial color="#0c0d14" roughness={0.8} metalness={0.9} />
      </mesh>

      {/* Main Lower Cabinet Body */}
      <mesh position={[0, -0.4, -0.05]}>
        <boxGeometry args={[1.44, 1.6, 1.1]} />
        <meshStandardMaterial color="#10121e" roughness={0.7} metalness={0.6} />
      </mesh>

      {/* ========================================== */}
      {/* COIN DOOR */}
      {/* ========================================== */}
      <group position={[0, -0.4, 0.51]}>
        {/* Door Plate */}
        <mesh>
          <boxGeometry args={[0.7, 0.8, 0.03]} />
          <meshStandardMaterial color="#08080c" roughness={0.9} metalness={0.9} />
        </mesh>
        {/* Left Coin Slot */}
        <mesh position={[-0.18, 0.15, 0.02]}>
          <boxGeometry args={[0.15, 0.2, 0.02]} />
          <meshStandardMaterial color="#1c1d24" roughness={0.5} />
        </mesh>
        <mesh position={[-0.18, 0.15, 0.03]}>
          <boxGeometry args={[0.02, 0.08, 0.01]} />
          <meshBasicMaterial color="#ff2200" />
        </mesh>
        {/* Right Coin Slot */}
        <mesh position={[0.18, 0.15, 0.02]}>
          <boxGeometry args={[0.15, 0.2, 0.02]} />
          <meshStandardMaterial color="#1c1d24" roughness={0.5} />
        </mesh>
        <mesh position={[0.18, 0.15, 0.03]}>
          <boxGeometry args={[0.02, 0.08, 0.01]} />
          <meshBasicMaterial color="#ff2200" />
        </mesh>
      </group>

      {/* ========================================== */}
      {/* CABINET GLOWING NEON SIDE OUTLINES */}
      {/* ========================================== */}
      {/* Left side panel */}
      <mesh position={[-0.73, 0.4, 0]}>
        <boxGeometry args={[0.04, 3.2, 1.22]} />
        <meshStandardMaterial color="#0b0c16" roughness={0.6} metalness={0.7} />
      </mesh>
      {/* Left neon border stripe */}
      <mesh position={[-0.76, 0.4, 0.02]}>
        <boxGeometry args={[0.01, 3.22, 1.2]} />
        <meshBasicMaterial color={neonColor} />
      </mesh>

      {/* Right side panel */}
      <mesh position={[0.73, 0.4, 0]}>
        <boxGeometry args={[0.04, 3.2, 1.22]} />
        <meshStandardMaterial color="#0b0c16" roughness={0.6} metalness={0.7} />
      </mesh>
      {/* Right neon border stripe */}
      <mesh position={[0.76, 0.4, 0.02]}>
        <boxGeometry args={[0.01, 3.22, 1.2]} />
        <meshBasicMaterial color={neonColor} />
      </mesh>

      {/* ========================================== */}
      {/* CONTROL PANEL SECTION */}
      {/* ========================================== */}
      {/* Slanted CP Wedge Base */}
      <mesh position={[0, 0.45, 0.4]} rotation={[-0.22, 0, 0]}>
        <boxGeometry args={[1.42, 0.25, 0.7]} />
        <meshStandardMaterial color="#121528" roughness={0.4} metalness={0.8} />
      </mesh>
      {/* CP Under-Glow Neon Accent */}
      <mesh position={[0, 0.32, 0.65]}>
        <boxGeometry args={[1.38, 0.02, 0.1]} />
        <meshBasicMaterial color={neonColor} />
      </mesh>

      {/* Controls: Player 1 (Left Side of CP) */}
      <group position={[-0.35, 0.52, 0.45]} rotation={[-0.22, 0, 0]}>
        {/* Joystick Base Ring */}
        <mesh position={[0, 0, 0]}>
          <cylinderGeometry args={[0.08, 0.08, 0.01, 16]} />
          <meshStandardMaterial color="#000" roughness={0.9} />
        </mesh>
        {/* Joystick Shaft & Ball */}
        <group ref={joystick1Ref}>
          <mesh position={[0, 0.12, 0]}>
            <cylinderGeometry args={[0.012, 0.012, 0.22, 8]} />
            <meshStandardMaterial color="#bbb" metalness={0.9} roughness={0.1} />
          </mesh>
          <mesh position={[0, 0.22, 0]}>
            <sphereGeometry args={[0.06, 16, 16]} />
            <meshBasicMaterial color="#ff0055" />
          </mesh>
        </group>
        {/* Action Buttons P1 */}
        <mesh position={[0.15, 0.01, 0.08]}>
          <cylinderGeometry args={[0.035, 0.035, 0.02, 12]} />
          <meshBasicMaterial color={neonColor} />
        </mesh>
        <mesh position={[0.24, 0.01, 0.05]}>
          <cylinderGeometry args={[0.035, 0.035, 0.02, 12]} />
          <meshBasicMaterial color="#ff00cc" />
        </mesh>
        <mesh position={[0.18, 0.01, -0.05]}>
          <cylinderGeometry args={[0.035, 0.035, 0.02, 12]} />
          <meshBasicMaterial color="#00ffff" />
        </mesh>
      </group>

      {/* Controls: Player 2 (Right Side of CP) */}
      <group position={[0.35, 0.52, 0.45]} rotation={[-0.22, 0, 0]}>
        {/* Joystick Base Ring */}
        <mesh position={[0, 0, 0]}>
          <cylinderGeometry args={[0.08, 0.08, 0.01, 16]} />
          <meshStandardMaterial color="#000" roughness={0.9} />
        </mesh>
        {/* Joystick Shaft & Ball */}
        <group ref={joystick2Ref}>
          <mesh position={[0, 0.12, 0]}>
            <cylinderGeometry args={[0.012, 0.012, 0.22, 8]} />
            <meshStandardMaterial color="#bbb" metalness={0.9} roughness={0.1} />
          </mesh>
          <mesh position={[0, 0.22, 0]}>
            <sphereGeometry args={[0.06, 16, 16]} />
            <meshBasicMaterial color="#00bbff" />
          </mesh>
        </group>
        {/* Action Buttons P2 */}
        <mesh position={[-0.15, 0.01, 0.08]}>
          <cylinderGeometry args={[0.035, 0.035, 0.02, 12]} />
          <meshBasicMaterial color={neonColor} />
        </mesh>
        <mesh position={[-0.24, 0.01, 0.05]}>
          <cylinderGeometry args={[0.035, 0.035, 0.02, 12]} />
          <meshBasicMaterial color="#ffcc00" />
        </mesh>
        <mesh position={[-0.18, 0.01, -0.05]}>
          <cylinderGeometry args={[0.035, 0.035, 0.02, 12]} />
          <meshBasicMaterial color="#00ff66" />
        </mesh>
      </group>

      {/* ========================================== */}
      {/* SCREEN SECTION (BEZEL AND EMBEDDED SCREEN) */}
      {/* ========================================== */}
      {/* Slanted bezel boundary panel */}
      <mesh position={[0, 1.12, 0.12]} rotation={[-0.15, 0, 0]}>
        <boxGeometry args={[1.42, 1.05, 0.45]} />
        <meshStandardMaterial color="#0a0a0f" roughness={0.9} />
      </mesh>

      {/* Pulse Screen Bezel glowing border */}
      <mesh position={[0, 1.12, 0.35]} rotation={[-0.15, 0, 0]}>
        <boxGeometry args={[1.22, 0.82, 0.02]} />
        <meshStandardMaterial color="#16182a" roughness={0.8} />
      </mesh>

      {/* Actual CRT Screen Panel */}
      <mesh ref={screenRef} position={[0, 1.12, 0.36]} rotation={[-0.15, 0, 0]}>
        <boxGeometry args={[1.18, 0.78, 0.02]} />
        <meshStandardMaterial 
          color="#060914" 
          emissive={neonColor}
          emissiveIntensity={0.8}
          roughness={0.2}
          metalness={0.1}
        />
      </mesh>

      {/* Fake retro grid overlay on screen to represent graphics */}
      <mesh position={[0, 1.12, 0.375]} rotation={[-0.15, 0, 0]}>
        <planeGeometry args={[1.16, 0.76]} />
        <meshBasicMaterial 
          color={neonColor} 
          wireframe 
          transparent 
          opacity={isLaunching ? 0.9 : 0.25} 
        />
      </mesh>

      {/* ========================================== */}
      {/* MARQUEE SECTION (GLOWING LOGO AT THE TOP) */}
      {/* ========================================== */}
      {/* Marquee Housing */}
      <mesh position={[0, 1.82, 0.25]} rotation={[0.08, 0, 0]}>
        <boxGeometry args={[1.42, 0.38, 0.6]} />
        <meshStandardMaterial color="#0c0d16" roughness={0.6} metalness={0.8} />
      </mesh>

      {/* Glowing Marquee Panel */}
      <mesh ref={marqueeRef} position={[0, 1.82, 0.55]} rotation={[0.08, 0, 0]}>
        <boxGeometry args={[1.36, 0.32, 0.01]} />
        <meshBasicMaterial color={neonColor} transparent opacity={0.85} />
      </mesh>

      {/* White inner core marquee (gives neon glow outline effect) */}
      <mesh position={[0, 1.82, 0.555]} rotation={[0.08, 0, 0]}>
        <planeGeometry args={[1.28, 0.24]} />
        <meshStandardMaterial color="#ffffff" emissive="#ffffff" emissiveIntensity={1.2} />
      </mesh>
    </group>
  );
};

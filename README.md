# 🧟 Zombie Combat

A 3D OpenGL closed-world zombie survival game: fight, craft, scavenge, and survive across a forest and a city.

You play as a lone Hero trapped inside a walled territory split into a **Forest** and a **City**. Scavenge resources, craft bonfires, throw knives, swing melee strikes, and survive against two types of zombies.

## ✨ Features

| # | Feature | Description |
|---|---------|-------------|
| 1 | **Tactical Projectile Combat** | Left-click throws knives that follow a gravity-affected arc. Knives vanish on hitting the ground or a zombie and deal 1 HP of damage. |
| 2 | **Close Combat** | Right-click performs an area-of-effect melee strike dealing 1 HP damage to every enemy within a 180-unit radius. The hero's body flashes red when damaged. |
| 3 | **Health Acquisition System** | Eat apples (`E`) that spawn under trees for +15 HP, or stand inside a bonfire's 300-unit zone to regenerate 2 HP every 0.5 s. |
| 4 | **Crafting & Resource Management** | Chop trees (`X`) for a 70% chance to drop timber; trees also have a 70% chance to spawn apples beneath them. Wood is spent to craft bonfires. |
| 5 | **Two Game Zones & Solid Obstacles** | A Forest (trees, bushes, logs) and a City (buildings, barricades). Players and zombies cannot pass through walls, buildings, trees, or the map edges. |
| 6 | **Dynamic Traversal** | Jump (`Space`) with natural forward + upward motion and gravity-based landing to clear city barricades and forest logs. |
| 7 | **Star Power-Ups** | Floating stars randomly appear near the player for a limited time; eating one restores health to 100%. |
| 8 | **Zombies in Bonfire & Wood Collection** | Collect wood from fallen logs; zombies standing near a freshly built bonfire are burned instantly. |
| 9 | **Atmospheric Weather Control** | Press `P` to cycle between **rainy**, **snowy** and **sunny** weather. |
| 10 | **Diverse Enemy Hierarchy** | Two zombie types with distinct visual designs and different health pools. |
| 11 | **The Bonfire Sanctuary** | Bonfires act as temporary safe zones that enemies cannot enter while healing the Hero. |
| 12 | **Scavenging & Random Loot Drops** | Defeated zombies drop Dead Meat, which restores health when collected and increases your score. |
| 13 | **Advanced Hero Animations** | Throwing and striking trigger hand animations, and legs animate alongside movement. |

---

## 🎮 Controls

| Input | Action |
|-------|--------|
| `W` / `S` | Move forward / backward |
| `A` / `D` | Rotate left / right |
| `Space` | Jump |
| **Left Mouse Button** | Throw a knife |
| **Right Mouse Button** | Melee strike (area-of-effect) |
| `E` | Eat a nearby apple |
| `X` | Chop a nearby tree / collect a nearby log |
| `B` | Build a bonfire (costs 4 wood) |
| `C` | Switch camera mode (3 modes) |
| `P` | Change weather (rainy / snowy / sunny) |
| `R` | Restart after dying |

---

## 📜 Gameplay Rules

- **Health:** starts at 100 and is shown as a bar in the top-left HUD.
- **Zombies:** Type 1 has 3 HP and Type 2 has 2 HP. Defeated zombies respawn at the far edges of the map.
- **Bonfire:** costs 4 wood, kills zombies within 300 units when placed, and heals you while you stand within 300 units.
- **Wood:** collecting a fallen log gives +2 wood.
- **Score:** `(wood × 2) + (dead meat × 5)`, displayed in the HUD and on the game-over screen.
- **Game over:** when health reaches zero, press `R` to restart.


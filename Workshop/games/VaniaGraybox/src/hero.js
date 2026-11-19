// hero.js: the controller. Moves are data: add a row here + a tag in Aseprite, nothing else.
//   anim   Aseprite tag to play (missing tag -> falls back to idle, listed in the HUD)
//   loop   loop the tag, or play once
//   then   state to go to when a play-once tag ends
//   lock   ignore walk input while it plays
//   air    happens in the air (gravity keeps going)
//   dash   horizontal push, px/s, in facing direction (negative = backwards)

export const MOVES = {
  idle:          { anim: 'idle',          loop: true },
  walk:          { anim: 'walk',          loop: true },
  crouch:        { anim: 'crouch',        loop: true },
  jump:          { anim: 'jump',          loop: true, air: true },
  fall:          { anim: 'fall',          loop: true, air: true },
  land:          { anim: 'land',          loop: false, then: 'idle', lock: true },
  attack:        { anim: 'attack',        loop: false, then: 'idle', lock: true },
  crouch_attack: { anim: 'crouch_attack', loop: false, then: 'crouch', lock: true },
  jump_attack:   { anim: 'jump_attack',   loop: false, then: 'fall', air: true },
  backdash:      { anim: 'backdash',      loop: false, then: 'idle', lock: true, dash: -170 },
  hurt:          { anim: 'hurt',          loop: false, then: 'idle', lock: true, dash: -60 },
  death:         { anim: 'death',         loop: false, then: null, lock: true },
};

export const TUNE = { walk: 88, gravity: 980, jump: 330, landAfter: 120 };

export class Hero {
  constructor(anim, x, floorY) {
    this.anim = anim; this.x = x; this.y = floorY; this.vx = 0; this.vy = 0;
    this.floorY = floorY; this.facing = 1; this.ground = true; this.fallSpeed = 0;
    this.set('idle');
  }
  set(state) {
    if (!MOVES[state]) return;
    this.state = state; this.move = MOVES[state];
    this.anim.play(this.move.anim, true);
  }
  get missing() { return Object.values(MOVES).map(m => m.anim).filter(a => !this.anim.has(a)); }

  update(dt, k, room) {
    const m = this.move, s = this.state;
    const dir = (k.right ? 1 : 0) - (k.left ? 1 : 0);

    if (s !== 'death') {
      if (k.pressed('hurt')) this.set('hurt');
      else if (k.pressed('die')) this.set('death');
    }
    if (!m.lock && s !== 'death') {
      if (this.ground) {
        if (k.pressed('attack')) this.set(k.down ? 'crouch_attack' : 'attack');
        else if (k.pressed('dash')) this.set('backdash');
        else if (k.pressed('jump')) { this.vy = -TUNE.jump; this.ground = false; this.set('jump'); }
        else if (k.down) { if (s !== 'crouch') this.set('crouch'); }
        else if (dir) { this.facing = dir; if (s !== 'walk') this.set('walk'); }
        else if (s !== 'idle') this.set('idle');
      } else {
        if (k.pressed('attack') && s !== 'jump_attack') this.set('jump_attack');
        if (dir) this.facing = s === 'jump_attack' ? this.facing : dir;
      }
    }

    // horizontal
    if (m.dash) this.vx = m.dash * this.facing;
    else if (m.lock && this.ground) this.vx = 0;
    else if (s === 'crouch') this.vx = 0;
    else this.vx = dir * TUNE.walk;

    // vertical
    if (!this.ground || m.air) this.vy += TUNE.gravity * dt;
    this.x += this.vx * dt; this.y += this.vy * dt;
    if (!this.ground && this.vy > 0 && (s === 'jump')) this.set('fall');
    if (this.y >= this.floorY) {
      const hard = !this.ground;
      this.fallSpeed = this.vy;
      this.y = this.floorY; this.vy = 0; this.ground = true;
      if (hard && s !== 'death') this.set(this.fallSpeed > TUNE.landAfter ? 'land' : 'idle');
    }
    this.x = Math.max(16, Math.min(room.width - 16, this.x));

    this.anim.update(dt, m.loop);
    if (this.anim.done && m.then && (this.ground || m.air)) this.set(m.then);
  }
}

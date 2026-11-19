// main.js: loop, input, camera, parallax room, HUD, viewer.
import { loadSheet, Animator } from './sprite.js';
import { Hero, MOVES, TUNE } from './hero.js';

const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
const hud = document.getElementById('hud');
const help = document.getElementById('help');

const KEYS = {
  left: ['ArrowLeft', 'KeyA'], right: ['ArrowRight', 'KeyD'], down: ['ArrowDown', 'KeyS'],
  jump: ['Space', 'KeyZ', 'KeyW', 'ArrowUp'], attack: ['KeyX', 'KeyJ'], shoot: ['KeyC', 'KeyK'], dash: ['ShiftLeft', 'ShiftRight', 'KeyL'],
  hurt: ['KeyH'], die: ['Digit9'], reset: ['KeyR'], viewer: ['KeyV'], guides: ['KeyG'],
  slow: ['KeyT'], reload: ['KeyO'], prev: ['BracketLeft', 'Comma'], next: ['BracketRight', 'Period'], help: ['Slash'],
};
const held = new Set(), hit = new Set();
addEventListener('keydown', e => { if (!e.repeat) hit.add(e.code); held.add(e.code); if (e.code === 'Space') e.preventDefault(); });
addEventListener('keyup', e => held.delete(e.code));
const k = {
  is: n => KEYS[n].some(c => held.has(c)),
  pressed: n => KEYS[n].some(c => hit.has(c)),
  get left() { return this.is('left'); }, get right() { return this.is('right'); }, get down() { return this.is('down'); },
};

let room, layers = {}, floorImg, sheet, bulletSheet, hero, camX = 0, bullets = [];
let viewer = false, guides = false, slow = false, vi = 0;

async function img(src) { const i = new Image(); i.src = `${src}?t=${Date.now()}`; await i.decode(); return i; }

async function loadAll(keepHero = false) {
  room = await (await fetch(`assets/room.json?t=${Date.now()}`)).json();
  canvas.width = room.view.w; canvas.height = room.view.h;
  for (const l of [...room.back, ...room.front]) layers[l.name] = await img(l.image);
  floorImg = await img(room.floor.image);
  sheet = await loadSheet('assets/hero/hero.json');
  bulletSheet = await loadSheet('assets/bullet/bullet.json');
  const anim = new Animator(sheet);
  if (keepHero && hero) { hero.anim = anim; hero.set(hero.state); }
  else hero = new Hero(anim, room.spawn.x, room.floorY);
  fit();
}

function fit() {
  const s = Math.max(1, Math.floor(Math.min(innerWidth / room.view.w, (innerHeight - 40) / room.view.h)));
  canvas.style.width = `${room.view.w * s}px`; canvas.style.height = `${room.view.h * s}px`;
}
addEventListener('resize', () => room && fit());

function drawLayer(l) {
  const im = layers[l.name]; if (!im) return;
  const x = -Math.round(camX * l.speed);
  if (!l.repeat) { ctx.drawImage(im, 0, 0); return; }
  const w = im.width; let sx = ((x % w) + w) % w - w;
  for (; sx < room.view.w; sx += w) ctx.drawImage(im, sx, 0);
}

function drawFloor() {
  const w = floorImg.width; let sx = -(((Math.round(camX) % w) + w) % w);
  for (; sx < room.view.w; sx += w) ctx.drawImage(floorImg, sx, room.floorY);
}

function drawGuides(px, py) {
  const c = sheet.cell, p = sheet.pivot;
  ctx.strokeStyle = 'rgba(30,30,140,.8)'; ctx.lineWidth = 1;
  const left = hero.facing > 0 ? px - p.x : px - (c.w - p.x);
  ctx.strokeRect(Math.round(left) + .5, Math.round(py - p.y) + .5, c.w - 1, c.h - 1);
  ctx.fillStyle = 'rgb(230,60,60)'; ctx.fillRect(Math.round(px) - 2, Math.round(py), 5, 1);
  ctx.fillRect(Math.round(px), Math.round(py) - 2, 1, 5);
}

let last = performance.now();
function frame(now) {
  let dt = Math.min(0.05, (now - last) / 1000); last = now;
  if (slow) dt *= 0.25;

  if (k.pressed('viewer')) { viewer = !viewer; if (viewer) { hero.x = camX + room.view.w / 2; hero.y = room.floorY; } }
  if (k.pressed('guides')) guides = !guides;
  if (k.pressed('slow')) slow = !slow;
  if (k.pressed('help')) help.hidden = !help.hidden;
  if (k.pressed('reload')) loadAll(true);
  if (k.pressed('reset')) { hero = new Hero(new Animator(sheet), room.spawn.x, room.floorY); bullets = []; }

  const tags = Object.keys(sheet.tags);
  if (viewer) {
    if (k.pressed('next') || k.pressed('right')) vi = (vi + 1) % tags.length;
    if (k.pressed('prev') || k.pressed('left')) vi = (vi - 1 + tags.length) % tags.length;
    hero.anim.play(tags[vi]); hero.anim.update(dt, true);
  } else {
    hero.update(dt, k, room);
    for (const s of hero.shots.splice(0)) {
      if (bullets.filter(b => !b.hit).length >= TUNE.maxBullets) continue;
      const a = new Animator(bulletSheet); a.play('fly');
      bullets.push({ ...s, a, hit: false });
    }
    for (const b of bullets) {
      if (!b.hit) {
        b.x += b.dir * TUNE.bullet * dt;
        if (b.x < 0 || b.x > room.width || Math.abs(b.x - hero.x) > room.view.w) { b.hit = true; b.a.play('hit'); }
        b.a.update(dt, true);
      } else b.a.update(dt, false);
    }
    bullets = bullets.filter(b => !(b.hit && b.a.done));
    const target = hero.x - room.view.w / 2;
    camX += (target - camX) * Math.min(1, dt * 6);
    camX = Math.max(0, Math.min(room.width - room.view.w, camX));
  }
  hit.clear();

  ctx.clearRect(0, 0, canvas.width, canvas.height);
  for (const l of room.back) drawLayer(l);
  drawFloor();
  const px = hero.x - camX, py = hero.y;
  hero.anim.draw(ctx, px, py, hero.facing);
  for (const b of bullets) b.a.draw(ctx, b.x - camX, b.y, b.dir);
  if (guides) {
    drawGuides(px, py);
    const m = hero.anim.muzzle;
    if (m) { ctx.fillStyle = 'rgb(230,60,60)'; ctx.fillRect(Math.round(px + m.x * hero.facing) - 1, Math.round(py + m.y) - 1, 3, 3); }
  }
  for (const l of room.front) drawLayer(l);

  const a = hero.anim;
  const miss = hero.missing;
  hud.textContent =
    `${viewer ? 'VIEWER  ' + (vi + 1) + '/' + tags.length + '  ' : ''}` +
    `${a.name}  FRAME ${a.i + 1}/${a.count}` +
    `${slow ? '  SLOW 1/4' : ''}${miss.length ? '  MISSING: ' + miss.join(' ') : ''}`;
  requestAnimationFrame(frame);
}

loadAll().then(() => requestAnimationFrame(frame)).catch(err => {
  hud.textContent = 'LOAD FAILED: ' + err.message + ' (run serve.py, open localhost:8000)';
});
export { MOVES };

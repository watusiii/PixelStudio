// sprite.js: reads an Aseprite sprite-sheet export (JSON Array or JSON Hash) and plays its tags.
// Saji's export drops in as-is: frames, per-frame durations, frameTags, and a "pivot" slice.

export async function loadSheet(jsonUrl) {
  const bust = `?t=${Date.now()}`;
  const data = await (await fetch(jsonUrl + bust)).json();
  const base = jsonUrl.slice(0, jsonUrl.lastIndexOf('/') + 1);
  const img = new Image();
  img.src = base + data.meta.image + bust;
  await img.decode();

  const list = Array.isArray(data.frames) ? data.frames : Object.values(data.frames);
  const frames = list.map(f => ({ ...f.frame, duration: f.duration || 100, src: f.spriteSourceSize, size: f.sourceSize }));

  const tags = {};
  for (const t of data.meta.frameTags || []) {
    const ids = [];
    for (let i = t.from; i <= t.to; i++) ids.push(i);
    if (t.direction === 'reverse') ids.reverse();
    if (t.direction === 'pingpong') for (let i = t.to - 1; i > t.from; i--) ids.push(i);
    tags[t.name] = ids;
  }

  // pivot: from a slice named "pivot" (bounds origin + pivot), else bottom centre of the cell
  const cell = list[0].sourceSize;
  let pivot = { x: Math.floor(cell.w / 2), y: cell.h - 1 };
  const ps = (data.meta.slices || []).find(s => s.name.toLowerCase() === 'pivot');
  if (ps && ps.keys.length) {
    const k = ps.keys[0];
    pivot = k.pivot ? { x: k.bounds.x + k.pivot.x, y: k.bounds.y + k.pivot.y } : { x: k.bounds.x, y: k.bounds.y };
  }
  // muzzle: a slice named "muzzle", one key per shooting frame (Aseprite slice keys). Where bullets start.
  const muzzle = {};
  const ms = (data.meta.slices || []).find(s => s.name.toLowerCase() === 'muzzle');
  if (ms) for (const k of ms.keys) muzzle[k.frame] = { x: k.bounds.x, y: k.bounds.y };
  return { img, frames, tags, pivot, cell, muzzle };
}

export class Animator {
  constructor(sheet) { this.sheet = sheet; this.play('idle'); }
  has(name) { return !!this.sheet.tags[name]; }
  play(name, restart = false, keepFrame = false) {
    if (!this.has(name)) name = this.has('idle') ? 'idle' : Object.keys(this.sheet.tags)[0];
    if (this.name === name && !restart) return;
    const i = keepFrame ? this.i : 0, t = keepFrame ? this.t : 0;
    this.name = name; this.done = false;
    this.i = Math.min(i, this.sheet.tags[name].length - 1); this.t = t;
  }
  // muzzle of the current frame relative to the pivot, or null
  get muzzle() {
    const id = this.sheet.tags[this.name][this.i], m = this.sheet.muzzle[id];
    if (!m) return null;
    return { x: m.x - this.sheet.pivot.x, y: m.y - this.sheet.pivot.y };
  }
  update(dt, loop) {
    const ids = this.sheet.tags[this.name];
    this.t += dt * 1000;
    while (this.t >= this.sheet.frames[ids[this.i]].duration) {
      this.t -= this.sheet.frames[ids[this.i]].duration;
      if (this.i < ids.length - 1) this.i++;
      else if (loop) this.i = 0;
      else { this.done = true; this.t = 0; break; }
    }
  }
  get frame() { return this.sheet.frames[this.sheet.tags[this.name][this.i]]; }
  get count() { return this.sheet.tags[this.name].length; }

  // draw with the pivot at (x, y); facing -1 mirrors around the pivot
  draw(ctx, x, y, facing) {
    const f = this.frame, s = this.sheet, p = s.pivot;
    const ox = (f.src ? f.src.x : 0), oy = (f.src ? f.src.y : 0);   // trimmed exports
    ctx.save();
    ctx.translate(Math.round(x), Math.round(y));
    if (facing < 0) ctx.scale(-1, 1);
    ctx.drawImage(s.img, f.x, f.y, f.w, f.h, ox - p.x, oy - p.y, f.w, f.h);
    ctx.restore();
  }
}

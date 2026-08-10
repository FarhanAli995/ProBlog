/**
 * Gallery Tunnel — Interactive 3D Tunnel Component
 * Built with Three.js for ProBlog
 */

(function() {
  'use strict';

  const DEFAULT_IMAGES = [
    "https://imagedelivery.net/IEUjvl3YUlxY-MrTpOAWDQ/f8b3688c-11d0-425c-0b6f-66f133322c00/w=800",
    "https://imagedelivery.net/IEUjvl3YUlxY-MrTpOAWDQ/c083d83a-f5a4-4434-989f-4eaa9bbe7500/w=800",
    "https://imagedelivery.net/IEUjvl3YUlxY-MrTpOAWDQ/12e8b0be-f114-4134-1ab7-53116bfc2800/w=800",
    "https://imagedelivery.net/IEUjvl3YUlxY-MrTpOAWDQ/b14ae2a2-1116-4a7f-0a18-1d74c4a46f00/w=800",
    "https://imagedelivery.net/IEUjvl3YUlxY-MrTpOAWDQ/babdb603-8b5b-4520-58d6-240a34463c00/w=800",
  ];

  const DEFAULTS = {
    background: "#000000",
    lineColor: "#B0B0B0",
    lineOpacity: 50,
    colors: ["#FF6A00", "#AB54F7", "#EA3737", "#0072E3", "#00AA3C", "#FFB200"],
    grid: 4,
    speed: 100,
    boost: 100,
    fade: 100,
    label: true,
    labelText: "Press to Start",
    labelFill: "#FFFFFF",
    labelColor: "#000000",
  };

  const TUNNEL_WIDTH = 2;
  const TUNNEL_HEIGHT = 1.8;
  const SEGMENT_DEPTH = 1;
  const NUM_SEGMENTS = 15;
  const LINE_RADIUS = 0.003;
  const SCROLL_TO_Z = 0.05;
  const CAMERA_CHASE = 0.1;
  const FADE_IN = 1;
  const FOG_FAR = NUM_SEGMENTS * SEGMENT_DEPTH * 0.95;

  class GalleryTunnel {
    constructor(containerSelector, config = {}) {
      this.container = document.querySelector(containerSelector);
      if (!this.container) {
        console.error(`Container "${containerSelector}" not found`);
        return;
      }

      this.config = { ...DEFAULTS, ...config };
      this.initScene();
      this.animate();
    }

    initScene() {
      // Three.js scene setup
      this.scene = new THREE.Scene();
      this.scene.background = new THREE.Color(this.config.background);

      const fogNear = Math.min(
        FOG_FAR * (1 - Math.min(100, Math.max(0, this.config.fade)) / 100),
        FOG_FAR - 0.01
      );
      this.scene.fog = new THREE.Fog(
        new THREE.Color(this.config.background),
        fogNear,
        FOG_FAR
      );

      // Camera
      this.camera = new THREE.PerspectiveCamera(45, 1, 1, 1000);
      this.camera.position.set(0, 0, 0);

      // Canvas setup
      this.canvas = document.createElement('canvas');
      this.container.appendChild(this.canvas);

      // Renderer
      this.renderer = new THREE.WebGLRenderer({
        canvas: this.canvas,
        antialias: true,
        alpha: false,
        powerPreference: "high-performance",
      });
      this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

      // Setup materials and geometries
      this.setupMaterials();
      this.setupGeometries();
      this.createTunnel();
      this.setupEventListeners();
      this.resize();

      // ResizeObserver
      this.resizeObserver = new ResizeObserver(() => this.resize());
      this.resizeObserver.observe(this.container);
    }

    setupMaterials() {
      this.lineMaterial = new THREE.MeshBasicMaterial({
        color: new THREE.Color(this.config.lineColor),
        transparent: true,
        opacity: Math.min(100, Math.max(0, this.config.lineOpacity)) / 100,
      });

      this.colorMats = this.config.colors.map(
        (hex) =>
          new THREE.MeshBasicMaterial({
            color: new THREE.Color(hex),
            side: THREE.DoubleSide,
          })
      );

      this.loader = new THREE.TextureLoader();
      this.loader.setCrossOrigin("anonymous");
      this.imageMats = (this.config.images || DEFAULT_IMAGES).map((url) => {
        const mat = new THREE.MeshBasicMaterial({
          transparent: true,
          opacity: 0,
          side: THREE.DoubleSide,
        });
        this.loader.load(
          url,
          (tex) => {
            tex.minFilter = THREE.LinearFilter;
            tex.generateMipmaps = false;
            tex.colorSpace = THREE.SRGBColorSpace;
            mat.map = tex;
            mat.needsUpdate = true;
            this.fadingMats.push(mat);
          },
          undefined,
          () => {}
        );
        return mat;
      });

      this.fadingMats = [];
    }

    setupGeometries() {
      const cols = Math.max(1, Math.round(this.config.grid));
      const rows = Math.max(1, Math.round(this.config.grid));

      this.geoFloor = new THREE.PlaneGeometry(TUNNEL_WIDTH / cols, SEGMENT_DEPTH);
      this.geoWall = new THREE.PlaneGeometry(SEGMENT_DEPTH, TUNNEL_HEIGHT / rows);

      this.geoTubeZ = new THREE.TubeGeometry(
        new THREE.LineCurve3(
          new THREE.Vector3(0, 0, 0),
          new THREE.Vector3(0, 0, -SEGMENT_DEPTH)
        ),
        1,
        LINE_RADIUS,
        8
      );

      this.geoTubeX = new THREE.TubeGeometry(
        new THREE.LineCurve3(
          new THREE.Vector3(0, 0, 0),
          new THREE.Vector3(TUNNEL_WIDTH, 0, 0)
        ),
        1,
        LINE_RADIUS,
        8
      );

      this.geoTubeY = new THREE.TubeGeometry(
        new THREE.LineCurve3(
          new THREE.Vector3(0, 0, 0),
          new THREE.Vector3(0, TUNNEL_HEIGHT, 0)
        ),
        1,
        LINE_RADIUS,
        8
      );
    }

    createTunnel() {
      const hw = TUNNEL_WIDTH / 2;
      const hh = TUNNEL_HEIGHT / 2;
      const cols = Math.max(1, Math.round(this.config.grid));
      const rows = Math.max(1, Math.round(this.config.grid));
      const colW = TUNNEL_WIDTH / cols;
      const rowH = TUNNEL_HEIGHT / rows;

      this.slots = [];
      const z = -SEGMENT_DEPTH / 2;

      for (let i = 0; i < cols; i++) {
        const x = -hw + i * colW + colW / 2;
        this.slots.push({
          geo: this.geoFloor,
          pos: new THREE.Vector3(x, -hh, z),
          rot: new THREE.Euler(-Math.PI / 2, 0, 0),
        });
        this.slots.push({
          geo: this.geoFloor,
          pos: new THREE.Vector3(x, hh, z),
          rot: new THREE.Euler(Math.PI / 2, 0, 0),
        });
      }

      for (let i = 0; i < rows; i++) {
        const y = -hh + i * rowH + rowH / 2;
        this.slots.push({
          geo: this.geoWall,
          pos: new THREE.Vector3(-hw, y, z),
          rot: new THREE.Euler(0, Math.PI / 2, 0),
        });
        this.slots.push({
          geo: this.geoWall,
          pos: new THREE.Vector3(hw, y, z),
          rot: new THREE.Euler(0, -Math.PI / 2, 0),
        });
      }

      this.segments = [];
      for (let i = 0; i < NUM_SEGMENTS; i++) {
        const seg = this.createSegment(-i * SEGMENT_DEPTH);
        this.scene.add(seg);
        this.segments.push(seg);
      }

      this.imageIndex = 0;
      this.colorIndex = 0;
      this.populateIndex = 0;
    }

    createSegment(z) {
      const hw = TUNNEL_WIDTH / 2;
      const hh = TUNNEL_HEIGHT / 2;
      const cols = Math.max(1, Math.round(this.config.grid));
      const rows = Math.max(1, Math.round(this.config.grid));
      const colW = TUNNEL_WIDTH / cols;
      const rowH = TUNNEL_HEIGHT / rows;

      const group = new THREE.Group();
      group.position.z = z;

      const tube = (geo, x, y, z = 0) => {
        const m = new THREE.Mesh(geo, this.lineMaterial);
        m.position.set(x, y, z);
        return m;
      };

      for (let i = 0; i <= cols; i++) {
        const x = -hw + i * colW;
        group.add(tube(this.geoTubeZ, x, -hh));
        group.add(tube(this.geoTubeZ, x, hh));
      }

      for (let i = 1; i < rows; i++) {
        const y = -hh + i * rowH;
        group.add(tube(this.geoTubeZ, -hw, y));
        group.add(tube(this.geoTubeZ, hw, y));
      }

      group.add(tube(this.geoTubeX, -hw, -hh));
      group.add(tube(this.geoTubeX, -hw, hh));
      group.add(tube(this.geoTubeY, -hw, -hh));
      group.add(tube(this.geoTubeY, hw, -hh));

      const slabs = this.slots.map((slot) => {
        const m = new THREE.Mesh(slot.geo, this.colorMats[0]);
        m.position.copy(slot.pos);
        m.rotation.copy(slot.rot);
        m.visible = false;
        group.add(m);
        return m;
      });

      group.userData.slabs = slabs;
      this.populateSegment(group);

      return group;
    }

    populateSegment(group) {
      const takesSlabs = this.populateIndex % 2 === 0;
      this.populateIndex++;
      const slabs = group.userData.slabs;

      for (const slab of slabs) {
        if (!takesSlabs || Math.random() > 0.5) {
          slab.visible = false;
          continue;
        }

        slab.visible = true;
        if (Math.random() > 0.5) {
          slab.material = this.colorMats[(5 * this.colorIndex) % this.colorMats.length];
          this.colorIndex++;
        } else {
          slab.material = this.imageMats[(3 * this.imageIndex) % this.imageMats.length];
          this.imageIndex++;
        }
      }
    }

    setupEventListeners() {
      this.scrollPos = 0;
      this.pressed = false;
      this.cfgRef = { speed: this.config.speed / 100, boost: this.config.boost / 10 };

      // Create custom cursor
      if (this.config.label) {
        this.cursorEl = document.createElement('div');
        this.cursorEl.style.cssText = `
          position: absolute;
          top: 0;
          left: 0;
          transform: translate(0%, -100%) scale(1);
          pointer-events: none;
          opacity: 0;
          background: ${this.config.labelFill};
          color: ${this.config.labelColor};
          border-radius: 9999px;
          padding: 10px 20px;
          transition: transform 0.1s ease, opacity 0.2s ease;
          white-space: nowrap;
          user-select: none;
          font-family: 'Inter', sans-serif;
          font-size: 14px;
          font-weight: 500;
          z-index: 1000;
        `;
        this.cursorEl.textContent = this.config.labelText;
        this.container.appendChild(this.cursorEl);
      }

      // Event handlers
      this.container.addEventListener('pointermove', (e) => this.onMove(e));
      this.container.addEventListener('pointerenter', () => this.onEnter());
      this.container.addEventListener('pointerleave', () => this.onLeave());
      this.container.addEventListener('pointerdown', () => this.onDown());
      window.addEventListener('pointerup', () => this.onUp());
    }

    onMove(e) {
      if (!this.config.label || !this.cursorEl) return;
      const rect = this.container.getBoundingClientRect();
      const sx = rect.width > 0 ? this.container.clientWidth / rect.width : 1;
      const sy = rect.height > 0 ? this.container.clientHeight / rect.height : 1;
      this.cursorEl.style.left = `${(e.clientX - rect.left) * sx}px`;
      this.cursorEl.style.top = `${(e.clientY - rect.top) * sy}px`;
    }

    onEnter() {
      if (this.config.label && this.cursorEl) {
        this.cursorEl.style.opacity = '1';
      }
    }

    onLeave() {
      this.pressed = false;
      if (this.config.label && this.cursorEl) {
        this.cursorEl.style.opacity = '0';
        this.cursorEl.style.transform = 'translate(0%, -100%) scale(1)';
      }
    }

    onDown() {
      this.pressed = true;
      if (this.config.label && this.cursorEl) {
        this.cursorEl.style.transform = 'translate(0%, -100%) scale(0.85)';
      }
    }

    onUp() {
      this.pressed = false;
      if (this.config.label && this.cursorEl) {
        this.cursorEl.style.transform = 'translate(0%, -100%) scale(1)';
      }
    }

    resize() {
      const w = Math.max(1, this.container.clientWidth);
      const h = Math.max(1, this.container.clientHeight);
      this.camera.aspect = w / h;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(w, h, false);
    }

    animate = () => {
      this.animationId = requestAnimationFrame(() => this.animate());

      const cfg = this.cfgRef;
      this.scrollPos += this.pressed ? cfg.boost : cfg.speed;

      const want = -SCROLL_TO_Z * this.scrollPos;
      this.camera.position.z += CAMERA_CHASE * (want - this.camera.position.z);

      const span = NUM_SEGMENTS * SEGMENT_DEPTH;
      const z = this.camera.position.z;

      for (const seg of this.segments) {
        if (seg.position.z > z + SEGMENT_DEPTH) {
          let min = 0;
          for (const s of this.segments) min = Math.min(min, s.position.z);
          seg.position.z = min - SEGMENT_DEPTH;
          this.populateSegment(seg);
        } else if (seg.position.z < z - span - SEGMENT_DEPTH) {
          let max = -999999;
          for (const s of this.segments) max = Math.max(max, s.position.z);
          seg.position.z = max + SEGMENT_DEPTH;
          this.populateSegment(seg);
        }
      }

      for (let i = this.fadingMats.length - 1; i >= 0; i--) {
        const m = this.fadingMats[i];
        const dt = 1 / 60; // approximate delta time
        m.opacity = Math.min(1, m.opacity + dt / FADE_IN);
        if (m.opacity >= 1) this.fadingMats.splice(i, 1);
      }

      this.renderer.render(this.scene, this.camera);
    };

    dispose() {
      cancelAnimationFrame(this.animationId);
      this.resizeObserver?.disconnect();

      this.container.removeEventListener('pointermove', (e) => this.onMove(e));
      this.container.removeEventListener('pointerenter', () => this.onEnter());
      this.container.removeEventListener('pointerleave', () => this.onLeave());
      this.container.removeEventListener('pointerdown', () => this.onDown());
      window.removeEventListener('pointerup', () => this.onUp());

      this.geoFloor?.dispose();
      this.geoWall?.dispose();
      this.geoTubeZ?.dispose();
      this.geoTubeX?.dispose();
      this.geoTubeY?.dispose();
      this.colorMats.forEach((m) => m.dispose());
      this.imageMats.forEach((m) => {
        m.map?.dispose();
        m.dispose();
      });
      this.lineMaterial?.dispose();
      this.renderer?.dispose();
    }
  }

  // Export to global scope
  window.GalleryTunnel = GalleryTunnel;
})();

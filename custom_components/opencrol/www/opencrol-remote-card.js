// OpenCtrol Remote Card for Home Assistant Lovelace
// Version: 2.1.0
// Auto-loaded by OpenCtrol Integration

// Load CSS
const link = document.createElement('link');
link.rel = 'stylesheet';
link.type = 'text/css';
link.href = '/local/opencrol/opencrol-remote-card.css';
document.head.appendChild(link);

class OpenCtrolRemoteCard extends HTMLElement {
  constructor() {
    super();
    this._screenStreamUrl = null;
    this._imgElement = null;
    this._fullscreenOverlay = null;
    this._activeModifiers = new Set();
    this._isFullscreenOpen = false;
  }

  static getConfigElement() {
    return document.createElement('opencrol-remote-card-editor');
  }

  static getStubConfig() {
    return {
      type: 'custom:opencrol-remote-card',
      entity: '',
      base_url: null
    };
  }

  setConfig(config) {
    if (!config.entity) {
      throw new Error('Entity is required');
    }
    this.config = config;
    this.entity = config.entity;
  }

  set hass(hass) {
    this._hass = hass;
    if (!this._hass || !this.config) return;
    this.updateCard();
  }

  connectedCallback() {
    this.updateCard();
    // Close fullscreen on ESC key
    document.addEventListener('keydown', this._handleEscKey.bind(this));
  }

  disconnectedCallback() {
    // Stop screen stream when card is removed
    if (this._imgElement) {
      this._imgElement.src = '';
      this._imgElement = null;
    }

    // Remove fullscreen overlay if open
    this.closeFullscreenRemote();
    
    document.removeEventListener('keydown', this._handleEscKey.bind(this));
  }

  _handleEscKey(e) {
    if (e.key === 'Escape' && this._isFullscreenOpen) {
      this.closeFullscreenRemote();
    }
  }

  updateCard() {
    if (!this.config || !this._hass) return;

    const entity = this._hass.states[this.config.entity];
    if (!entity) {
      this.innerHTML = '<ha-card><div class="error">Entity not found</div></ha-card>';
      return;
    }

    const state = entity.state;
    const attributes = entity.attributes || {};
    const isOnline = state === 'on' || state === 'online';
    
    // Get base URL from entity attributes or config
    const baseUrl = this.config.base_url || this.getBaseUrlFromEntity(entity);
    this._screenStreamUrl = baseUrl ? `${baseUrl}/api/v1/screenstream/stream` : null;

    const clientId = attributes.client_id || entity.attributes.friendly_name || this.config.entity;
    const monitors = attributes.monitors || [];
    const currentMonitor = attributes.current_monitor !== undefined ? attributes.current_monitor : 0;

    // Header controls: status dot, power, screens, sound, keyboard
    this.innerHTML = `
      <ha-card>
        <div class="card-header">
          <div class="header-left">
            <div class="status-dot ${isOnline ? 'online' : 'offline'}" title="${isOnline ? 'Online' : 'Offline'}"></div>
            <div class="name">${this._escapeHtml(clientId)}</div>
          </div>
          <div class="header-right">
            <button class="header-btn power-btn" title="Lock Workstation" aria-label="Lock Workstation">
              <ha-icon icon="mdi:lock"></ha-icon>
            </button>
            <div class="header-divider"></div>
            <div class="screen-buttons" title="Monitor Selection">
              ${monitors.length > 0 ? monitors.map((monitor, index) => `
                <button class="header-btn screen-btn ${index === currentMonitor ? 'active' : ''}" 
                        data-monitor-index="${index}" 
                        aria-label="Monitor ${index + 1}"
                        title="Switch to Monitor ${index + 1}">
                  ${index + 1}
                </button>
              `).join('') : '<span class="no-monitors">No monitors</span>'}
            </div>
            <div class="header-divider"></div>
            <button class="header-btn sound-btn" title="Sound Mixer" aria-label="Sound Mixer">
              <ha-icon icon="mdi:volume-high"></ha-icon>
            </button>
            <button class="header-btn keyboard-btn" title="Keyboard" aria-label="Keyboard">
              <ha-icon icon="mdi:keyboard"></ha-icon>
            </button>
          </div>
        </div>
        <div class="card-content">
          <div class="screen-container ${!isOnline ? 'offline' : ''}">
            ${isOnline && this._screenStreamUrl ? `
              <div class="screen-wrapper">
                <img id="screen-stream" 
                     src="${this._screenStreamUrl}" 
                     alt="Screen Stream"
                     class="screen-stream"
                     loading="lazy">
                <div id="screen-overlay" class="screen-overlay"></div>
                <button class="fullscreen-btn" title="Fullscreen" aria-label="Open Fullscreen">
                  <ha-icon icon="mdi:fullscreen"></ha-icon>
                </button>
              </div>
            ` : `
              <div class="touchpad-placeholder ${isOnline ? '' : 'offline'}" id="touchpad-placeholder">
                <div class="touchpad-icon">${isOnline ? '🖱️' : '📴'}</div>
                <div class="touchpad-text">${isOnline ? 'Touchpad Mode' : 'Device Offline'}</div>
                <div class="touchpad-hint">${isOnline ? 'Move your finger to control the mouse' : 'Waiting for connection...'}</div>
              </div>
            `}
          </div>

          <div class="controls-panel popups">
            <div class="control-section keyboard-section">
              <div class="section-header">
                <div class="section-title">Keyboard</div>
                <button class="close-popup" aria-label="Close Keyboard">
                  <ha-icon icon="mdi:close"></ha-icon>
                </button>
              </div>
              <div class="input-group">
                <input type="text" id="text-input" placeholder="Type text here..." class="text-input" aria-label="Text Input">
                <button class="control-btn" id="type-btn" aria-label="Send Text">
                  <ha-icon icon="mdi:send"></ha-icon> Type
                </button>
              </div>
              <div class="keyboard-grid">
                <div class="keyboard-row">
                  <button class="keyboard-key" data-key="ESC" aria-label="Escape">Esc</button>
                  <button class="keyboard-key" data-key="F1" aria-label="F1">F1</button>
                  <button class="keyboard-key" data-key="F2" aria-label="F2">F2</button>
                  <button class="keyboard-key" data-key="F3" aria-label="F3">F3</button>
                  <button class="keyboard-key" data-key="F4" aria-label="F4">F4</button>
                  <button class="keyboard-key" data-key="F5" aria-label="F5">F5</button>
                  <button class="keyboard-key" data-key="F6" aria-label="F6">F6</button>
                  <button class="keyboard-key" data-key="F7" aria-label="F7">F7</button>
                  <button class="keyboard-key" data-key="F8" aria-label="F8">F8</button>
                  <button class="keyboard-key" data-key="F9" aria-label="F9">F9</button>
                  <button class="keyboard-key" data-key="F10" aria-label="F10">F10</button>
                  <button class="keyboard-key" data-key="F11" aria-label="F11">F11</button>
                  <button class="keyboard-key" data-key="F12" aria-label="F12">F12</button>
                </div>
                <div class="keyboard-row">
                  <button class="keyboard-key toggle" data-key="CTRL" aria-label="Control">Ctrl</button>
                  <button class="keyboard-key toggle" data-key="ALT" aria-label="Alt">Alt</button>
                  <button class="keyboard-key toggle" data-key="SHIFT" aria-label="Shift">Shift</button>
                  <button class="keyboard-key toggle" data-key="WIN" aria-label="Windows">Win</button>
                  <button class="keyboard-key" data-key="TAB" aria-label="Tab">Tab</button>
                  <button class="keyboard-key" data-key="CAPS_LOCK" aria-label="Caps Lock">Caps</button>
                  <button class="keyboard-key" data-key="SPACE" aria-label="Space">Space</button>
                  <button class="keyboard-key" data-key="ENTER" aria-label="Enter">Enter</button>
                </div>
                <div class="keyboard-row">
                  <button class="keyboard-key" data-key="INSERT" aria-label="Insert">Ins</button>
                  <button class="keyboard-key" data-key="DELETE" aria-label="Delete">Del</button>
                  <button class="keyboard-key" data-key="HOME" aria-label="Home">Home</button>
                  <button class="keyboard-key" data-key="END" aria-label="End">End</button>
                  <button class="keyboard-key" data-key="PAGEUP" aria-label="Page Up">PgUp</button>
                  <button class="keyboard-key" data-key="PAGEDOWN" aria-label="Page Down">PgDn</button>
                  <button class="keyboard-key" data-key="UP" aria-label="Arrow Up">↑</button>
                  <button class="keyboard-key" data-key="LEFT" aria-label="Arrow Left">←</button>
                  <button class="keyboard-key" data-key="DOWN" aria-label="Arrow Down">↓</button>
                  <button class="keyboard-key" data-key="RIGHT" aria-label="Arrow Right">→</button>
                </div>
                <div class="keyboard-row">
                  <button class="keyboard-key" data-keys="CTRL+ALT+DEL" aria-label="Ctrl Alt Del">Ctrl+Alt+Del</button>
                  <button class="keyboard-key" data-keys="ALT+TAB" aria-label="Alt Tab">Alt+Tab</button>
                  <button class="keyboard-key" data-keys="CTRL+C" aria-label="Copy">Ctrl+C</button>
                  <button class="keyboard-key" data-keys="CTRL+V" aria-label="Paste">Ctrl+V</button>
                  <button class="keyboard-key" data-keys="CTRL+SHIFT+ESC" aria-label="Task Manager">TaskMgr</button>
                </div>
              </div>
            </div>

            <div class="control-section sound-section">
              <div class="section-header">
                <div class="section-title">Volume Control</div>
                <button class="close-popup" aria-label="Close Volume">
                  <ha-icon icon="mdi:close"></ha-icon>
                </button>
              </div>
              <div class="volume-control">
                <ha-icon icon="mdi:volume-low" class="volume-icon"></ha-icon>
                <input type="range" id="volume-slider" min="0" max="100" 
                       value="${Math.round((attributes.master_volume || 0) * 100)}" 
                       class="volume-slider" 
                       aria-label="Volume">
                <ha-icon icon="mdi:volume-high" class="volume-icon"></ha-icon>
                <span id="volume-value" class="volume-value">${Math.round((attributes.master_volume || 0) * 100)}%</span>
              </div>
            </div>
          </div>
        </div>
      </ha-card>
    `;

    this.attachEventHandlers();
    this.setupScreenInteraction();
  }

  _escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  getBaseUrlFromEntity(entity) {
    // Try to extract base URL from entity attributes
    const attrs = entity.attributes || {};
    if (attrs.base_url) return attrs.base_url;
    
    // Try to get from config entry
    if (this._hass.config_entries && this._hass.config_entries.entries) {
      const configEntry = this._hass.config_entries.entries.find(
        e => e.domain === 'opencrol' && (e.title?.includes(attrs.client_id || '') || e.title?.includes(entity.entity_id))
      );
      if (configEntry?.data?.host) {
        const port = configEntry.data.port || 8080;
        const protocol = configEntry.data.use_https ? 'https' : 'http';
        return `${protocol}://${configEntry.data.host}:${port}`;
      }
    }
    
    return null;
  }

  setupScreenInteraction() {
    const screenOverlay = this.querySelector('#screen-overlay');
    const screenImg = this.querySelector('#screen-stream');
    const touchpadPlaceholder = this.querySelector('#touchpad-placeholder');
    const screenContainer = this.querySelector('.screen-container');
    
    if (!screenImg || !screenOverlay) {
      // Touchpad mode
      if (touchpadPlaceholder) {
        this.setupTouchpadMode(touchpadPlaceholder);
      }
      return;
    }

    this._imgElement = screenImg;

    // Handle clicks on screen
    screenOverlay.addEventListener('click', (e) => {
      if (e.target === screenOverlay || e.target.classList.contains('screen-overlay')) {
        const rect = screenImg.getBoundingClientRect();
        const x = Math.round((e.clientX - rect.left) * (screenImg.naturalWidth / rect.width));
        const y = Math.round((e.clientY - rect.top) * (screenImg.naturalHeight / rect.height));
        
        this.sendCommand('click', { 
          button: 'left', 
          x: x, 
          y: y 
        });
      }
    });

    // Handle right-click
    screenOverlay.addEventListener('contextmenu', (e) => {
      e.preventDefault();
      const rect = screenImg.getBoundingClientRect();
      const x = Math.round((e.clientX - rect.left) * (screenImg.naturalWidth / rect.width));
      const y = Math.round((e.clientY - rect.top) * (screenImg.naturalHeight / rect.height));
      
      this.sendCommand('click', { 
        button: 'right', 
        x: x, 
        y: y 
      });
    });

    // Handle double-click
    let lastClickTime = 0;
    screenOverlay.addEventListener('click', (e) => {
      const now = Date.now();
      if (now - lastClickTime < 300) {
        // Double click
        const rect = screenImg.getBoundingClientRect();
        const x = Math.round((e.clientX - rect.left) * (screenImg.naturalWidth / rect.width));
        const y = Math.round((e.clientY - rect.top) * (screenImg.naturalHeight / rect.height));
        this.sendCommand('click', { button: 'left', x: x, y: y });
        setTimeout(() => {
          this.sendCommand('click', { button: 'left', x: x, y: y });
        }, 50);
      }
      lastClickTime = now;
    });

    // Handle mouse movement for drag
    let isDragging = false;
    let lastMoveTime = 0;
    screenOverlay.addEventListener('mousedown', () => { 
      isDragging = true; 
    });
    screenOverlay.addEventListener('mouseup', () => { 
      isDragging = false; 
    });
    screenOverlay.addEventListener('mousemove', (e) => {
      if (isDragging) {
        const now = Date.now();
        if (now - lastMoveTime > 50) { // Throttle to ~20fps
          const rect = screenImg.getBoundingClientRect();
          const x = Math.round((e.clientX - rect.left) * (screenImg.naturalWidth / rect.width));
          const y = Math.round((e.clientY - rect.top) * (screenImg.naturalHeight / rect.height));
          
          this.sendCommand('move_mouse', { x: x, y: y });
          lastMoveTime = now;
        }
      }
    });

    // Handle scroll
    screenOverlay.addEventListener('wheel', (e) => {
      e.preventDefault();
      const delta = Math.round(e.deltaY);
      if (delta !== 0) {
        this.sendCommand('scroll', { delta: delta });
      }
    });

    // Check for screen stream errors (screen off)
    screenImg.addEventListener('error', () => {
      screenImg.style.display = 'none';
      if (screenContainer) screenContainer.classList.add('touchpad-mode');
      if (touchpadPlaceholder) {
        touchpadPlaceholder.style.display = 'flex';
        this.setupTouchpadMode(touchpadPlaceholder);
      }
    });

    // Fullscreen button
    const fullscreenBtn = this.querySelector('.fullscreen-btn');
    if (fullscreenBtn) {
      fullscreenBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        const baseUrl = this.config.base_url || this.getBaseUrlFromEntity(this._hass.states[this.config.entity]);
        if (baseUrl) {
          const entity = this._hass.states[this.config.entity];
          const attributes = entity?.attributes || {};
          const currentMonitor = attributes.current_monitor !== undefined ? attributes.current_monitor : 0;
          this.openFullscreenRemote(baseUrl, currentMonitor);
        }
      });
    }
  }

  setupTouchpadMode(container) {
    if (!container) return;

    let lastX = null;
    let lastY = null;
    let isDown = false;
    let touchStartTime = 0;

    // Touchpad-style relative movement
    container.addEventListener('mousedown', (e) => {
      isDown = true;
      lastX = e.clientX;
      lastY = e.clientY;
      touchStartTime = Date.now();
    });

    container.addEventListener('mouseup', () => {
      const now = Date.now();
      if (isDown && (now - touchStartTime < 200) && lastX === null && lastY === null) {
        // Quick tap - left click
        this.sendCommand('click', { button: 'left' });
      }
      isDown = false;
      lastX = null;
      lastY = null;
    });

    container.addEventListener('mousemove', (e) => {
      if (isDown && lastX !== null && lastY !== null) {
        const deltaX = e.clientX - lastX;
        const deltaY = e.clientY - lastY;
        
        if (Math.abs(deltaX) > 2 || Math.abs(deltaY) > 2) {
          this.sendCommand('move_mouse', { 
            x: Math.round(deltaX * 2), 
            y: Math.round(deltaY * 2),
            relative: true
          });
          
          lastX = e.clientX;
          lastY = e.clientY;
        }
      } else if (isDown) {
        lastX = e.clientX;
        lastY = e.clientY;
      }
    });

    // Right-click (long press or context menu)
    container.addEventListener('contextmenu', (e) => {
      e.preventDefault();
      this.sendCommand('click', { button: 'right' });
    });

    // Touch support for mobile
    container.addEventListener('touchstart', (e) => {
      e.preventDefault();
      const touch = e.touches[0];
      lastX = touch.clientX;
      lastY = touch.clientY;
      isDown = true;
      touchStartTime = Date.now();
    });

    container.addEventListener('touchend', (e) => {
      e.preventDefault();
      const now = Date.now();
      if (isDown && (now - touchStartTime < 300)) {
        // Quick tap
        this.sendCommand('click', { button: 'left' });
      }
      isDown = false;
      lastX = null;
      lastY = null;
    });

    container.addEventListener('touchmove', (e) => {
      e.preventDefault();
      if (isDown && lastX !== null && lastY !== null) {
        const touch = e.touches[0];
        const deltaX = touch.clientX - lastX;
        const deltaY = touch.clientY - lastY;
        
        if (Math.abs(deltaX) > 2 || Math.abs(deltaY) > 2) {
          this.sendCommand('move_mouse', { 
            x: Math.round(deltaX * 2),
            y: Math.round(deltaY * 2),
            relative: true
          });
          
          lastX = touch.clientX;
          lastY = touch.clientY;
        }
      }
    });
  }

  attachEventHandlers() {
    // Header buttons
    const powerBtn = this.querySelector('.power-btn');
    if (powerBtn && this._hass && this.config?.entity) {
      powerBtn.addEventListener('click', () => {
        this._hass.callService('opencrol', 'lock', {
          entity_id: this.config.entity,
        });
      });
    }

    // Screen buttons - select monitor and open full-screen stream
    const screenButtons = this.querySelectorAll('.screen-btn');
    screenButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        const index = parseInt(btn.dataset.monitorIndex);
        const baseUrl = this.config.base_url || this.getBaseUrlFromEntity(this._hass.states[this.config.entity]);
        if (!baseUrl || Number.isNaN(index)) return;

        // Mark active button
        screenButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        // Ask backend to switch monitor
        fetch(`${baseUrl}/api/v1/status/monitors/${index}/select`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          }
        }).catch(() => {});

        // Open full-screen remote desktop overlay
        this.openFullscreenRemote(baseUrl, index);
      });
    });

    // Sound / keyboard popups with close buttons
    const soundBtn = this.querySelector('.sound-btn');
    if (soundBtn) {
      soundBtn.addEventListener('click', () => {
        this.classList.toggle('show-sound');
        if (this.classList.contains('show-keyboard')) {
          this.classList.remove('show-keyboard');
        }
      });
    }

    const keyboardBtn = this.querySelector('.keyboard-btn');
    if (keyboardBtn) {
      keyboardBtn.addEventListener('click', () => {
        this.classList.toggle('show-keyboard');
        if (this.classList.contains('show-sound')) {
          this.classList.remove('show-sound');
        }
        if (this.classList.contains('show-keyboard')) {
          const textInput = this.querySelector('#text-input');
          if (textInput) {
            setTimeout(() => textInput.focus(), 100);
          }
        }
      });
    }

    // Close popup buttons
    this.querySelectorAll('.close-popup').forEach(btn => {
      btn.addEventListener('click', () => {
        this.classList.remove('show-keyboard', 'show-sound');
      });
    });

    // Volume slider (master volume)
    const volumeSlider = this.querySelector('#volume-slider');
    if (volumeSlider) {
      let volumeTimeout = null;
      volumeSlider.addEventListener('input', (e) => {
        const value = e.target.value;
        const volumeValue = this.querySelector('#volume-value');
        if (volumeValue) {
          volumeValue.textContent = value + '%';
        }
        
        // Debounce volume changes
        clearTimeout(volumeTimeout);
        volumeTimeout = setTimeout(() => {
          this.sendCommand('set_volume', { volume: value / 100 });
        }, 100);
      });
    }

    // Type text button
    const typeBtn = this.querySelector('#type-btn');
    const textInput = this.querySelector('#text-input');
    if (typeBtn && textInput) {
      typeBtn.addEventListener('click', () => {
        if (textInput.value.trim()) {
          this.sendCommand('type_text', { text: textInput.value });
          textInput.value = '';
        }
      });
      textInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          typeBtn.click();
        }
      });
    }

    // Keyboard grid keys with toggle/combination support
    this._activeModifiers = this._activeModifiers || new Set();

    const updateModifierStyles = () => {
      this.querySelectorAll('.keyboard-key.toggle').forEach(btn => {
        const key = (btn.dataset.key || '').toUpperCase();
        if (this._activeModifiers.has(key)) {
          btn.classList.add('toggled');
        } else {
          btn.classList.remove('toggled');
        }
      });
    };

    this.querySelectorAll('.keyboard-key').forEach(btn => {
      btn.addEventListener('click', () => {
        const key = (btn.dataset.key || '').toUpperCase();
        const combo = btn.dataset.keys;
        const isToggle = btn.classList.contains('toggle');

        if (combo) {
          // Explicit combination button (e.g., Ctrl+Alt+Del)
          this.sendCommand('send_key', { keys: combo });
          // Clear any active modifiers after explicit combo
          this._activeModifiers.clear();
          updateModifierStyles();
          return;
        }

        if (!key && !combo) {
          return;
        }

        if (isToggle && key) {
          // Toggle modifier state
          if (this._activeModifiers.has(key)) {
            this._activeModifiers.delete(key);
          } else {
            this._activeModifiers.add(key);
          }
          updateModifierStyles();
        } else if (key) {
          // Non-modifier: combine with any active modifiers and send
          const mods = Array.from(this._activeModifiers);
          const parts = mods.length > 0 ? [...mods, key] : [key];
          const keysString = parts.join('+');
          this.sendCommand('send_key', { keys: keysString });
          // Clear modifiers after use
          this._activeModifiers.clear();
          updateModifierStyles();
        }
      });
    });
  }

  openFullscreenRemote(baseUrl, monitorIndex = 0) {
    if (this._isFullscreenOpen) {
      this.closeFullscreenRemote();
      return;
    }

    const entity = this._hass.states[this.config.entity];
    const attributes = entity?.attributes || {};
    const clientId = attributes.client_id || entity?.attributes?.friendly_name || this.config.entity;
    const streamUrl = `${baseUrl}/api/v1/screenstream/stream?monitor=${monitorIndex}`;

    // Create fullscreen overlay
    this._fullscreenOverlay = document.createElement('div');
    this._fullscreenOverlay.className = 'opencrol-fullscreen-overlay';
    this._fullscreenOverlay.innerHTML = `
      <div class="opencrol-fullscreen-header">
        <div class="opencrol-fullscreen-title">
          <ha-icon icon="mdi:monitor"></ha-icon>
          ${this._escapeHtml(clientId)} - Monitor ${monitorIndex + 1}
        </div>
        <button class="opencrol-fullscreen-close" aria-label="Close Fullscreen">
          <ha-icon icon="mdi:close"></ha-icon>
        </button>
      </div>
      <div class="opencrol-fullscreen-body">
        <div class="opencrol-fullscreen-screen-container">
          <img src="${streamUrl}" 
               alt="Fullscreen Screen Stream" 
               class="opencrol-fullscreen-screen">
          <div class="opencrol-fullscreen-overlay-layer"></div>
        </div>
      </div>
    `;

    document.body.appendChild(this._fullscreenOverlay);
    this._isFullscreenOpen = true;

    // Setup event handlers for fullscreen
    const fullscreenImg = this._fullscreenOverlay.querySelector('.opencrol-fullscreen-screen');
    const fullscreenOverlay = this._fullscreenOverlay.querySelector('.opencrol-fullscreen-overlay-layer');
    const closeBtn = this._fullscreenOverlay.querySelector('.opencrol-fullscreen-close');

    if (closeBtn) {
      closeBtn.addEventListener('click', () => this.closeFullscreenRemote());
    }

    // Handle clicks in fullscreen
    if (fullscreenImg && fullscreenOverlay) {
      fullscreenOverlay.addEventListener('click', (e) => {
        if (e.target === fullscreenOverlay) {
          const rect = fullscreenImg.getBoundingClientRect();
          const x = Math.round((e.clientX - rect.left) * (fullscreenImg.naturalWidth / rect.width));
          const y = Math.round((e.clientY - rect.top) * (fullscreenImg.naturalHeight / rect.height));
          this.sendCommand('click', { button: 'left', x: x, y: y });
        }
      });

      fullscreenOverlay.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        const rect = fullscreenImg.getBoundingClientRect();
        const x = Math.round((e.clientX - rect.left) * (fullscreenImg.naturalWidth / rect.width));
        const y = Math.round((e.clientY - rect.top) * (fullscreenImg.naturalHeight / rect.height));
        this.sendCommand('click', { button: 'right', x: x, y: y });
      });

      // Handle scroll in fullscreen
      fullscreenOverlay.addEventListener('wheel', (e) => {
        e.preventDefault();
        const delta = Math.round(e.deltaY);
        if (delta !== 0) {
          this.sendCommand('scroll', { delta: delta });
        }
      });

      // Handle mouse movement
      let isDragging = false;
      let lastMoveTime = 0;
      fullscreenOverlay.addEventListener('mousedown', () => { isDragging = true; });
      fullscreenOverlay.addEventListener('mouseup', () => { isDragging = false; });
      fullscreenOverlay.addEventListener('mousemove', (e) => {
        if (isDragging) {
          const now = Date.now();
          if (now - lastMoveTime > 50) {
            const rect = fullscreenImg.getBoundingClientRect();
            const x = Math.round((e.clientX - rect.left) * (fullscreenImg.naturalWidth / rect.width));
            const y = Math.round((e.clientY - rect.top) * (fullscreenImg.naturalHeight / rect.height));
            this.sendCommand('move_mouse', { x: x, y: y });
            lastMoveTime = now;
          }
        }
      });

      // Handle errors
      fullscreenImg.addEventListener('error', () => {
        this.closeFullscreenRemote();
      });
    }
  }

  closeFullscreenRemote() {
    if (this._fullscreenOverlay && this._fullscreenOverlay.parentElement) {
      this._fullscreenOverlay.parentElement.removeChild(this._fullscreenOverlay);
    }
    this._fullscreenOverlay = null;
    this._isFullscreenOpen = false;
  }

  sendCommand(service, data = {}) {
    if (!this.config?.entity || !this._hass) return;
    
    const entityId = this.config.entity;
    this._hass.callService('opencrol', service, {
      entity_id: entityId,
      ...data
    }).catch(err => {
      console.error(`OpenCtrol card: Error calling service ${service}:`, err);
    });
  }
}

customElements.define('opencrol-remote-card', OpenCtrolRemoteCard);

// Card registration for Home Assistant card picker
if (window.customCards) {
  window.customCards.push({
    type: 'custom:opencrol-remote-card',
    name: 'OpenCtrol Remote',
    description: 'Remote control card for OpenCtrol devices with screen streaming and touchpad support',
    preview: true,
    documentationURL: 'https://github.com/Kaando2000/opencrol-integration',
    author: 'Kaando2000'
  });
}

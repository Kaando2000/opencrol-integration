// OpenCtrol Remote Card for Home Assistant Lovelace
// Version: 2.0.0
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
  }

  disconnectedCallback() {
    // Stop screen stream when card is removed
    if (this._imgElement) {
      this._imgElement.src = '';
      this._imgElement = null;
    }

    // Remove fullscreen overlay if open
    if (this._fullscreenOverlay && this._fullscreenOverlay.parentElement) {
      this._fullscreenOverlay.parentElement.removeChild(this._fullscreenOverlay);
      this._fullscreenOverlay = null;
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

    // Header controls: status dot, power, screens, sound, keyboard
    this.innerHTML = `
      <ha-card>
        <div class="card-header">
          <div class="header-left">
            <div class="status-dot ${isOnline ? 'online' : 'offline'}"></div>
            <div class="name">${clientId}</div>
          </div>
          <div class="header-right">
            <button class="header-btn power-btn" title="Power">
              <span class="icon">⏻</span>
            </button>
            <div class="header-divider"></div>
            <div class="screen-buttons" title="Screens">
              ${(attributes.monitors || []).map((monitor, index) => `
                <button class="header-btn screen-btn" data-monitor-index="${index}">
                  ${index + 1}
                </button>
              `).join('')}
            </div>
            <div class="header-divider"></div>
            <button class="header-btn sound-btn" title="Sound mixer">
              <span class="icon">🔊</span>
            </button>
            <button class="header-btn keyboard-btn" title="Keyboard">
              <span class="icon">⌨</span>
            </button>
          </div>
        </div>
        <div class="card-content">
          <div class="touchpad-container ${isOnline ? 'touchpad-mode' : 'offline'}">
            ${isOnline ? `
              <div class="touchpad-placeholder" id="touchpad-placeholder">
                <div class="touchpad-icon">🖱️</div>
                <div class="touchpad-text">Touchpad Mode</div>
                <div class="touchpad-hint">Move your finger to control the mouse</div>
              </div>
            ` : `
              <div class="screen-placeholder">
                <div class="placeholder-text">Device offline</div>
              </div>
            `}
          </div>

          <div class="controls-panel popups">
            <div class="control-section keyboard-section">
              <div class="section-title">Keyboard</div>
              <div class="input-group">
                <input type="text" id="text-input" placeholder="Type text here..." class="text-input">
                <button class="control-btn" id="type-btn">Type</button>
              </div>
              <div class="keyboard-grid">
                <div class="keyboard-row">
                  <button class="keyboard-key" data-key="ESC">Esc</button>
                  <button class="keyboard-key" data-key="F1">F1</button>
                  <button class="keyboard-key" data-key="F2">F2</button>
                  <button class="keyboard-key" data-key="F3">F3</button>
                  <button class="keyboard-key" data-key="F4">F4</button>
                  <button class="keyboard-key" data-key="F5">F5</button>
                  <button class="keyboard-key" data-key="F6">F6</button>
                  <button class="keyboard-key" data-key="F7">F7</button>
                  <button class="keyboard-key" data-key="F8">F8</button>
                  <button class="keyboard-key" data-key="F9">F9</button>
                  <button class="keyboard-key" data-key="F10">F10</button>
                  <button class="keyboard-key" data-key="F11">F11</button>
                  <button class="keyboard-key" data-key="F12">F12</button>
                </div>
                <div class="keyboard-row">
                  <button class="keyboard-key toggle" data-key="CTRL">Ctrl</button>
                  <button class="keyboard-key toggle" data-key="ALT">Alt</button>
                  <button class="keyboard-key toggle" data-key="SHIFT">Shift</button>
                  <button class="keyboard-key toggle" data-key="WIN">Win</button>
                  <button class="keyboard-key" data-key="TAB">Tab</button>
                  <button class="keyboard-key" data-key="CAPS_LOCK">Caps</button>
                  <button class="keyboard-key" data-key="SPACE">Space</button>
                  <button class="keyboard-key" data-key="ENTER">Enter</button>
                </div>
                <div class="keyboard-row">
                  <button class="keyboard-key" data-key="INSERT">Ins</button>
                  <button class="keyboard-key" data-key="DELETE">Del</button>
                  <button class="keyboard-key" data-key="HOME">Home</button>
                  <button class="keyboard-key" data-key="END">End</button>
                  <button class="keyboard-key" data-key="PAGEUP">PgUp</button>
                  <button class="keyboard-key" data-key="PAGEDOWN">PgDn</button>
                  <button class="keyboard-key" data-key="UP">↑</button>
                  <button class="keyboard-key" data-key="LEFT">←</button>
                  <button class="keyboard-key" data-key="DOWN">↓</button>
                  <button class="keyboard-key" data-key="RIGHT">→</button>
                </div>
                <div class="keyboard-row">
                  <button class="keyboard-key" data-keys="CTRL+ALT+DEL">Ctrl+Alt+Del</button>
                  <button class="keyboard-key" data-keys="ALT+TAB">Alt+Tab</button>
                  <button class="keyboard-key" data-keys="CTRL+C">Ctrl+C</button>
                  <button class="keyboard-key" data-keys="CTRL+V">Ctrl+V</button>
                  <button class="keyboard-key" data-keys="CTRL+SHIFT+ESC">TaskMgr</button>
                </div>
              </div>
            </div>

            <div class="control-section sound-section">
              <div class="section-title">Volume Control</div>
              <div class="volume-control">
                <input type="range" id="volume-slider" min="0" max="100" 
                       value="${Math.round((attributes.master_volume || 0) * 100)}" 
                       class="volume-slider">
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

  getBaseUrlFromEntity(entity) {
    // Try to extract base URL from entity attributes
    const attrs = entity.attributes || {};
    if (attrs.base_url) return attrs.base_url;
    
    // Try to get from config entry
    const configEntry = this._hass.config_entries?.entries?.find(
      e => e.domain === 'opencrol' && e.title?.includes(attrs.client_id || '')
    );
    if (configEntry?.data?.host) {
      const port = configEntry.data.port || 8080;
      return `http://${configEntry.data.host}:${port}`;
    }
    
    return null;
  }

  setupScreenInteraction() {
    const screenOverlay = this.querySelector('#screen-overlay');
    const screenImg = this.querySelector('#screen-stream');
    const touchpadPlaceholder = this.querySelector('#touchpad-placeholder');
    const screenContainer = this.querySelector('.screen-container');
    const placeholder = this.querySelector('.screen-placeholder');
    
    // Determine if we're in touchpad mode (screen off/unavailable)
    const isTouchpadMode = !screenImg || screenImg.style.display === 'none' || 
                          (screenContainer && screenContainer.classList.contains('touchpad-mode')) ||
                          (placeholder && placeholder.classList.contains('touchpad-mode'));
    
    if (isTouchpadMode) {
      // Touchpad mode - use relative movement
      this.setupTouchpadMode(screenOverlay || placeholder || screenContainer);
    } else if (screenOverlay && screenImg) {
      // Screen mode - use absolute coordinates
      this._imgElement = screenImg;

      // Handle clicks on screen
      screenOverlay.addEventListener('click', (e) => {
        const rect = screenImg.getBoundingClientRect();
        const x = Math.round((e.clientX - rect.left) * (screenImg.naturalWidth / rect.width));
        const y = Math.round((e.clientY - rect.top) * (screenImg.naturalHeight / rect.height));
        
        this.sendCommand('click', { 
          button: 'left', 
          x: x, 
          y: y 
        });
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

      // Handle mouse movement for visual feedback
      let isDragging = false;
      screenOverlay.addEventListener('mousedown', () => { isDragging = true; });
      screenOverlay.addEventListener('mouseup', () => { isDragging = false; });
      screenOverlay.addEventListener('mousemove', (e) => {
        if (isDragging) {
          const rect = screenImg.getBoundingClientRect();
          const x = Math.round((e.clientX - rect.left) * (screenImg.naturalWidth / rect.width));
          const y = Math.round((e.clientY - rect.top) * (screenImg.naturalHeight / rect.height));
          
          this.sendCommand('move_mouse', { x: x, y: y });
        }
      });

      // Check for screen stream errors (screen off)
      screenImg.addEventListener('error', () => {
        screenImg.style.display = 'none';
        if (screenContainer) screenContainer.classList.add('touchpad-mode');
        if (touchpadPlaceholder) touchpadPlaceholder.style.display = 'flex';
        this.setupTouchpadMode(screenContainer || placeholder);
      });
    }
  }

  setupTouchpadMode(container) {
    if (!container) return;

    let lastX = null;
    let lastY = null;
    let isDown = false;

    // Touchpad-style relative movement
    container.addEventListener('mousedown', (e) => {
      isDown = true;
      lastX = e.clientX;
      lastY = e.clientY;
    });

    container.addEventListener('mouseup', () => {
      isDown = false;
      lastX = null;
      lastY = null;
    });

    container.addEventListener('mousemove', (e) => {
      if (isDown && lastX !== null && lastY !== null) {
        const deltaX = e.clientX - lastX;
        const deltaY = e.clientY - lastY;
        
        // Use scroll command for relative movement (common API pattern)
        // Or implement relative move_mouse_delta if available
        // For now, convert to absolute movement estimate
        this.sendCommand('move_mouse', { 
          x: Math.round(deltaX * 2), // Scale factor for touchpad sensitivity
          y: Math.round(deltaY * 2),
          relative: true // Hint that this is relative movement
        });
        
        lastX = e.clientX;
        lastY = e.clientY;
      }
    });

    // Handle clicks in touchpad mode (tap to click)
    container.addEventListener('click', (e) => {
      if (!isDown || (lastX === null && lastY === null)) {
        // Single tap - left click
        this.sendCommand('click', { button: 'left' });
      }
    });

    // Touch support for mobile
    container.addEventListener('touchstart', (e) => {
      e.preventDefault();
      const touch = e.touches[0];
      lastX = touch.clientX;
      lastY = touch.clientY;
      isDown = true;
    });

    container.addEventListener('touchend', (e) => {
      e.preventDefault();
      if (!isDown || lastX === null) {
        // Tap detected
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
        
        this.sendCommand('move_mouse', { 
          x: Math.round(deltaX * 2),
          y: Math.round(deltaY * 2),
          relative: true
        });
        
        lastX = touch.clientX;
        lastY = touch.clientY;
      }
    });
  }

  attachEventHandlers() {
    // Header buttons
    const powerBtn = this.querySelector('.power-btn');
    if (powerBtn && this._hass && this.config?.entity) {
      powerBtn.addEventListener('click', () => {
        // Use dedicated lock service for safe \"power\" action (lock workstation)
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
        fetch(`${baseUrl}/api/v1/screen/monitor/${index}`, {
          method: 'POST'
        }).catch(() => {});

        // Open full-screen remote desktop overlay
        this.openFullscreenRemote(baseUrl, index);
      });
    });

    // Sound / keyboard popups
    const soundBtn = this.querySelector('.sound-btn');
    if (soundBtn) {
      soundBtn.addEventListener('click', () => {
        this.classList.toggle('show-sound');
      });
    }

    const keyboardBtn = this.querySelector('.keyboard-btn');
    if (keyboardBtn) {
      keyboardBtn.addEventListener('click', () => {
        this.classList.toggle('show-keyboard');
        if (this.classList.contains('show-keyboard')) {
          const textInput = this.querySelector('#text-input');
          if (textInput) {
            textInput.focus();
          }
        }
      });
    }
    // Volume slider (master volume)
    const volumeSlider = this.querySelector('#volume-slider');
    if (volumeSlider) {
      volumeSlider.addEventListener('input', (e) => {
        const value = e.target.value;
        const volumeValue = this.querySelector('#volume-value');
        if (volumeValue) {
          volumeValue.textContent = value + '%';
        }
        this.sendCommand('set_volume', { volume: value / 100 });
      });
    }

    // Type text button
    const typeBtn = this.querySelector('#type-btn');
    const textInput = this.querySelector('#text-input');
    if (typeBtn && textInput) {
      typeBtn.addEventListener('click', () => {
        if (textInput.value) {
          this.sendCommand('type_text', { text: textInput.value });
          textInput.value = '';
        }
      });
      textInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
          typeBtn.click();
        }
      });
    }

    // Control buttons (legacy small controls inside popups)
    this.querySelectorAll('.control-btn[data-action]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const action = btn.dataset.action;
        const button = btn.dataset.button;
        const key = btn.dataset.key;
        const keys = btn.dataset.keys;

        if (action === 'click' && button) {
          this.sendCommand('click', { button: button });
        } else if (action === 'secure_attention') {
          this.sendCommand('secure_attention', {});
        } else if (action === 'send_key') {
          if (keys) {
            this.sendCommand('send_key', { keys: keys });
          } else if (key) {
            this.sendCommand('send_key', { key: key });
          }
        }
      });
    });

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
          // Toggle modifier state; actual combo will be sent when another key is pressed
          if (this._activeModifiers.has(key)) {
            this._activeModifiers.delete(key);
          } else {
            this._activeModifiers.add(key);
          }
          updateModifierStyles();
        } else if (key) {
          // Non-modifier: combine with any active modifiers and send as one combo
          const mods = Array.from(this._activeModifiers);
          const parts = [...mods, key];
          const keysString = parts.join('+');
          this.sendCommand('send_key', { keys: keysString });
          // Clear modifiers after use
          this._activeModifiers.clear();
          updateModifierStyles();
        }
      });
    });

  }

  sendCommand(service, data = {}) {
    const entityId = this.config.entity;
    this._hass.callService('opencrol', service, {
      entity_id: entityId,
      ...data
    });
  }
}

customElements.define('opencrol-remote-card', OpenCtrolRemoteCard);

// Card configuration
window.customCards = window.customCards || [];
window.customCards.push({
  type: 'opencrol-remote-card',
  name: 'OpenCtrol Remote',
  description: 'Remote control card for OpenCtrol devices',
  preview: true,
  documentationURL: 'https://github.com/Kaando2000/opencrol-integration'
});


